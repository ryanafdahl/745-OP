# StarPilot Bluetooth port — development

Status: **source prototype; not included in the installer and not enabled on the comma**.

Requested scope is pairing, audio, and controller features. Pairing/audio adapters and a controller input-test screen are staged on `starpilot-bluetooth`. Controller action mappings and hardware qualification remain unfinished.

## Source and adaptation

Ported from [firestar5683/StarPilot](https://github.com/firestar5683/StarPilot/tree/c3e4ec630f41c4baa43254a90f718abd1bf764a1), pinned at `c3e4ec630f41c4baa43254a90f718abd1bf764a1`. MIT notices are retained in [LICENSE](../openpilot/system/bluetooth/LICENSE).

- BlueZ pairing, saved devices, explicit pairing confirmation, scanning, connect/disconnect/forget, reconnect backoff, and optional delayed controller disconnect offroad.
- comma 4 Settings → Bluetooth with an audio destination and offroad audio test.
- 48 kHz, signed 16-bit stereo A2DP through BlueALSA. Bluetooth mirrors existing soundd output; the comma speaker remains active. A disconnected sink, full queue, or sink exception does not suppress local audio.
- Typed JetStream Params API and process-manager predicates replace StarPilot-specific APIs. Bluetooth defaults off.
- Controller input testing recognizes Bluetooth HID buttons and D-pad presses, ignores repeats/releases and analog sticks, and never sends vehicle commands. No controller or button assignments have been chosen.

StarPilot's cruise-speed, engagement, AOL, coasting, selfie, bookmark and personality actions depend on its own vehicle/UI services. Those mappings are **not ported yet**; adding their counters alone would not make them work in JetStream.

## Verified OS blocker

Read-only inspection of the comma on 2026-09-20 UTC found AGNOS **19.7**, Ubuntu **24.04.4**, kernel **4.9.103**, and `# CONFIG_BT is not set`. BlueZ, BlueALSA, the radio helper/service, and `hci0` are absent. Python `jeepney` and `evdev` are present.

A package install or openpilot update cannot enable Bluetooth in this kernel. StarPilot supplies its radio support through a custom AGNOS image (19.6.20), including a Bluetooth-enabled kernel and QCA UART radio setup. Its OS installer/reset configuration also differs from JetStream. That image has not been flashed or adopted.

The [radio helper](https://github.com/firestar5683/agnos-builder/blob/master/userspace/usr/comma/bluetooth-radio) and [service](https://github.com/firestar5683/agnos-builder/blob/master/userspace/files/starpilot-bluetooth-radio.service) document the required OS integration: Bluetooth firmware partition, `/dev/btpower`, `/dev/ttyHS1`, QCA `btattach`, BlueZ, BlueALSA, persistent pairing storage and D-Bus permissions.

Read-only prerequisite check from this development branch:

```sh
python -m openpilot.system.bluetooth.preflight
```

A successful prerequisite check means runtime files/kernel support were found; it does not prove radio, pairing, or audio functionality.

## Validation and remaining work

**27 tests passed** on the comma's Python 3.12 environment using a temporary source overlay and mocked Bluetooth services, plus successful imports of both settings layouts and their target UI APIs. Tests cover protocol/device classification, explicit offroad operations, pairing, reconnect/disconnect policy, bounded audio buffering, PCM conversion, kernel prerequisite detection, controller event filtering and local audio on a Bluetooth exception.

No live runtime files or settings were changed. Test dependencies and source copies were isolated under `/tmp`. No actual Bluetooth pairing, speaker playback, controller, rendered UI, target Params rebuild, or combined Jetlink/Bluetooth load test has been qualified.

Before this can become a release:
1. Build/review Bluetooth kernel and userspace support compatible with JetStream's AGNOS 19.7 hardware and boot chain.
2. Rebuild target Params and validate Settings rendering, reboot persistence, offroad pairing and radio shutdown.
3. Choose a controller, port selected button actions through JetStream's existing interfaces, and verify press/release, reconnect and stale-input handling.
4. Bench-test audio latency/disconnects and simultaneous Jetlink USB inference. Keep the installer on the validated release until these pass.
