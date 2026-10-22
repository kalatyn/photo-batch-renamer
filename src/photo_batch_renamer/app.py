"""Main window. Same layout on Windows, macOS and Linux (Qt "Fusion" style)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
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
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from . import __version__, core
from .i18n import tr

ICON = Path(__file__).with_name("icon.png")

# Accent color of the main button, taken from the app icon.
STYLE = """
QPushButton#primary { background: #4f46e5; color: white; border: 1px solid #4338ca;
                      border-radius: 5px; padding: 0 18px; font-weight: bold; }
QPushButton#primary:hover { background: #4338ca; }
QPushButton#primary:disabled { background: #a5b4fc; border-color: #a5b4fc; color: #eef2ff; }
"""


class RenamerWindow(QWidget):
    def __init__(self, folder: str = ""):
        super().__init__()
        self.files: list[str] = []
        self.undo_plan: list[tuple[str, str]] = []
        self.undo_folder = ""

        self.setWindowTitle(f"{tr('title')} {__version__}")
        self.resize(660, 580)
        self.setMinimumSize(560, 460)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # 1. Folder
        layout.addWidget(QLabel(tr("folder_label")))
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
        self.txt_name.textChanged.connect(self.update_preview)
        layout.addWidget(self.txt_name)

        # Order and zeros
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("order")))
        self.cmb_sort = QComboBox()
        self.cmb_sort.addItems([tr("sort_name"), tr("sort_date")])
        self.cmb_sort.currentIndexChanged.connect(self.reload_files)
        row.addWidget(self.cmb_sort)
        row.addSpacing(12)
        self.chk_pad = QCheckBox(tr("pad"))
        self.chk_pad.toggled.connect(self.update_preview)
        row.addWidget(self.chk_pad)
        row.addStretch(1)
        layout.addSpacing(4)
        layout.addLayout(row)

        # Preview
        layout.addSpacing(4)
        layout.addWidget(QLabel(tr("preview")))
        self.list = QTreeWidget()
        self.list.setHeaderLabels([tr("col_old"), tr("col_new")])
        self.list.setRootIsDecorated(False)
        self.list.setAlternatingRowColors(True)
        self.list.setUniformRowHeights(True)
        self.list.header().setSectionResizeMode(QHeaderView.Stretch)
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
        self.reload_files()

    # --- preview ---
    def reload_files(self):
        """Re-read the folder (only when the folder or the order changes: EXIF reading is slow)."""
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.files = core.list_files(self.txt_folder.text(), self.cmb_sort.currentIndex())
        finally:
            QApplication.restoreOverrideCursor()
        self.update_preview()

    def update_preview(self):
        base = self.txt_name.text().strip()
        pad = self.chk_pad.isChecked()
        self.list.clear()
        items = []
        for i, name in enumerate(self.files, 1):
            new = core.new_name(base, i, len(self.files), pad, name) if base else ""
            items.append(QTreeWidgetItem([name, new]))
        self.list.addTopLevelItems(items)
        self.lbl_count.setText(tr("count", n=len(self.files)) if self.txt_folder.text() else "")
        self.btn_go.setEnabled(bool(self.files) and bool(base))

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
        plan = core.build_plan(self.files, base, self.chk_pad.isChecked())
        if not plan:
            self.update_preview()
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
        self.reload_files()
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
        self.reload_files()
        self.show_message(QMessageBox.Information, tr("done_title"), tr("undo_done", n=n))

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
