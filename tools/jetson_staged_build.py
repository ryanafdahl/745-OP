#!/usr/bin/env python3
"""Build a fresh comma 4 staging checkout; never install, launch services, or publish."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

BASE = "b3366b5b56512805be8f0bf832b4981bfd958072"
JETLINK = "a01fcae9709cb4924854f0c52806849c62dec5c9"


def require(condition, message):
  if not condition:
    raise RuntimeError(message)


def check_staging_path(root, live):
  root, live = root.resolve(), live.resolve()
  require(root.parent == Path("/data").resolve() and root.name.startswith("jetson-trt-stage-"),
          "use a fresh /data/jetson-trt-stage-<revision> clone")
  require(root != live and not root.is_relative_to(live) and not live.is_relative_to(root),
          "staging checkout overlaps the installed /data/openpilot tree")
  return root


def capture(root, *command):
  return subprocess.check_output(command, cwd=root, text=True).strip()


def preflight(root, expected):
  check_staging_path(root, Path("/data/openpilot"))
  require(platform.system() == "Linux" and platform.machine() == "aarch64" and Path("/AGNOS").is_file(),
          "native build requires an AGNOS comma 4, not a desktop or Jetson")
  model = Path("/sys/firmware/devicetree/base/model").read_text().strip("\0\n")
  require(model == "comma mici", f"expected comma 4 (comma mici), found {model!r}")
  agnos = Path("/VERSION").read_text().strip()
  versions = re.findall(r'export AGNOS_VERSION="([^"]+)"', (root / "launch_env.sh").read_text())
  require(len(versions) == 1 and agnos == versions[0],
          f"AGNOS {agnos!r} does not match source requirement {versions}; do not auto-upgrade")
  require((root / ".git").is_dir(), "use an independent clone, not a linked worktree")
  require(re.fullmatch(r"[0-9a-f]{40}", expected), "--expected-commit must be a full commit SHA")
  head = capture(root, "git", "rev-parse", "HEAD")
  require(head == expected, f"HEAD {head} differs from reviewed commit {expected}")
  require(not capture(root, "git", "status", "--porcelain", "--untracked-files=normal"),
          "checkout is not clean; preserve it and use a fresh clone")
  require(not (root / "prebuilt").exists(), "unexpected prebuilt shortcut")
  require(not (root / ".sconsign.dblite").exists(), "build history exists; use a fresh clone for this evidence run")
  submodules = capture(root, "git", "submodule", "status", "--recursive")
  require(all(line.startswith(" ") for line in subprocess.check_output(
    ["git", "submodule", "status", "--recursive"], cwd=root, text=True).splitlines()),
    "submodule is uninitialized, conflicted, or at the wrong revision")
  require(capture(root / "jetlink_repo", "git", "rev-parse", "HEAD") == JETLINK, "wrong Jetlink pin")
  subprocess.run(["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=root, check=True)
  # Git LFS reports '-' for a pointer and '+' for hydrated content.
  lfs = capture(root, "git", "lfs", "ls-files")
  require(all(len(line.split(maxsplit=2)) == 3 and line.split(maxsplit=2)[1] == "+"
              for line in lfs.splitlines()), "unhydrated LFS assets; run git lfs pull in this staging clone")
  require(shutil.disk_usage(root).free >= 12 * 1024**3, "need at least 12 GiB free for staging build and logs")
  require(Path(sys.prefix).resolve() == Path("/usr/local/venv").resolve(),
          "run with /usr/local/venv/bin/python3")
  subprocess.run([sys.executable, "-c", "import SCons, numpy, zmq, capnp, zstandard"], cwd=root, check=True)
  return {"commit": head, "base": BASE, "jetlink": JETLINK, "model": model,
          "agnos": agnos, "python": sys.version, "submodules": submodules}


def run_logged(root, command, env, log):
  print("+ " + " ".join(map(str, command)), flush=True)
  with log.open("w") as stream:
    result = subprocess.run(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
  require(result.returncode == 0, f"command failed ({result.returncode}); see {log}")


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--expected-commit", required=True)
  parser.add_argument("--build", action="store_true", help="without this, only read-only preflight runs")
  parser.add_argument("--jobs", type=int, default=2)
  args = parser.parse_args()
  require(1 <= args.jobs <= 4, "--jobs must be between 1 and 4")
  root = Path(__file__).resolve().parents[1]
  report = preflight(root, args.expected_commit)
  print(json.dumps(report, indent=2), flush=True)
  if not args.build:
    print("Preflight passed. No build or device configuration changes performed.")
    return
  # Logs live outside the checkout, so failures preserve both source and evidence.
  output = Path("/data/jetson-trt-evidence") / (time.strftime("%Y%m%d-%H%M%S") + "-" + report["commit"][:12])
  output.mkdir(parents=True, exist_ok=False)
  print(f"Build evidence: {output}", flush=True)
  env = os.environ.copy()
  env.update(PYTHONPATH=os.pathsep.join(str(root / p) for p in ("", "jetlink_repo")),
             PATH="/usr/local/venv/bin:/usr/comma/shims:" + env.get("PATH", ""),
             NRDR_BASE=BASE, JETLINK_PIN=JETLINK, PREBUILT_ALL_CAMERAS="1",
             OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
  for key in ("SKIP_TINYGRAD_COMPILE", "DEV", "DEVICE", "OPENPILOT_PREFIX", "SCONSFLAGS"):
    env.pop(key, None)
  report["status"] = "IN_PROGRESS"
  try:
    run_logged(root, [sys.executable, "tools/jetson_source_audit.py"], env, output / "source-audit.log")
    run_logged(root, [sys.executable, "-m", "pip", "freeze"], env, output / "dependencies.txt")
    run_logged(root, [sys.executable, "-m", "SCons", "--minimal", "--cache-disable", f"-j{args.jobs}"],
               env, output / "build.log")
    run_logged(root, [sys.executable, "openpilot/nrdr/tools/release/validate_model_artifacts.py", str(root)],
               env, output / "model-assets.log")
    # Exercise freshly built bindings and deserialize the freshly built warp.
    # No Params instance, daemon, camera, manager, or panda is started here.
    smoke = (
      "import json; from openpilot.common.params import Params; "
      "from openpilot.cereal import messaging; "
      "from openpilot.sunnypilot.accelerators.jetlink.warp_cache import device_geometry, load_warp, warp_path; "
      "g=device_geometry(); w=load_warp(*g); "
      "m=messaging.new_message('modelDataV2SP'); "
      "m.modelDataV2SP.bigModelAvailable=False; "
      "print(json.dumps({'warp':str(warp_path(*g)), 'schema_bytes':len(m.to_bytes())}))"
    )
    run_logged(root, [sys.executable, "-c", smoke], env, output / "native-smoke.log")
    camera = root / "openpilot/system/camerad/camerad"
    require(camera.is_file() and os.access(camera, os.X_OK), "missing executable camerad")
    # Hash artifacts without loading or executing them.
    artifacts = {}
    for folder in ("openpilot/common", "openpilot/cereal", "openpilot/system/camerad",
                   "openpilot/selfdrive/modeld/models", "openpilot/sunnypilot/accelerators/jetlink/models"):
      for path in sorted((root / folder).rglob("*")):
        if path.is_file() and (path.suffix in (".so", ".pkl") or ".pkl.chunk" in path.name or path == camera):
          with path.open("rb") as stream:
            artifacts[str(path.relative_to(root))] = hashlib.file_digest(stream, "sha256").hexdigest()
    (output / "artifact-sha256.json").write_text(json.dumps(artifacts, indent=2) + "\n")
    report["status"] = "BUILD_AND_SMOKE_PASSED"
    report["next_gate"] = "isolated native camera/model inference, then Jetson inference and fallback"
  except BaseException as exc:
    report["status"] = "FAILED"
    report["error"] = str(exc)
    raise
  finally:
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Result: {report['status']}; evidence: {output}", flush=True)
  print("Staged build only. No installation, services, firmware flashing, publishing, or vehicle test performed.")


if __name__ == "__main__":
  main()
