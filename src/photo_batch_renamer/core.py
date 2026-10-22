"""Rename logic without any GUI, so it can be tested on its own."""
from __future__ import annotations

import os
import re
import uuid
from datetime import datetime

EXIF_EXT = {".jpg", ".jpeg", ".tif", ".tiff"}
# Characters forbidden on Windows; we forbid them everywhere so names stay portable.
INVALID_CHARS = set('<>:"/\\|?*') | {chr(c) for c in range(32)}

# Only these files are shown and renamed; everything else in the folder is left alone.
PHOTO_EXT = {
    # common formats
    ".jpg", ".jpeg", ".jpe", ".jfif", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp",
    ".heic", ".heif", ".hif", ".avif", ".jxl",
    # camera RAW formats
    ".dng", ".cr2", ".cr3", ".crw",              # Canon
    ".nef", ".nrw",                              # Nikon
    ".arw", ".srf", ".sr2",                      # Sony
    ".raf",                                      # Fujifilm
    ".orf", ".ori",                              # Olympus / OM System
    ".rw2", ".raw", ".rwl",                      # Panasonic, Leica
    ".pef", ".ptx",                              # Pentax
    ".srw",                                      # Samsung
    ".x3f",                                      # Sigma
    ".3fr", ".fff",                              # Hasselblad
    ".iiq",                                      # Phase One
    ".mos", ".mef", ".mrw", ".erf", ".kdc", ".dcr", ".gpr",
}
VIDEO_EXT = {
    ".mp4", ".m4v", ".mov", ".qt", ".avi", ".mkv", ".wmv", ".asf", ".webm", ".flv", ".ogv",
    ".mts", ".m2ts", ".ts", ".mpg", ".mpeg", ".m2v", ".vob", ".mod", ".tod", ".dv",
    ".3gp", ".3g2",
    ".insv", ".360", ".lrv",                     # Insta360, GoPro
    ".braw", ".r3d", ".mxf", ".crm",             # cinema cameras
}
PHOTO = "photo"
VIDEO = "video"

SORT_NAME = 0
SORT_DATE = 1
SORT_TYPE = 2


class RenameError(Exception):
    """Raised with a translation key and its format arguments."""

    def __init__(self, key: str, **kwargs):
        super().__init__(key)
        self.key = key
        self.kwargs = kwargs


def natural_key(name: str):
    """IMG_9 before IMG_10."""
    return [int(t) if t.isdigit() else t.casefold() for t in re.split(r"(\d+)", name)]


def shot_time(path: str) -> float:
    """EXIF capture date for JPEG/TIFF, otherwise the file's modification time."""
    if os.path.splitext(path)[1].lower() in EXIF_EXT:
        try:
            from PIL import Image

            with Image.open(path) as im:
                exif = im.getexif()
                value = exif.get_ifd(0x8769).get(36867) or exif.get(306)
            if value:
                return datetime.strptime(str(value).strip("\x00 "), "%Y:%m:%d %H:%M:%S").timestamp()
        except Exception:
            pass
    return os.stat(path).st_mtime


def media_kind(name: str) -> str | None:
    """PHOTO, VIDEO, or None for any other file."""
    ext = os.path.splitext(name)[1].lower()
    if ext in PHOTO_EXT:
        return PHOTO
    if ext in VIDEO_EXT:
        return VIDEO
    return None


def list_files(folder: str, sort_mode: int = SORT_NAME) -> list[str]:
    """Photo and video files in the folder (no subfolders, hidden or other files)."""
    if not folder or not os.path.isdir(folder):
        return []
    names = [
        e.name
        for e in os.scandir(folder)
        if e.is_file() and not e.name.startswith(".") and media_kind(e.name)
    ]
    if sort_mode == SORT_DATE:
        names.sort(key=lambda n: (shot_time(os.path.join(folder, n)), natural_key(n)))
    elif sort_mode == SORT_TYPE:
        names.sort(key=lambda n: (media_kind(n) != PHOTO, natural_key(n)))
    else:
        names.sort(key=natural_key)
    return names


def validate_base(base: str) -> str | None:
    """Return a translation key describing the problem, or None if the name is fine."""
    if not base.strip():
        return "err_empty"
    if any(c in INVALID_CHARS for c in base) or base.rstrip().endswith("."):
        return "err_chars"
    return None


def new_name(base: str, index: int, total: int, pad: bool, old_name: str) -> str:
    num = str(index).zfill(max(3, len(str(total)))) if pad else str(index)
    ext = os.path.splitext(old_name)[1].lower()
    return f"{base.strip()}_{num}{ext}"


def build_plan(files: list[str], base: str, pad: bool) -> list[tuple[str, str]]:
    return [(old, new_name(base, i, len(files), pad, old)) for i, old in enumerate(files, 1)]


def rename_all(folder: str, plan: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Apply (old, new) pairs and return the reverse plan for undo.

    Two steps through temporary names, so a new name may equal another file's old
    name. If anything fails, files already moved are put back.
    """
    olds = {old.casefold() for old, _ in plan}
    existing = {n.casefold() for n in os.listdir(folder)}
    for _, new in plan:
        if new.casefold() in existing - olds:
            raise RenameError("err_exists", name=new)

    path = lambda n: os.path.join(folder, n)  # noqa: E731
    temps: list[tuple[str, str]] = []  # (temp, old)
    finals: list[tuple[str, str]] = []  # (new, temp)
    try:
        for old, _ in plan:
            temp = f"~ren_{uuid.uuid4().hex}{os.path.splitext(old)[1]}"
            os.rename(path(old), path(temp))
            temps.append((temp, old))
        for (temp, _), (_, new) in zip(temps, plan):
            os.rename(path(temp), path(new))
            finals.append((new, temp))
    except OSError as e:
        for new, temp in reversed(finals):
            try:
                os.rename(path(new), path(temp))
            except OSError:
                pass
        for temp, old in reversed(temps):
            try:
                os.rename(path(temp), path(old))
            except OSError:
                pass
        raise RenameError("err_os", message=str(e)) from e
    return [(new, old) for old, new in plan]
