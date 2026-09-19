# nrdr-jetson

NRDR openpilot for **comma 4 + Jetson Orin Nano Super**, using USB Jetlink and TensorRT for large-model inference. The comma handles cameras and vehicle control.

## Install

Factory reset the comma, connect to Wi-Fi, choose **Custom Software**, and enter:

```text
ryanafdahl/nrdr-jetson
```

Keep power and internet connected through installation and first-boot compilation. The [installer](https://installer.comma.ai/ryanafdahl/nrdr-jetson) uses [ryanafdahl/openpilot → nrdr-jetson](https://github.com/ryanafdahl/openpilot/tree/nrdr-jetson), targeting **AGNOS 19.7**.

## Connect

1. Install the matching [Jetlink server](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md) on the Jetson.
2. Complete normal comma calibration with the native setup, then park before connecting the Jetson. This order is a **user-reported workaround** for persistent grey flashing.
3. Power both devices separately; use a Jetson supply suitable for **25 W mode** and a **USB 3 data cable, Jetson USB-A → comma USB-C**.
4. While parked, enable **Settings → Models → Accelerator Link** and select the big model.
5. Prepare the model online, or precache it on the Jetson before moving it to the car.

A flashing GPU icon can mean download, preparation, or connection waiting. Confirm operation using the matching model hash, live `modelV2.big=true`, valid/alive messages, and fresh Jetlink telemetry.

## Latest drive · September 19, 2026

**Cinque Terre V2 ran successfully after precaching**, verified from all **19 full-rate segments**, 21:16:23–21:34:59 UTC.

| Measurement | Result |
| --- | --- |
| Drive | 18:36 · 14.85 km / 9.23 mi |
| Large-model use | 21,175 / 22,175 messages (95.49%); all large-model messages valid |
| Startup | Native model for ~50 s, then continuous large-model use |
| Model execution | Mean 40.12 ms · p95 42.02 ms · max 70.81 ms |
| Telemetry | 1,004 readings; all reported `dead=false` |
| Temperature | Mean 52.13°C · peak 64.5°C |
| Power / cooling | Mean 13.08 W · 1,633 RPM |
| GPU | Mean 77.14% load · 1,020 MHz |

Temporary steering-fault flags totaled **12.17 s** across 28 episodes, including 11.19 s while moving; cause remains unresolved. Fully offline startup remains to be verified.

[Latest drive analysis](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/docs/CINQUE_TERRE_DRIVE_2026-09-19.md) includes timing, controls, capture details, and comparison with the [earlier BMRLNAP drive](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/docs/DRIVE_RECAP_2026-09-19.md). [Check history](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/docs/HARDWARE_CHECK_HISTORY_2026-09-19.md) retains UTC windows and pooled averages. Results stay separate by model; raw logs/video remain private.

## Precache for the car

Cinque Terre V2 ref: `37bfa1413edcdc2e8844984b83727c33f81d8f46`; model SHA prefix: `09d080f36965bb2a`.

The Jetson cache contains its **766,040,736-byte ONNX** and **767,367,060-byte engine** under `/mnt/data/jetlink/{models,engines}/`. Runtime: **TensorRT 10.3.0 / Orin-sm87**, observed host **L4T R39.2.1**.

Use the installed container's `python3 -m jetlink.registry fetch <ref>` and `prepare <ref> --backend trt --cache /mnt/data/jetlink`, with its pinned image, NVIDIA runtime, and cache mount. Stop Jetlink for standalone preparation and restart afterward. [Complete procedure](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/models.md#on-a-jetson).

## Changes and source

**September 19:** integrated Jetlink; restored hash-verified native ONNX chunks; fixed lease cleanup and compilation failure handling; added the short installer; verified BMRLNAP inference; precached Cinque Terre in 30.5 s and verified it across the latest drive.

Development: [jetson-trt](https://github.com/ryanafdahl/nrdr-jetson/tree/jetson-trt). Install candidate: `b6756fe80c3df2e0bbfde3c512d29e02cf1127b5`. Install branches are updated separately from development. [Validation](https://github.com/ryanafdahl/nrdr-jetson/actions/runs/35460627418): 69 portable tests passed twice. [Installer checks](https://github.com/ryanafdahl/nrdr-jetson/actions/runs/35461743304) passed.

[Install guide](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/docs/JETSON_INSTALL.md) · [Hardware checks](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/docs/COMMA4_JETSON_PARKED_TEST.md)

Built on NRDR, comma.ai, sunnypilot, Zoompilot, and Jetlink. [License](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/LICENSE) · [Additional notices](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/LICENSE.md).
