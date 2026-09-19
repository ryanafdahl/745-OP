"""Installer filesystem transactions; these tests never install software."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("installer", Path(__file__).with_name("install_jetson.py"))
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    self.root = Path(self.tmp.name)
    self.candidate, self.live, self.backup = [self.root / name for name in ("candidate", "live", "backup")]
    self.candidate.mkdir()
    (self.candidate / "new").write_text("candidate")

  def test_fresh_install(self):
    self.assertFalse(installer.exchange(self.candidate, self.live, self.backup))
    self.assertTrue((self.live / "new").exists())
    self.assertFalse(self.backup.exists())

  def test_preserves_existing_checkout(self):
    self.live.mkdir()
    (self.live / "local-work").write_text("keep")
    self.assertTrue(installer.exchange(self.candidate, self.live, self.backup))
    self.assertEqual((self.backup / "local-work").read_text(), "keep")
    self.assertTrue((self.live / "new").exists())

  def test_failed_swap_restores_old_checkout(self):
    self.live.mkdir()
    (self.live / "old").write_text("old")
    rename = Path.rename
    def fail_candidate(path, target):
      if path == self.candidate:
        raise OSError("simulated rename failure")
      return rename(path, target)
    with patch.object(Path, "rename", fail_candidate), self.assertRaises(OSError):
      installer.exchange(self.candidate, self.live, self.backup)
    self.assertTrue((self.live / "old").exists())
    self.assertTrue((self.candidate / "new").exists())
    self.assertFalse(self.backup.exists())

  def test_existing_backup_not_overwritten(self):
    self.backup.mkdir()
    with self.assertRaises(RuntimeError):
      installer.exchange(self.candidate, self.live, self.backup)
    self.assertTrue((self.candidate / "new").exists())

  def test_wrong_platform_stops_before_commands(self):
    with patch.object(installer.platform, "system", return_value="Windows"), \
         patch.object(installer, "run") as run, self.assertRaises(RuntimeError):
      installer.main()
    run.assert_not_called()


if __name__ == "__main__":
  unittest.main()
