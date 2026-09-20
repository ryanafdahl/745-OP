# Adapted from firestar5683/StarPilot c3e4ec630f41c4baa43254a90f718abd1bf764a1.
# Copyright (c) 2026, firestar5683 and StarPilot contributors.
# MIT license: openpilot/system/bluetooth/LICENSE.
import gzip
from pathlib import Path

import numpy as np

from openpilot.system.bluetooth.preflight import problems, REQUIRED, SERVICE
from openpilot.system.bluetooth.controller import event_label, device_id
from openpilot.system.bluetooth.audio import BluetoothAudioSink


def test_kernel_disabled_is_reported_even_when_runtime_is_present(tmp_path):
  config = tmp_path / "proc/config.gz"
  config.parent.mkdir()
  config.write_bytes(gzip.compress(b"# CONFIG_BT is not set\n"))
  for name in REQUIRED:
    p = tmp_path / name.lstrip("/")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch()
  service = tmp_path / "etc/systemd/system" / SERVICE
  service.parent.mkdir(parents=True)
  service.touch()
  assert problems(tmp_path) == ["OS kernel has Bluetooth disabled"]
  config.write_bytes(gzip.compress(b"CONFIG_BT=y\n"))
  assert problems(tmp_path) == []


def test_controller_ignores_repeats_release_and_analog_sticks():
  assert event_label(1, 304, 1) == "button 304"
  assert event_label(1, 304, 2) is None
  assert event_label(1, 304, 0) is None
  assert event_label(3, 0, 32767) is None
  assert event_label(3, 16, 0) is None
  assert event_label(3, 16, -1) == "d-pad 0: left"
  assert event_label(3, 17, 1) == "d-pad 0: down"


def test_controller_identity_is_stable_and_distinguishes_devices():
  assert device_id(5, 1, 2, "Pad", "AA") == device_id(5, 1, 2, "pad", "aa")
  assert device_id(5, 1, 2, "Pad", "AA") != device_id(5, 1, 2, "Pad", "BB")


def test_pcm_clips_and_duplicates_channels():
  data = BluetoothAudioSink.pcm_bytes(np.array([-2.0, 0, 2.0]))
  assert np.frombuffer(data, dtype=np.int16).tolist() == [-32767, -32767, 0, 0, 32767, 32767]


def test_bluetooth_failure_does_not_interrupt_local_audio():
  from openpilot.selfdrive.ui.soundd import Soundd
  class BrokenSink:
    def submit(self, _samples):
      raise BrokenPipeError
  sound = object.__new__(Soundd)
  sound.get_sound_data = lambda frames: np.ones(frames, dtype=np.float32) * 0.25
  sound.bluetooth_sink = BrokenSink()
  output = np.zeros((4, 1), dtype=np.float32)
  sound.callback(output, 4, None, None)
  assert output[:, 0].tolist() == [0.25] * 4
