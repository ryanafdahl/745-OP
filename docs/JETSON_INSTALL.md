# Install the experimental Jetson TRT candidate

This repository is public. The installer targets `ryanafdahl/nrdr-OP-jetson-trt`, not the account's `openpilot` repository.

The initial source revision is pinned to `97629ae3bd9f501777d4282c9cef2032c28e4efd`, including the fix that stops startup if compilation fails. This is a source installation: the comma compiles it on first startup. No precompiled comma 4 image or hardware inference pass is claimed.

## Existing comma 4 installation: run from SSH

With ignition off and the comma powered and online, run these commands in a direct SSH shell on the comma (outside tmux):

```bash
curl --fail --location --retry 3 https://raw.githubusercontent.com/ryanafdahl/nrdr-OP-jetson-trt/af6bf0afb069f0fdca9cd89c131496005bf9fe78/tools/install_jetson.py -o /tmp/install-jetson.py &&
python3 /tmp/install-jetson.py
```

The installer downloads and verifies the candidate before stopping the current app. It preserves the entire old checkout as `/data/openpilot-before-jetson-<timestamp>`, saves the previous launcher, and prints a `bash /data/rollback-jetson-<timestamp>.sh` command. Save that command. It then starts the normal launcher, which builds locally. Keep power connected until compilation finishes.

Requirements are detected automatically: comma 4, AGNOS 19.7, Git LFS, passwordless sudo, and at least 12 GiB free. A mismatch stops installation before replacing the current checkout. No separate staging build or hardware-version questionnaire is required.

## Device already at the software setup screen

Use this complete custom software URL:

```text
https://raw.githubusercontent.com/ryanafdahl/nrdr-OP-jetson-trt/af6bf0afb069f0fdca9cd89c131496005bf9fe78/tools/install_jetson.py
```

This uses the same source installer. Do not uninstall a working installation just to reach setup; the SSH method retains a rollback checkout. The public payload is verified by CI; execution through the physical device's setup UI has not yet been tested.

## First parked test and failure reporting

Start with successful boot, camera/UI operation and the native model path. Keep controls disabled and do not drive; Park alone does not prevent steering actuation. Jetlink remains opt-in, but an existing enabled setting persists across installation. The pinned Jetson server is `zoompilot/jetlink@a01fcae9709cb4924854f0c52806849c62dec5c9`. The comma installer does not install that server or change Jetson firmware.

If compilation fails, manager will not start. From SSH, capture the output:

```bash
tmux capture-pane -p -S -2000 -t comma > /data/jetson-first-boot.txt
```

Return that log and the error shown on screen. To restore the old software, run the exact rollback command printed during installation. It preserves the failed candidate in another directory and restarts the previous checkout. This is software rollback; shared Params and any runtime migrations are not restored. The installer does not change AGNOS.

Full hardware validation and optional isolated build tooling are documented in [the validation guide](COMMA4_JETSON_PARKED_TEST.md).
