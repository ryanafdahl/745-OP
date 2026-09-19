"""Portable guards for the comma-only staging builder."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("staged_build", Path(__file__).with_name("jetson_staged_build.py"))
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


class StagingGuards(unittest.TestCase):
  def test_separate_clone_allowed(self):
    root = Path("/data/jetson-trt-stage-test")
    self.assertEqual(build.check_staging_path(root, Path("/data/openpilot")), root.resolve())

  def test_live_tree_and_overlaps_refused(self):
    stage = Path("/data/jetson-trt-stage-test")
    for root, live in [
      (Path("/data/openpilot"), Path("/data/openpilot")),
      (stage, stage), (stage, stage / "installed"), (stage, Path("/data")),
      (stage / "nested", Path("/data/openpilot")),
    ]:
      with self.subTest(root=root, live=live), self.assertRaises(RuntimeError):
        build.check_staging_path(root, live)

  def test_symlink_alias_of_live_tree_refused(self):
    stage, live = Path("/data/jetson-trt-stage-test"), Path("/data/openpilot")
    original = Path.resolve
    def resolve(path, *args, **kwargs):
      return original(stage if path == live else path, *args, **kwargs)
    with patch.object(Path, "resolve", resolve), self.assertRaisesRegex(RuntimeError, "overlaps"):
      build.check_staging_path(stage, live)

  def test_wrong_platform_refused_before_git(self):
    with patch.object(build.platform, "system", return_value="Windows"), \
         patch.object(build, "capture") as git, self.assertRaisesRegex(RuntimeError, "AGNOS"):
      build.preflight(Path("/data/jetson-trt-stage-test"), "a" * 40)
    git.assert_not_called()

  def test_failed_preflight_never_starts_build(self):
    with patch.object(build.sys, "argv", ["build", "--expected-commit", "a" * 40, "--build"]), \
         patch.object(build, "preflight", side_effect=RuntimeError("blocked")), \
         patch.object(build, "run_logged") as run, self.assertRaisesRegex(RuntimeError, "blocked"):
      build.main()
    run.assert_not_called()


if __name__ == "__main__":
  unittest.main()
