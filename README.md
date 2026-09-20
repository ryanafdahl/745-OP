# 745-OP

NRDR openpilot for **comma 4 + Jetson Orin Nano Super**, using USB Jetlink and TensorRT for large-model inference. The comma handles cameras and vehicle control.

**This is a custom build for my car. Do not use this.**

## Automatic nightly updates

[Daily GitHub Actions checks](https://github.com/ryanafdahl/745-OP/actions/workflows/sync-nrdr-nightly.yml) track **NRDR `nrdr-nightly`** at **10:23 UTC** and commit compatible changes to `jetson-trt`. Customized/protected files are listed for manual integration, and the source audit runs after each update. The comma installer stays pinned. [How it works](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/AUTOMATIC_UPDATES.md).

## Nightly compatibility update

Selected changes from `nrdr-nightly` snapshot `e0bf1e63`: longitudinal door/seat-belt/parking-brake/gear checks and clearer speed-limit alerts. 745-OP retains its current driver monitoring, disengagement safeguards, MADS activation, Jetlink, branding, and comma Connect uploads. This is a selective port on the clean base.

[Update details and validation](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/NIGHTLY_COMPATIBILITY.md). Drive measurements below were recorded before this update.

## Install

Factory reset the comma, connect to Wi-Fi, choose **Custom Software**, and enter:

```text
ryanafdahl/745-OP
```

Keep power and internet connected through installation and first-boot compilation. The [installer](https://installer.comma.ai/ryanafdahl/745-OP) uses [ryanafdahl/openpilot → 745-OP](https://github.com/ryanafdahl/openpilot/tree/745-OP), targeting **AGNOS 19.7**.

## Connect

1. Install the matching [Jetlink server](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md) on the Jetson.
2. Complete normal comma calibration with the native setup, then park before connecting the Jetson. This order is a **user-reported workaround** for persistent grey flashing.
3. Power both devices separately; use a Jetson supply suitable for **25 W mode** and a **USB 3 data cable, Jetson USB-A → comma USB-C**.
4. While parked, enable **Settings → Models → Accelerator Link** and select the big model.
5. Prepare the model online, or precache it on the Jetson before moving it to the car.

**Fan:** the test Jetson uses NVIDIA’s `cool` profile (`FAN_DEFAULT_PROFILE cool` in `/etc/nvfancontrol.conf`). Confirmed after reboot on September 20 at 17:28 UTC: `nvfancontrol -q` reports `FAN_PROFILE:cool`, governor `cont`, and control `close_loop`; nvfancontrol and Jetlink services are active. SSH over USB Wi-Fi is reachable.

A flashing GPU icon can mean download, preparation, or connection waiting. Confirm operation using the matching model hash, live `modelV2.big=true`, valid/alive messages, and fresh Jetlink telemetry.

## Latest capture · September 20, 2026

Collected logs from both devices. The latest recording includes early accelerator interruptions and a later uninterrupted large-model interval; the owner reports correcting insufficient power between drives. TP-Link USB Wi-Fi automatically reconnects after reboot with Ethernet unplugged; internet checks passed and the internal radios remain disabled. [Capture and hardware details](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/JETSON_WIFI_AND_CAPTURE_2026-09-20.md).

## Previous drive · September 19, 2026

**Cinque Terre V2 verified across all 20 full-rate segments**, 23:03:59–23:23:04 UTC.

| Measurement | Result |
| --- | --- |
| Drive | 19:05 total · 16:22 moving · 14.858 km / 9.232 mi |
| Large-model use | 22,209 / 22,610 messages (98.23%); all large-model messages valid |
| Startup | ~20 s from first model message to handoff, then no fallback |
| Model execution | Mean 34.25 ms · p95 37.54 ms · max 55.01 ms |
| Telemetry | 1,051 readings; all reported `dead=false` |
| Temperature | Mean 67.15°C · peak 71.7°C |
| Power / cooling | Mean 13.45 W · 3,204 RPM |
| GPU | Mean 78.77% load · 1,020 MHz |

Temporary steering-fault flags totaled **9.22 s** across 10 episodes (8.23 s moving). Six messages carried a **stock forward-collision-warning flag** near the end; context and cause remain unresolved. One model-message interval reached 100.89 ms.

**Three Cinque Terre recordings:** 48,985 large-model messages; sample-weighted execution **36.73 ms**. Across 2,322 telemetry readings: **60.07°C, 13.26 W, 2,464 RPM**. BMRLNAP results remain separate.

[Latest analysis](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/CINQUE_TERRE_DRIVE_2026-09-19_2303.md) · [Previous recording](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/CINQUE_TERRE_DRIVE_2026-09-19_2212.md) · [Check history](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/HARDWARE_CHECK_HISTORY_2026-09-19.md). Jetson data here comes from comma-side logs; direct Jetson logs were unavailable while it was offline. Raw logs/video remain private.

## Precache for the car

Cinque Terre V2 ref: `37bfa1413edcdc2e8844984b83727c33f81d8f46`; model SHA prefix: `09d080f36965bb2a`.

The Jetson cache contains its **766,040,736-byte ONNX** and **767,367,060-byte engine** under `/mnt/data/jetlink/{models,engines}/`. Runtime: **TensorRT 10.3.0 / Orin-sm87**, observed host **L4T R39.2.1**.

Use the installed container's `python3 -m jetlink.registry fetch <ref>` and `prepare <ref> --backend trt --cache /mnt/data/jetlink`, with its pinned image, NVIDIA runtime, and cache mount. Stop Jetlink for standalone preparation and restart afterward. [Complete procedure](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/models.md#on-a-jetson).

## Changes and source

**September 20:** renamed the repository to **745-OP**; the comma 4 home-screen title is **745 OP**. New custom install entry: `ryanafdahl/745-OP`.

**September 19:** added the validated nightly compatibility update; renamed the project and comma 4 home-screen title to **745-OP**; integrated Jetlink; restored hash-verified native ONNX chunks; fixed lease cleanup and compilation failure handling; added the short installer; verified BMRLNAP inference; precached Cinque Terre in 30.5 s and verified it across three recordings.

Development: [jetson-trt](https://github.com/ryanafdahl/745-OP/tree/jetson-trt). Installed runtime: `aa2fd69ba4ce1a5e7d716248e281d4dea8d853a6`. Install branches are updated separately from development. [Validation](https://github.com/ryanafdahl/745-OP/actions/runs/35476805824): 75 portable tests passed twice for this update. [Installer checks](https://github.com/ryanafdahl/745-OP/actions/runs/35461743304) passed.

[Install guide](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/JETSON_INSTALL.md) · [Hardware checks](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/COMMA4_JETSON_PARKED_TEST.md)

Built on NRDR, comma.ai, sunnypilot, Zoompilot, and Jetlink. [License](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/LICENSE) · [Additional notices](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/LICENSE.md).

<!-- nrdr-nightly-sync:start -->
### Reviewed nightly integration

All nine deferred files reviewed: startup LKAS retry added as a **default-off** option; existing interlocks/speed-limit updates kept; comma Connect and monitoring/fault protections retained. **0 unresolved, 9 recorded decisions** for snapshot `e0bf1e63`. Changes on either side reopen review. Installed on the comma September 20 as `92c539b`: native build and 12 compatibility tests passed; UI, hardwared, pandad and jetlinkd were running in all 21 startup samples. Startup retry remains OFF. [Details](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/NRDR_NIGHTLY_SYNC.md).
<!-- nrdr-nightly-sync:end -->
