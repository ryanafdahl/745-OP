"""Opt-in adaptation of NRDR nightly's startup LKAS request policy."""


class AutoLkas:
  def __init__(self, params=None):
    if params is None:
      from openpilot.common.params import Params
      params = Params()
    self.params = params
    self.armed = False
    self.enabled_prev = False
    self.opted_in_prev = False

  def request(self, CS, main_enabled: bool, events, event_name) -> None:
    opted_in = self.params.get_bool("JetstreamAutoLkas") and main_enabled
    if not opted_in:
      self.armed = False
      self.opted_in_prev = False
      return
    main_available = bool(CS.cruiseState.available)
    if not self.opted_in_prev or not main_available:
      self.armed = True
    self.opted_in_prev = True
    if self.enabled_prev:
      self.armed = False
    if self.armed and main_available and not self.enabled_prev:
      # Only request engagement; the existing MADS state machine owns readiness,
      # brake/gear restrictions, faults and the final control state.
      events.add(event_name.lkasEnable)

  def update(self, enabled: bool) -> None:
    if enabled:
      self.armed = False
    self.enabled_prev = enabled
