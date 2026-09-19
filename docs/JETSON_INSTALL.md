# Factory-reset installation: comma 4 + Jetson TRT

Use a factory reset before every installation of this experimental candidate. This procedure does not require SSH, a staging build, or rollback. A factory reset removes the previous installation and local configuration.

## Installation

1. Factory reset the comma 4.
2. Reconnect to Wi-Fi and proceed to the custom software URL prompt.
3. Enter this full URL:

```text
https://raw.githubusercontent.com/ryanafdahl/nrdr-OP-jetson-trt/af6bf0afb069f0fdca9cd89c131496005bf9fe78/tools/install_jetson.py
```

4. Keep the comma powered and online during the download and first-startup compilation.
5. Complete the normal setup and calibration prompts after installation.

The repository is public; no GitHub login is required to download this installer. The URL selects this exact repository rather than an account's differently named `openpilot` repository.

## Candidate and requirements

- Installed source: `97629ae3bd9f501777d4282c9cef2032c28e4efd`.
- Installer payload: `af6bf0afb069f0fdca9cd89c131496005bf9fe78`.
- Target: comma 4 on AGNOS 19.7.
- Other installer checks: Git LFS, passwordless sudo, and at least 12 GiB free.

The installer checks requirements automatically. It does not upgrade AGNOS, and resetting the device should not be treated as an OS upgrade. Reusing this URL reinstalls the same pinned candidate; it does not select the latest branch commit.

This is a source installation, not a precompiled image. The normal launcher compiles on the comma. If compilation fails, manager will not start. Do not create a `prebuilt` marker to bypass that failure.

## Jetson and parked testing

The comma installer does not install the Jetson server or change Jetson firmware. Use the matching [Jetlink server setup reference](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md). Jetlink is opt-in; fresh settings do not enable it by default.

For the first parked test, check boot, camera/UI operation, and the native model path. Keep controls disabled and do not drive; Park alone does not prevent steering actuation.

## If installation fails

Record the error shown on the device. If SSH is available, capture first-startup output:

```bash
tmux capture-pane -p -S -2000 -t comma > /data/jetson-first-boot.txt
```

Provide the error or log to diagnose the failure. For another clean installation, factory reset again and reuse the URL. There is no rollback step in this procedure.

## Verification limits

CI verified anonymous installer download and 64 portable tests in each of two passes. Physical setup-screen execution, native comma compilation, and live Jetson inference remain unverified. See [the hardware validation guide](COMMA4_JETSON_PARKED_TEST.md) for the remaining checks.
