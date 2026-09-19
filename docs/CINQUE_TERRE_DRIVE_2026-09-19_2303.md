# Cinque Terre V2 drive · September 19, 2026, 23:03 UTC

## Capture

Analyzed **all 20 full-rate rlog segments**, with carState window **23:03:58.968–23:23:03.551 UTC**, **1,144.583 seconds (19:05)**. UTC is reconstructed from logged wall-clock/monotonic offsets.

Integrated vehicle speed gives **14.858 km / 9.232 mi**, moving time **982.153 s (16:22)** above 0.5 m/s, mean speed including stops **29.04 mph**, maximum **74.38 mph**.

All **120 route files** (20 rlogs, 20 qlogs, 80 video files) and **212 comma diagnostic logs** are preserved in a private archive on the comma: **1,698,017,280 bytes**, SHA-256 `d8758213558859b8fabf84eddc054edadec27665113ae7e39391daa65abb1fd6`. Structured analysis and manifest are local. Raw video was not visually reviewed.

The Jetson was offline from the home network. This analysis uses **comma-recorded Jetlink messages and Jetson telemetry**, not a newly retrieved Jetson service journal.

## Model identity and continuity

The route's startup parameters identify **Cinque Terre Model V2 (September 08, 2026)**, internal name CTMV2, and matching engine/spec SHA-256 `09d080f36965bb2a0790500452bd328aa03c484d0222aa79d1ad9f021a522aec`.

- **22,610 model messages:** 401 native startup messages, then **22,209 large-model messages (98.23%)**.
- Large-model handoff occurred **20.103 seconds after the first model message**. No later return to native was recorded.
- **22,609/22,610 messages valid**; the only invalid message was the first native startup message. All large-model messages were valid.
- Message intervals: mean **50.002 ms**, p95 **53.177 ms**, maximum **100.891 ms**; one interval slightly exceeded 100 ms.
- Reported frame-drop percentage was zero throughout.

Startup recorded one USB gadget “No such device” retry. The successful Orin handshake was followed by link-ready in approximately **1.29 s**, then handoff. No subsequent link-loss messages appeared in the route's recorded Jetlink messages. The current USB controller was detached during collection, so the drive's negotiated USB version is not confirmed.

## Execution and telemetry

Large-model execution on the comma: **mean 34.250 ms**, p95 **37.543 ms**, maximum **55.012 ms**, across **22,209 samples**. Native startup: mean **30.563 ms**, maximum **1,166.292 ms** across 401 samples; the maximum was the invalid first message.

Three model execution samples exceeded 50 ms: that startup outlier and two valid large-model samples (**55.012 / 50.170 ms**). These measurements cover the comma's model call, not GPU-only execution.

**1,051 telemetry readings**, all reporting `dead=false`; first temperature **46.5°C**, final **67.7°C**.

| Metric | Samples | Mean | Minimum | Maximum |
| --- | ---: | ---: | ---: | ---: |
| temp_c | 1051 | 67.151 | 46.5 | 71.7 |
| memory_temp_c | 1051 | 65.410 | 44.9 | 69.7 |
| power_w | 1051 | 13.449 | 10.15 | 13.96 |
| gpu_load_pct | 1051 | 78.770 | 35 | 99 |
| gpu_clock_mhz | 1051 | 1020.000 | 1020 | 1020 |
| fan_rpm | 1051 | 3203.826 | 1155 | 3649 |
| supply_mv | 1051 | 4930.131 | 4920 | 4976 |

Units: temperatures °C, power W, GPU load %, clock MHz, fan RPM, supply mV. Means use individual readings. The peak temperature was **71.7°C**, above the previous recordings' 64.5°C and 66.0°C; GPU clock remained 1,020 MHz in the sampled telemetry. Different conditions prevent attributing that temperature difference to a specific cause.

## Vehicle-state findings

Honda Clarity. Recorded durations: lateral active **1,073.007 s (17:53)**, longitudinal active **772.207 s (12:52)**, selfdrive enabled **861.126 s**, MADS active **1,077.129 s**. All **4,551 calibration messages** were calibrated.

Temporary steering-fault flags totaled **9.224 s** across **10 episodes**, including **8.228 s while moving**. Some overlapped the latest lateral-active observation; cause remains unresolved. Permanent steering-fault and CAN-timeout flags were zero.

**Stock forward-collision-warning flag:** six onroadEvents messages carried `stockFcw` in segment 17, spanning **1.013 s** from first to last flagged message. Vehicle speed declined from approximately **22.20 to 19.64 mph**. The latest recorded control state had both lateral and longitudinal active, and brakePressed was false at those observations. Six messages are not six separate incidents; the flag alone does not establish the traffic situation, collision risk, or cause.

Startup communication/localization events cleared near startup. The route also recorded driver overrides, lane-change prompts, a road-edge lane-change-unavailable alert, and a manual-speed-control-required alert. Model continuity does not determine the quality of those driving interactions.

## Three Cinque Terre recordings: sample-weighted totals

Windows: **21:16:23–21:34:59**, **22:12:10–22:20:17**, and **23:03:59–23:23:04 UTC**.

| Metric | Pooled result |
| --- | ---: |
| All model messages | 54,380 |
| Large-model messages | 48,985 |
| Large-model execution mean | 36.734 ms across 48,985 samples |
| Telemetry readings | 2,322 |
| Mean temperature | 60.070°C |
| Mean power | 13.263 W |
| Mean fan speed | 2,464.454 RPM |
| Mean GPU load | 77.817% |
| Mean GPU clock | 1,020 MHz |

These are sample-weighted means using unrounded values, not means of rounded drive averages. Native startup/connection waiting remains part of the overall model counts. BMRLNAP is excluded. These are three observed recordings, not continuous uptime or an independent offline-startup qualification.

[Previous recording](CINQUE_TERRE_DRIVE_2026-09-19_2212.md) · [First Cinque Terre drive](CINQUE_TERRE_DRIVE_2026-09-19.md)
