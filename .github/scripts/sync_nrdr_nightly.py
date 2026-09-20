#!/usr/bin/env python3
"""Conservative snapshot updates. Never execute upstream code with a write token."""
import argparse
import ast
import base64
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

UPSTREAM = "nrdr/openpilot"
UPSTREAM_BRANCH = "nrdr-nightly"
TARGET = "jetson-trt"
INITIAL_BASE = "b3366b5b56512805be8f0bf832b4981bfd958072"
STATE = ".github/nrdr-nightly-sync.json"
REPORT = "docs/NRDR_NIGHTLY_SYNC.md"
MAX_BLOB = 1024 * 1024
START = "<!-- nrdr-nightly-sync:start -->"
END = "<!-- nrdr-nightly-sync:end -->"

# These areas require explicit integration and hardware/build review.
PROTECTED_PREFIXES = (
  ".github/", "tools/", "panda/", "opendbc_repo/", "openpilot/nrdr/",
  "openpilot/cereal/", "openpilot/common/", "openpilot/selfdrive/car/",
  "openpilot/selfdrive/controls/", "openpilot/selfdrive/monitoring/",
  "openpilot/selfdrive/selfdrived/", "openpilot/selfdrive/modeld/",
  "openpilot/selfdrive/locationd/", "openpilot/selfdrive/pandad/",
  "openpilot/sunnypilot/mads/", "openpilot/sunnypilot/accelerators/",
  "openpilot/sunnypilot/models/", "openpilot/sunnypilot/modeld_v2/",
  "openpilot/sunnypilot/selfdrive/", "openpilot/system/manager/",
  "openpilot/system/hardware/", "openpilot/system/camerad/",
  "openpilot/system/updated/", "openpilot/system/bluetooth/",
  "msgq_repo/", "tinygrad_repo/", "rednose_repo/", "jetlink_repo",
  "openpilot/third_party/",
)
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".css", ".html", ".js", ".svg"}


def protected(path):
  return (not path.startswith(("openpilot/", "docs/")) or path.startswith(PROTECTED_PREFIXES) or "/" not in path or
          path in {REPORT, "openpilot/selfdrive/ui/soundd.py"} or
          path.endswith(("SConscript", "SConstruct")))


def valid_path(path):
  return bool(path) and not path.startswith("/") and "\\" not in path and all(
    part not in {"", ".", ".."} for part in path.split("/")) and not any(ord(c) < 32 for c in path)


def classify(path, before, after, ours):
  if identity(ours) == identity(after):
    return "current"
  if not valid_path(path) or protected(path):
    return "protected integration area"
  if identity(ours) != identity(before):
    return "JetStream differs from previous upstream snapshot"
  for entry in (before, after, ours):
    if entry and (entry["type"] != "blob" or entry["mode"] not in {"100644", "100755"}):
      return "symlink, submodule or unsupported mode"
  if os.path.splitext(path)[1] not in TEXT_SUFFIXES:
    return "binary/build asset or unsupported file type"
  if after and after.get("size", MAX_BLOB + 1) > MAX_BLOB:
    return "file exceeds 1 MiB limit"
  return "apply"


def identity(entry):
  return None if entry is None else {k: entry[k] for k in ("mode", "type", "sha")}


def classify_entries(path, before, after, ours):
  # Tree API sizes are not part of Git identity.
  if identity(ours) == identity(after):
    return "current"
  if identity(ours) != identity(before) and not protected(path):
    return "JetStream differs from previous upstream snapshot"
  return classify(path, before, after, ours)


class GitHub:
  def __init__(self, token):
    self.token = token

  def request(self, method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request("https://api.github.com" + path, data=data, method=method, headers={
      "Authorization": "Bearer " + self.token,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json",
      "User-Agent": "nrdr-jetstream-upstream-sync",
    })
    try:
      with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)
    except urllib.error.HTTPError as error:
      raise RuntimeError(f"GitHub {method} {path}: HTTP {error.code}; no automatic retry of writes") from None

  def tree(self, repo, ref):
    data = self.request("GET", f"/repos/{repo}/git/trees/{ref}?recursive=1")
    if data.get("truncated"):
      raise RuntimeError("Refusing an incomplete Git tree")
    return {x["path"]: x for x in data["tree"] if x["type"] != "tree"}

  def text(self, repo, entry):
    if entry.get("size", MAX_BLOB + 1) > MAX_BLOB:
      raise ValueError("file exceeds 1 MiB limit")
    data = self.request("GET", f"/repos/{repo}/git/blobs/{entry['sha']}")
    if data.get("encoding") != "base64":
      raise ValueError("unsupported blob encoding")
    raw = base64.b64decode(data["content"])
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if digest != entry["sha"] or len(raw) > MAX_BLOB or b"\0" in raw:
      raise ValueError("invalid, oversized or binary blob")
    return raw.decode("utf-8")


def readme_status(readme, sha, applied, pending):
  block = (START + "\n### Daily NRDR nightly updates\n\n"
           f"Last observed snapshot: [`{sha[:12]}`](https://github.com/{UPSTREAM}/commit/{sha}). "
           f"This check applied **{applied}** compatible file updates; **{pending}** paths remain for manual integration. "
           "Daily commits target `jetson-trt`; the comma installer stays pinned. "
           "[Changes and policy](https://github.com/ryanafdahl/nrdr-jetstream/blob/jetson-trt/docs/NRDR_NIGHTLY_SYNC.md).\n" + END)
  if START in readme:
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(END) < readme.index(START):
      raise ValueError("Malformed README sync markers")
    return readme[:readme.index(START)] + block + readme[readme.index(END) + len(END):]
  return readme.rstrip() + "\n\n" + block + "\n"


def plan(api, repo, current_sha, upstream_sha):
  ours = api.tree(repo, current_sha)
  upstream = api.tree(UPSTREAM, upstream_sha)
  state = json.loads(api.text(repo, ours[STATE])) if STATE in ours else {
    "upstream_sha": INITIAL_BASE, "pending": {},
  }
  if state["upstream_sha"] == upstream_sha:
    return [], {"unchanged": True, "pending": len(state.get("pending", {}))}
  previous = api.tree(UPSTREAM, state["upstream_sha"])
  paths = {p for p in set(previous) | set(upstream) if identity(previous.get(p)) != identity(upstream.get(p))}
  paths.update(state.get("pending", {}))
  pending, applied, entries = {}, [], []
  for path in sorted(paths):
    old, new, local = previous.get(path), upstream.get(path), ours.get(path)
    reason = classify_entries(path, old, new, local)
    if reason == "current":
      continue
    if reason == "apply":
      try:
        content = None if new is None else api.text(UPSTREAM, new)
        if content is not None and path.endswith(".py"):
          ast.parse(content, filename=path)
      except (ValueError, UnicodeError, SyntaxError) as error:
        reason = "text/syntax validation failed: " + type(error).__name__
      else:
        entries.append({"path": path, "mode": (new or old)["mode"], "type": "blob",
                        **({"sha": None} if new is None else {"content": content})})
        applied.append(path)
    if reason != "apply":
      pending[path] = reason
  new_state = {"upstream_repo": UPSTREAM, "upstream_branch": UPSTREAM_BRANCH,
               "upstream_sha": upstream_sha, "pending": pending}
  report = ("# Daily NRDR nightly sync\n\n"
            f"Upstream: [{upstream_sha}](https://github.com/{UPSTREAM}/commit/{upstream_sha})\n\n"
            f"Previous observed snapshot: `{state['upstream_sha']}`. Target before this commit: `{current_sha}`.\n\n"
            "The upstream marker records observation, not full integration. Updates only copy ordinary text files "
            "that still match the previous upstream snapshot. Customized files, driving/safety logic, model/Jetlink "
            "integration, OS/build assets, dependencies, and automation require manual review. Unresolved paths "
            "carry forward into subsequent reports. No upstream code runs in the write-token job.\n\n"
            "The workflow checks daily at 10:23 UTC and can run manually. It commits to `jetson-trt`, "
            "then runs the existing source audit against that exact commit. An audit failure is visible in Actions "
            "and does not deploy or roll back the commit. The installer and installed comma remain pinned.\n\n"
            "## Applied files\n\n" + ("\n".join(f"- `{p}`" for p in applied) or "None.") + "\n\n"
            "## Manual integration\n\n" + ("\n".join(f"- `{p}` — {why}" for p, why in pending.items()) or "None.") + "\n")
  for path, content in ((STATE, json.dumps(new_state, indent=2) + "\n"), (REPORT, report),
                        ("README.md", readme_status(api.text(repo, ours["README.md"]), upstream_sha, len(applied), len(pending)))):
    entries.append({"path": path, "mode": "100644", "type": "blob", "content": content})
  return entries, {"unchanged": False, "applied": len(applied), "pending": len(pending), "upstream": upstream_sha}


def run(api, repo, dry_run=False):
  target = api.request("GET", f"/repos/{repo}/git/ref/heads/{TARGET}")["object"]["sha"]
  upstream = api.request("GET", f"/repos/{UPSTREAM}/git/ref/heads/{UPSTREAM_BRANCH}")["object"]["sha"]
  entries, result = plan(api, repo, target, upstream)
  print(json.dumps(result, indent=2))
  if not entries or dry_run:
    return ""
  # Check again before creating the child commit; a concurrent edit must never be overwritten.
  if api.request("GET", f"/repos/{repo}/git/ref/heads/{TARGET}")["object"]["sha"] != target:
    raise RuntimeError("Target moved during planning; next scheduled run will retry")
  tree_sha = api.request("GET", f"/repos/{repo}/git/commits/{target}")["tree"]["sha"]
  tree = api.request("POST", f"/repos/{repo}/git/trees", {"base_tree": tree_sha, "tree": entries})["sha"]
  commit = api.request("POST", f"/repos/{repo}/git/commits", {
    "message": f"Sync compatible NRDR nightly updates from {upstream[:12]}",
    "tree": tree, "parents": [target],
  })["sha"]
  api.request("PATCH", f"/repos/{repo}/git/refs/heads/{TARGET}", {"sha": commit, "force": False})
  print("Committed", commit)
  return commit


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--dry-run", action="store_true")
  args = parser.parse_args()
  repo = os.environ["GITHUB_REPOSITORY"]
  if repo != "ryanafdahl/nrdr-jetstream":
    raise SystemExit("This automation is scoped to ryanafdahl/nrdr-jetstream")
  revision = run(GitHub(os.environ["GH_TOKEN"]), repo, args.dry_run)
  if os.getenv("GITHUB_OUTPUT"):
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
      output.write(f"revision={revision}\n")
