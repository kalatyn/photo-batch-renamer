import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_batch_renamer import updater  # noqa: E402

ASSETS = ["PhotoBatchRenamer-1.2.0-Windows-Setup.exe", "PhotoBatchRenamer-1.2.0-macOS-arm64.dmg",
          "PhotoBatchRenamer-1.2.0-macOS-intel.dmg", "photo-batch-renamer_1.2.0_amd64.deb",
          "PhotoBatchRenamer-1.2.0-Linux-x86_64.tar.gz", "SHA256SUMS.txt"]


def release(assets=None, folder: Path | None = None):
    names = assets if assets is not None else ASSETS
    base = folder.as_uri() + "/" if folder else "https://example.invalid/"
    return updater.Release("1.2.0", "notes", "https://example.invalid", {n: base + n for n in names})


@pytest.mark.parametrize("latest,current,newer", [
    ("1.1.0", "1.0.1", True), ("v1.10.0", "1.9.9", True), ("1.0.1", "1.0.1", False),
    ("1.0.0", "1.0.1", False), ("2.0", "1.9.9", True), ("1.2.0-beta", "1.1.0", True), ("", "1.0.0", False),
])
def test_is_newer(latest, current, newer):
    assert updater.is_newer(latest, current) is newer


@pytest.mark.parametrize("kind,machine,expected", [
    ("windows", "AMD64", "PhotoBatchRenamer-1.2.0-Windows-Setup.exe"),
    ("macos", "arm64", "PhotoBatchRenamer-1.2.0-macOS-arm64.dmg"),
    ("macos", "x86_64", "PhotoBatchRenamer-1.2.0-macOS-intel.dmg"),
    ("deb", "x86_64", "photo-batch-renamer_1.2.0_amd64.deb"),
    ("portable", "x86_64", "PhotoBatchRenamer-1.2.0-Linux-x86_64.tar.gz"),
    ("source", "x86_64", None),
])
def test_pick_asset(kind, machine, expected):
    assert updater.pick_asset(release(), kind, machine) == expected


def test_pick_asset_missing_file():
    assert updater.pick_asset(release(["SHA256SUMS.txt"]), "windows", "AMD64") is None


def test_running_from_source_is_detected():
    assert updater.install_kind() == "source"


def test_expected_sha256():
    sums = "aaa  one.exe\nBBB *two.dmg\n"
    assert updater.expected_sha256(sums, "one.exe") == "aaa"
    assert updater.expected_sha256(sums, "two.dmg") == "bbb"
    assert updater.expected_sha256(sums, "three.deb") is None


def _publish(folder: Path, name: str, data: bytes, sums_data: bytes | None = None):
    (folder / name).write_bytes(data)
    digest = hashlib.sha256(sums_data if sums_data is not None else data).hexdigest()
    (folder / "SHA256SUMS.txt").write_text(f"{digest}  {name}\n")


def test_download_verified_ok(tmp_path):
    server, dl = tmp_path / "server", tmp_path / "dl"
    server.mkdir(), dl.mkdir()
    name = "PhotoBatchRenamer-1.2.0-Windows-Setup.exe"
    _publish(server, name, b"installer bytes")
    seen = []
    path = updater.download_verified(release([name, "SHA256SUMS.txt"], server), name, dl,
                                     lambda done, total: seen.append((done, total)))
    assert path.read_bytes() == b"installer bytes"
    assert seen[-1] == (15, 15)


def test_download_verified_rejects_damaged_file(tmp_path):
    server, dl = tmp_path / "server", tmp_path / "dl"
    server.mkdir(), dl.mkdir()
    name = "PhotoBatchRenamer-1.2.0-Windows-Setup.exe"
    _publish(server, name, b"tampered bytes", sums_data=b"original bytes")
    with pytest.raises(updater.UpdateError, match="damaged"):
        updater.download_verified(release([name, "SHA256SUMS.txt"], server), name, dl)
    assert not (dl / name).exists()


def test_download_verified_needs_checksums(tmp_path):
    name = "PhotoBatchRenamer-1.2.0-Windows-Setup.exe"
    with pytest.raises(updater.UpdateError, match="checksum"):
        updater.download_verified(release([name]), name, tmp_path)


def test_portable_update_refuses_unexpected_folder(tmp_path, monkeypatch):
    exe = tmp_path / "somewhere" / "Photo Batch Renamer"
    exe.parent.mkdir()
    exe.write_text("")
    monkeypatch.setattr(updater.sys, "executable", str(exe))
    with pytest.raises(updater.UpdateError, match="Unexpected app folder"):
        updater.apply("portable", tmp_path / "new.tar.gz")
    assert exe.exists()


def test_source_cannot_self_update(tmp_path):
    with pytest.raises(updater.UpdateError):
        updater.apply("source", tmp_path / "x")
