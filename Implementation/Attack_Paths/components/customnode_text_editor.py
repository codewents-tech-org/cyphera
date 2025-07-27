"""
Module: Custom Text Editors      \n 
File: customnode_text_editor.py      \n
Layer: UI / Graphics Items    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-02     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Provides editable and display-only text components for use in tree node UIs,
allowing fixed height, custom line spacing, and event-driven signal control.

Description:
------------
This module defines two classes:
- `CustomTextEdit`: A QTextEdit that emits signal only on user-initiated changes
  when focus is lost, and supports line spacing configuration.
- `FixedHeightTextItem`: A QGraphicsTextItem that constrains its height and applies
  line spacing for static or display-only text.

Responsibilities
----------------
- Handle two-line text input with no scrollbars or rich formatting
- Move cursor to top when focus is lost
- Prevent signal spam by only emitting after edit completes
- Apply proportional line spacing to both input and output text

Dependencies:
-------------
- PyQt5.QtWidgets: QTextEdit, QGraphicsTextItem
- PyQt5.QtGui: QTextCursor, QTextBlockFormat
- PyQt5.QtCore: QRectF, pyqtSignal

Classes:
-------------
- CustomTextEdit(QTextEdit)
    - Signals:
        - textEdited(str): emitted when focus leaves and user modified text
- FixedHeightTextItem(QGraphicsTextItem)
    - A static, fixed-height text item with line spacing

Signals:
-------------
- CustomTextEdit.textEdited(str): fires once on focus out if text was changed

Limitations
-----------
- No undo/redo history maintained
- No spell check, rich text, or markdown rendering
- Fixed height only configurable at construction

Improvements
------------
- Add placeholder support or watermarks
- Add undo/redo and change history tracking
- Support maximum character length or validation rules

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-02           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from PyQt5.QtWidgets import QTextEdit, QGraphicsTextItem
from PyQt5.QtGui import QTextCursor, QTextBlockFormat
from PyQt5.QtCore import QRectF, pyqtSignal

class CustomTextEdit(QTextEdit):
    textEdited = pyqtSignal(str)

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setPlainText(text)
        self._last_text = text
        self._user_modified = False
        self.textChanged.connect(self._on_text_changed)

    """QTextEdit that resets cursor to start when focus is lost."""
    def focusOutEvent(self, event):
        super().focusOutEvent(event)

        # Move cursor to top visually
        self.moveCursor(QTextCursor.Start)

        # Emit only if user modified
        if self._user_modified:
            current = self.toPlainText()
            if current != self._last_text:
                self._last_text = current
                self.textEdited.emit(current)
            self._user_modified = False  # reset dirty flag

    def _on_text_changed(self):
        # Only mark as dirty; emit happens on focus out
        self._user_modified = True

    def set_line_spacing(self, multiplier: float = 0.5):
        """Set line spacing multiplier (0.5 = 50%) for the text."""
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.Document)

        block_format = QTextBlockFormat()
        block_format.setLineHeight(int(100 * multiplier), QTextBlockFormat.ProportionalHeight)
        cursor.setBlockFormat(block_format)

        # Move cursor to start after applying format
        cursor.setPosition(0)
        self.setTextCursor(cursor)


class FixedHeightTextItem(QGraphicsTextItem):
    def __init__(self, text='', max_height=40, parent=None):
        super().__init__(text, parent)
        self._max_height = max_height

    def boundingRect(self) -> QRectF:
        rect = super().boundingRect()
        rect.setHeight(self._max_height)
        return rect

    def set_line_spacing(self, multiplier: float = 0.5):
        """Set line spacing multiplier (0.5 = 50%) for the text."""
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.Document)

        block_format = QTextBlockFormat()
        block_format.setLineHeight(int(100 * multiplier), QTextBlockFormat.ProportionalHeight)
        cursor.setBlockFormat(block_format)

        # Move cursor to start after applying format
        cursor.setPosition(0)
        self.setTextCursor(cursor)
