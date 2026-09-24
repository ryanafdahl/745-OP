# Daily NRDR nightly sync

Upstream: [56b4f1125accca62cf4f0b6d93eb1e01c5439c16](https://github.com/nrdr/openpilot/commit/56b4f1125accca62cf4f0b6d93eb1e01c5439c16)

Previous observed snapshot: `e0bf1e63b2ea2bcbe1d48c990d0e6786ccfbe50e`. Target before this commit: `3652ee24fd0777dc2939839aeae87b7619e19e19`.

The upstream marker records observation, not full integration. Updates only copy ordinary text files that still match the previous upstream snapshot. Customized files, driving/safety logic, model/Jetlink integration, OS/build assets, dependencies, and automation require manual review. Unresolved paths carry forward into subsequent reports. No upstream code runs in the write-token job.

The workflow checks daily at 10:23 UTC and can run manually. It commits to `jetson-trt`, then runs the existing source audit against that exact commit. An audit failure is visible in Actions and does not deploy or roll back the commit. The installer and installed comma remain pinned.

## Applied files

- `openpilot/selfdrive/ui/mici/layouts/home.py`

## Manual integration

- `compile_commands.json` — protected integration area
- `openpilot/nrdr/tests/test_no_donation_promotions.py` — protected integration area
- `openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/acados_ocp_long.json` — protected integration area
- `openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/c_generated_code/Makefile` — protected integration area
- `openpilot/selfdrive/locationd/models/generated/libcar.so` — protected integration area
- `openpilot/selfdrive/modeld/models/dm_warp_1344x760_tinygrad.pkl` — protected integration area
- `openpilot/selfdrive/modeld/models/dm_warp_1928x1208_tinygrad.pkl` — protected integration area
- `openpilot/selfdrive/modeld/models/dmonitoring_model_tinygrad.pkl.chunk01of01` — protected integration area
- `openpilot/selfdrive/modeld/models/driving_tinygrad.pkl.chunk01of06` — protected integration area
- `openpilot/selfdrive/selfdrived/events.py` — protected integration area
- `panda/board/obj/body_h7.bin.signed` — protected integration area
- `panda/board/obj/body_h7/bootstub.elf` — protected integration area
- `panda/board/obj/body_h7/main.bin` — protected integration area
- `panda/board/obj/body_h7/main.elf` — protected integration area
- `panda/board/obj/bootstub.body_h7.bin` — protected integration area
- `panda/board/obj/bootstub.panda_h7.bin` — protected integration area
- `panda/board/obj/bootstub.panda_jungle_h7.bin` — protected integration area
- `panda/board/obj/gitversion.h` — protected integration area
- `panda/board/obj/panda_h7.bin.signed` — protected integration area
- `panda/board/obj/panda_h7/bootstub.elf` — protected integration area
- `panda/board/obj/panda_h7/main.bin` — protected integration area
- `panda/board/obj/panda_h7/main.elf` — protected integration area
- `panda/board/obj/panda_jungle_h7.bin.signed` — protected integration area
- `panda/board/obj/panda_jungle_h7/bootstub.elf` — protected integration area
- `panda/board/obj/panda_jungle_h7/main.bin` — protected integration area
- `panda/board/obj/panda_jungle_h7/main.elf` — protected integration area
- `panda/board/obj/version` — protected integration area

## Reviewed decisions

- `openpilot/nrdr/config/backend_env.sh` — Retained comma Connect registration/uploads at the user's request; no Konik migration.
- `openpilot/nrdr/features/driver_policy/mads.py` — Adapted nightly startup-request retry as JetstreamAutoLkas, default off, using normal MADS readiness checks.
- `openpilot/nrdr/hooks/driver_monitoring.py` — Retained driver-monitoring timeouts; excluded nightly's 24-hour timeout overrides.
- `openpilot/nrdr/hooks/events.py` — Integrated longitudinal interlocks previously; retained event reporting, lateral fault handling and existing allowed gears.
- `openpilot/nrdr/hooks/events_sp.py` — Integrated speed-limit messages/chime previously; retained controls-mismatch and turn alerts.
- `openpilot/nrdr/ui/home/layout.py` — Retained comma Connect destination text, consistent with the selected backend.
- `openpilot/nrdr/ui/home/mici.py` — Retained comma Connect destination text and 745-OP branding.
- `openpilot/nrdr/ui/settings/party_tricks.py` — Kept Konik re-registration hidden because this build uses comma Connect.
