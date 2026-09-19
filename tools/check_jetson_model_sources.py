#!/usr/bin/env python3
"""Verify the pinned native driving ONNX input, including release-style chunks."""
import hashlib
import json
from pathlib import Path


def verify(root):
  manifest = json.loads((root / "tools/jetson_model_sources.json").read_text())
  for model in manifest["models"]:
    path = root / model["path"]
    chunks = Path(str(path) + ".chunkmanifest")
    if chunks.is_file():
      count = int(chunks.read_text().strip())
      if not 1 <= count <= 100:
        raise ValueError(f"invalid chunk count: {chunks}")
      paths = [Path(f"{path}.chunk{i:02d}of{count:02d}") for i in range(1, count + 1)]
    else:
      paths = [path]
    digest, size = hashlib.sha256(), 0
    for part in paths:
      with part.open("rb") as stream:
        while data := stream.read(1024 * 1024):
          digest.update(data)
          size += len(data)
    if size != model["size"] or digest.hexdigest() != model["sha256"]:
      raise ValueError(f"model input differs from pinned NRDR source: {path}")
    print(f"Verified {model['path']}: {size} bytes, SHA256 {digest.hexdigest()}")


if __name__ == "__main__":
  verify(Path(__file__).resolve().parents[1])
