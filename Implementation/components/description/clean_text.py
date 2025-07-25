# File: components/description/clean_text.py

"""
Module: CleanTextEdit Module
File: clean_text.py
Layer: UI / Text Editing Layer
Component ID: 
Requirement IDs: 
Author: Vijaya Ragavan
Created On: 2025-06-26
Version: 

Purpose:
--------
Normalize paste behavior in a QTextEdit, preserving rich content
and ensuring subsequent formatting commands apply correctly.

Responsibilities:
-----------------
• Intercept QMimeData pastes (images, HTML, plain text).  
• Save clipboard images to disk and insert them as real resources.  
• Insert HTML fragments via QTextDocumentFragment for full fidelity.  
• Fall back to plain-text paste and reset formatting for new typing.  

Public API:
-----------
class CleanTextEdit(QTextEdit):
    insertFromMimeData(source: QMimeData) -> None
    _resetCurrentFormat()            -> None
"""

import os
import uuid
import logging

from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui     import (
    QTextDocumentFragment,
    QTextCharFormat,
    QTextImageFormat,
    QTextDocument,
    QFont,
    QBrush,
    QColor,
)
from PyQt5.QtCore    import QUrl
from bs4 import BeautifulSoup

import models.Parameters as P

logger = logging.getLogger(__name__)

class CleanTextEdit(QTextEdit):
    """
    A QTextEdit subclass that overrides paste:
      1) Saves images to disk and re-inserts via QTextImageFormat.
      2) Inserts images in their own centered blocks.
      3) Inserts HTML fragments via fromHtml(), preserving all inline styles.
      4) Falls back to plain-text paste and re-applies default formatting.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize default formatting state.
        """
        super().__init__(*args, **kwargs)
        # default typing format
        self.current_font_family     = "Arial"
        self.current_font_size       = 8
        self.current_bold            = False
        self.current_italic          = False
        self.current_font_color      = QColor("black")
        self.current_highlight_color = QColor("white")

    def insertFromMimeData(self, source) -> None:
        """
        Override paste behavior:
          - If source.hasImage(): save & insert image in its own blocks.
          - Elif source.hasHtml(): insert rich HTML fragment via fromHtml().
          - Else: paste plain text then reset to default format.

        Args:
            source (QMimeData): the clipboard or drag-and-drop data.
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()

        # 1) Handle images
        if source.hasImage():
            img = source.imageData()
            if img and P.project_path:
                try:
                    folder = os.path.join(P.project_path, "descriptionimage")
                    os.makedirs(folder, exist_ok=True)
                    fname = os.path.join(folder, f"{uuid.uuid4().hex}.png")
                    img.save(fname, "PNG")
                    img_fmt = QTextImageFormat()
                    img_fmt.setName(fname)
                    img_fmt.setWidth(img.width())
                    img_fmt.setHeight(img.height())
                    # own paragraph
                    cursor.insertBlock()
                    cursor.insertImage(img_fmt)
                    cursor.insertBlock()
                except Exception:
                    logger.exception("Failed to save pasted image")
            else:
                logger.warning("Paste image skipped: no project path or empty image")
            cursor.endEditBlock()
            return

        # 2) Handle rich HTML
        if source.hasHtml():
            raw = source.html()
            # wrap body fragment only
            soup = BeautifulSoup(raw, "html.parser")
            fragment_html = soup.body.decode_contents() if soup.body else raw
            # use native fragment insertion
            frag = QTextDocumentFragment.fromHtml(fragment_html, self.document())
            cursor.insertFragment(frag)
            cursor.endEditBlock()
            return

        # 3) Plain text fallback
        super().insertFromMimeData(source)
        cursor.endEditBlock()
        self._resetCurrentFormat()

    def _resetCurrentFormat(self) -> None:
        """
        Re-apply the editor’s default QTextCharFormat for subsequent typing.
        """
        fmt = QTextCharFormat()
        fmt.setFontFamily(self.current_font_family)
        fmt.setFontPointSize(self.current_font_size)
        fmt.setFontWeight(QFont.Bold if self.current_bold else QFont.Normal)
        fmt.setFontItalic(self.current_italic)
        fmt.setForeground(QBrush(self.current_font_color))
        fmt.setBackground(QBrush(self.current_highlight_color))
        cursor = self.textCursor()
        cursor.setCharFormat(fmt)
        self.setTextCursor(cursor)
        self.setCurrentCharFormat(fmt)
