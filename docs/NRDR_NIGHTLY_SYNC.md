# NRDR nightly integration review · September 20, 2026

Reviewed all nine deferred paths from [NRDR nightly e0bf1e63](https://github.com/nrdr/openpilot/commit/e0bf1e63b2ea2bcbe1d48c990d0e6786ccfbe50e).

**One adapted feature, two previously integrated changes, six retained JetStream behaviors.** This is a selective integration, not an exact nightly mirror. No installation or device-setting change was performed.

## Newly integrated

**Steering → MADS → Retry Startup Lane Centering (Default: OFF)** adds nightly's startup request retry behind the new persistent `JetstreamAutoLkas` toggle. It requires main-cruise engagement to be enabled, requests engagement through the existing MADS state machine, and does not directly activate controls. The option can only be changed offroad in the UI. Once MADS engages, manual disengagement remains respected until main cruise cycles off/on. Turning the option off stops further requests; normal steering controls remain responsible for disengagement.

This is source integration only: the target Params library must be rebuilt before installation, and the new option remains unqualified on physical hardware. The installer remains pinned to the existing build.

## File decisions

- `openpilot/nrdr/config/backend_env.sh` — Retained comma Connect registration/uploads at the user's request; no Konik migration.
- `openpilot/nrdr/features/driver_policy/mads.py` — Adapted nightly startup-request retry as JetstreamAutoLkas, default off, using normal MADS readiness checks.
- `openpilot/nrdr/hooks/driver_monitoring.py` — Retained driver-monitoring timeouts; excluded nightly's 24-hour timeout overrides.
- `openpilot/nrdr/hooks/events.py` — Integrated longitudinal interlocks previously; retained event reporting, lateral fault handling and existing allowed gears.
- `openpilot/nrdr/hooks/events_sp.py` — Integrated speed-limit messages/chime previously; retained controls-mismatch and turn alerts.
- `openpilot/nrdr/ui/home/layout.py` — Retained comma Connect destination text, consistent with the selected backend.
- `openpilot/nrdr/ui/home/mici.py` — Retained comma Connect destination text and JetStream branding.
- `openpilot/nrdr/ui/settings/party_tricks.py` — Kept Konik re-registration hidden because this build uses comma Connect.
- `openpilot/selfdrive/selfdrived/events.py` — Retained communication-failure disengagement/no-entry alerts and Jetlink reconnection guidance.

## Validation and future checks

Six new unit tests cover opt-in/main-cruise gating, startup retries, cancellation, rearming, disabling the option, and already-engaged behavior. They passed locally. Thirteen snapshot-updater tests passed, including stable review records, changed upstream blobs and changed local blobs. The full [source audit](https://github.com/ryanafdahl/nrdr-jetstream/actions/workflows/validate-jetson-trt.yml) runs on the integration commit.

The daily workflow records each decision against both upstream and local Git blob identities. These nine reviewed differences are no longer unresolved items. A later change to either side invalidates its review and returns the file to manual integration; protected source is never silently overwritten.
