# Daily NRDR nightly sync

Upstream: [31bd1d6a2f9e2af1d645966b6f23e3318ae2f9f1](https://github.com/nrdr/openpilot/commit/31bd1d6a2f9e2af1d645966b6f23e3318ae2f9f1)

Previous observed snapshot: `56b4f1125accca62cf4f0b6d93eb1e01c5439c16`. Target before this commit: `190febd405d0faf4822fe5ab1c890d999d5cf9cf`.

The upstream marker records observation, not full integration. Updates only copy ordinary text files that still match the previous upstream snapshot. Customized files, driving/safety logic, model/Jetlink integration, OS/build assets, dependencies, and automation require manual review. Unresolved paths carry forward into subsequent reports. No upstream code runs in the write-token job.

The workflow checks daily at 10:23 UTC and can run manually. It commits to `jetson-trt`, then runs the existing source audit against that exact commit. An audit failure is visible in Actions and does not deploy or roll back the commit. The installer and installed comma remain pinned.

## Applied files

- `openpilot/selfdrive/ui/sunnypilot/layouts/settings/steering_sub_layouts/lane_change_settings.py`
- `openpilot/sunnypilot/sunnylink/athena/tests/test_sunnylinkd.py`
- `openpilot/sunnypilot/sunnylink/settings_ui.json`
- `openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py`

## Manual integration

- `compile_commands.json` — protected integration area
- `msgq_repo/msgq/ipc_pyx.so` — protected integration area
- `openpilot/common/libparams_c.so` — protected integration area
- `openpilot/nrdr/docs/LANE_CHANGE_TUNING.md` — protected integration area
- `openpilot/nrdr/features/driver_policy/lane_change.py` — protected integration area
- `openpilot/nrdr/features/lateral/lane_change_tuning.py` — protected integration area
- `openpilot/nrdr/features/longitudinal/longitudinal_mpc.py` — protected integration area
- `openpilot/nrdr/features/longitudinal/longitudinal_planner.py` — protected integration area
- `openpilot/nrdr/features/services/sunnylink.py` — protected integration area
- `openpilot/nrdr/hooks/controlsd.py` — protected integration area
- `openpilot/nrdr/hooks/selfdrived.py` — protected integration area
- `openpilot/nrdr/params/generated/keys.py` — protected integration area
- `openpilot/nrdr/params/generated/params_keys.inc` — protected integration area
- `openpilot/nrdr/params/snapshots.py` — protected integration area
- `openpilot/nrdr/params/specs.py` — protected integration area
- `openpilot/nrdr/params/ui_metadata.py` — protected integration area
- `openpilot/nrdr/tests/test_cruise_engagement.py` — protected integration area
- `openpilot/nrdr/tests/test_experimental_button_regressions.py` — protected integration area
- `openpilot/nrdr/tests/test_lane_change_runtime.py` — protected integration area
- `openpilot/nrdr/tests/test_lane_change_tuning.py` — protected integration area
- `openpilot/nrdr/tests/test_legacy_prompt_sound.py` — protected integration area
- `openpilot/nrdr/tests/test_live_tuning.py` — protected integration area
- `openpilot/nrdr/tests/test_no_donation_promotions.py` — protected integration area
- `openpilot/nrdr/tests/test_non_honda_longitudinal.py` — protected integration area
- `openpilot/nrdr/tests/test_numeric_ui_types.py` — protected integration area
- `openpilot/nrdr/tests/test_param_catalog.py` — protected integration area
- `openpilot/nrdr/tests/test_param_snapshots.py` — protected integration area
- `openpilot/nrdr/tests/test_param_ui_metadata.py` — protected integration area
- `openpilot/nrdr/tests/test_sound_volume.py` — protected integration area
- `openpilot/nrdr/tests/test_standstill_gap.py` — protected integration area
- `openpilot/nrdr/tests/test_standstill_gap_native.py` — protected integration area
- `openpilot/nrdr/tests/test_sunnylink_source.py` — protected integration area
- `openpilot/nrdr/tests/test_torque_output_filter.py` — protected integration area
- `openpilot/nrdr/ui/settings/longitudinal_tuning.py` — protected integration area
- `openpilot/nrdr/ui/settings/steer_filters.py` — protected integration area
- `openpilot/nrdr/ui/settings/steer_ratio_tuning.py` — protected integration area
- `openpilot/nrdr/ui/sunnylink/__init__.py` — protected integration area
- `openpilot/nrdr/ui/sunnylink/items/steering.yaml` — protected integration area
- `openpilot/nrdr/ui/sunnylink/pages/cruise.yaml` — protected integration area
- `openpilot/nrdr/ui/sunnylink/pages/steering.yaml` — protected integration area
- `openpilot/selfdrive/assets/sounds/prompt.wav` — binary/build asset or unsupported file type
- `openpilot/selfdrive/car/cruise.py` — protected integration area
- `openpilot/selfdrive/controls/controlsd.py` — protected integration area
- `openpilot/selfdrive/controls/lib/desire_helper.py` — protected integration area
- `openpilot/selfdrive/controls/lib/latcontrol_torque.py` — protected integration area
- `openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/acados_ocp_long.json` — protected integration area
- `openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/c_generated_code/Makefile` — protected integration area
- `openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py` — protected integration area
- `openpilot/selfdrive/controls/lib/longitudinal_planner.py` — protected integration area
- `openpilot/selfdrive/locationd/models/generated/libcar.so` — protected integration area
- `openpilot/selfdrive/modeld/models/dm_warp_1344x760_tinygrad.pkl` — protected integration area
- `openpilot/selfdrive/modeld/models/dm_warp_1928x1208_tinygrad.pkl` — protected integration area
- `openpilot/selfdrive/modeld/models/dmonitoring_model_tinygrad.pkl.chunk01of01` — protected integration area
- `openpilot/selfdrive/modeld/models/driving_tinygrad.pkl.chunk01of06` — protected integration area
- `openpilot/selfdrive/modeld/models/driving_tinygrad.pkl.chunk02of06` — protected integration area
- `openpilot/selfdrive/modeld/models/driving_tinygrad.pkl.chunk03of06` — protected integration area
- `openpilot/selfdrive/modeld/models/driving_tinygrad.pkl.chunk04of06` — protected integration area
- `openpilot/selfdrive/pandad/pandad` — protected integration area
- `openpilot/selfdrive/selfdrived/events.py` — protected integration area
- `openpilot/selfdrive/selfdrived/selfdrived.py` — protected integration area
- `openpilot/selfdrive/ui/soundd.py` — protected integration area
- `openpilot/selfdrive/ui/sunnypilot/ui_state.py` — 745-OP differs from previous upstream snapshot
- `openpilot/sunnypilot/selfdrive/car/cruise_helpers.py` — protected integration area
- `openpilot/sunnypilot/selfdrive/locationd/locationd` — protected integration area
- `openpilot/system/camerad/camerad` — protected integration area
- `openpilot/system/loggerd/bootlog` — binary/build asset or unsupported file type
- `openpilot/system/loggerd/encoderd` — binary/build asset or unsupported file type
- `openpilot/system/loggerd/loggerd` — binary/build asset or unsupported file type
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
