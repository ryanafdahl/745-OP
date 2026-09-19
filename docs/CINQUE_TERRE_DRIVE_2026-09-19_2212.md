# Cinque Terre V2 · latest recording, September 19, 2026

## Recording and identity

All **9 full-rate log segments** were analyzed. CarState window: **22:12:10.514–22:20:17.471 UTC**, **486.957 seconds (8:07)**. UTC uses the median wall-clock/monotonic offset from logged messages.

Integrated distance: **0.844 km / 0.525 mi**. Moving time above 0.5 m/s: **127.685 seconds (2:08)**; maximum speed **35.82 mph**, time-weighted mean including stops **3.88 mph**. Most of this recording was stationary, so its averages should not be treated as sustained driving performance.

Jetlink's handshake reported loaded model hash **`09d080f36965bb2a`**, matching precached **Cinque Terre Model V2 (September 08, 2026)**. The post-recording engine-ready parameter matched the full SHA-256 `09d080f36965bb2a0790500452bd328aa03c484d0222aa79d1ad9f021a522aec`.

## Connection and inference

- **9,595 model messages:** 3,994 native, then **5,601 large-model messages (58.37%)**.
- One native-to-large transition after **199.526 seconds** from the first model message; no subsequent return to native.
- Four “no Jetson attached within 45s” retries preceded connection. Once the Jetson appeared, link-ready followed in **25 ms**. This was connection waiting, not a recorded engine build.
- **9,594/9,595 model messages valid**. The only invalid message was the first native startup message; all large-model messages were valid.
- Message interval mean **49.988 ms**, p95 **51.945 ms**, maximum **115.430 ms**; **one gap above 100 ms**.
- Reported frame-drop percentage: mean **0.00733**, max **0.49505**. This field describes the model's reported drops, not every pipeline stage.

| Model-call execution | Messages | Mean | p95 | Maximum |
| --- | ---: | ---: | ---: | ---: |
| Large model | 5,601 | 33.776 ms | 36.933 ms | 101.248 ms |
| Native model | 3,994 | 27.424 ms | 28.101 ms | 1,276.321 ms |

Execution is measured on the comma, not GPU-only time. Three samples exceeded 50 ms: the initial invalid native message and two valid large-model messages (**101.25 / 61.49 ms**) while stationary. Near those two samples, logs reported reply/send delays and brief `commIssue` / `locationdTemporaryError` events; the events cleared in the reviewed interval and no model fallback occurred. This does not identify the underlying cause.

## Jetson telemetry

**267 readings**, all reporting `dead=false`. Each mean uses individual logged values. First/final temperature: **58.0 / 62.2°C**.

| Metric | Samples | Mean | Minimum | Maximum |
| --- | ---: | ---: | ---: | ---: |
| temp_c | 267 | 62.045 | 58 | 66 |
| memory_temp_c | 267 | 60.482 | 56.9 | 64.3 |
| power_w | 267 | 13.223 | 6.71 | 13.84 |
| gpu_load_pct | 267 | 76.629 | 0 | 99 |
| gpu_clock_mhz | 267 | 1020.000 | 1020 | 1020 |
| fan_rpm | 267 | 2682.045 | 2336 | 3056 |
| supply_mv | 267 | 4942.622 | 4928 | 4992 |

Units: temperatures °C, power W, load %, clock MHz, fan RPM, supply mV. These are logged samples, not a complete continuous timeline.

## Vehicle state

Honda Clarity. Lateral-active duration **113.189 s**, MADS active **118.627 s**, MADS enabled **134.055 s**. Selfdrive enabled and longitudinal-active durations were **zero**; MADS lateral operation is represented separately.

Temporary steering-fault flags totaled **8.024 s** across **17 episodes**, including **7.149 s while moving**. Some overlapped the latest lateral-active observation; cause remains unresolved. No permanent steering-fault or CAN-timeout flags were recorded. All **1,935 calibration messages** were calibrated.

## Two Cinque Terre recordings: sample-weighted totals

The earlier recording covered **21:16:23.086–21:34:58.608 UTC**. Pooling it with this recording yields:

| Metric | Combined result |
| --- | ---: |
| Model messages | 31,770 |
| Large-model messages | 26,776 (84.28%) |
| Large-model execution mean | 38.795 ms across 26,776 samples |
| Telemetry readings | 1,271 |
| Temperature mean | 54.214°C |
| Power mean | 13.108 W |
| Fan mean | 1,853.061 RPM |
| GPU load mean | 77.030% |
| GPU clock mean | 1,020 MHz |

Means are weighted by sample count, using unrounded values. Pooled model share includes native connection-wait periods and is not an uptime percentage. Both recordings stayed on the large model after their respective handoffs. Different stationary/moving proportions explain why these are descriptive totals, not a controlled comparison. BMRLNAP results remain separate.

## Private capture

All **54 route files** (9 rlogs, 9 qlogs, 36 video files) and available comma-side diagnostic logs were archived on the comma. Archive size **1,043,261,440 bytes**, SHA-256 **`dd353eff103dcf86f52699bd3b7dae23f09790a0989acd0576e30946982542b9`**. Structured analysis and manifest were saved locally; the raw archive remains on the comma. No video review or independent offline-startup verification was performed.

[Previous Cinque Terre drive](CINQUE_TERRE_DRIVE_2026-09-19.md) · [BMRLNAP drive](DRIVE_RECAP_2026-09-19.md)
