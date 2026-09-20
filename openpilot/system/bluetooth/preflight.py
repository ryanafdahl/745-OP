# Adapted from firestar5683/StarPilot c3e4ec630f41c4baa43254a90f718abd1bf764a1.
# Copyright (c) 2026, firestar5683 and StarPilot contributors.
# MIT license: openpilot/system/bluetooth/LICENSE.
"""Read-only Bluetooth runtime check; never installs packages or changes the radio."""
import gzip
import json
from pathlib import Path

REQUIRED = (
  "/usr/comma/bluetooth-radio",
  "/usr/bin/bluetoothctl",
  "/usr/bin/btattach",
  "/usr/bin/bluealsa",
  "/usr/bin/aplay",
  "/usr/lib/aarch64-linux-gnu/alsa-lib/libasound_module_pcm_bluealsa.so",
)
SERVICE = "starpilot-bluetooth-radio.service"


def problems(root: Path = Path("/")) -> list[str]:
  issues = []
  try:
    config = gzip.decompress((root / "proc/config.gz").read_bytes()).decode()
    if "CONFIG_BT=y" not in config and "CONFIG_BT=m" not in config:
      issues.append("OS kernel has Bluetooth disabled")
  except (OSError, EOFError, UnicodeError):
    if not (root / "sys/class/bluetooth").is_dir():
      issues.append("Bluetooth kernel support could not be verified")
  missing = [p for p in REQUIRED if not (root / p.lstrip("/")).is_file()]
  if missing:
    issues.append("Bluetooth OS runtime is missing: " + ", ".join(missing))
  if not any((root / base / SERVICE).is_file() for base in ("etc/systemd/system", "usr/lib/systemd/system", "lib/systemd/system")):
    issues.append("Bluetooth radio service is missing")
  return issues


if __name__ == "__main__":
  issues = problems()
  print(json.dumps({"ready_for_enable": not issues, "problems": issues}, indent=2))
  raise SystemExit(bool(issues))
