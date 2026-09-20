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

class AutoLkasTests(unittest.TestCase):
  def setUp(self):
    from openpilot.nrdr.features.driver_policy.mads import AutoLkas
    self.params = SimpleNamespace(enabled=False)
    self.params.get_bool = lambda key: self.params.enabled
    self.policy = AutoLkas(self.params)
    self.cs = SimpleNamespace(cruiseState=SimpleNamespace(available=True))
    self.events = set()
    self.names = SimpleNamespace(lkasEnable=7)

  def request(self, main=True):
    self.events.clear()
    self.policy.request(self.cs, main, self.events, self.names)
    return bool(self.events)

  def test_default_off_and_main_toggle_required(self):
    self.assertFalse(self.request())
    self.params.enabled = True
    self.assertFalse(self.request(main=False))
    self.assertTrue(self.request())

  def test_initial_block_retries_without_direct_engagement(self):
    self.params.enabled = True
    self.assertTrue(self.request())
    self.policy.update(False)
    self.assertTrue(self.request())
    self.assertFalse(self.policy.enabled_prev)

  def test_manual_disengagement_does_not_reengage(self):
    self.params.enabled = True
    self.assertTrue(self.request())
    self.policy.update(True)
    self.assertFalse(self.request())
    self.policy.update(False)
    self.assertFalse(self.request())

  def test_main_cruise_cycle_rearms(self):
    self.params.enabled = True
    self.request()
    self.policy.update(True)
    self.policy.update(False)
    self.cs.cruiseState.available = False
    self.assertFalse(self.request())
    self.cs.cruiseState.available = True
    self.assertTrue(self.request())

  def test_disabling_option_stops_retries(self):
    self.params.enabled = True
    self.assertTrue(self.request())
    self.params.enabled = False
    self.assertFalse(self.request())
    self.assertFalse(self.policy.armed)

  def test_already_enabled_does_not_request(self):
    self.params.enabled = True
    self.policy.update(True)
    self.assertFalse(self.request())
    self.policy.update(False)
    # The opt-in edge while already enabled must not rearm after cancellation.
    self.assertFalse(self.request())

if __name__ == "__main__":
  unittest.main()
