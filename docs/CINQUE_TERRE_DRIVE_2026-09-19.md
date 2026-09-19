# Cinque Terre V2 drive recap · September 19, 2026

## Capture and method

Analyzed all **19 full-rate rlog segments** covering **21:16:23.086–21:34:58.608 UTC** (carState observation window, **1,115.523 seconds / 18 min 36 s**). UTC is reconstructed from the median wall-clock/monotonic offset in logged messages. Speed integration gives **14.85 km / 9.23 mi**; maximum **65.46 mph**, time-weighted mean **29.78 mph**, moving time **15 min 43 s** above 0.5 m/s.

A private, checksum-verified archive on the comma contains all **114 route files** (19 rlogs, 19 qlogs, and 76 video files) plus **161 comma-side diagnostic log files**. Raw capture is **2,383,216,640 bytes**. Windows filesystem errors prevented downloading that archive to the workstation; structured analyses and its manifest were retrieved. No video review was performed. This report contains aggregate measurements only.

## Model identity and continuity

The route's Jetlink messages name **Cinque Terre Model V2 (September 08, 2026)**. Post-drive `JetlinkEngineReady` and `JetlinkSpec` match SHA-256 `09d080f36965bb2a0790500452bd328aa03c484d0222aa79d1ad9f021a522aec` and size **766,040,736 bytes**.

- **22,175 model messages:** 1,000 native startup messages followed by **21,175 large-model messages (95.49% of the complete recording)**.
- One native-to-large transition, **50.036 seconds after the first model message**; no subsequent return to native.
- **22,174/22,175 valid messages**; the only invalid message was the first native startup message. All recorded large-model messages were valid.
- Model message intervals: mean **50.003 ms**, p95 **51.948 ms**, maximum **81.710 ms**; no interval above 100 ms.
- Reported `frameDropPerc` was zero throughout. This field is not a measurement of every pipeline stage.

Before handoff, the log recorded a USB reader timeout and retry. The next Jetlink handshake was followed by link-ready in approximately **2.16 seconds**. Its generic “not built yet” message does not establish that a full build occurred: the engine had already been precached at 21:14:25 UTC. Subsequent frame timing messages and fresh telemetry support active Jetson inference during the route.

## Execution and telemetry

Large-model execution measures the model call on the comma, not GPU-only time.

| Execution population | Count | Mean | p95 | Maximum |
| --- | ---: | ---: | ---: | ---: |
| Cinque Terre large model | 21,175 | 40.123 ms | 42.025 ms | 70.814 ms |
| Native startup | 1,000 | 28.077 ms | 27.525 ms | 1,285.067 ms |

There were **76 execution samples above 50 ms** across both paths. The largest was the initial invalid native-model message.

Telemetry comprises **1,004 readings**, all with `dead=false`. Means are calculated from individual readings, not rounded per-segment means. Each metric below has 1,004 values.

| Metric | Mean | Minimum | Maximum |
| --- | ---: | ---: | ---: |
| Temperature | 52.131°C | 42.5°C | 64.5°C |
| Memory temperature | 50.193°C | 40.8°C | 62.7°C |
| Power | 13.078 W | 10.93 W | 13.70 W |
| GPU load | 77.136% | 35% | 100% |
| GPU clock | 1,020 MHz | 1,020 MHz | 1,020 MHz |
| Fan | 1,632.605 RPM | 642 RPM | 2,823 RPM |
| Supply voltage | 4,956.064 mV | 4,928 mV | 4,968 mV |

First temperature was **48.2°C**, final **64.4°C**. These are logged telemetry readings, not a continuous one-second series.

## Vehicle-state observations

Honda Clarity; openpilot longitudinal control reported enabled in car parameters. Integrated state durations: lateral active **1,022.813 s**, longitudinal active **649.650 s**, selfdrive enabled **782.978 s**, MADS active **1,031.115 s**. These fields have different meanings and need not have equal durations.

Temporary steering-fault flags occurred in **28 episodes**, totaling **12.169 s**, including **11.193 s while moving**. Some overlapped the latest observed lateral-active state; cause remains unresolved. Permanent steering-fault and CAN-timeout flags were zero in the analyzed samples.

All **4,451 calibration messages** were calibrated. Startup communication/localization events, driver overrides, lane-change prompts, reverse, and user-disable events were recorded. The largest execution outlier was at startup. Model continuity alone does not establish steering quality.

## Comparison with the earlier drive

| Measurement | BMRLNAP v4 | Cinque Terre V2 |
| --- | ---: | ---: |
| Recording duration | 14:58 | 18:36 |
| Distance | 7.82 km | 14.85 km |
| Large-model messages | 17,227 / 17,830 | 21,175 / 22,175 |
| Large-model mean execution | 44.36 ms | 40.12 ms |
| Telemetry readings | 814 | 1,004 |
| Mean temperature | 62.96°C | 52.13°C |
| Peak temperature | 83.9°C | 64.5°C |
| Mean power | 12.90 W | 13.08 W |
| Mean fan speed | 2,621 RPM | 1,633 RPM |
| Temporary steering-fault duration | 22.96 s | 12.17 s |

Keep each model's results separate. These were different drives with different conditions; the comparison does not isolate a model-related performance or thermal improvement. Fully offline startup was not independently established by this analysis.

[Earlier drive report](DRIVE_RECAP_2026-09-19.md) · [Parked checks and preparation history](HARDWARE_CHECK_HISTORY_2026-09-19.md)
