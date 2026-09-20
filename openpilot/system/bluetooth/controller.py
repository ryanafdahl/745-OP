# Adapted from firestar5683/StarPilot c3e4ec630f41c4baa43254a90f718abd1bf764a1.
# Copyright (c) 2026, firestar5683 and StarPilot contributors.
# MIT license: openpilot/system/bluetooth/LICENSE.
"""Bluetooth HID input inspection adapted from StarPilot wheel_controlsd.

No vehicle actions are assigned. This reader only opens external Bluetooth
input devices while its offroad test panel is visible.
"""
import hashlib
import threading
import time
from pathlib import Path

from openpilot.common.params import Params

EV_KEY = 1
EV_ABS = 3
ABS_HAT0X = 16
ABS_HAT3Y = 23
HAT_EVENT_BASE = 0x10000


def device_id(bus: int, vendor: int, product: int, name: str, uniq: str) -> str:
  identity = f"{bus:04x}:{vendor:04x}:{product:04x}:{name.casefold()}:{uniq.casefold()}"
  return hashlib.sha256(identity.encode()).hexdigest()[:20]


def event_label(event_type: int, code: int, value: int) -> str | None:
  if event_type == EV_KEY and value == 1:
    return f"button {code}"
  if event_type == EV_ABS and ABS_HAT0X <= code <= ABS_HAT3Y and value in (-1, 1):
    vertical = bool((code - ABS_HAT0X) % 2)
    direction = ("down" if value > 0 else "up") if vertical else ("right" if value > 0 else "left")
    return f"d-pad {(code - ABS_HAT0X) // 2}: {direction}"
  return None


class ControllerMonitor:
  def __init__(self):
    self._stop = threading.Event()
    self._lock = threading.Lock()
    self._status = "Press a button on a paired controller"
    self._thread = None

  @property
  def status(self):
    with self._lock:
      return self._status

  def _set_status(self, text):
    with self._lock:
      self._status = text

  def start(self):
    if self._thread is None or not self._thread.is_alive():
      self._stop.clear()
      self._thread = threading.Thread(target=self._run, daemon=True)
      self._thread.start()

  def stop(self):
    self._stop.set()

  def _run(self):
    # Import lazily: unavailable HID support must not prevent UI startup.
    devices = {}
    try:
      import evdev
      params = Params()
      next_scan = 0.0
      while not self._stop.is_set():
        if not params.get_bool("IsOffroad") or not params.get_bool("BluetoothEnabled"):
          self._set_status("Controller test is available offroad with Bluetooth enabled")
          break
        now = time.monotonic()
        if now >= next_scan:
          next_scan = now + 1.0
          current = set(evdev.list_devices())
          for path in list(devices):
            if path not in current:
              devices.pop(path).close()
          for path in current - devices.keys():
            dev = evdev.InputDevice(path)
            # 0x0005 is Bluetooth. Never consume the comma touchscreen or car buttons.
            if dev.info.bustype == 0x0005:
              devices[path] = dev
            else:
              dev.close()
          if not devices:
            self._set_status("No Bluetooth controller input device connected")
        for path, dev in list(devices.items()):
          try:
            for event in dev.read():
              label = event_label(event.type, event.code, event.value)
              if label:
                self._set_status(f"{dev.name}: {label}")
          except BlockingIOError:
            pass
          except OSError:
            devices.pop(path).close()
        self._stop.wait(0.05)
    except Exception as error:
      self._set_status(f"Controller input unavailable: {error}")
    finally:
      for dev in devices.values():
        dev.close()
