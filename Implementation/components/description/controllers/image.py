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
import shutil
import ntpath  # For cross-platform path handling
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
        saves it inside the project's `descriptionimage/` folder (local or cloud),
        and inserts it into the QTextEdit using a relative path.
        """
        try:
            import uuid
            import ntpath
            from utils.server_connection import get_sftp

            # Step 0: Ensure project path is set
            project_path = P.project_path
            if not project_path:
                QMessageBox.warning(self.text_edit, "Error", "Project path is not set.")
                return False
            print(f"[DEBUG] Project path: {project_path}")

            # Step 1: Define image folder path
            image_folder = os.path.join(project_path, "descriptionimage")
            print(f"[DEBUG] Target image folder: {image_folder}")

            # Step 2: Prompt image file selection
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

            # Step 4: Create unique file name
            ext = os.path.splitext(fname)[1].lower()
            unique_name = f"img_{uuid.uuid4().hex[:8]}{ext}"
            final_image_path = os.path.join(image_folder, unique_name)

            # Step 5: Store image locally or via SFTP
            if P.project_storage_mode == "cloud":
                # Ensure SFTP path exists and upload
                file_name = ntpath.basename(final_image_path)
                transport, sftp = get_sftp()
                try:
                    try:
                        sftp.chdir(image_folder)
                    except IOError:
                        sftp.mkdir(image_folder)
                        sftp.chdir(image_folder)
                    sftp.put(temp_resized_path, os.path.join(image_folder, file_name).replace("\\", "/"))
                    print(f"[DEBUG] ✅ Uploaded image to cloud path: {image_folder}/{file_name}")
                finally:
                    sftp.close()
                    transport.close()
            else:
                os.makedirs(image_folder, exist_ok=True)
                os.replace(temp_resized_path, final_image_path)
                print(f"[DEBUG] ✅ Moved image to local path: {final_image_path}")

            # Step 6: Compute relative path
            relative_image_path = os.path.relpath(final_image_path, start=project_path)
            relative_image_path = relative_image_path.replace("\\", "/")
            print(f"[DEBUG] Relative image path to insert: {relative_image_path}")

            # Step 7: Insert into QTextEdit
            cursor = self.text_edit.textCursor()
            cursor.beginEditBlock()
            cursor.movePosition(QTextCursor.End)

            blk_fmt = QTextBlockFormat()
            blk_fmt.setAlignment(Qt.AlignLeft)
            cursor.insertBlock(blk_fmt)

            img_fmt = QTextImageFormat()
            if P.project_storage_mode == "cloud":
                preview_local_path = temp_resized_path.replace("\\", "/")
                img_fmt.setName(preview_local_path)
            else:
                img_fmt.setName(relative_image_path)
            img_fmt.setWidth(width)
            img_fmt.setHeight(height)
            cursor.insertImage(img_fmt)

            cursor.insertBlock()
            cursor.mergeCharFormat(self.text_edit.currentCharFormat())
            cursor.endEditBlock()

            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()

            if hasattr(self.text_edit.parent(), "update_toolbar_state"):
                self.text_edit.parent().update_toolbar_state()

            logger.info("Inserted image '%s' (%dx%d)", relative_image_path, width, height)
            print("[DEBUG] Image inserted successfully!")
            return True

        except Exception as e:
            logger.exception("Image insert failed")
            QMessageBox.critical(self.text_edit, "Error", f"Image insert failed:\n{e}")
            return False
