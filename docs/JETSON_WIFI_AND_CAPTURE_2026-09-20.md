# Jetson USB Wi-Fi and log capture — September 20, 2026

## USB Wi-Fi

Tested on Orin Nano Super with kernel `6.8.12-1021-tegra`:
- TP-Link Archer T2U Nano, USB ID `2357:011e`, RTL8811AU.
- Driver `8821au`, DKMS package `rtl8821au/5.12.5.2`, from [morrownr/8821au-20210708](https://github.com/morrownr/8821au-20210708/tree/1a819991f5b75e64dfcf922b96a6681f367cbba0).
- Built and installed against the running kernel; USB interface connected with automatic reconnect and Wi-Fi power saving disabled.
- Interface-bound tests passed: three gateway pings, zero loss, and HTTPS response 200 from GitHub. Credentials remain only in the private NetworkManager profile.

The internal RTL8822CE PCIe Wi-Fi driver is unloaded and blacklisted in `/etc/modprobe.d/jetstream-internal-wifi.conf`. Its PCIe function reports runtime suspended. The internal Bluetooth device (`13d3:3549`) is deauthorized by a device-specific udev rule. Its USB runtime state still reports active: complete removal of electrical power is **not verified**.

Persistent rules are `/etc/udev/rules.d/81-jetstream-internal-bluetooth.rules` and `82-jetstream-internal-wifi-power.rules`. Reboot persistence verified at 16:36 UTC: the USB adapter automatically reconnected on 5 GHz with Ethernet carrier 0, the internal Wi-Fi remained suspended, and Bluetooth remained deauthorized. Ten interface-bound gateway pings had zero loss (3.969 ms mean); HTTPS returned 200 through the USB interface. Jetlink was active after startup. This verifies networking and service startup, not live inference. The USB adapter and Jetlink server were working after these changes. This adapter provides Wi-Fi, not replacement Bluetooth.

To restore the internal card after antenna repair, remove those three configuration files, reload udev rules, and reboot. Driver installation evidence is retained privately under `/home/username/jetstream-wifi-20260920/`.

## Latest recording

The comma recording spans **15:41:39–16:09:41 UTC**, 29 segments, 28:02 total, 19:02 moving, and 22.033 km. The owner reports insufficient Jetson power during the first drive and a corrected supply for the later drive. These phases should not be pooled as one uninterrupted accelerator run; the precise supply-change time was not independently recorded.

Full-rate log analysis found 33,485 model messages, including 15,741 large-model messages. Two early large-model intervals returned to native inference; the final large-model transition had no subsequent fallback before recording ended. Maximum model-message interval was 91.20 ms, with no intervals above 100 ms and zero reported frame drops.

Across 744 available Jetlink telemetry messages, all reported `dead=false`: mean temperature **59.37°C**, peak **66.7°C**, mean power **13.23 W**, mean GPU load **77.76%**, clock **1,020 MHz**, and mean fan speed **2,432 RPM**. Missing telemetry while disconnected is unavailable, not zero. These are whole-recording telemetry means, not isolated later-drive means.

The recording also contains communication/low-frequency alerts and 25.45 seconds of temporary steering-fault flags; their distribution across the power-change phases needs further analysis. No permanent steering fault or CAN timeout was recorded. This collection does not establish release readiness.

## Private archives

Comma: `/data/jetson-diagnostics/comma-20260920-logs.tar.gz` — 305,823,857 bytes, SHA-256 `19c35fd9c25237be08791bff5a1cb5d748b62e6481e594a55f41e0efc0a47b97`. Contains latest-route logs (video excluded), swaglogs, service/kernel journals, and launch output. Analysis JSON is stored separately under `/data/jetson-diagnostics/2026-09-20-drive-0e-analysis.json`.

Jetson: `/home/username/jetson-20260920-logs.tar.gz` — 20,262 bytes, SHA-256 `cc6f7bae42f53830016c574d827638d87caf0ea8477063e3073841b00120ee51`. Contains available Jetlink service/container/kernel logs, boot history, cache manifest, engine identity, and precache log. Current server is active and reports Cinque Terre engine `09d080f36965bb2a` ready. Some Jetson timestamps are 1970 before time synchronization, and rotated logs limit historical coverage.

Archives are retained on the devices and have now been downloaded privately to the PC. Both local sizes and SHA-256 checksums match the originals. Allowing scp.exe through Windows Defender Controlled Folder Access resolved the file-write errors. Raw logs and credentials are not published.
