# pylint: disable=E0611,E0401,W0718
"""
Module: Formatting Controller
File: formatting.py
Layer: UI / Controller Layer
Component ID: 
Requirement IDs: 
Author: Vijaya Ragavan
Created On: 2025-06-27
Version: 

Purpose:
--------
Provides `FormattingController`, which handles toggling and applying text
formats in a QTextEdit via toolbar actions.

Responsibilities:
-----------------
• Listen for formatting signals (bold, italic, underline, size, style, color, highlight).
• Preserve existing text attributes and skip image fragments when applying formats.
• Apply formats to selected text and configure future typing format.
• Update toolbar state to reflect current formatting of the editor.

Public API:
-----------
class FormattingController:
  __init__(text_edit: QTextEdit, toolbar: QWidget) -> None  
    • Connects toolbar formatting signals to controller methods.

  toggle_bold() -> None  
    • Toggle bold weight on selection or caret.

  toggle_italic() -> None  
    • Toggle italic style on selection or caret.

  toggle_underline() -> None  
    • Toggle underline on selection or caret.

  change_font_size(size: int) -> None  
    • Set font point size for selection or future typing.

  change_font_style(style: str) -> None  
    • Apply Normal (10pt) or Heading (16pt bold) style.

  select_font_color() -> None  
    • Open color dialog and apply chosen font color.

  toggle_highlight() -> None  
    • Toggle yellow background highlight on selection or caret.

  update_toolbar_state() -> None  
    • Read current text format and emit states to the toolbar.
"""
import logging
from PyQt5.QtGui import QTextCharFormat, QFont, QColor, QTextCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QColorDialog, QTextEdit, QWidget

logger = logging.getLogger(__name__)

class FormattingController:
    """
    Controller to manage text formatting in a QTextEdit via toolbar inputs.
    """

    def __init__(self, text_edit: QTextEdit, toolbar: QWidget) -> None:
        """
        Args:
            text_edit: The QTextEdit instance to format.
            toolbar:   The toolbar emitting formatting signals.

        Returns:
            None
        """
        self.text_edit = text_edit
        self.toolbar   = toolbar

        toolbar.boldClicked.connect(self.toggle_bold)
        toolbar.italicClicked.connect(self.toggle_italic)
        if hasattr(toolbar, "underlineClicked"):
            toolbar.underlineClicked.connect(self.toggle_underline)

        toolbar.fontSizeChanged.connect(self.change_font_size)
        toolbar.fontStyleChanged.connect(self.change_font_style)
        toolbar.fontColorClicked.connect(self.select_font_color)
        toolbar.highlightClicked.connect(self.toggle_highlight)

    def _skip_image(self) -> QTextCursor:
        """
        If cursor is on an image with no selection, advance to next text character.

        Returns:
            Adjusted QTextCursor.
        """
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection() and cursor.charFormat().isImageFormat():
            cursor.movePosition(QTextCursor.NextCharacter)
            self.text_edit.setTextCursor(cursor)
        return cursor

    def toggle_bold(self) -> None:
        """
        Toggle bold weight on current selection or caret.

        Returns:
            None
        """
        cursor = self._skip_image()
        fmt = QTextCharFormat()
        is_bold = self.text_edit.fontWeight() == QFont.Bold
        fmt.setFontWeight(QFont.Normal if is_bold else QFont.Bold)
        self._apply_format(cursor, fmt)

    def toggle_italic(self) -> None:
        """
        Toggle italic style on current selection or caret.

        Returns:
            None
        """
        cursor = self._skip_image()
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.text_edit.fontItalic())
        self._apply_format(cursor, fmt)

        

    def change_font_size(self, size: int) -> None:
        """
        Set font point size for current selection and future typing, preserving existing styles.

        Args:
            size: The new point size.
        Returns:
            None
        """
        cursor = self._skip_image()
        # If text is selected, apply size change only to selection
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        self._apply_format(cursor, fmt)

        # Also update future typing to this size, preserving other attributes
        current_fmt = self.text_edit.currentCharFormat()
        current_fmt.setFontPointSize(size)
        self.text_edit.setCurrentCharFormat(current_fmt)
        self.update_toolbar_state()

    def change_font_style(self, style: str) -> None:
        """
        Apply Normal or Heading style.

        Args:
            style: "Normal" or "Heading".
        Returns:
            None
        """
        cursor = self._skip_image()
        fmt = QTextCharFormat()
        if style == "Normal":
            fmt.setFontWeight(QFont.Normal)
            fmt.setFontPointSize(10)
        elif style == "Heading":
            fmt.setFontWeight(QFont.Bold)
            fmt.setFontPointSize(16)
        self._apply_format(cursor, fmt)

    def select_font_color(self) -> None:
        """
        Open color dialog and apply chosen font color.

        Returns:
            None
        """
        cursor = self._skip_image()
        initial = self.text_edit.textColor()
        color = QColorDialog.getColor(initial, self.text_edit, "Select font color")
        if not color.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        self._apply_format(cursor, fmt)

    def toggle_highlight(self) -> None:
        """
        Toggle yellow background highlight on selection or caret.

        Returns:
            None
        """
        cursor = self._skip_image()
        current_fmt = cursor.charFormat()
        bg = current_fmt.background().color()
        new_bg = QColor("white") if bg == QColor("#ffff00") else QColor("#ffff00")
        fmt = QTextCharFormat()
        fmt.setBackground(new_bg)
        self._apply_format(cursor, fmt)

    def _apply_format(self, cursor: QTextCursor, fmt: QTextCharFormat) -> None:
        """
        Merge a QTextCharFormat into selection or configure it for new typing.

        Args:
            cursor: The active QTextCursor.
            fmt:    The QTextCharFormat to apply.
        Returns:
            None
        """
        if cursor.hasSelection():
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            tmp = QTextCursor(self.text_edit.document())
            tmp.setPosition(start)
            while tmp.position() < end:
                if not tmp.charFormat().isImageFormat():
                    tmp.mergeCharFormat(fmt)
                tmp.movePosition(QTextCursor.NextCharacter)
        else:
            self.text_edit.mergeCurrentCharFormat(fmt)
            self.update_toolbar_state()
            return

        self.text_edit.mergeCurrentCharFormat(fmt)
        self.update_toolbar_state()

    def update_toolbar_state(self) -> None:
        """
        Read current text format and emit states to the toolbar.

        Returns:
            None
        """
        try:
            cursor = self.text_edit.textCursor()
            fmt = cursor.charFormat() if cursor.hasSelection() else self.text_edit.currentCharFormat()

            bold      = fmt.fontWeight() == QFont.Bold
            italic    = fmt.fontItalic()
            underline = fmt.fontUnderline()
            highlight = fmt.background().color() == QColor("#ffff00")
            size      = fmt.fontPointSize()
            color     = fmt.foreground().color().name()
            align_map = {
                Qt.AlignLeft:   "Left",
                Qt.AlignCenter: "Center",
                Qt.AlignRight:  "Right",
                Qt.AlignJustify:"Justify"
            }
            alignment = align_map.get(cursor.blockFormat().alignment(), "Left")

            self.toolbar.apply_text_format_states(
                bold, italic, underline, highlight, size, color, alignment
            )
        except Exception as e:
            logger.error("Failed to update toolbar state: %s", e)
