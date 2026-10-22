import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_batch_renamer import core  # noqa: E402
from photo_batch_renamer.i18n import STRINGS, tr  # noqa: E402


def make(folder: Path, *names: str, mtime_start: int = 1_460_000_000):
    for i, n in enumerate(names):
        p = folder / n
        p.write_bytes(b"x")
        os.utime(p, (mtime_start + i * 60, mtime_start + i * 60))


def test_list_skips_hidden_system_and_subfolders(tmp_path):
    make(tmp_path, "DSC0001.JPG", ".hidden", "Thumbs.db", "desktop.ini", ".DS_Store")
    (tmp_path / "sub").mkdir()
    assert core.list_files(str(tmp_path)) == ["DSC0001.JPG"]


def test_natural_name_order(tmp_path):
    make(tmp_path, "IMG_10.jpg", "IMG_9.jpg", "IMG_100.jpg")
    assert core.list_files(str(tmp_path)) == ["IMG_9.jpg", "IMG_10.jpg", "IMG_100.jpg"]


def test_date_order_uses_mtime_without_exif(tmp_path):
    make(tmp_path, "b.jpg", "a.jpg", "c.mp4")  # b is the oldest
    assert core.list_files(str(tmp_path), core.SORT_DATE) == ["b.jpg", "a.jpg", "c.mp4"]


def test_date_order_prefers_exif(tmp_path):
    from PIL import Image

    def jpg(name, date, mtime):
        exif = Image.Exif()
        exif.get_ifd(0x8769)[36867] = date
        Image.new("RGB", (4, 4)).save(tmp_path / name, exif=exif)
        os.utime(tmp_path / name, (mtime, mtime))

    # File times say the opposite of EXIF; EXIF must win.
    jpg("first.jpg", "2016:05:01 10:00:00", 2_000_000_000)
    jpg("second.jpg", "2016:05:02 10:00:00", 1_000_000_000)
    assert core.list_files(str(tmp_path), core.SORT_DATE) == ["first.jpg", "second.jpg"]


@pytest.mark.parametrize(
    "pad,total,expected",
    [(False, 5, "Your Name_3.jpg"), (True, 5, "Your Name_003.jpg"), (True, 1500, "Your Name_0003.jpg")],
)
def test_new_name(pad, total, expected):
    assert core.new_name(" Your Name ", 3, total, pad, "DSC0003.JPG") == expected


def test_new_name_without_extension():
    assert core.new_name("Trip", 1, 1, False, "README") == "Trip_1"


@pytest.mark.parametrize("base,err", [("", "err_empty"), ("  ", "err_empty"), ("a/b", "err_chars"),
                                      ("a:b", "err_chars"), ("trip.", "err_chars"), ("Your Name", None)])
def test_validate(base, err):
    assert core.validate_base(base) == err


def test_rename_and_undo(tmp_path):
    make(tmp_path, "DSC0001.JPG", "DSC0002.JPG", "MOV0003.MP4")
    files = core.list_files(str(tmp_path))
    undo = core.rename_all(str(tmp_path), core.build_plan(files, "Trip", False))
    assert sorted(os.listdir(tmp_path)) == ["Trip_1.jpg", "Trip_2.jpg", "Trip_3.mp4"]
    core.rename_all(str(tmp_path), undo)
    assert sorted(os.listdir(tmp_path)) == ["DSC0001.JPG", "DSC0002.JPG", "MOV0003.MP4"]


def test_new_name_may_equal_another_files_old_name(tmp_path):
    make(tmp_path, "Trip_2.jpg", "a.jpg", "b.jpg")
    files = core.list_files(str(tmp_path))
    core.rename_all(str(tmp_path), core.build_plan(files, "Trip", False))
    assert sorted(os.listdir(tmp_path)) == ["Trip_1.jpg", "Trip_2.jpg", "Trip_3.jpg"]


def test_refuses_to_overwrite_file_outside_plan(tmp_path):
    make(tmp_path, "a.jpg", "Trip_1.jpg")
    with pytest.raises(core.RenameError) as e:
        core.rename_all(str(tmp_path), [("a.jpg", "Trip_1.jpg")])
    assert e.value.key == "err_exists"
    assert sorted(os.listdir(tmp_path)) == ["Trip_1.jpg", "a.jpg"]


def test_failure_rolls_back(tmp_path, monkeypatch):
    make(tmp_path, "a.jpg", "b.jpg", "c.jpg")
    real = os.rename
    calls = {"n": 0}

    def flaky(src, dst):
        calls["n"] += 1
        if calls["n"] == 5:  # fail during the second step
            raise PermissionError("locked")
        real(src, dst)

    monkeypatch.setattr(core.os, "rename", flaky)
    with pytest.raises(core.RenameError) as e:
        core.rename_all(str(tmp_path), core.build_plan(["a.jpg", "b.jpg", "c.jpg"], "T", False))
    monkeypatch.setattr(core.os, "rename", real)
    assert e.value.key == "err_os"
    assert sorted(os.listdir(tmp_path)) == ["a.jpg", "b.jpg", "c.jpg"]


def test_every_error_key_has_a_text():
    for key in ("err_empty", "err_chars", "err_exists", "err_os"):
        assert key in STRINGS
    assert tr("count", sel=2, n=3, photos=2, videos=1) == "Selected 2 of 3  ·  Photos: 2  ·  Videos: 1"


def test_only_photos_and_videos_are_listed(tmp_path):
    make(tmp_path, "DSC0001.JPG", "IMG_2.heic", "R0003.CR3", "clip.MP4", "GX010004.MOV",
         "notes.txt", "setup.exe", "list.pdf", "song.mp3", "photo.jpg.part", "README")
    assert core.list_files(str(tmp_path)) == ["clip.MP4", "DSC0001.JPG", "GX010004.MOV", "IMG_2.heic", "R0003.CR3"]


@pytest.mark.parametrize("name,kind", [("a.JPG", core.PHOTO), ("a.nef", core.PHOTO), ("a.DNG", core.PHOTO),
                                       ("a.mov", core.VIDEO), ("a.MTS", core.VIDEO), ("a.insv", core.VIDEO),
                                       ("a.txt", None), ("a.exe", None), ("noext", None)])
def test_media_kind(name, kind):
    assert core.media_kind(name) == kind


def test_photo_and_video_extensions_do_not_overlap():
    assert not core.PHOTO_EXT & core.VIDEO_EXT


def test_type_order_puts_photos_first(tmp_path):
    make(tmp_path, "a.mp4", "b.jpg", "c.mov", "d.cr2")
    assert core.list_files(str(tmp_path), core.SORT_TYPE) == ["b.jpg", "d.cr2", "a.mp4", "c.mov"]


def test_rename_only_selected_files(tmp_path):
    make(tmp_path, "a.jpg", "b.mp4", "c.jpg", "d.mp4", "notes.txt")
    files = core.list_files(str(tmp_path))
    photos = [f for f in files if core.media_kind(f) == core.PHOTO]
    core.rename_all(str(tmp_path), core.build_plan(photos, "Trip photo", False))
    videos = [f for f in core.list_files(str(tmp_path)) if core.media_kind(f) == core.VIDEO]
    core.rename_all(str(tmp_path), core.build_plan(videos, "Trip video", False))
    assert sorted(os.listdir(tmp_path)) == ["Trip photo_1.jpg", "Trip photo_2.jpg",
                                            "Trip video_1.mp4", "Trip video_2.mp4", "notes.txt"]
