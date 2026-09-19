#!/usr/bin/env python3
"""Optional comma 4 source installer for SSH; not a setup-screen ELF installer."""
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import tempfile
import time

REPOSITORY = "https://github.com/ryanafdahl/nrdr-jetstream.git"
REVISION = "b6320347c06c0dce3d353efdca0df80fad5c240f"
JETLINK = "a01fcae9709cb4924854f0c52806849c62dec5c9"
CONTINUE = "#!/usr/bin/env bash\ncd /data/openpilot\nexec ./launch_openpilot.sh\n"


def require(ok, message):
  if not ok:
    raise RuntimeError(message)


def run(*args, cwd=None):
  subprocess.run(args, cwd=cwd, check=True)


def output(*args, cwd=None):
  return subprocess.check_output(args, cwd=cwd, text=True).strip()


def exchange(candidate, live, backup):
  """Preserve the old tree, and restore it if the second rename fails."""
  require(not backup.exists() and not backup.is_symlink(), "backup destination already exists")
  require(not candidate.is_symlink() and candidate.is_dir(), "candidate must be a real directory")
  require(not live.is_symlink(), "refusing to replace a symlink installation")
  moved = live.exists()
  if moved:
    live.rename(backup)
  try:
    candidate.rename(live)
  except BaseException:
    if moved:
      backup.rename(live)
    raise
  return moved


def rollback_script(live, backup, failed, continue_backup):
  q = lambda path: shlex.quote(str(path))
  return (
    "#!/usr/bin/env bash\nset -euo pipefail\n"
    + f"test -d {q(backup)}\ntest ! -e {q(failed)}\n"
    + "sudo systemctl stop comma\n"
    + f"mv -- {q(live)} {q(failed)}\n"
    + f"if ! mv -- {q(backup)} {q(live)}; then\n"
    + f"  mv -- {q(failed)} {q(live)}\n  sudo systemctl start comma\n  exit 1\nfi\n"
    + f"cp -- {q(continue_backup)} /data/continue.sh\nchmod +x /data/continue.sh\n"
    + "sync\nsudo systemctl start comma\n"
  )


def main():
  require(platform.system() == "Linux" and platform.machine() == "aarch64" and Path("/AGNOS").is_file(),
          "this installer runs on a comma 4, not a desktop or Jetson")
  model = Path("/sys/firmware/devicetree/base/model").read_text().strip("\0\n")
  require(model == "comma mici", f"expected comma 4, found {model!r}")
  data, live, continuation = Path("/data"), Path("/data/openpilot"), Path("/data/continue.sh")
  require(not live.is_symlink() and not continuation.is_symlink(), "custom symlink installation is unsupported")
  existing = continuation.exists()
  if existing:
    require(os.environ.get("SSH_CONNECTION") and not os.environ.get("TMUX"),
            "run from a direct SSH shell outside tmux when replacing installed software")
    require(Path("/data/params/d/IsOffroad").read_bytes() == b"1", "turn ignition off before installation")
    require(live.is_dir(), "existing launcher has no /data/openpilot checkout")
  require(shutil.disk_usage(data).free >= 12 * 1024**3, "need 12 GiB free to download and build")
  run("sudo", "-n", "true")
  run("git", "lfs", "version")
  print(f"Downloading experimental source candidate {REVISION}.", flush=True)
  candidate = Path(tempfile.mkdtemp(prefix="jetson-install-", dir=data))
  # Keep downloads on failure for diagnosis; never delete the existing installation.
  run("git", "init", str(candidate))
  run("git", "remote", "add", "origin", REPOSITORY, cwd=candidate)
  run("git", "fetch", "--depth=1", "origin", REVISION, cwd=candidate)
  run("git", "checkout", "-b", "jetson-trt", "FETCH_HEAD", cwd=candidate)
  require(output("git", "rev-parse", "HEAD", cwd=candidate) == REVISION, "downloaded revision mismatch")
  run("git", "submodule", "update", "--init", "--recursive", cwd=candidate)
  run("git", "lfs", "pull", cwd=candidate)
  require(output("git", "rev-parse", "HEAD", cwd=candidate / "jetlink_repo") == JETLINK, "Jetlink pin mismatch")
  statuses = subprocess.check_output(["git", "submodule", "status", "--recursive"], cwd=candidate, text=True)
  require(all(line.startswith(" ") for line in statuses.splitlines()), "submodule checkout incomplete")
  lfs = output("git", "lfs", "ls-files", cwd=candidate)
  require(all(len(line.split(maxsplit=2)) == 3 and line.split(maxsplit=2)[1] == "+"
              for line in lfs.splitlines()), "model assets contain Git LFS pointers")
  require(not (candidate / "prebuilt").exists(), "source candidate unexpectedly contains prebuilt marker")
  required_os = re.findall(r'export AGNOS_VERSION="([^"]+)"', (candidate / "launch_env.sh").read_text())
  require(len(required_os) == 1 and Path("/VERSION").read_text().strip() == required_os[0],
          f"this source requires AGNOS {required_os}; installed software has not been replaced")
  require((candidate / "launch_openpilot.sh").is_file(), "download has no launcher")
  stamp = time.strftime("%Y%m%d-%H%M%S") + "-" + str(os.getpid())
  backup = data / ("openpilot-before-jetson-" + stamp)
  continue_backup = data / ("continue-before-jetson-" + stamp + ".sh")
  rollback = data / ("rollback-jetson-" + stamp + ".sh")
  previous_continue = continuation.read_bytes() if existing else None
  if existing:
    continue_backup.write_bytes(previous_continue)
    rollback.write_text(rollback_script(live, backup, data / ("openpilot-failed-jetson-" + stamp), continue_backup))
    rollback.chmod(0o755)
  # Finish all network and compatibility checks before stopping the current app.
  if existing:
    run("sudo", "systemctl", "stop", "comma")
  moved = switched = False
  try:
    moved = exchange(candidate, live, backup)
    switched = True
    pending = data / ("continue-jetson-" + stamp + ".tmp")
    pending.write_text(CONTINUE)
    pending.chmod(0o755)
    pending.replace(continuation)
  except BaseException:
    if switched:
      live.rename(candidate)
      if moved:
        backup.rename(live)
    if existing:
      continuation.write_bytes(previous_continue)
      continuation.chmod(0o755)
      run("sudo", "systemctl", "start", "comma")
    raise
  os.sync()
  print(f"Installed source {REVISION}. First startup compiles locally.", flush=True)
  if moved:
    print(f"Previous checkout: {backup}", flush=True)
  if existing:
    print(f"Rollback from SSH: bash {rollback}", flush=True)
    run("sudo", "systemctl", "start", "comma")
  print("Keep the device powered during compilation. This is an unqualified experimental test candidate.", flush=True)


if __name__ == "__main__":
  main()
