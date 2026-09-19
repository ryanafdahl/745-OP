# Comma 4: factory-reset installation

## Install after a factory reset

1. Factory reset the comma 4.
2. Reconnect to Wi-Fi and choose custom software.
3. Enter exactly:

```text
ryanafdahl/nrdr-OP-jetson-trt
```

4. Keep the device powered and online while software downloads and compiles on first startup.

No SSH, long URL, separate staging build, or rollback step is required.

Comma's setup screen expands `username/branch` to its compiled fork installer. This entry installs branch `nrdr-OP-jetson-trt` from [ryanafdahl/openpilot](https://github.com/ryanafdahl/openpilot/tree/nrdr-OP-jetson-trt). That branch publishes the candidate from this development repository; it currently points to `97629ae3bd9f501777d4282c9cef2032c28e4efd`. It does not automatically track new development commits.

The equivalent full URL is:

```text
https://installer.comma.ai/ryanafdahl/nrdr-OP-jetson-trt
```

The candidate targets comma 4 and AGNOS 19.7. The normal launcher handles OS compatibility and may run its AGNOS update procedure if the installed version differs. Keep stable power available through setup and compilation. A failed source build stops before manager starts.

**Correction to earlier instructions:** comma 4's setup screen accepts compiled ELF installers. The earlier raw `install_jetson.py` URL is an SSH helper, not a valid setup-screen installer. Do not enter that Python URL after a factory reset.


## Jetson and parked testing

The installer installs comma-side software. Configure the Jetson separately using the [pinned Jetlink reference](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md). Fresh Jetlink settings are opt-in.

For the first parked test, verify boot, camera/UI operation, and native model output. Keep controls disabled and do not drive; Park alone does not prevent steering actuation. Native compilation and live Jetson inference still require hardware validation.

## Troubleshooting

Record any on-screen error. If SSH is available after installation, capture startup output:

```bash
tmux capture-pane -p -S -2000 -t comma > /data/jetson-first-boot.txt
```

To reinstall, factory reset and use the same short entry. Do not add a `prebuilt` marker to bypass compilation failures. See [the validation guide](COMMA4_JETSON_PARKED_TEST.md) for hardware checks.
