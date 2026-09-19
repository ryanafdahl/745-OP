import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.check_jetson_model_sources import verify


class ModelInputTests(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    self.root = Path(self.tmp.name)
    (self.root / "tools").mkdir()
    self.data = b"native-model-input"
    self.model = self.root / "model.onnx"
    entry = {"path": "model.onnx", "size": len(self.data), "sha256": hashlib.sha256(self.data).hexdigest()}
    (self.root / "tools/jetson_model_sources.json").write_text(json.dumps({"models": [entry]}))

  def test_missing_source_rejected(self):
    with self.assertRaises(FileNotFoundError):
      verify(self.root)

  def test_whole_model_verified(self):
    self.model.write_bytes(self.data)
    verify(self.root)

  def test_chunked_model_verified(self):
    Path(str(self.model) + ".chunkmanifest").write_text("2")
    Path(str(self.model) + ".chunk01of02").write_bytes(self.data[:5])
    Path(str(self.model) + ".chunk02of02").write_bytes(self.data[5:])
    verify(self.root)

  def test_missing_chunk_rejected(self):
    Path(str(self.model) + ".chunkmanifest").write_text("2")
    Path(str(self.model) + ".chunk01of02").write_bytes(self.data[:5])
    with self.assertRaises(FileNotFoundError):
      verify(self.root)

  def test_corrupt_same_size_model_rejected(self):
    self.model.write_bytes(b"x" * len(self.data))
    with self.assertRaises(ValueError):
      verify(self.root)


if __name__ == "__main__":
  unittest.main()
