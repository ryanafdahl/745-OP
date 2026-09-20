# Hardware check history · September 19, 2026

Snapshot of documented checks and preparation through 21:14 UTC. For subsequent Cinque Terre drive verification, see [the latest drive analysis](CINQUE_TERRE_DRIVE_2026-09-19.md).


NRDR openpilot for **comma 4**, with **Jetson Orin Nano Super** acceleration through USB Jetlink and TensorRT. The native small-model path remains available as fallback.

**Status:** installed and booted on comma 4; live large-model inference verified while parked and across one analyzed drive. Experimental—sustained reliability, offline cold starts, reconnect/fallback, and vehicle operation are not yet qualified.

## Install

Factory reset the comma 4, connect to Wi-Fi, choose **Custom Software**, and enter:

```text
ryanafdahl/nrdr-jetson
```

Keep stable power and internet through download and first-boot compilation. No SSH or staging build is required. Target OS: **AGNOS 19.7**; the launcher handles any required OS update.

The [compiled installer](https://installer.comma.ai/ryanafdahl/nrdr-jetson) installs branch `nrdr-jetson` from [ryanafdahl/openpilot](https://github.com/ryanafdahl/openpilot/tree/nrdr-jetson). Old entries `nrdr-op-jetson-trt` and `nrdr-OP-jetson-trt` still work. Renaming does not require reinstalling.

## Connect the Jetson

**Calibration first (user-reported workaround):** before plugging in the Jetson, complete the comma's normal driving calibration using a known-working native setup, then park and connect the accelerator. The user reported that connecting before calibration left the GPU icon flashing grey indefinitely. This sequence has not been independently verified as a fix; grey flashing also occurs during connection waits, downloads, or failures. This note does not qualify this experimental build for road use.

1. Install the matching [Jetlink server](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md) separately; the comma installer does not install it.
2. Power the Jetson separately, with a supply suitable for **25 W mode**. Connect a **USB 3 data cable: Jetson USB-A → comma USB-C**.
3. While offroad, enable **Settings → Models → Accelerator Link**. Start with the default big model.
4. Complete initial model download and engine preparation online. Cached engines can load without rebuilding; fully offline startup of the connected pair still needs verification.

Jetlink is opt-in (`JetlinkEnabled`). A flashing grey GPU icon means preparation or waiting, **not necessarily compilation**. Check the Models panel for the actual stage. A ready icon alone does not prove live inference.

## Verified hardware results · September 19, 2026

| Check | Observation |
| --- | --- |
| Live model | BMRLNAP Model v4, August 30, 2026; SHA prefix `a086d5249fc308bb` |
| Parked checks | 760/760 messages had `modelV2.big=true` across four separate checks totaling 38 seconds (~20 messages/s) |
| State | Stationary, controls disabled; no displayed alert at the checks |
| Timing | Initial server GPU time ~19.2 ms/frame; cached engine build recorded 155.7 seconds |
| Telemetry averages | 75.14°C, 13.68 W, 3,817 RPM across 29 logged readings in the three timed windows below |
| Software | TensorRT 10.3.0 / Orin-sm87; observed host L4T R39.2.1 |

The donor reference uses **JetPack 6.2 / L4T R36.4.3**; the observed host differs. These short checks are not a sustained performance or thermal qualification. The server loaded its cached engine at startup, but complete offline cold-start behavior remains unverified. Earlier DNS failures and USB endpoint-busy/disconnect errors still require recovery testing.

### Check averages

Telemetry means below use logged readings in each UTC interval `[start, start + 10 seconds)` on September 19, 2026. Model counts come from the corresponding live subscriptions. The initial eight-second check returned 160/160 large-model messages, but its exact telemetry window was not recorded, so it is excluded from telemetry averages.

| Check start (UTC) | Large-model messages | Telemetry readings | Mean °C | Mean W | Mean fan RPM | Mean GPU load |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 19:56:04 | 200/200 | 10 | 70.62 | 13.20 | 3,517 | 74.70% |
| 19:57:07 | 200/200 | 10 | 73.89 | 13.97 | 3,899 | 83.00% |
| 20:01:39 | 200/200 | 9 | 81.54 | 13.88 | 4,060 | 83.67% |
| **Pooled** | **600/600** | **29** | **75.14** | **13.68** | **3,817** | **80.34%** |

Pooled telemetry means are weighted by reading count, not averaged from rounded rows; mean GPU clock was 1,020 MHz in all three windows. These are sampled windows, not continuous monitoring. Temperature rose between checks; the pooled mean does not establish thermal stability. No new disconnect/fallback entries were found in the reviewed refresh logs. Per-frame GPU timing above is an initial observation, not a telemetry-window average.

For each subsequent requested check, record its UTC start/end, model and telemetry sample counts, per-check means, and updated sample-weighted totals here. Keep missing readings explicit and retain temperature trends.

### New-model preparation checks · September 19, 2026

Selected: **Cinque Terre Model V2 (September 08, 2026)**, SHA prefix `09d080f36965bb2a` (~730 MiB). The comma reached the Orin and requested engine preparation at **20:40:18 UTC**, after a USB reader timeout/retry.

| UTC sampling window | Native messages | Large-model messages | Jetlink telemetry readings |
| --- | ---: | ---: | ---: |
| 20:42:15–20:42:25 | 201 | 0 | 0 |
| 20:43:52–20:44:02 | 200 | 0 | 0 |
| 20:48:40–20:48:50 | 200 | 0 | 0 |
| 20:50:12–20:50:22 | 200 | 0 | 0 |
| 21:02:44.696–21:02:54.703 | 200 | 0 | 0 |
| **Total (~50 seconds sampled)** | **1,001** | **0** | **0** |

Latest check: **200/200 model messages alive and valid**, mean speed **0 m/s**, controls disabled throughout, no displayed alert. Across the five sampled windows, the sample-weighted large-model fraction is **0/1,001 (0%)**. Temperature, power, fan, GPU load, and GPU clock means remain **unavailable**, not zero; no telemetry readings were available to pool. These checks remain separate from BMRLNAP results.

At **21:02:54 UTC**, approximately **22 min 36 s** after the preparation request, the reviewed comma-side Jetlink logs still showed no subsequent handoff, completion, or error. `AcceleratorProgress` remained `load / ready`, but `JetlinkEngineReady` and `JetlinkSpec` still identified the previous BMRLNAP hash `a086d5249fc308bb`. **Cinque Terre activation is not verified.** Jetson-side service logs are needed to distinguish a transfer/build stall from ongoing work; the stale ready parameter cannot establish progress.

Scheduled attempts at 20:46:47 and 20:56:17 UTC were blocked before SSH by a local Windows sandbox error and contributed no samples. Manual SSH worked for the latest check. No device settings or services were changed.

### Cinque Terre precache · September 19, 2026

**Prepared on the Jetson at 21:14:25 UTC**, without the comma connected. Download verified: **766,040,736 bytes**, SHA-256 `09d080f36965bb2a0790500452bd328aa03c484d0222aa79d1ad9f021a522aec`. TensorRT **10.3.0 / Orin-sm87**, FP16 engine: **767,367,060 bytes**, recorded build time **30.5 seconds**; prepare exited successfully. One build observation, not an average or inference benchmark.

The model and matching engine are stored in `/mnt/data/jetlink/models/` and `/mnt/data/jetlink/engines/`. Jetlink was stopped for compilation, then restarted and confirmed active. Both models remain cached. The server still preloads last-used BMRLNAP while waiting for USB; **Cinque Terre is cached, but live activation remains unverified**.

For desk preparation, use the installed container's `python3 -m jetlink.registry fetch <ref>`, then `prepare <ref> --backend trt --cache /mnt/data/jetlink` with the same pinned image, NVIDIA runtime, and cache mount. Cinque Terre ref: `37bfa1413edcdc2e8844984b83727c33f81d8f46`. Stop the service before standalone preparation and restart afterward; do not build concurrently against its cache. See the [prefetch procedure](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/models.md#on-a-jetson).

After reconnecting while parked, verify the selected hash, live `modelV2.big=true`, valid/alive model messages, and fresh telemetry. Cached artifacts avoid another model download/build for this runtime; a fully offline startup still needs verification.

## Drive recap · September 19, 2026

Analyzed all **16 full-rate log segments**: **14 min 58 s**, approximately **7.82 km (4.86 mi)**, maximum **44.59 mph**.

- **Inference:** 17,227/17,830 messages used the large model (96.62%). The first 603 were native; after handoff, no return to native was recorded.
- **Large-model execution:** mean **44.36 ms**, p95 **45.53 ms**, maximum **76.51 ms**. This measures the model call on the comma, not GPU-only time.
- **814 telemetry readings:** mean **62.96°C**, **12.90 W**, **2,621 RPM**; peak **83.9°C**, ending **49.9°C**. Drive averages are separate from parked checks.
- **Controls:** lateral-active time **12 min 14 s**. Temporary steering-fault flags totaled **22.96 s** across 41 episodes, including **19.18 s while moving**. Cause remains unresolved; sustained inference does not mean fault-free steering.
- Calibration messages were all calibrated. Startup communication/localization events and an initial native-model timing outlier were recorded.

[Detailed analysis, averages, and limitations](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/DRIVE_RECAP_2026-09-19.md). Raw logs/video remain private; no visual driving review or fully offline cold-start qualification has been completed.

## Source and validation

Development lives on [`jetson-trt`](https://github.com/ryanafdahl/745-OP/tree/jetson-trt); `main` is the landing page. Install branches are pinned candidates and **do not automatically follow development**.

| Component | Revision |
| --- | --- |
| Installed candidate | `b6756fe80c3df2e0bbfde3c512d29e02cf1127b5` |
| NRDR clean base | `b3366b5b56512805be8f0bf832b4981bfd958072` |
| Zoompilot donor | `bcb49d740eb7f7181c2c4aba6de5177b03f88ba3` |
| Jetlink source pin | `a01fcae9709cb4924854f0c52806849c62dec5c9` |

[Source validation](https://github.com/ryanafdahl/745-OP/actions/runs/35460627418) passed **69 portable tests twice**, provenance checks, and model integrity checks. [Install verification](https://github.com/ryanafdahl/745-OP/actions/runs/35461743304) passed compiled-installer and anonymous-clone model checks.

## Change notes

**2026-09-19:** integrated Jetlink while preserving protected NRDR control/safety subtrees; fixed lease-socket cleanup; restored the missing 60,881,999-byte native ONNX input as hash-verified chunks; stopped startup after failed compilation; added the short installer; renamed the repository and install entry; verified parked Jetson inference. The destructive bootstrap is retired.

## Troubleshooting and details

- **“Incompatible openpilot version”:** check the exact install spelling. The setup screen requires an ELF installer; `tools/install_jetson.py` is an optional SSH helper.
- **Flashing GPU:** inspect Models status; “waiting for the Jetson” means no completed connection. Do not bypass build failures with a `prebuilt` marker.
- **Logs:** comma: `tmux capture-pane -p -S -2000 -t comma`; Jetson: `sudo journalctl -u jetlink-server -b --no-pager`.
- Keep controls disabled during parked diagnostics. EPS flashing is not a requirement for this port.

[Installation guide](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/JETSON_INSTALL.md) · [Hardware checks / optional staging](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/COMMA4_JETSON_PARKED_TEST.md)

Built on NRDR, comma.ai, sunnypilot, Zoompilot, and Jetlink. See [LICENSE](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/LICENSE), [LICENSE.md](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/LICENSE.md), and component notices.
