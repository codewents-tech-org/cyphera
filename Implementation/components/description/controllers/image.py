# pylint: disable=E0611,E0401,W0718
"""
Module: Image Controller
File: image.py
Layer: UI / Controller Layer
Component ID: 
Requirement IDs: 
Author: Vijaya Ragavan
Created On: 2025-06-27
Version: 

Purpose:
--------
Provides `ImageController`, which handles inserting and resizing images
in the QTextEdit via toolbar actions or double-click.

Responsibilities:
-----------------
• Listen for insert‐picture signals from the toolbar.  
• Prompt for file selection, allow interactive resizing, and insert image.  
• Maintain document structure: image in its own left‐aligned block, then text.  
• Restore cursor position and focus, and refresh toolbar state on the parent editor.  

Public API:
-----------
class ImageController:
  __init__(text_edit: QTextEdit, toolbar) -> None  
    • Connects toolbar insertPictureClicked to `insert_picture`.  

  insert_picture() -> bool  
    • Prompts for image selection & resize, inserts into document.  
    • Returns True on success; False on cancel or error.
"""

import os
import logging

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QTextEdit
from PyQt5.QtGui     import QTextImageFormat, QTextCursor, QTextBlockFormat
from PyQt5.QtCore    import Qt

import models.Parameters as P
from ..image_editor_dialog import ResizableImageDialog

logger = logging.getLogger(__name__)

class ImageController:
    """
    Handles “Insert Image” from the toolbar and
    double-click resizing of already-inserted images.
    """

    def __init__(self, text_edit: QTextEdit, toolbar) -> None:
        """
        Args:
            text_edit: The QTextEdit into which images will be inserted.
            toolbar:   The toolbar emitting insertPictureClicked signals.

        Returns:
            None
        """
        self.text_edit = text_edit
        self.toolbar   = toolbar

        # Support both Qt signals and stub callables
        sig = getattr(toolbar, "insertPictureClicked", None)
        if hasattr(sig, "connect"):
            sig.connect(self.insert_picture)
        elif callable(sig):
            sig(self.insert_picture)

    def insert_picture(self) -> bool:
        """
        Prompts the user to select and optionally resize an image file,
        then inserts it as its own left‐aligned paragraph block.

        Returns:
            True if an image was successfully inserted; False otherwise.
        """
        try:
            # Ensure project path is configured
            project_path = P.project_path
            if not project_path:
                QMessageBox.warning(
                    self.text_edit,
                    "Error",
                    "Project path is not set."
                )
                return False

            # Prepare image storage folder
            image_folder = os.path.join(project_path, "descriptionimage")
            os.makedirs(image_folder, exist_ok=True)

            # 1) Prompt for file
            fname, _ = QFileDialog.getOpenFileName(
                self.text_edit,
                "Open Image File",
                str(project_path),                # <-- ensure this is a str, not a Path
                "Images (*.png *.jpg *.bmp)"
            )
            if not fname:
                return False

            # 2) Show resize dialog
            dlg = ResizableImageDialog(fname, parent=self.text_edit)
            # guard against stubs without setWindowState()
            if hasattr(dlg, "setWindowState") and hasattr(dlg, "windowState"):
                dlg.setWindowState(dlg.windowState() | Qt.WindowMaximized)
            if dlg.exec_() != QDialog.Accepted:
                return False

            image_path, w, h = dlg.get_resized_image()

            # 3) Insert image block
            cursor = self.text_edit.textCursor()
            cursor.beginEditBlock()

            # Move to end and insert a left-aligned paragraph
            cursor.movePosition(QTextCursor.End)
            blk_fmt = QTextBlockFormat()
            blk_fmt.setAlignment(Qt.AlignLeft)
            cursor.insertBlock(blk_fmt)

            # Insert image with explicit size
            img_fmt = QTextImageFormat()
            img_fmt.setName(image_path)
            img_fmt.setWidth(w)
            img_fmt.setHeight(h)
            cursor.insertImage(img_fmt)

            # Insert a new paragraph after the image
            cursor.insertBlock()
            cursor.mergeCharFormat(self.text_edit.currentCharFormat())
            cursor.endEditBlock()

            # 4) Restore cursor & focus
            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()

            # 5) Update toolbar state on parent editor
            parent = self.text_edit.parent()
            if hasattr(parent, "update_toolbar_state"):
                parent.update_toolbar_state()

            logger.info("Inserted image '%s' (%dx%d)", image_path, w, h)
            return True

        except Exception as e:
            logger.exception("Image insert failed")
            QMessageBox.critical(
                self.text_edit,
                "Error",
                f"Image insert failed:\n{e}"
            )
            return False
