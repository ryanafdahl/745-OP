# Daily NRDR nightly sync

Upstream: [e0bf1e63b2ea2bcbe1d48c990d0e6786ccfbe50e](https://github.com/nrdr/openpilot/commit/e0bf1e63b2ea2bcbe1d48c990d0e6786ccfbe50e)

Previous observed snapshot: `b3366b5b56512805be8f0bf832b4981bfd958072`. Target before this commit: `20d4eb5c65112fe0bde4425b80ba6a4f8b87f097`.

The upstream marker records observation, not full integration. Updates only copy ordinary text files that still match the previous upstream snapshot. Customized files, driving/safety logic, model/Jetlink integration, OS/build assets, dependencies, and automation require manual review. Unresolved paths carry forward into subsequent reports. No upstream code runs in the write-token job.

The workflow checks daily at 10:23 UTC and can run manually. It commits to `jetson-trt`, then runs the existing source audit against that exact commit. An audit failure is visible in Actions and does not deploy or roll back the commit. The installer and installed comma remain pinned.

## Applied files

None.

## Manual integration

- `openpilot/nrdr/config/backend_env.sh` — protected integration area
- `openpilot/nrdr/features/driver_policy/mads.py` — protected integration area
- `openpilot/nrdr/hooks/driver_monitoring.py` — protected integration area
- `openpilot/nrdr/hooks/events.py` — protected integration area
- `openpilot/nrdr/hooks/events_sp.py` — protected integration area
- `openpilot/nrdr/ui/home/layout.py` — protected integration area
- `openpilot/nrdr/ui/home/mici.py` — protected integration area
- `openpilot/nrdr/ui/settings/party_tricks.py` — protected integration area
- `openpilot/selfdrive/selfdrived/events.py` — protected integration area
