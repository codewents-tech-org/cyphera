"""
Module: DescriptionEditor Module
File: editor.py
Layer: UI / Description Editing Layer
Component ID: 
Requirement IDs: 
Author: Vijaya Ragavan
Created On: 2025-06-26
Version: 

Purpose:
--------
Provides `DescriptionEditor`, a composite widget combining a toolbar, clean-text editor,
and feature controllers for formatting, lists, alignment, tables, and images.

Description:
------------
`DescriptionEditor` is responsible for:
  • Initializing and laying out its toolbar and `CleanTextEdit` editor.
  • Managing default formatting state (font, size, colors, alignment).
  • Loading and saving HTML content.
  • Detecting newlines to reset formatting.
  • Debouncing and emitting formatting-state updates.
  • Handling double-clicks on images to invoke the resize dialog.

Responsibilities:
-----------------
  • Build UI and apply styles in `_init_ui`.
  • Wire up controllers in `_init_controllers`.
  • Connect signals for toolbar sync and save/refresh in `_init_signals`.
  • Filter and handle events in `_install_event_filters` & `eventFilter`.
  • Expose public signals:
      - `content_changed(html: str)`
      - `text_format_updated(bold, italic, underline, highlight, size, color, align)`

Inputs:
-------
- `heading_text` (str): Title for the toolbar.
- Clipboard/drag data via QMimeData for paste operations.

Outputs:
--------
- Modifies its own layout and document contents.
- Emits `content_changed` and `text_format_updated` signals.

Returns:
--------
None (widget methods modify UI/state in place).
"""

import logging
from typing import Optional

# PyQt5 imports (disable false-positive no-name-in-module)
# pylint: disable=E0611
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDialog
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore    import pyqtSignal, QTimer, Qt, QEvent, QObject
from PyQt5.QtGui     import QColor, QFont, QTextCharFormat, QTextCursor, QTextBlockFormat
# pylint: enable=E0611

from .clean_text import CleanTextEdit
from .image_editor_dialog import ResizableImageDialog
import models.Parameters as P
from .toolbar import DescriptionToolbar
from .controllers.formatting import FormattingController
from .controllers.lists      import ListController
from .controllers.alignment  import AlignmentController
from .controllers.table      import TableController
from .controllers.image      import ImageController

logger = logging.getLogger(__name__)


class DescriptionEditor(QWidget):  # pylint: disable=too-few-public-methods
    """
    Composite widget with toolbar + editor + feature controllers.

    Signals:
        content_changed(html: str)
        text_format_updated(bold: bool, italic: bool, underline: bool,
                            highlight: bool, size: int, color: str, align: str)
    """

    content_changed     = pyqtSignal(str)
    text_format_updated = pyqtSignal(bool, bool, bool, bool, int, str, str)

    def __init__(self, heading_text: str, parent: Optional[QWidget] = None) -> None:
        """
        Initialize UI, state, controllers, and signals; schedule initial toolbar sync.

        Args:
            heading_text (str): The title to display in the toolbar.
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)
        self._init_state()
        self._init_ui(heading_text)
        self._init_controllers()
        self._init_signals()
        self._install_event_filters()
        QTimer.singleShot(0, self.update_toolbar_state)

    def _init_state(self) -> None:
        """Set up initial formatting state variables."""
        self.current_font_family     = "Arial"
        self.current_font_size       = 8
        self.current_bold            = False
        self.current_italic          = False
        self.current_underline       = False
        self.current_font_color      = QColor("black")
        self.current_highlight_color = QColor("white")
        self.current_alignment       = Qt.AlignLeft

    def _init_ui(self, heading_text: str) -> None:
        """
        Build toolbar and editor UI, apply default styling.

        Args:
            heading_text (str): The title for the toolbar.
        """
        # Debounce timer for selection changes
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_toolbar_state)

        # Define toolbar buttons
        buttons = {
            "Bold":             (P.bold_icon, "Bold"),
            "Italic":           (P.italic_icon, "Italic"),
            "Font Color":       (P.text_color_icon, "Font Color"),
            "Highlight":        (P.highlight_icon, "Highlight"),
            "Insert Picture":   (P.insert_image_icon, "Insert Picture"),
            "Bullets":          (P.bullet_index_icon, "Bullets"),
            "Numbering":        (P.number_index_icon, "Numbering"),
            "Left Align":       (P.left_align_icon, "Left Align"),
            "Center Align":     (P.center_align_icon, "Center Align"),
            "Right Align":      (P.right_align_icon, "Right Align"),
            "Justify":          (P.justify_icon, "Justify"),
            "Insert Table":     (P.insert_table_icon, "Insert Table"),
            "Insert Row Above": (P.insert_row_above_icon, "Insert Row Above"),
            "Insert Row Below": (P.insert_row_below_icon, "Insert Row Below"),
            "Delete Row":       (P.delete_row_icon, "Delete Row"),
            "Insert Column Left":  (P.insert_column_left_icon, "Insert Column Left"),
            "Insert Column Right": (P.insert_column_right_icon, "Insert Column Right"),
            "Delete Column":    (P.delete_column_icon, "Delete Column"),
            "Save":             (P.save_icon, "Save"),
            "Refresh":          (P.Reload_icon, "Refresh"),
        }

        # Create toolbar
        self.toolbar = DescriptionToolbar(heading_text, buttons, parent=self)

        # Create clean-text editor
        self.text_edit = CleanTextEdit(parent=self)
        self.text_edit.setFont(QFont(self.current_font_family, self.current_font_size))

        # Default character format
        default_fmt = QTextCharFormat()
        default_fmt.setFontPointSize(self.current_font_size)
        default_fmt.setBackground(QColor("white"))
        self.text_edit.setCurrentCharFormat(default_fmt)

        # Editor stylesheet
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF; color: black; font-size: 8pt;
                padding: 8px; border: 1px solid #D3D3D3; border-radius: 8px;
            }
            QTextEdit QScrollBar:vertical {
                border: none; background: #f0f0f0; width: 10px; margin: 0;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #c1c1c1; min-height: 20px; border-radius: 5px;
            }
            QTextEdit QScrollBar:horizontal {
                border: none; background: #f0f0f0; height: 10px; margin: 0;
            }
            QTextEdit QScrollBar::handle:horizontal {
                background: #c1c1c1; min-width: 20px; border-radius: 5px;
            }
        """)

        # Layout assembly
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def _init_controllers(self) -> None:
        """Instantiate feature controllers for formatting, lists, alignment, tables, and images."""
        self.format_ctrl = FormattingController(self.text_edit, self.toolbar)
        self.list_ctrl   = ListController(self.text_edit, self.toolbar)
        self.align_ctrl  = AlignmentController(self.text_edit, self.toolbar)
        self.table_ctrl  = TableController(self.text_edit, self.toolbar)
        self.image_ctrl  = ImageController(self.text_edit, self.toolbar)

    def _init_signals(self) -> None:
        """Connect editor signals to toolbar updates and save/refresh actions."""
        self.text_format_updated.connect(self.toolbar.apply_text_format_states)
        self.text_edit.cursorPositionChanged.connect(self.on_selection_change)
        self.text_edit.selectionChanged.connect(self.on_selection_change)
        self.text_edit.document().undoAvailable.connect(
            lambda _: QTimer.singleShot(50, self.update_toolbar_state)
        )
        self.text_edit.textChanged.connect(self.detect_newline_reset)
        self.toolbar.saveClicked.connect(self.on_save)
        self.toolbar.refreshClicked.connect(
            lambda: self.load_content(self._last_loaded_html)
        )

    def _install_event_filters(self) -> None:
        """Install event filters on editor and viewport to catch double-clicks."""
        self.text_edit.installEventFilter(self)
        self.text_edit.viewport().installEventFilter(self)

    def load_content(self, html: str) -> None:
        """
        Load HTML into the editor and reset default format.

        Args:
            html (str): The HTML string to load.

        Returns:
            None
        """
        self._last_loaded_html = html
        self.text_edit.setHtml(html)
        fmt = QTextCharFormat()
        fmt.setFontPointSize(self.current_font_size)
        fmt.setBackground(QColor("white"))
        self.text_edit.setCurrentCharFormat(fmt)
        QTimer.singleShot(0, self.update_toolbar_state)

    def on_save(self) -> None:
        """
        Emit the current document HTML via content_changed signal.

        Returns:
            None
        """
        html = self.text_edit.toHtml()
        self.content_changed.emit(html)

    def detect_newline_reset(self) -> None:
        """
        Detects a trailing newline and schedules a format reset.

        Returns:
            None
        """
        if self.text_edit.toPlainText().endswith("\n"):
            QTimer.singleShot(10, self.reset_format_on_newline)

    def reset_format_on_newline(self) -> None:
        """
        Reset the editor's current CharFormat to default after newline.

        Returns:
            None
        """
        fmt = QTextCharFormat()
        fmt.setFontFamily(self.current_font_family)
        fmt.setFontPointSize(self.current_font_size)
        fmt.setFontWeight(QFont.Normal)
        fmt.setFontItalic(False)
        fmt.setFontUnderline(False)
        fmt.setBackground(self.current_highlight_color)
        fmt.setForeground(self.current_font_color)
        self.text_edit.setCurrentCharFormat(fmt)
        self.update_toolbar_state()

    def on_selection_change(self) -> None:
        """
        Debounce and schedule toolbar state update when selection changes.

        Returns:
            None
        """
        if self.update_timer.isActive():
            self.update_timer.stop()
        self.update_timer.start(250)

    def update_toolbar_state(self) -> None:
        """
        Emit current text formatting to toolbar (with debug output and size fallback).
        """
        try:
            cursor       = self.text_edit.textCursor()
            fmt          = cursor.charFormat()

            # — DEBUG: what sizes are we seeing? —
            primary_size  = fmt.fontPointSize()
            fallback_size = self.text_edit.currentCharFormat().fontPointSize()
           

            # 1) pick the real float size
            size = primary_size if primary_size > 0 else fallback_size
            # 2) cast to int so "24.0" → 24, which matches your combo entries
            size = int(size)

            bold      = fmt.fontWeight() == QFont.Bold
            italic    = fmt.fontItalic()
            underline = fmt.fontUnderline()
            highlight = fmt.background().color().name().lower() == "#ffff00"
            color     = fmt.foreground().color().name()

            alignment = cursor.blockFormat().alignment()
            align_map = {
                Qt.AlignLeft:    "Left",
                Qt.AlignCenter:  "Center",
                Qt.AlignRight:   "Right",
                Qt.AlignJustify: "Justify"
            }
            align_str = align_map.get(alignment, "Left")

            self.text_format_updated.emit(
                bold, italic, underline, highlight, size, color, align_str
            )
        except Exception as e:
            logger.error("update_toolbar_state failed: %s", e)


    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Catch double-clicks on images and open resize dialog.

        Args:
            obj (QObject): The object receiving the event.
            event (QEvent): The QEvent being filtered.

        Returns:
            bool: True if handled; False otherwise.
        """
        if (event.type() == QEvent.MouseButtonDblClick and
            (obj is self.text_edit or obj is self.text_edit.viewport())):
            cursor = self.text_edit.cursorForPosition(event.pos())
            fmt    = cursor.charFormat()
            if fmt.isImageFormat():
                path = fmt.toImageFormat().name()
                dlg  = ResizableImageDialog(path, parent=self)
                dlg.setWindowState(dlg.windowState() | Qt.WindowMaximized)
                if dlg.exec_() == QDialog.Accepted:
                    new_path, w, h = dlg.get_resized_image()
                    block_cursor = QTextCursor(self.text_edit.document())
                    block_cursor.setPosition(cursor.block().position())
                    block_cursor.select(QTextCursor.BlockUnderCursor)
                    block_cursor.removeSelectedText()
                    block_cursor.deletePreviousChar()

                    insert_cursor = QTextCursor(block_cursor)
                    insert_cursor.insertHtml(
                        f'<img src="{new_path}" width="{w}" height="{h}">'
                    )
                    insert_cursor.mergeCharFormat(self.text_edit.currentCharFormat())
                    insert_cursor.movePosition(QTextCursor.NextCharacter)
                    self.text_edit.setTextCursor(insert_cursor)
                    self.update_toolbar_state()
                return True

        return super().eventFilter(obj, event)
