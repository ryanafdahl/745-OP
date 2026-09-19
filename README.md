# NRDR Openpilot — Jetson TensorRT

Experimental Jetson acceleration port for **comma 4**, based on NRDR's `nrdr-clean` source. Jetlink connects the comma-side model pipeline to a separately configured NVIDIA Jetson running TensorRT. The native model path remains available as the fallback.

**Current status:** a short installation entry is available through comma's standard fork installer. Source audits and portable tests pass; native compilation, USB connectivity, TensorRT inference, and vehicle behavior still require hardware testing. This is not a precompiled image or a road-qualified release.

## Repository and release layout

- **[jetson-trt](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/tree/jetson-trt)** contains the implementation, installer, tests, and detailed documentation.
- **main** is the repository landing page. Install the candidate described below rather than treating `main` as the device software.
- The short-install branch in `ryanafdahl/openpilot` publishes a specific candidate. Later commits here do not automatically update that branch.
- The historical bootstrap workflow is retired. It must not reset or force-push over subsequent work.

| Component | Pinned revision |
| --- | --- |
| Installed source candidate | `97629ae3bd9f501777d4282c9cef2032c28e4efd` |
| Short-install branch | `ryanafdahl/openpilot` → `nrdr-OP-jetson-trt` |
| NRDR clean base | `b3366b5b56512805be8f0bf832b4981bfd958072` |
| Zoompilot donor | `bcb49d740eb7f7181c2c4aba6de5177b03f88ba3` |
| Jetlink client/server | `a01fcae9709cb4924854f0c52806849c62dec5c9` |

The development repository and install branch have different names. The published candidate commit is the same in both.

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

### 2026-09-19 — Short-name factory-reset installation

- Published the exact candidate as `ryanafdahl/openpilot:nrdr-OP-jetson-trt` so setup accepts `ryanafdahl/nrdr-OP-jetson-trt`.
- Switched the setup instructions to comma's compiled fork installer.
- Corrected the earlier Python URL recommendation: the setup screen rejects non-ELF downloads.
- Retained the Python installer as an optional SSH tool; its checks and rollback behavior are not part of the standard fork installer.

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

Develop against `jetson-trt` and review changes against the pinned clean base. The standard NRDR release publisher has publishing enabled by default; it is not the experimental install command above. Advancing the short installation entry requires explicitly updating and validating the published branch in `ryanafdahl/openpilot`.

## Upstream history and licenses

This project builds on NRDR, comma.ai openpilot, Sunnypilot, Zoompilot, and Jetlink. The inherited Honda/PTC tuning README is retained in [repository history](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/de524fd61003cc2e69368b9d7f8069761146e614/README.md); it is not the installation procedure for this Jetson candidate.

See [LICENSE](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/jetson-trt/LICENSE), [LICENSE.md](https://github.com/ryanafdahl/nrdr-OP-jetson-trt/blob/jetson-trt/LICENSE.md), and the notices in individual components.
