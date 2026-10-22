"""Check GitHub Releases for a newer version and install it in place.

How an update is applied depends on how the app was installed:

- windows:  run the new Inno Setup installer silently over the old install; it restarts the app
- macos:    a helper script replaces the .app bundle after the app quits, then reopens it
- deb:      "pkexec apt-get install" of the new .deb (asks for the password), then restart
- portable: a helper script replaces the unpacked folder after the app quits, then restarts it
- source:   running from source code; only the release page can be offered
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shlex
import ssl
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO = "kalatyn/photo-batch-renamer"
# Can be pointed at a local test server.
API_URL = os.environ.get("PBR_UPDATE_URL", f"https://api.github.com/repos/{REPO}/releases/latest")
RELEASES_PAGE = f"https://github.com/{REPO}/releases/latest"
SUMS_FILE = "SHA256SUMS.txt"
DEB_PREFIX = "/opt/photo-batch-renamer/"


class UpdateError(Exception):
    pass


@dataclass
class Release:
    version: str
    notes: str
    page: str
    assets: dict[str, str]  # file name -> download URL


def parse_version(text: str) -> tuple[int, ...]:
    """"v1.2.3" -> (1, 2, 3). Anything after the numbers is ignored."""
    parts = []
    for piece in text.strip().lstrip("vV").split("."):
        digits = "".join(c for c in piece if c.isdigit()) if piece[:1].isdigit() else ""
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    return parse_version(latest) > parse_version(current)


def _ssl_context():
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _open(url: str, timeout: float = 15):
    req = urllib.request.Request(url, headers={"User-Agent": "photo-batch-renamer-updater",
                                               "Accept": "application/vnd.github+json"})
    return urllib.request.urlopen(req, timeout=timeout, context=_ssl_context())


def fetch_latest(timeout: float = 15) -> Release:
    try:
        with _open(API_URL, timeout) as r:
            data = json.load(r)
    except Exception as e:
        raise UpdateError(str(e)) from e
    return Release(
        version=data.get("tag_name", "").lstrip("vV"),
        notes=data.get("body") or "",
        page=data.get("html_url") or RELEASES_PAGE,
        assets={a["name"]: a["browser_download_url"] for a in data.get("assets", [])},
    )


def install_kind() -> str:
    if not getattr(sys, "frozen", False):
        return "source"
    system = platform.system()
    if system == "Windows":
        return "windows"
    if system == "Darwin":
        return "macos"
    if sys.executable.startswith(DEB_PREFIX):
        return "deb"
    return "portable"


def asset_suffix(kind: str, machine: str | None = None) -> str | None:
    machine = (machine or platform.machine()).lower()
    return {
        "windows": "-Windows-Setup.exe",
        "macos": "-macOS-arm64.dmg" if machine == "arm64" else "-macOS-intel.dmg",
        "deb": "_amd64.deb",
        "portable": "-Linux-x86_64.tar.gz",
    }.get(kind)


def pick_asset(release: Release, kind: str, machine: str | None = None) -> str | None:
    suffix = asset_suffix(kind, machine)
    if not suffix:
        return None
    return next((name for name in release.assets if name.endswith(suffix)), None)


def download(url: str, dest: Path, progress=None, timeout: float = 30):
    """Download to dest; progress(done_bytes, total_bytes) is called while downloading."""
    try:
        with _open(url, timeout) as r, open(dest, "wb") as f:
            total = int(r.headers.get("Content-Length") or 0)
            done = 0
            while chunk := r.read(256 * 1024):
                f.write(chunk)
                done += len(chunk)
                if progress:
                    progress(done, total)
    except Exception as e:
        raise UpdateError(str(e)) from e


def expected_sha256(sums_text: str, name: str) -> str | None:
    for line in sums_text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("*") == name:
            return parts[0].lower()
    return None


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def download_verified(release: Release, name: str, folder: Path, progress=None) -> Path:
    """Download an asset and check it against the release's SHA256SUMS.txt."""
    if SUMS_FILE not in release.assets:
        raise UpdateError("The release has no checksum file, so the download cannot be verified.")
    sums = folder / SUMS_FILE
    download(release.assets[SUMS_FILE], sums)
    want = expected_sha256(sums.read_text(), name)
    if not want:
        raise UpdateError(f"No checksum for {name}.")
    dest = folder / name
    download(release.assets[name], dest, progress)
    if sha256_of(dest) != want:
        dest.unlink(missing_ok=True)
        raise UpdateError("The downloaded file is damaged (checksum mismatch). Please try again.")
    return dest


# --- applying an update -----------------------------------------------------------------

def _detached(cmd: list[str]):
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, close_fds=True, **kw)


def _helper_script(body: str) -> Path:
    """Shell script that first waits until this app has quit."""
    script = Path(tempfile.mkdtemp(prefix="pbr-update-")) / "update.sh"
    script.write_text(
        "#!/bin/sh\n"
        f"while kill -0 {os.getpid()} 2>/dev/null; do sleep 0.3; done\n"
        + body
    )
    script.chmod(0o755)
    return script


def app_bundle() -> Path:
    """macOS: /Applications/Photo Batch Renamer.app (sys.executable is inside Contents/MacOS)."""
    return Path(sys.executable).resolve().parents[2]


def portable_dir() -> Path:
    return Path(sys.executable).resolve().parent


def apply(kind: str, file: Path) -> bool:
    """Start installing the update. Returns True if the app must now quit."""
    q = shlex.quote
    if kind == "windows":
        app_dir = Path(sys.executable).resolve().parent
        all_users = str(app_dir).lower().startswith(os.environ.get("ProgramFiles", "C:\\Program Files").lower())
        _detached([str(file), "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS",
                   "/ALLUSERS" if all_users else "/CURRENTUSER"])
        return True

    if kind == "macos":
        app = app_bundle()
        mount = tempfile.mkdtemp(prefix="pbr-dmg-")
        copy = (f'rm -rf {q(str(app))} && ditto "$MNT/{app.name}" {q(str(app))}')
        if not os.access(app.parent, os.W_OK):
            # /Applications not writable for this user: ask for the admin password.
            copy = ("osascript -e " + q(f"do shell script {json.dumps(copy.replace('$MNT', mount))} "
                                         "with administrator privileges"))
        body = (f"MNT={q(mount)}\n"
                f"hdiutil attach -nobrowse -quiet -mountpoint \"$MNT\" {q(str(file))} || exit 1\n"
                f"{copy}\n"
                f"hdiutil detach -quiet \"$MNT\"\n"
                f"open {q(str(app))}\n")
        _detached(["/bin/sh", str(_helper_script(body))])
        return True

    if kind == "deb":
        result = subprocess.run(["pkexec", "apt-get", "install", "-y", "--allow-downgrades", str(file)],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise UpdateError((result.stderr or result.stdout or "Installation was cancelled.").strip()[-500:])
        _detached(["/usr/bin/photo-batch-renamer"])
        return True

    if kind == "portable":
        target = portable_dir()
        # The folder is deleted and replaced, so make sure it is really the app's own folder.
        if not (target / "_internal").is_dir() or target.parent == target:
            raise UpdateError("Unexpected app folder; please update manually from the release page.")
        if not os.access(target.parent, os.W_OK):
            raise UpdateError(f"No permission to write to {target.parent}.")
        staging = Path(tempfile.mkdtemp(prefix="pbr-new-", dir=target.parent))
        with tarfile.open(file) as tar:
            tar.extractall(staging, filter="data")
        new_dir = next(staging.iterdir())  # the archive holds one top-level folder
        exe = target / Path(sys.executable).name
        body = (f"rm -rf {q(str(target))} && mv {q(str(new_dir))} {q(str(target))} && rmdir {q(str(staging))}\n"
                f"{q(str(exe))} &\n")
        _detached(["/bin/sh", str(_helper_script(body))])
        return True

    raise UpdateError("Automatic update is not available here. Please download the new version from the release page.")
