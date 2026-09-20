# Scheduled NRDR nightly updates

GitHub Actions checks [nrdr/openpilot → nrdr-nightly](https://github.com/nrdr/openpilot/tree/nrdr-nightly) **daily at 10:23 UTC** (3:23 a.m. Pacific during daylight saving time, 2:23 a.m. during standard time). GitHub may delay scheduled runs. A manual **Run workflow** and a read-only **dry_run** option are available.

The workflow lives on the default branch, `main`, and automatically commits compatible source updates to `jetson-trt`. It does not track sunnypilot staging and does not create PRs or auto-deploy to the comma.

## What gets committed

The updater compares complete Git trees between recorded NRDR nightly snapshots. An ordinary UTF-8 text file is eligible only if 745-OP still matches the previous upstream version. New files and deletions follow the same rule. Python updates must parse successfully. Customized files, binaries, symlinks, dependencies, OS/build files, automation, vehicle/safety logic, NRDR policy, and Jetlink/model integration are deferred for manual integration.

Every new observed snapshot produces one atomic, non-forced commit containing eligible file changes, the observation marker, a detailed report, and a compact README recap. The initial comparison starts from NRDR clean `b3366b5b56512805be8f0bf832b4981bfd958072`. Unresolved paths carry forward; the marker does **not** mean every nightly change was imported. No commit is made for an unchanged snapshot.

The existing source audit runs against the exact new commit in a separate job with read-only permissions. It checks provenance, model inputs, imports and the existing portable tests. A failed audit marks the workflow failed; the source commit remains for inspection. Physical comma/Jetson qualification and installer promotion remain separate.

## Operation

- [Daily workflow](https://github.com/ryanafdahl/745-OP/actions/workflows/sync-nrdr-nightly.yml)
- [Latest report](https://github.com/ryanafdahl/745-OP/blob/jetson-trt/docs/NRDR_NIGHTLY_SYNC.md)
- State: `.github/nrdr-nightly-sync.json` on `jetson-trt`.
- Uses the repository's built-in `GITHUB_TOKEN`; no personal token or SSH credentials are needed.
- The update job reads blobs through the GitHub API and never executes upstream code. Its writes use a fast-forward ref update, so concurrent edits cannot be overwritten.
- The schedule configuration and updater are maintained on `main`; copies on `jetson-trt` are for reference. Disable the workflow in Actions to stop it.
