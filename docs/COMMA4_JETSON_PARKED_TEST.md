<!-- Setup URL correction: see the current installation guide. -->
# Comma four + Jetson: experimental installation and hardware validation

**Status: experimental source installer available; hardware validation pending.**

Use [the direct installation guide](JETSON_INSTALL.md) for the short-name factory-reset procedure and first-boot build. The isolated staging procedure below is optional diagnostic tooling, not a prerequisite to that installation.
A successful source-audit workflow does not establish hardware compatibility or qualify this candidate for driving. The selected installation procedure is a factory reset; it does not use the optional SSH helper's backup procedure.

## Source revisions under review

- Destination: `ryanafdahl/nrdr-OP-jetson-trt`, branch `jetson-trt`.
- NRDR clean base: `b3366b5b56512805be8f0bf832b4981bfd958072`.
- Zoompilot donor: `bcb49d740eb7f7181c2c4aba6de5177b03f88ba3`.
- Jetlink server/client submodule: `a01fcae9709cb4924854f0c52806849c62dec5c9` in `zoompilot/jetlink`.

Review a particular destination commit, not just the branch name. The source-audit artifact records the exact commit tested. The old bootstrap is retired; it must not reset or force-push this branch over subsequent fixes and documentation.

## What has and has not been checked

The source audit checks ancestry, protected NRDR subtree equality, parameter preservation, the Jetlink pin, fresh-install opt-in, syntax, and some local import references. Portable upstream tests exercise simulated file, socket, transfer-validation and tuning behavior. These checks are not a complete runtime import test, a target build, or physical hardware tests.

The `prebuilt` marker was removed so an inherited marker cannot bypass rebuilding changed source. That does **not** mean a new comma-four build has been produced. Native libraries, cereal bindings, camera/model artifacts and the comma-side warp must be built and validated together for the target hardware. An Ubuntu x86 runner cannot establish this by parsing Python.

The following remain required: a clean target build, native boot/import checks, actual USB enumeration, TensorRT engine execution, live model outputs, restart/reconnect behavior and verification that the initial test cannot actuate a vehicle.

## Corrections to earlier installation instructions

The earlier `installer.comma.ai/ryanafdahl/jetson-trt` URL is **not a verified installer for this repository**. The documented comma example uses an account's `openpilot` repository; this repository is named `nrdr-OP-jetson-trt`. It is now public. The direct installation guide now uses `ryanafdahl/nrdr-OP-jetson-trt`, backed by a published candidate branch in `ryanafdahl/openpilot`. The earlier raw Python URL is invalid for the setup screen because that screen requires an ELF installer.

Before any install, inspect the actual installer payload and establish that its repository, branch, revision, authentication and submodule behavior match this project. Use an authenticated staging method or a reviewed installer with the exact repository. Do not put a GitHub token in a publicly shared URL, publish the repository without explicit permission, or rename it merely to follow the earlier URL.

Official example: https://docs.comma.ai/how-to/turn-the-speed-blue/

## First hardware test: off-vehicle, without an actuator path

Use a separate staging checkout on a correctly powered comma four that is physically disconnected from the vehicle CAN/harness. Preserve a known-good installation and recovery path. Confirm its AGNOS version and the exact Jetson model, memory, JetPack/L4T and TensorRT versions before choosing build or wiring instructions.

Being in Park with the parking brake set is an additional precaution, **not** proof that experimental software cannot send steering or other control commands. Do not enable controls, spoof engagement, flash EPS firmware, change panda safety modes, weaken driver monitoring, or bypass calibration/safety checks for this test. The first proposed car-connected test requires a separately reviewed non-actuating setup; this document does not yet approve it.

For power/data topology, consult the pinned Jetlink documentation and the hardware manuals. The donor's documented reference uses a separately powered Orin Nano Super 8 GB on JetPack 6.2 / L4T r36.4.3, and its container uses CUDA 12.6 / TensorRT 10.3. This is not confirmation of the user's Jetson configuration or validation of this port. Use the matching pinned server, not an unreviewed latest branch.

Pinned setup reference: https://github.com/zoompilot/jetlink/blob/a01fcae9709cb4924854f0c52806849c62dec5c9/docs/jetson.md

## Required bench evidence before progressing

1. Record the exact source, submodule and environment revisions. Complete a target build with no stale prebuilt shortcut and retain its logs.
2. With Jetlink disabled, verify the rebuilt native software boots and the native model path works. `JetlinkEnabled` has no true default, but its value is persistent: an existing device can retain a previous opt-in. Check the actual value.
3. In the physically isolated bench setup, verify the pinned server connects and the intended model provisions. Record engine/model hashes and actual frame outputs, not just the ready parameter or a green icon.
4. Verify sustained live `modelV2` output, accelerator state, finite outputs, timing, restart/reconnect behavior and recovery to the native path. A populated `JetlinkEngineReady` is cached provisioning evidence, not proof that the Jetson is currently running inference.
5. Review the resulting evidence and remaining failures before deciding whether a non-actuating parked-car test is appropriate. Passing this checklist is not road-use qualification.

## Read-only diagnostics after a successful staged target build

The following is for a correctly built, isolated staging checkout. It does not install software or enable Jetlink. Run from that checkout using its project environment:

```python
from openpilot.common.params import Params
p = Params()
for key in ("JetlinkEnabled", "JetlinkEndpoint", "JetlinkEngineReady", "JetlinkSpec", "JetlinkCachedModels", "AcceleratorProgress"):
    print(key, repr(p.get(key)))
```

This branch's `Params.get` returns typed values and does not accept the old `encoding="utf-8"` argument. An import or native-library error here is a build blocker, not a reason to ignore the diagnostic.

The source-audit artifacts are evidence only, **not an installable image or release**. No safety certification or road-use approval is implied.

Safety reference: https://docs.comma.ai/SAFETY/

## Concrete next step: build in a separate comma 4 checkout

`tools/jetson_staged_build.py` now prepares native build evidence without installing or launching this branch. Run it on the physically disconnected, correctly powered comma 4 described above. Its default mode is read-only preflight. It requires the source's AGNOS version (currently 19.7); an OS mismatch stops the procedure rather than upgrading the device.

Use the full commit SHA from a **successful source-audit run containing this tool**, with GitHub authentication already configured for this private repository. Do not embed credentials in the clone URL. Replace the value of `REV` below:

```bash
set -euo pipefail
REV=REPLACE_WITH_REVIEWED_40_CHARACTER_COMMIT_SHA
STAGE="/data/jetson-trt-stage-$REV"
GIT_LFS_SKIP_SMUDGE=1 git clone --no-checkout https://github.com/ryanafdahl/nrdr-OP-jetson-trt.git "$STAGE"
cd "$STAGE"
git checkout --detach "$REV"
git submodule update --init --recursive
git lfs pull
/usr/local/venv/bin/python3 tools/jetson_staged_build.py --expected-commit "$REV"
```

Proceed to the build only after preflight succeeds. Keep the existing installation in place. This command compiles in the staging checkout and writes logs under `/data/jetson-trt-evidence/`:

```bash
/usr/local/venv/bin/python3 tools/jetson_staged_build.py --expected-commit "$REV" --build --jobs 2
```

The build uses SCons with its cache disabled and no existing build signature, builds both camera configurations, validates native model assets, imports fresh Params/cereal bindings, and loads the comma-side Jetlink warp to verify its captured inputs. It records dependency versions, source/submodule revisions, artifact SHA-256 hashes, and a final `result.json`. A successful result is `BUILD_AND_SMOKE_PASSED`; this is **not** proof of live inference or a car-test pass. Watch `build.log` from a second SSH session if desired.

If it fails, preserve the evidence directory and checkout. Return `result.json` and the failing log for the next fix. Do not manually create a `prebuilt` marker or start manager to get around a failure. A new evidence build uses a fresh staging directory; rename the failed staging directory to preserve it before reusing the same revision's name.

After a successful build, the next step is a separately reviewed isolated camera/native-model run, followed by the pinned Jetson server and reconnect/fallback tests. The existing `jetlink_live_bench.sh` defaults to the accelerator path and `jetlink_bench.py` includes a synthetic-engagement option; neither is the first-step command here. Confirm Jetson model/RAM, JetPack/L4T/TensorRT, power/data wiring, and the isolated runtime setup before that stage. Do not run the standard release publisher for this staging build: its defaults include publishing branches.
