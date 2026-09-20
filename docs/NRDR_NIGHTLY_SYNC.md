# NRDR nightly integration review · September 20, 2026

Reviewed all nine deferred paths from [NRDR nightly e0bf1e63](https://github.com/nrdr/openpilot/commit/e0bf1e63b2ea2bcbe1d48c990d0e6786ccfbe50e).

**One adapted feature, two previously integrated changes, six retained 745-OP behaviors.** This is a selective integration, not an exact nightly mirror. Installed September 20 as `92c539b5d737915db3b3976967a4ff4080328145`, after on-device build and compatibility checks. The new option remains OFF.

## Newly integrated

**Steering → MADS → Retry Startup Lane Centering (Default: OFF)** adds nightly's startup request retry behind the new persistent `JetstreamAutoLkas` toggle. It requires main-cruise engagement to be enabled, requests engagement through the existing MADS state machine, and does not directly activate controls. The option can only be changed offroad in the UI. Once MADS engages, manual disengagement remains respected until main cruise cycles off/on. Turning the option off stops further requests; normal steering controls remain responsible for disengagement.

The target Params library and full startup build completed on the comma; all 12 compatibility tests passed. A 10-second startup sample showed UI, hardwared, pandad and jetlinkd running in all 21 managerState updates. No driving qualification of the opt-in behavior is claimed. The installer branch now points to `92c539b`.

## File decisions

- `openpilot/nrdr/config/backend_env.sh` — Retained comma Connect registration/uploads at the user's request; no Konik migration.
- `openpilot/nrdr/features/driver_policy/mads.py` — Adapted nightly startup-request retry as JetstreamAutoLkas, default off, using normal MADS readiness checks.
- `openpilot/nrdr/hooks/driver_monitoring.py` — Retained driver-monitoring timeouts; excluded nightly's 24-hour timeout overrides.
- `openpilot/nrdr/hooks/events.py` — Integrated longitudinal interlocks previously; retained event reporting, lateral fault handling and existing allowed gears.
- `openpilot/nrdr/hooks/events_sp.py` — Integrated speed-limit messages/chime previously; retained controls-mismatch and turn alerts.
- `openpilot/nrdr/ui/home/layout.py` — Retained comma Connect destination text, consistent with the selected backend.
- `openpilot/nrdr/ui/home/mici.py` — Retained comma Connect destination text and 745-OP branding.
- `openpilot/nrdr/ui/settings/party_tricks.py` — Kept Konik re-registration hidden because this build uses comma Connect.
- `openpilot/selfdrive/selfdrived/events.py` — Retained communication-failure disengagement/no-entry alerts and Jetlink reconnection guidance.

## Validation and future checks

Six new unit tests cover opt-in/main-cruise gating, startup retries, cancellation, rearming, disabling the option, and already-engaged behavior. They passed locally. Thirteen snapshot-updater tests passed, including stable review records, changed upstream blobs and changed local blobs. The full [source audit](https://github.com/ryanafdahl/745-OP/actions/workflows/validate-jetson-trt.yml) runs on the integration commit.

The daily workflow records each decision against both upstream and local Git blob identities. These nine reviewed differences are no longer unresolved items. A later change to either side invalidates its review and returns the file to manual integration; protected source is never silently overwritten.
