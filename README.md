# NRDR JetStream

NRDR openpilot for **comma 4 + Jetson Orin Nano Super**, using USB Jetlink and TensorRT for large-model inference. The comma handles cameras and vehicle control.

## Install

Factory reset the comma, connect to Wi-Fi, choose **Custom Software**, and enter:

```text
ryanafdahl/nrdr-jetstream
```

Keep power and internet connected through installation and first-boot compilation. The [installer](https://installer.comma.ai/ryanafdahl/nrdr-jetstream) uses [ryanafdahl/openpilot → nrdr-jetstream](https://github.com/ryanafdahl/openpilot/tree/nrdr-jetstream), targeting **AGNOS 19.7**.

## Connect

1. Install the matching [Jetlink server](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md) on the Jetson.
2. Complete normal comma calibration with the native setup, then park before connecting the Jetson. This order is a **user-reported workaround** for persistent grey flashing.
3. Power both devices separately; use a Jetson supply suitable for **25 W mode** and a **USB 3 data cable, Jetson USB-A → comma USB-C**.
4. While parked, enable **Settings → Models → Accelerator Link** and select the big model.
5. Prepare the model online, or precache it on the Jetson before moving it to the car.

A flashing GPU icon can mean download, preparation, or connection waiting. Confirm operation using the matching model hash, live `modelV2.big=true`, valid/alive messages, and fresh Jetlink telemetry.

## Latest drive · September 19, 2026

**Cinque Terre V2 verified across all 9 full-rate segments**, 22:12:10–22:20:17 UTC. This recording includes substantial parked time.

| Measurement | Result |
| --- | --- |
| Recording / movement | 8:07 total · 2:08 moving · 0.844 km / 0.525 mi |
| Large-model use | 5,601 / 9,595 messages (58.37%); all large-model messages valid |
| Connection | ~200 s waiting for Jetson, then continuous large-model use |
| Model execution | Mean 33.78 ms · p95 36.93 ms · max 101.25 ms |
| Telemetry | 267 readings; all reported `dead=false` |
| Temperature | Mean 62.04°C · peak 66.0°C |
| Power / cooling | Mean 13.22 W · 2,682 RPM |
| GPU | Mean 76.63% load · 1,020 MHz |

One 115 ms model-message gap occurred while stationary, with brief communication/localization events and no fallback. Temporary steering-fault flags totaled **8.02 s** across 17 episodes (7.15 s moving); cause remains unresolved.

**Both Cinque Terre recordings:** 26,776 large-model messages; sample-weighted execution **38.80 ms**. Across 1,271 telemetry readings: **54.21°C, 13.11 W, 1,853 RPM**. Keep these separate from BMRLNAP results.

[Latest analysis](https://github.com/ryanafdahl/nrdr-jetstream/blob/jetson-trt/docs/CINQUE_TERRE_DRIVE_2026-09-19_2212.md) · [Previous drive](https://github.com/ryanafdahl/nrdr-jetstream/blob/jetson-trt/docs/CINQUE_TERRE_DRIVE_2026-09-19.md) · [Check history](https://github.com/ryanafdahl/nrdr-jetstream/blob/jetson-trt/docs/HARDWARE_CHECK_HISTORY_2026-09-19.md). Raw logs/video remain private; fully offline startup awaits verification.

## Precache for the car

Cinque Terre V2 ref: `37bfa1413edcdc2e8844984b83727c33f81d8f46`; model SHA prefix: `09d080f36965bb2a`.

The Jetson cache contains its **766,040,736-byte ONNX** and **767,367,060-byte engine** under `/mnt/data/jetlink/{models,engines}/`. Runtime: **TensorRT 10.3.0 / Orin-sm87**, observed host **L4T R39.2.1**.

Use the installed container's `python3 -m jetlink.registry fetch <ref>` and `prepare <ref> --backend trt --cache /mnt/data/jetlink`, with its pinned image, NVIDIA runtime, and cache mount. Stop Jetlink for standalone preparation and restart afterward. [Complete procedure](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/models.md#on-a-jetson).

## Changes and source

**September 19:** renamed the project and comma 4 home-screen title to **NRDR JetStream**; integrated Jetlink; restored hash-verified native ONNX chunks; fixed lease cleanup and compilation failure handling; added the short installer; verified BMRLNAP inference; precached Cinque Terre in 30.5 s and verified it across two recordings.

Development: [jetson-trt](https://github.com/ryanafdahl/nrdr-jetstream/tree/jetson-trt). Install candidate: `9abb37bf7e5b29e08566c077e7a319fa11b51b52`. Install branches are updated separately from development. [Validation](https://github.com/ryanafdahl/nrdr-jetstream/actions/runs/35460627418): 69 portable tests passed twice. [Installer checks](https://github.com/ryanafdahl/nrdr-jetstream/actions/runs/35461743304) passed.

[Install guide](https://github.com/ryanafdahl/nrdr-jetstream/blob/jetson-trt/docs/JETSON_INSTALL.md) · [Hardware checks](https://github.com/ryanafdahl/nrdr-jetstream/blob/jetson-trt/docs/COMMA4_JETSON_PARKED_TEST.md)

Built on NRDR, comma.ai, sunnypilot, Zoompilot, and Jetlink. [License](https://github.com/ryanafdahl/nrdr-jetstream/blob/jetson-trt/LICENSE) · [Additional notices](https://github.com/ryanafdahl/nrdr-jetstream/blob/jetson-trt/LICENSE.md).
