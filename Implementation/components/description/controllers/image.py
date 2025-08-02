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
from shutil import copyfile
import uuid
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
        saves it inside the project's `descriptionimage/` folder,
        and inserts it into the QTextEdit using a relative path.
        """
        try:
            # Step 0: Ensure project path is set
            project_path = P.project_path
            if not project_path:
                QMessageBox.warning(
                    self.text_edit,
                    "Error",
                    "Project path is not set."
                )
                return False
            print(f"[DEBUG] Project path: {project_path}")

            # Step 1: Create `descriptionimage/` folder if not exists
            image_folder = os.path.join(project_path, "descriptionimage")
            os.makedirs(image_folder, exist_ok=True)
            print(f"[DEBUG] Ensured image folder exists: {image_folder}")

            # Step 2: Prompt file picker
            fname, _ = QFileDialog.getOpenFileName(
                self.text_edit,
                "Select Image File",
                str(project_path),
                "Images (*.png *.jpg *.jpeg *.bmp)"
            )
            if not fname:
                print("[DEBUG] Image selection canceled.")
                return False
            print(f"[DEBUG] Selected image: {fname}")

            # Step 3: Resize dialog
            dlg = ResizableImageDialog(fname, parent=self.text_edit)
            if hasattr(dlg, "setWindowState") and hasattr(dlg, "windowState"):
                dlg.setWindowState(dlg.windowState() | Qt.WindowMaximized)
            if dlg.exec_() != QDialog.Accepted:
                print("[DEBUG] Resize dialog canceled.")
                return False

            temp_resized_path, width, height = dlg.get_resized_image()
            print(f"[DEBUG] Resized image saved at: {temp_resized_path} with size {width}x{height}")

            # Step 4: Generate unique filename and move resized image to project folder
            import uuid
            ext = os.path.splitext(fname)[1].lower()
            unique_name = f"img_{uuid.uuid4().hex[:8]}{ext}"
            final_image_path = os.path.join(image_folder, unique_name)
            os.replace(temp_resized_path, final_image_path)
            print(f"[DEBUG] Final image moved to: {final_image_path}")

            # Step 5: Calculate relative path for QTextEdit
            relative_image_path = os.path.relpath(final_image_path, start=project_path)
            relative_image_path = relative_image_path.replace("\\", "/")  # always forward slashes
            print(f"[DEBUG] Relative image path to insert: {relative_image_path}")

            # Step 6: Insert image in QTextEdit
            cursor = self.text_edit.textCursor()
            cursor.beginEditBlock()
            cursor.movePosition(QTextCursor.End)

            blk_fmt = QTextBlockFormat()
            blk_fmt.setAlignment(Qt.AlignLeft)
            cursor.insertBlock(blk_fmt)

            img_fmt = QTextImageFormat()
            img_fmt.setName(relative_image_path)
            img_fmt.setWidth(width)
            img_fmt.setHeight(height)
            cursor.insertImage(img_fmt)

            # Add new empty block
            cursor.insertBlock()
            cursor.mergeCharFormat(self.text_edit.currentCharFormat())
            cursor.endEditBlock()

            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()

            # Step 7: Notify editor (optional update toolbar)
            parent = self.text_edit.parent()
            if hasattr(parent, "update_toolbar_state"):
                parent.update_toolbar_state()

            logger.info("Inserted image '%s' (%dx%d)", relative_image_path, width, height)
            print(f"[DEBUG] Image inserted successfully!")

            return True

        except Exception as e:
            logger.exception("Image insert failed")
            QMessageBox.critical(
                self.text_edit,
                "Error",
                f"Image insert failed:\n{e}"
            )
            return False

