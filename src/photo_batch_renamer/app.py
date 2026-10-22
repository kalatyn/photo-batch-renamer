"""Main window. Same layout on Windows, macOS and Linux (Qt "Fusion" style)."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QThread, QTimer, QUrl, Qt, Signal
from PySide6.QtGui import QBrush, QDesktopServices, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from . import __version__, core, updater
from .i18n import tr

ICON = Path(__file__).with_name("icon.png")

# Accent color of the main button, taken from the app icon.
STYLE = """
QPushButton#primary { background: #4f46e5; color: white; border: 1px solid #4338ca;
                      border-radius: 5px; padding: 0 18px; font-weight: bold; }
QPushButton#primary:hover { background: #4338ca; }
QPushButton#primary:disabled { background: #a5b4fc; border-color: #a5b4fc; color: #eef2ff; }
QPushButton#select { padding: 2px 12px; }
"""


class Worker(QThread):
    """Runs fn(progress) in the background so the window stays responsive."""

    done = Signal(object)
    failed = Signal(str)
    progress = Signal(int, int)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        try:
            self.done.emit(self.fn(self.progress.emit))
        except Exception as e:
            self.failed.emit(str(e))


class RenamerWindow(QWidget):
    def __init__(self, folder: str = ""):
        super().__init__()
        self.files: list[str] = []
        self.checked: set[str] = set()
        self.undo_plan: list[tuple[str, str]] = []
        self.undo_folder = ""
        self.release: updater.Release | None = None
        self.worker: Worker | None = None

        self.setWindowTitle(f"{tr('title')} {__version__}")
        self.resize(700, 620)
        self.setMinimumSize(600, 480)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # 1. Folder, and the update link on the right
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("folder_label")))
        row.addStretch(1)
        self.lnk_update = QLabel()
        self.lnk_update.linkActivated.connect(self.on_update_link)
        self.set_update_link(tr("check_updates"))
        row.addWidget(self.lnk_update)
        layout.addLayout(row)
        row = QHBoxLayout()
        self.txt_folder = QLineEdit(readOnly=True, placeholderText=tr("folder_hint"))
        self.txt_folder.setFocusPolicy(Qt.NoFocus)
        btn_browse = QPushButton(tr("browse"))
        btn_browse.setMinimumWidth(120)
        btn_browse.clicked.connect(self.on_browse)
        row.addWidget(self.txt_folder, 1)
        row.addWidget(btn_browse)
        layout.addLayout(row)

        # 2. Name
        layout.addSpacing(4)
        layout.addWidget(QLabel(tr("name_label")))
        self.txt_name = QLineEdit()
        self.txt_name.textChanged.connect(self.refresh_names)
        layout.addWidget(self.txt_name)

        # Order and zeros
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("order")))
        self.cmb_sort = QComboBox()
        self.cmb_sort.addItems([tr("sort_name"), tr("sort_date"), tr("sort_type")])
        self.cmb_sort.currentIndexChanged.connect(lambda: self.reload_files())
        row.addWidget(self.cmb_sort)
        row.addSpacing(12)
        self.chk_pad = QCheckBox(tr("pad"))
        self.chk_pad.toggled.connect(self.refresh_names)
        row.addWidget(self.chk_pad)
        row.addStretch(1)
        layout.addSpacing(4)
        layout.addLayout(row)

        # Preview with selection buttons
        layout.addSpacing(4)
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("preview")))
        row.addStretch(1)
        row.addWidget(QLabel(tr("select")))
        for key, kind in (("sel_all", "all"), ("sel_none", "none"),
                          ("sel_photos", core.PHOTO), ("sel_videos", core.VIDEO)):
            btn = QPushButton(tr(key))
            btn.setObjectName("select")
            btn.clicked.connect(lambda _=False, k=kind: self.select(k))
            row.addWidget(btn)
        layout.addLayout(row)

        self.list = QTreeWidget()
        self.list.setHeaderLabels([tr("col_old"), tr("col_new"), tr("col_type")])
        self.list.setRootIsDecorated(False)
        self.list.setAlternatingRowColors(True)
        self.list.setUniformRowHeights(True)
        header = self.list.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)
        self.list.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.list, 1)

        # Bottom
        row = QHBoxLayout()
        self.lbl_count = QLabel()
        row.addWidget(self.lbl_count)
        row.addStretch(1)
        self.btn_undo = QPushButton(tr("undo"))
        self.btn_undo.setMinimumHeight(38)
        self.btn_undo.setVisible(False)
        self.btn_undo.clicked.connect(self.on_undo)
        row.addWidget(self.btn_undo)
        self.btn_go = QPushButton(tr("rename"))
        self.btn_go.setObjectName("primary")
        self.btn_go.setMinimumSize(150, 38)
        self.btn_go.setDefault(True)
        self.btn_go.setEnabled(False)
        self.btn_go.clicked.connect(self.on_rename)
        row.addWidget(self.btn_go)
        layout.addLayout(row)

        if folder and os.path.isdir(folder):
            self.set_folder(os.path.abspath(folder))

        # Installed copies look for updates quietly at startup; nothing is shown unless one exists.
        if getattr(sys, "frozen", False):
            QTimer.singleShot(2000, lambda: self.check_updates(quiet=True))

    # --- helpers ---
    def ask(self, title: str, text: str) -> bool:
        box = QMessageBox(QMessageBox.Question, title, text, parent=self)
        yes = box.addButton(tr("yes"), QMessageBox.YesRole)
        box.addButton(tr("no"), QMessageBox.NoRole)
        box.setDefaultButton(yes)
        box.exec()
        return box.clickedButton() is yes

    def show_message(self, icon, title: str, text: str):
        box = QMessageBox(icon, title, text, parent=self)
        box.addButton("OK", QMessageBox.AcceptRole)
        box.exec()

    def set_folder(self, path: str):
        self.txt_folder.setText(path)
        if not self.txt_name.text():
            self.txt_name.setText(os.path.basename(path.rstrip("/\\")))
        self.reload_files(keep_checks=False)

    def selected_files(self) -> list[str]:
        return [f for f in self.files if f in self.checked]

    # --- preview ---
    def reload_files(self, keep_checks: bool = True):
        """Re-read the folder (only when the folder or the order changes: EXIF reading is slow).

        New files start checked; with keep_checks=False every file is checked again.
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            old = set(self.files)
            self.files = core.list_files(self.txt_folder.text(), self.cmb_sort.currentIndex())
        finally:
            QApplication.restoreOverrideCursor()
        if keep_checks:
            self.checked = {f for f in self.files if f in self.checked or f not in old}
        else:
            self.checked = set(self.files)
        self.rebuild_list()

    def rebuild_list(self):
        kinds = {core.PHOTO: tr("kind_photo"), core.VIDEO: tr("kind_video")}
        self.list.blockSignals(True)
        self.list.clear()
        items = []
        for name in self.files:
            item = QTreeWidgetItem([name, "", kinds[core.media_kind(name)]])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Checked if name in self.checked else Qt.Unchecked)
            items.append(item)
        self.list.addTopLevelItems(items)
        self.list.blockSignals(False)
        self.refresh_names()

    def refresh_names(self):
        """Update the "After" column in place, so the list keeps its scroll position."""
        base = self.txt_name.text().strip()
        pad = self.chk_pad.isChecked()
        selected = self.selected_files()
        position = {name: i for i, name in enumerate(selected, 1)}
        normal = QBrush(self.palette().color(QPalette.Active, QPalette.Text))
        dimmed = QBrush(self.palette().color(QPalette.Disabled, QPalette.Text))

        self.list.blockSignals(True)
        for i in range(self.list.topLevelItemCount()):
            item = self.list.topLevelItem(i)
            name = item.text(0)
            on = name in position
            item.setText(1, core.new_name(base, position[name], len(selected), pad, name) if on and base else "")
            for col in range(3):
                item.setForeground(col, normal if on else dimmed)
        self.list.blockSignals(False)

        if self.txt_folder.text():
            photos = sum(core.media_kind(f) == core.PHOTO for f in self.files)
            self.lbl_count.setText(tr("count", sel=len(selected), n=len(self.files),
                                      photos=photos, videos=len(self.files) - photos))
        else:
            self.lbl_count.setText("")
        self.btn_go.setEnabled(bool(selected) and bool(base))

    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        if column != 0:
            return
        if item.checkState(0) == Qt.Checked:
            self.checked.add(item.text(0))
        else:
            self.checked.discard(item.text(0))
        self.refresh_names()

    def select(self, kind: str):
        """Check all, none, only photos or only videos."""
        if kind == "all":
            self.checked = set(self.files)
        elif kind == "none":
            self.checked = set()
        else:
            self.checked = {f for f in self.files if core.media_kind(f) == kind}
        self.list.blockSignals(True)
        for i in range(self.list.topLevelItemCount()):
            item = self.list.topLevelItem(i)
            item.setCheckState(0, Qt.Checked if item.text(0) in self.checked else Qt.Unchecked)
        self.list.blockSignals(False)
        self.refresh_names()

    # --- actions ---
    def on_browse(self):
        path = QFileDialog.getExistingDirectory(self, tr("choose_folder"), self.txt_folder.text())
        if path:
            self.set_folder(os.path.normpath(path))

    def on_rename(self):
        base = self.txt_name.text().strip()
        problem = core.validate_base(base)
        if problem:
            self.show_message(QMessageBox.Warning, tr("error_title"), tr(problem))
            return
        folder = self.txt_folder.text()
        self.files = core.list_files(folder, self.cmb_sort.currentIndex())
        plan = core.build_plan(self.selected_files(), base, self.chk_pad.isChecked())
        if not plan:
            self.reload_files()
            return
        second = plan[1][1] if len(plan) > 1 else ""
        if not self.ask(tr("confirm_title"), tr("confirm_text", n=len(plan), first=plan[0][1], second=second)):
            return
        try:
            self.undo_plan = core.rename_all(folder, plan)
            self.undo_folder = folder
        except core.RenameError as e:
            self.show_message(QMessageBox.Critical, tr("error_title"), tr(e.key, **e.kwargs))
            self.reload_files()
            return
        self.btn_undo.setVisible(True)
        self.reload_files(keep_checks=False)
        self.show_message(QMessageBox.Information, tr("done_title"), tr("done_text", n=len(plan)))

    def on_undo(self):
        if not self.undo_plan or not self.ask(tr("confirm_title"), tr("undo_text", n=len(self.undo_plan))):
            return
        try:
            core.rename_all(self.undo_folder, self.undo_plan)
        except core.RenameError as e:
            self.show_message(QMessageBox.Critical, tr("error_title"), tr(e.key, **e.kwargs))
            return
        n = len(self.undo_plan)
        self.undo_plan = []
        self.btn_undo.setVisible(False)
        self.reload_files(keep_checks=False)
        self.show_message(QMessageBox.Information, tr("done_title"), tr("undo_done", n=n))

    # --- updates ---
    def set_update_link(self, text: str, bold: bool = False):
        style = "font-weight: bold;" if bold else ""
        self.lnk_update.setText(f'<a href="update" style="{style}">{text}</a>')

    def run_worker(self, fn, on_done, on_failed, on_progress=None):
        self.worker = Worker(fn)
        self.worker.done.connect(on_done)
        self.worker.failed.connect(on_failed)
        if on_progress:
            self.worker.progress.connect(on_progress)
        self.worker.start()

    def on_update_link(self, _link=""):
        if self.worker and self.worker.isRunning():
            return
        if self.release:
            self.offer_update()
        else:
            self.check_updates(quiet=False)

    def check_updates(self, quiet: bool):
        if self.worker and self.worker.isRunning():
            return
        self.lnk_update.setText(tr("checking"))
        self.run_worker(lambda _progress: updater.fetch_latest(),
                        lambda release: self.on_checked(release, quiet),
                        lambda message: self.on_check_failed(message, quiet))

    def on_checked(self, release: updater.Release, quiet: bool):
        if updater.is_newer(release.version, __version__):
            self.release = release
            self.set_update_link(tr("update_available", version=release.version), bold=True)
            if not quiet:
                self.offer_update()
        else:
            self.release = None
            self.set_update_link(tr("check_updates"))
            if not quiet:
                self.show_message(QMessageBox.Information, tr("up_to_date_title"),
                                  tr("up_to_date", version=__version__))

    def on_check_failed(self, message: str, quiet: bool):
        self.set_update_link(tr("check_updates"))
        if not quiet:
            self.show_message(QMessageBox.Warning, tr("error_title"), tr("check_failed", message=message))

    def offer_update(self):
        release, kind = self.release, updater.install_kind()
        if kind == "source":
            self.show_message(QMessageBox.Information, tr("update_title"),
                              tr("update_source", version=release.version))
            return
        asset = updater.pick_asset(release, kind)
        if not asset:
            if self.ask(tr("update_title"), tr("update_manual", version=release.version)):
                QDesktopServices.openUrl(QUrl(release.page))
            return
        notes = release.notes.strip()
        if len(notes) > 800:
            notes = notes[:800].rstrip() + "…"
        box = QMessageBox(QMessageBox.Question, tr("update_title"),
                          tr("update_text", version=release.version, current=__version__, notes=notes),
                          parent=self)
        install = box.addButton(tr("install"), QMessageBox.AcceptRole)
        box.addButton(tr("later"), QMessageBox.RejectRole)
        box.setDefaultButton(install)
        box.exec()
        if box.clickedButton() is install:
            self.install_update(release, kind, asset)

    def install_update(self, release: updater.Release, kind: str, asset: str):
        folder = Path(tempfile.mkdtemp(prefix="pbr-download-"))
        dialog = QProgressDialog(tr("downloading"), None, 0, 100, self)
        dialog.setWindowTitle(tr("update_title"))
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setMinimumDuration(0)
        dialog.setAutoClose(False)
        dialog.setValue(0)
        dialog.show()

        def progress(done: int, total: int):
            if total:
                dialog.setValue(min(100, done * 100 // total))
                if done >= total:
                    dialog.setLabelText(tr("installing"))

        def finished(must_quit):
            dialog.close()
            if must_quit:
                QApplication.quit()

        def failed(message: str):
            dialog.close()
            self.show_message(QMessageBox.Critical, tr("error_title"), tr("update_failed", message=message))

        self.run_worker(
            lambda report: updater.apply(kind, updater.download_verified(release, asset, folder, report)),
            finished, failed, progress)

    # --- drag and drop a folder ---
    def dragEnterEvent(self, event):
        urls = event.mimeData().urls()
        if urls and os.path.isdir(urls[0].toLocalFile()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.set_folder(os.path.normpath(event.mimeData().urls()[0].toLocalFile()))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    app.setApplicationName("Photo Batch Renamer")
    if ICON.exists():
        app.setWindowIcon(QIcon(str(ICON)))
    folder = sys.argv[1] if len(sys.argv) > 1 else ""
    win = RenamerWindow(folder)
    win.show()
    sys.exit(app.exec())
