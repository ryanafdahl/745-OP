# NRDR Openpilot — Jetson TensorRT

Experimental Jetson acceleration port for **comma 4**, based on NRDR's `nrdr-clean` source. Jetlink connects the comma-side model pipeline to a separately configured NVIDIA Jetson running TensorRT. The native model path remains available as the fallback.

**Current status:** a public, pinned source installer is available. Source audits and portable tests pass; native compilation, USB connectivity, TensorRT inference, and vehicle behavior still require hardware testing. This is not a precompiled image or a road-qualified release.

## Repository and release layout

- **[jetson-trt](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/tree/jetson-trt)** contains the implementation, installer, tests, and detailed documentation.
- **main** is the repository landing page. Install the candidate described below rather than treating `main` as the device software.
- The installer pins a specific source revision. Later commits to `jetson-trt` do not change what the linked installer initially installs.
- The historical bootstrap workflow is retired. It must not reset or force-push over subsequent work.

| Component | Pinned revision |
| --- | --- |
| Installed source candidate | `97629ae3bd9f501777d4282c9cef2032c28e4efd` |
| Public installer payload | `af6bf0afb069f0fdca9cd89c131496005bf9fe78` |
| NRDR clean base | `b3366b5b56512805be8f0bf832b4981bfd958072` |
| Zoompilot donor | `bcb49d740eb7f7181c2c4aba6de5177b03f88ba3` |
| Jetlink client/server | `a01fcae9709cb4924854f0c52806849c62dec5c9` |

The source and installer revisions differ intentionally: the installer was published after the source candidate and selects that candidate explicitly.

## Install after a factory reset

The preferred procedure for this repository is a fresh factory reset for every installation. Resetting removes the previous installation and local configuration; this route does not use a rollback checkout.

1. Factory reset the comma 4.
2. Reconnect it to Wi-Fi and complete setup until the custom software URL prompt.
3. Enter the complete URL below.
4. Keep the device powered and online while the installer downloads the source and the comma compiles it on first startup.

```text
https://raw.githubusercontent.com/ryanafdahl/nrdr-OP-jetson-trt/af6bf0afb069f0fdca9cd89c131496005bf9fe78/tools/install_jetson.py
```

No SSH session or separate staging build is required for this route. Use the same procedure for reinstalls.

The installer checks for comma 4, **AGNOS 19.7**, Git LFS, passwordless sudo, and at least **12 GiB free**. It downloads the pinned source and Jetlink submodule and hydrates model files. It does not upgrade AGNOS; a factory reset should not be treated as an OS upgrade.

**Keep power connected during compilation.** The launcher stops if compilation fails instead of continuing into manager with inherited binaries.

This URL installs the pinned candidate listed above, not whichever commit happens to be newest on the branch. Anonymous payload download has been verified in CI; execution through the physical setup UI has not yet been tested.

The old `installer.comma.ai/ryanafdahl/jetson-trt` URL is not the installer for this repository.

## Jetson setup and first test

The comma installer does **not** install the Jetson server or change Jetson firmware. Use the matching [pinned Jetlink setup documentation](https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md) for the server and power/data topology. Compatibility with a particular Jetson, JetPack, and TensorRT combination must be checked on that hardware.

Jetlink is opt-in. A fresh configuration does not enable it by default, but an existing `JetlinkEnabled` value persists across installation. Cached engine-ready information is not proof of live Jetson inference.

For the first parked test, verify boot, camera/UI operation, and the native model path before evaluating acceleration. Keep controls disabled and do not drive; Park alone does not prevent steering actuation. Check actual model output, timing, connection loss, and fallback before expanding testing. This Jetson port does not require EPS flashing.

## Troubleshooting

For a fresh reinstall, factory reset and use the same custom software URL again. No rollback command is required.

If installation fails at the setup screen, record the displayed error. If SSH is available after installation, the following command captures first-boot output:

```bash
tmux capture-pane -p -S -2000 -t comma > /data/jetson-first-boot.txt
```

Include the log, on-screen error, installed commit, AGNOS version, and Jetson model/software versions when reporting a failure. If the installer stops before replacing the checkout, fix the reported requirement instead of bypassing it. If compilation fails, do not create a `prebuilt` marker to skip the build.

## Change log

### 2026-09-19 — Public experimental installer

- Published a repository-specific installer with an immutable URL and pinned source revision.
- Added download, device, AGNOS, submodule, and Git LFS checks.
- Preserved the existing checkout and launcher, with a generated rollback command.
- Added tests for fresh installation, backup preservation, failed-swap recovery, and platform rejection.
- Added CI verification that the public installer payload matches the reviewed file.
- [Fixed first-boot startup](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/commit/97629ae3bd9f501777d4282c9cef2032c28e4efd) so a failed build cannot proceed into manager.
- Published installation, recovery, and test instructions.

### 2026-09-19 — Build preparation and connection cleanup

- Added optional comma 4 staging-build tooling with revision and environment checks.
- Added build logs, native-binding/model-asset checks, warp checks, and artifact hashes.
- Added guards against staging paths overlapping the installed software.
- [Fixed failed lease-socket cleanup](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/commit/8404f553ed3eb632a0d1b414543cd77508146edf), including failed connect, bind, listen, and timeout setup, with eight regression tests.

### 2026-09-19 — Source integration and audit baseline

- Established the port on the pinned NRDR clean base and pinned Jetlink dependency.
- Integrated accelerator parameters, model status fields, comma-side warp compilation, and model-pipeline joining/fallback support.
- Preserved NRDR timing fields and the native model integration.
- Removed the inherited `prebuilt` shortcut so changed source is rebuilt.
- Retired the destructive bootstrap and added repeatable source-audit evidence.

These notes describe this repository's Jetson integration. They are not a complete change log for upstream NRDR, openpilot, or Zoompilot.

## Validation status

The [installer validation run](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/actions/runs/35459097462) passed **64 portable tests in each of two passes**, along with source checks and anonymous installer download verification.

The audit checks provenance, selected protected NRDR subtree equality, parameter preservation, Jetlink pinning, opt-in behavior, syntax, and local source dependencies. Filesystem transaction tests exercise installer recovery. These checks do not establish a successful comma 4 build or live TensorRT inference.

Still unverified on hardware: first-boot compilation, setup-screen execution, USB enumeration, live model outputs and timing, reconnect/fallback behavior, and vehicle operation.

## Documentation and development

- [Factory-reset installation guide](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/jetson-trt/docs/JETSON_INSTALL.md)
- [Hardware validation and optional staging build](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/jetson-trt/docs/COMMA4_JETSON_PARKED_TEST.md)
- [Source-audit workflow](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/jetson-trt/.github/workflows/validate-jetson-trt.yml)
- [Installer implementation](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/jetson-trt/tools/install_jetson.py)
- [Optional staging builder](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/jetson-trt/tools/jetson_staged_build.py)

Develop against `jetson-trt` and review changes against the pinned clean base. The standard NRDR release publisher has publishing enabled by default; it is not the experimental install command above. Advancing the public installer requires explicitly updating and validating its source pin.

## Upstream history and licenses

This project builds on NRDR, comma.ai openpilot, Sunnypilot, Zoompilot, and Jetlink. The inherited Honda/PTC tuning README is retained in [repository history](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/de524fd61003cc2e69368b9d7f8069761146e614/README.md); it is not the installation procedure for this Jetson candidate.

See [LICENSE](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/jetson-trt/LICENSE), [LICENSE.md](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/jetson-trt/LICENSE.md), and the notices in individual components.
