# NRDR nightly compatibility update

Upstream reviewed: `nrdr/openpilot:nrdr-nightly`, **e0bf1e63b2ea2bcbe1d48c990d0e6786ccfbe50e**.
Retained base: **b3366b5b56512805be8f0bf832b4981bfd958072**.
Install candidate: **87e530f8914949b28e1fa00933b3297b7d0ee346**.

## September 20 follow-up

All nine deferred files were reviewed. Startup LKAS request retry is now a default-off source option; comma Connect, monitoring, fault alerts and Jetlink reconnect behavior are retained. [Per-file decisions and validation](NRDR_NIGHTLY_SYNC.md). The install candidate above remains unchanged; the new option is not deployed.

## Previously applied

- `openpilot/nrdr/hooks/events.py`: longitudinal operation requires closed doors, latched seat belt, parking brake released, and the existing allowed-gear policy.
- `openpilot/nrdr/hooks/events_sp.py`: clearer active/pending speed-limit notifications, including upstream's single confirmation chime.
- Six regression tests exercise interlocks, gear compatibility, event preservation, and absence of lateral exemptions.

## Retained behavior

Driver-monitoring timeouts, communication-failure disengagement and no-entry alerts, controls-mismatch and turn warnings, event filtering, MADS activation, and allowed gears retain JetStream's existing behavior. Registration and uploads remain on comma Connect; Konik migration and its re-registration button were not ported.

Jetlink, NRDR JetStream branding, native-model fallback, and model caches remain unchanged. This is a selective compatibility port, not the complete nightly snapshot.

## Validation

[Source audit](https://github.com/ryanafdahl/nrdr-jetstream/actions/runs/35476805824) passed: 75 portable tests twice, source syntax/import checks, native model inputs, and protected-tree checks. The NRDR-tree audit at that revision allowed only the two reviewed hook files to differ from the clean base; the other protected trees remain exact matches.

The six new tests also passed using the comma's Python runtime, before and after installation. A separate runtime check verified the speed-limit alert text and preservation of mismatch/turn event definitions.

Earlier drive reports describe the prior version. No driving result for this compatibility update is claimed here.
