import hashlib
import json
import unittest

from sync_nrdr_nightly import classify_entries, plan, readme_status, run, STATE, INITIAL_BASE, UPSTREAM


def blob(content, mode="100644"):
  raw = content.encode()
  return {"sha": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(),
          "mode": mode, "type": "blob", "size": len(raw)}


class FakeAPI:
  def __init__(self, before, after, ours, pending=None):
    self.trees = {}
    self.contents = {}
    for ref, files in ((INITIAL_BASE, before), ("new", after), ("ours", {
      "README.md": "# 745-OP\n", **ours,
      STATE: json.dumps({"upstream_sha": INITIAL_BASE, "pending": pending or {}}),
    })):
      self.trees[ref] = {path: blob(content) for path, content in files.items()}
      self.contents.update({blob(content)["sha"]: content for content in files.values()})

  def tree(self, repo, ref):
    return self.trees[ref]

  def text(self, repo, entry):
    return self.contents[entry["sha"]]


class SyncTests(unittest.TestCase):
  def test_matching_source_updates_despite_repository_metadata(self):
    before, after = blob("a = 1\n"), blob("a = 2\n")
    self.assertEqual(classify_entries("openpilot/system/example.py", before, after, {**before, "url": "other-repo"}), "apply")

  def test_customizations_and_protected_paths_are_deferred(self):
    self.assertIn("differs", classify_entries("openpilot/system/example.py", blob("a"), blob("b"), blob("custom")))
    for path in ("openpilot/nrdr/hooks/events.py", "openpilot/selfdrive/selfdrived/events.py",
                 "panda/board/safety.h", ".github/workflows/run.yml", "launch_env.sh",
                 "openpilot/sunnypilot/accelerators/jetlink/setup.sh"):
      self.assertEqual(classify_entries(path, blob("a"), blob("b"), blob("a")), "protected integration area")

  def test_add_delete_and_already_current(self):
    path = "docs/example.md"
    self.assertEqual(classify_entries(path, None, blob("new"), None), "apply")
    self.assertEqual(classify_entries(path, blob("old"), None, blob("old")), "apply")
    self.assertEqual(classify_entries(path, blob("old"), blob("new"), blob("new")), "current")

  def test_modes_binaries_size_and_paths(self):
    for path, new in (("docs/link.md", blob("x", "120000")), ("assets/model.bin", blob("x")),
                      ("docs/large.md", {**blob("x"), "size": 2**21}), ("../bad.md", blob("x"))):
      self.assertNotEqual(classify_entries(path, None, new, None), "apply")

  def test_plan_applies_only_clean_updates_and_preserves_pending(self):
    clean, custom, pending = "openpilot/system/example.py", "docs/custom.md", "openpilot/nrdr/hooks/events.py"
    api = FakeAPI({clean: "a=1", custom: "old", pending: "disabled"},
                  {clean: "a=2", custom: "new", pending: "disabled"},
                  {clean: "a=1", custom: "ours", pending: "enabled"}, {pending: "previous conflict"})
    entries, result = plan(api, "repo", "ours", "new")
    self.assertEqual((result["applied"], result["pending"]), (1, 2))
    self.assertEqual(next(e["content"] for e in entries if e["path"] == clean), "a=2")
    self.assertNotIn(custom, [e["path"] for e in entries])
    state = json.loads(next(e["content"] for e in entries if e["path"] == STATE))
    self.assertIn(pending, state["pending"])

  def test_invalid_python_is_deferred(self):
    path = "openpilot/system/example.py"
    entries, result = plan(FakeAPI({path: "a=1"}, {path: "def invalid("}, {path: "a=1"}), "repo", "ours", "new")
    self.assertEqual(result["applied"], 0)
    self.assertNotIn(path, [e["path"] for e in entries])

  def test_resolved_pending_is_removed(self):
    path = "docs/custom.md"
    api = FakeAPI({path: "new"}, {path: "new"}, {path: "new"}, {path: "custom"})
    _, result = plan(api, "repo", "ours", "new")
    self.assertEqual(result["pending"], 0)

  def test_readme_section_replaced_without_losing_existing_content(self):
    first = readme_status("# My notes\n", "a" * 40, 1, 2)
    second = readme_status(first, "b" * 40, 3, 4)
    self.assertTrue(second.startswith("# My notes"))
    self.assertEqual(second.count("### Daily NRDR nightly updates"), 1)
    self.assertIn("**4**", second)

  def test_same_snapshot_has_no_commit(self):
    api = FakeAPI({}, {}, {})
    api.trees["new"] = api.trees[INITIAL_BASE]
    entries, result = plan(api, "repo", "ours", INITIAL_BASE)
    self.assertEqual(entries, [])
    self.assertTrue(result["unchanged"])

  def test_concurrent_target_move_prevents_any_write(self):
    api = FakeAPI({}, {"docs/new.md": "new"}, {})
    targets = iter(["ours", "moved"])
    def request(method, path, body=None):
      self.assertEqual(method, "GET")
      return {"object": {"sha": "new" if f"/repos/{UPSTREAM}/" in path else next(targets)}}
    api.request = request
    with self.assertRaisesRegex(RuntimeError, "Target moved"):
      run(api, "repo")


class ReviewedDecisionTests(unittest.TestCase):
  def api(self):
    path = "openpilot/nrdr/hooks/events.py"
    api = FakeAPI({path: "upstream"}, {path: "upstream"}, {path: "retained"})
    review = {"upstream": {k: blob("upstream")[k] for k in ("mode", "type", "sha")},
              "local": {k: blob("retained")[k] for k in ("mode", "type", "sha")},
              "decision": "retain safeguards"}
    state = json.dumps({"upstream_sha": INITIAL_BASE, "pending": {}, "reviewed": {path: review}})
    api.trees["ours"][STATE] = blob(state)
    api.contents[blob(state)["sha"]] = state
    return api, path

  def test_reviewed_difference_is_not_repeated(self):
    api, path = self.api()
    entries, result = plan(api, "repo", "ours", "new")
    self.assertEqual(result["pending"], 0)
    state = json.loads(next(e["content"] for e in entries if e["path"] == STATE))
    self.assertIn(path, state["reviewed"])

  def test_new_upstream_blob_requires_new_review(self):
    api, path = self.api()
    api.trees["new"][path] = blob("new upstream")
    _, result = plan(api, "repo", "ours", "new")
    self.assertEqual(result["pending"], 1)

  def test_local_change_invalidates_review_without_upstream_update(self):
    api, path = self.api()
    api.trees["ours"][path] = blob("local changed")
    entries, result = plan(api, "repo", "ours", INITIAL_BASE)
    self.assertFalse(result["unchanged"])
    self.assertEqual(result["pending"], 1)
    state = json.loads(next(e["content"] for e in entries if e["path"] == STATE))
    self.assertNotIn(path, state["reviewed"])

if __name__ == "__main__":
  unittest.main()
