# nrdr-jetson

NRDR openpilot for **comma 4**, with **Jetson Orin Nano Super** acceleration through USB Jetlink and TensorRT. The native small-model path remains available as fallback.

**Status:** installed and booted on comma 4; live large-model inference verified while parked. Experimental—sustained reliability, offline cold starts, reconnect/fallback, and vehicle operation are not yet qualified.

## Install

Factory reset the comma 4, connect to Wi-Fi, choose **Custom Software**, and enter:

```text
ryanafdahl/nrdr-jetson
```

Keep stable power and internet through download and first-boot compilation. No SSH or staging build is required. Target OS: **AGNOS 19.7**; the launcher handles any required OS update.

The [compiled installer](https://installer.comma.ai/ryanafdahl/nrdr-jetson) installs branch `nrdr-jetson` from [ryanafdahl/openpilot](https://github.com/ryanafdahl/openpilot/tree/nrdr-jetson). Old entries `nrdr-op-jetson-trt` and `nrdr-OP-jetson-trt` still work. Renaming does not require reinstalling.

## Connect the Jetson

1. Install the matching [Jetlink server](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md) separately; the comma installer does not install it.
2. Power the Jetson separately, with a supply suitable for **25 W mode**. Connect a **USB 3 data cable: Jetson USB-A → comma USB-C**.
3. While offroad, enable **Settings → Models → Accelerator Link**. Start with the default big model.
4. Complete initial model download and engine preparation online. Cached engines can load without rebuilding; fully offline startup of the connected pair still needs verification.

Jetlink is opt-in (`JetlinkEnabled`). A flashing grey GPU icon means preparation or waiting, **not necessarily compilation**. Check the Models panel for the actual stage. A ready icon alone does not prove live inference.

## Verified hardware results · September 19, 2026

| Check | Observation |
| --- | --- |
| Live model | BMRLNAP Model v4, August 30, 2026; SHA prefix `a086d5249fc308bb` |
| Parked checks | 160/160, then 200/200 and 200/200 messages had `modelV2.big=true` across separate 8-, 10-, and 10-second samples |
| State | Stationary, controls disabled; no displayed alert at the checks |
| Timing | Initial server GPU time ~19.2 ms/frame; cached engine build recorded 155.7 seconds |
| Latest telemetry | 74.1°C, ~14 W, fan ~3,907 RPM; no new disconnect/fallback entries in reviewed logs |
| Software | TensorRT 10.3.0 / Orin-sm87; observed host L4T R39.2.1 |

The donor reference uses **JetPack 6.2 / L4T R36.4.3**; the observed host differs. These short checks are not a sustained performance or thermal qualification. The server loaded its cached engine at startup, but complete offline cold-start behavior remains unverified. Earlier DNS failures and USB endpoint-busy/disconnect errors still require recovery testing.

## Source and validation

Development lives on [`jetson-trt`](https://github.com/ryanafdahl/nrdr-jetson/tree/jetson-trt); `main` is the landing page. Install branches are pinned candidates and **do not automatically follow development**.

| Component | Revision |
| --- | --- |
| Installed candidate | `b6756fe80c3df2e0bbfde3c512d29e02cf1127b5` |
| NRDR clean base | `b3366b5b56512805be8f0bf832b4981bfd958072` |
| Zoompilot donor | `bcb49d740eb7f7181c2c4aba6de5177b03f88ba3` |
| Jetlink source pin | `a01fcae9709cb4924854f0c52806849c62dec5c9` |

[Source validation](https://github.com/ryanafdahl/nrdr-jetson/actions/runs/35460627418) passed **69 portable tests twice**, provenance checks, and model integrity checks. [Install verification](https://github.com/ryanafdahl/nrdr-jetson/actions/runs/35461743304) passed compiled-installer and anonymous-clone model checks.

## Change notes

**2026-09-19:** integrated Jetlink while preserving protected NRDR control/safety subtrees; fixed lease-socket cleanup; restored the missing 60,881,999-byte native ONNX input as hash-verified chunks; stopped startup after failed compilation; added the short installer; renamed the repository and install entry; verified parked Jetson inference. The destructive bootstrap is retired.

## Troubleshooting and details

- **“Incompatible openpilot version”:** check the exact install spelling. The setup screen requires an ELF installer; `tools/install_jetson.py` is an optional SSH helper.
- **Flashing GPU:** inspect Models status; “waiting for the Jetson” means no completed connection. Do not bypass build failures with a `prebuilt` marker.
- **Logs:** comma: `tmux capture-pane -p -S -2000 -t comma`; Jetson: `sudo journalctl -u jetlink-server -b --no-pager`.
- Keep controls disabled during parked diagnostics. EPS flashing is not a requirement for this port.

[Installation guide](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/docs/JETSON_INSTALL.md) · [Hardware checks / optional staging](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/docs/COMMA4_JETSON_PARKED_TEST.md)

Built on NRDR, comma.ai, sunnypilot, Zoompilot, and Jetlink. See [LICENSE](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/LICENSE), [LICENSE.md](https://github.com/ryanafdahl/nrdr-jetson/blob/jetson-trt/LICENSE.md), and component notices.
