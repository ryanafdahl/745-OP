"""Regression checks for the safeguarded nightly compatibility port."""
import unittest
from types import SimpleNamespace
from opendbc.car import structs
from openpilot.nrdr.hooks import events

Gear = structs.CarState.GearShifter

class NightlyCompatibilityTests(unittest.TestCase):
  def state(self, **changes):
    return SimpleNamespace(**dict(dict(doorOpen=False, seatbeltUnlatched=False, parkingBrake=False, gearShifter=Gear.drive), **changes))

  def test_drive_is_allowed(self):
    self.assertTrue(events.allow_longitudinal(self.state(), (), "honda"))

  def test_each_interlock_blocks_longitudinal(self):
    for flag in ("doorOpen", "seatbeltUnlatched", "parkingBrake"):
      with self.subTest(flag=flag):
        self.assertFalse(events.allow_longitudinal(self.state(**{flag: True}), (), "honda"))

  def test_disallowed_gears_remain_blocked(self):
    for gear in (Gear.park, Gear.reverse, Gear.neutral, Gear.low):
      with self.subTest(gear=gear):
        self.assertFalse(events.allow_longitudinal(self.state(gearShifter=gear), (), "honda"))

  def test_platform_gear_policy_is_preserved(self):
    self.assertTrue(events.allow_longitudinal(self.state(gearShifter=Gear.low), (Gear.low,), "honda"))
    self.assertFalse(events.allow_longitudinal(self.state(gearShifter=Gear.low, parkingBrake=True), (Gear.low,), "honda"))

  def test_car_events_are_not_suppressed(self):
    original = [object(), object()]
    self.assertIs(events.filter_car_events(original), original)

  def test_lateral_exemptions_are_not_added(self):
    for name in range(256):
      self.assertFalse(events.keep_lateral_active(name))

if __name__ == "__main__":
  unittest.main()
