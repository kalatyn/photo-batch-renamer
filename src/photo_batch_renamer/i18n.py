"""Interface texts, kept in one place."""
from __future__ import annotations

STRINGS = {
    "title": "Photo Batch Renamer",
    "folder_label": "1. Photo folder:",
    "folder_hint": "Click “Browse...” or drop a folder onto the window",
    "browse": "Browse...",
    "name_label": "2. New name (for example: Your Name):",
    "order": "Order:",
    "sort_name": "by file name (DSC0001, DSC0002...)",
    "sort_date": "by date taken",
    "pad": "Leading zeros (001, 002...)",
    "preview": "Preview:",
    "col_old": "Before",
    "col_new": "After",
    "count": "Files in folder: {n}",
    "rename": "Rename",
    "undo": "Undo",
    "choose_folder": "Choose the photo folder",
    "confirm_title": "Confirm",
    "confirm_text": "Rename {n} files to “{first}”, “{second}” ...?",
    "undo_text": "Restore the previous names of {n} files?",
    "yes": "Yes",
    "no": "No",
    "done_title": "Done",
    "done_text": "Done! Files renamed: {n}",
    "undo_done": "Previous names restored: {n}",
    "error_title": "Error",
    "err_empty": "Please enter a name.",
    "err_chars": 'The name contains characters that are not allowed:  \\ / : * ? " < > |',
    "err_exists": "The folder already has a file “{name}” that is not in the list. Please choose another name.",
    "err_os": "Could not rename the files. All names were restored.\n\n{message}",
}


def tr(key: str, **kwargs) -> str:
    text = STRINGS[key]
    return text.format(**kwargs) if kwargs else text
