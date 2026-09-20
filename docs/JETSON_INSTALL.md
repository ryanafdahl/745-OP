# Comma 4: factory-reset installation

The development repository is now [ryanafdahl/745-OP](https://github.com/ryanafdahl/745-OP). The custom-software entry below uses the new `745-OP` branch in `ryanafdahl/openpilot`; no reinstall is needed solely for the rename.

## Install after a factory reset

1. Factory reset the comma 4.
2. Reconnect to Wi-Fi and choose custom software.
3. Enter exactly:

```text
ryanafdahl/745-OP
```

4. Keep the device powered and online while software downloads and compiles on first startup.

No SSH, long URL, separate staging build, or rollback step is required.

The `745-OP` install branch is the current candidate. Use `ryanafdahl/745-OP` for new installations; legacy branches retain their earlier candidates.

Comma's setup screen expands `username/branch` to its compiled fork installer. This entry installs branch `745-OP` from [ryanafdahl/openpilot](https://github.com/ryanafdahl/openpilot/tree/745-OP). That branch publishes the candidate from this development repository; it currently points to `b92ad8d1086d38a1378b85e94753a7e17b2aea17`. It does not automatically track new development commits.

The equivalent full URL is:

```text
https://installer.comma.ai/ryanafdahl/745-OP
```

The candidate targets comma 4 and AGNOS 19.7. The normal launcher handles OS compatibility and may run its AGNOS update procedure if the installed version differs. Keep stable power available through setup and compilation. A failed source build stops before manager starts.

**Correction to earlier instructions:** comma 4's setup screen accepts compiled ELF installers. The earlier raw `install_jetson.py` URL is an SSH helper, not a valid setup-screen installer. Do not enter that Python URL after a factory reset.


## Jetson and parked testing

The installer installs comma-side software. Configure the Jetson separately using the [pinned Jetlink reference](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md). Fresh Jetlink settings are opt-in.

For the first parked test, verify boot, camera/UI operation, and native model output. Keep controls disabled and do not drive; Park alone does not prevent steering actuation. The user reported successful native compilation and boot on September 19, 2026. BMRLNAP and Cinque Terre inference have been recorded; see the README for current measurements.

## Troubleshooting

Record any on-screen error. If SSH is available after installation, capture startup output:

```bash
tmux capture-pane -p -S -2000 -t comma > /data/jetson-first-boot.txt
```

To reinstall, factory reset and use the same short entry. Do not add a `prebuilt` marker to bypass compilation failures. See [the validation guide](COMMA4_JETSON_PARKED_TEST.md) for hardware checks.
