"""Build the app and its installer for the current operating system.

    python packaging/build.py

Windows -> dist/PhotoBatchRenamer-<ver>-Windows-Setup.exe   (needs Inno Setup 6)
macOS   -> dist/PhotoBatchRenamer-<ver>-macOS-<arch>.dmg
Linux   -> dist/photo-batch-renamer_<ver>_amd64.deb  and  dist/PhotoBatchRenamer-<ver>-Linux-x86_64.tar.gz
"""
from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
APP_NAME = "Photo Batch Renamer"
FILE_NAME = "PhotoBatchRenamer"
PKG_NAME = "photo-batch-renamer"
VERSION = re.search(r'__version__ = "([^"]+)"',
                    (ROOT / "src/photo_batch_renamer/__init__.py").read_text()).group(1)


def run(*cmd, **kw):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, cwd=ROOT, **kw)


def pyinstaller(icon: str):
    env = {**os.environ, "PBR_ICON": icon, "PBR_VERSION": VERSION}
    run(sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
        "packaging/photo_batch_renamer.spec", env=env)


def build_windows():
    pyinstaller("icon.ico")
    iscc = shutil.which("iscc") or r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    run(iscc, f"/DAppVersion={VERSION}", f"/DSourceDir={DIST / APP_NAME}", f"/DOutputDir={DIST}",
        "packaging/windows/installer.iss")


def build_macos():
    pyinstaller("icon.icns")
    app = DIST / f"{APP_NAME}.app"

    arch = "arm64" if platform.machine() == "arm64" else "intel"
    stage = DIST / "dmg"
    shutil.rmtree(stage, ignore_errors=True)
    stage.mkdir()
    shutil.copytree(app, stage / app.name, symlinks=True)
    (stage / "Applications").symlink_to("/Applications")
    dmg = DIST / f"{FILE_NAME}-{VERSION}-macOS-{arch}.dmg"
    dmg.unlink(missing_ok=True)
    run("hdiutil", "create", "-volname", APP_NAME, "-srcfolder", stage, "-ov", "-format", "UDZO", dmg)


def build_linux():
    pyinstaller("icon.png")
    bundle = DIST / APP_NAME

    # Portable archive.
    tgz = DIST / f"{FILE_NAME}-{VERSION}-Linux-x86_64.tar.gz"
    with tarfile.open(tgz, "w:gz") as tar:
        tar.add(bundle, arcname=FILE_NAME)

    # .deb package: app in /opt, launcher in /usr/bin, menu entry and icon.
    root = DIST / "deb"
    shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(bundle, root / "opt" / PKG_NAME, symlinks=True)
    (root / "usr/bin").mkdir(parents=True)
    (root / "usr/bin" / PKG_NAME).symlink_to(f"/opt/{PKG_NAME}/{APP_NAME}")
    apps = root / "usr/share/applications"
    apps.mkdir(parents=True)
    shutil.copy(ROOT / "packaging/linux/photo-batch-renamer.desktop", apps)
    icons = root / "usr/share/icons/hicolor/256x256/apps"
    icons.mkdir(parents=True)
    shutil.copy(ROOT / "src/photo_batch_renamer/icon.png", icons / f"{PKG_NAME}.png")

    # Standard package permissions: 755 for folders and programs, 644 for other files.
    for p in [root, *root.rglob("*")]:
        if not p.is_symlink():
            p.chmod(0o755 if p.is_dir() or os.access(p, os.X_OK) else 0o644)

    size_kb = sum(f.stat().st_size for f in root.rglob("*") if f.is_file() and not f.is_symlink()) // 1024
    control = (ROOT / "packaging/linux/control").read_text()
    (root / "DEBIAN").mkdir()
    (root / "DEBIAN/control").write_text(
        control.replace("@VERSION@", VERSION).replace("@SIZE@", str(size_kb)))
    deb = DIST / f"{PKG_NAME}_{VERSION}_amd64.deb"
    run("dpkg-deb", "--root-owner-group", "--build", root, deb)


def main():
    system = platform.system()
    {"Windows": build_windows, "Darwin": build_macos, "Linux": build_linux}[system]()
    print("\nDone:")
    for f in sorted(DIST.iterdir()):
        if f.is_file():
            print(f"  {f.name}  ({f.stat().st_size / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
