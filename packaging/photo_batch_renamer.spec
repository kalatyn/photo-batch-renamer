# PyInstaller spec. Run through packaging/build.py, which sets PBR_ICON and PBR_VERSION.
import os
import re
import sys

ROOT = os.path.dirname(SPECPATH)
APP_NAME = "Photo Batch Renamer"
ICON = os.path.join(ROOT, "assets", os.environ.get("PBR_ICON", "icon.png"))
VERSION = os.environ.get("PBR_VERSION", "0.0.0")

# Left out of the bundle: Qt's own translations and network parts (unused), and the
# GTK theme plugin, which would copy the system's GTK libraries into the app.
DROP = re.compile(
    r"Qt[/\\]translations|Qt6Network|QtNetwork|plugins[/\\](tls|networkinformation)[/\\]"
    r"|platformthemes[/\\]libqgtk3"
    r"|(^|[/\\])lib(gtk-3|gdk-3|gdk_pixbuf|glycin|atk|atspi|epoxy|pango|cairo|rsvg)[^/\\]*$"
)

a = Analysis(
    [os.path.join(SPECPATH, "entry.py")],
    pathex=[os.path.join(ROOT, "src")],
    datas=[(os.path.join(ROOT, "src", "photo_batch_renamer", "icon.png"), "photo_batch_renamer")],
    excludes=["tkinter"],
)
a.binaries = [x for x in a.binaries if not DROP.search(x[0])]
a.datas = [x for x in a.datas if not DROP.search(x[0])]

pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=APP_NAME,
          console=False, icon=ICON, upx=False, strip=sys.platform == "linux")
coll = COLLECT(exe, a.binaries, a.datas, name=APP_NAME, upx=False, strip=sys.platform == "linux")

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=ICON,
        bundle_identifier="io.github.kalatyn.photo-batch-renamer",
        version=VERSION,
        info_plist={
            "CFBundleDisplayName": APP_NAME,
            "CFBundleShortVersionString": VERSION,
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,
            "LSApplicationCategoryType": "public.app-category.photography",
        },
    )
