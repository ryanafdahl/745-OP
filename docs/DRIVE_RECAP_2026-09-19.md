# Drive analysis · September 19, 2026

## Scope and method

Analyzed all **16 full-rate rlog segments** from the latest drive, separately from the preceding 11-segment parked session. Installed candidate: `b6756fe80c3df2e0bbfde3c512d29e02cf1127b5`; vehicle identified as Honda Clarity. The user reported an EPS firmware change before this drive; this is an observation of that configuration, not a controlled comparison.

The archive contains full route logs and camera recordings, but this analysis uses telemetry and events; it does **not** include a visual review of driving behavior. Raw recordings, location data, device identifiers, and credentials are not published here.

| Drive metric | Result |
| --- | ---: |
| Car-state observation window | 14 min 58.28 s |
| Moving time (vEgo > 0.5 m/s) | 12 min 7.74 s |
| Distance, integrated from vEgo | 7.82 km / 4.86 mi |
| Mean speed, including stops | 19.47 mph |
| Maximum recorded speed | 44.59 mph |
| Model messages | 17,830 |
| Large-model messages | 17,227 (96.62%) |
| Native-model messages | 603, before large-model handoff |
| Valid model messages | 17,829 / 17,830 |

Distance and state durations integrate consecutive car/control samples using the preceding value. Telemetry and execution-time means are arithmetic sample means; p95 uses the sorted sample at index floor(0.95 × (n−1)). UTC alignment was estimated from logged wall-clock/monotonic pairs; results do not rely on the Jetson's previously incorrect clock.

## Jetson continuity and timing

There was an initial USB reader timeout/retry. The large model joined approximately **30.17 seconds after the first native-model message**. Every subsequent recorded model message remained large; no return to native fallback was observed. All 814 Jetlink telemetry readings reported `dead=false`.

| Execution metric | Mean | p95 | Maximum |
| --- | ---: | ---: | ---: |
| Large-model execution, 17,227 samples | 44.36 ms | 45.53 ms | 76.51 ms |
| All model execution, 17,830 samples | 43.82 ms | 45.49 ms | 1,313.47 ms |
| Consecutive model-message interval | 50.00 ms | 51.35 ms | 85.17 ms |

`modelExecutionTime` is the comma's timed model execution call, not isolated Jetson GPU kernel time. The 1.313-second maximum belongs to the **first native-model message**, which was also the sole invalid model message. There were 77 execution samples above 50 ms across both model paths. No consecutive recorded model-message interval exceeded 100 ms; the first execution has no preceding model message to compare. Reported `frameDropPerc` was zero throughout, which does not establish that every internal stage met its deadline.

## Jetson telemetry averages

**814 readings**, analyzed separately from the earlier parked checks:

| Metric | Mean | Minimum | Maximum |
| --- | ---: | ---: | ---: |
| Temperature | 62.96°C | 49.1°C | 83.9°C |
| Memory temperature | 61.33°C | 47.2°C | 82.1°C |
| Power | 12.90 W | 9.51 W | 13.83 W |
| Fan | 2,621 RPM | 1,383 RPM | 4,201 RPM |
| GPU load | 89.39% | 63% | 100% |
| GPU clock | 918 MHz | 918 MHz | 918 MHz |
| Reported supply | 4,944 mV | 4,912 mV | 4,968 mV |

Temperature started at 75.1°C, peaked at 83.9°C, and ended at 49.9°C. GPU clock was lower than the earlier parked readings (1,020 MHz); these logs alone do not establish why. The falling temperature does not qualify all ambient conditions or rule out throttling.

## Controls, calibration, and exceptions

| Recorded state | Approximate duration |
| --- | ---: |
| MADS enabled | 13 min 49.80 s |
| MADS active | 12 min 29.56 s |
| Lateral control active | 12 min 14.20 s |
| Longitudinal control active | 7 min 53.02 s |
| General selfdrive enabled | 8 min 15.59 s |

These fields have different meanings and are not interchangeable. Driver steering/gas overrides, lane-change prompts, and user-disable events were recorded; an active-state change alone does not establish a system failure.

**Unresolved finding:** `steerFaultTemporary` was asserted in **41 episodes totaling 22.96 seconds**, including **19.18 seconds while moving**. Some episodes overlapped lateral-active observations. No permanent steering fault or CAN timeout was recorded. This does not identify the cause or prove that steering behaved correctly; review the vehicle/EPS signals and those intervals before treating the drive as fault-free.

All 3,582 recorded calibration messages reported `calibrated`. Communication, localization, and parameter-estimation events occurred during initial startup and ended by about 7.73 seconds after the first car-state message. They were not observed later in the route's onroad-event stream.

## Conclusion and remaining work

This drive supports **sustained large-model inference after the initial connection**, not general road qualification. Remaining work includes the temporary steering-fault episodes, startup/reconnect behavior, timing outliers, visual output/behavior review, thermal testing, and independently verified offline cold starts. It does not establish that calibration caused the earlier flashing icon or that an EPS change resolved every steering issue.

## Raw-data preservation

A private 3,180,021,760-byte archive on the comma preserves 16 drive rlogs, 11 preceding parked rlogs, system logs, and camera files (64 video files for the drive). SHA-256: `708037abcbcc74771743b3474d862b61b83e5c8684c43e4f37ec2217cadaf8c0`.

Local raw-data transfer was blocked by filesystem permissions. Local aggregate summaries were saved; the raw archive still needs downloading before a factory reset. No video, GPS trace, or raw device log is included in this public report.
