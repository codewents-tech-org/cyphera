# pylint: disable=E0611,E0401,R0914,R0915,R0913,R0917,W0718,W0613,R0903
"""
Module: Description Toolbar
File: toolbar.py
Layer: UI / Editor Toolbar Layer
Component ID: CY_DE_004
Requirement IDs: DE-TB-001, DE-TB-002, DE-TB-003
Author: Vijaya Karagi
Created On: 2025-06-27
Version: V1.0

Purpose:
--------
Provides `DescriptionToolbar`, a rich-text toolbar for the description editor,
exposing formatting, list, alignment, table, and picture insert controls.

Responsibilities:
-----------------
• Layout toolbar widgets (buttons, dropdowns, spacers) according to spec.  
• Expose signals for each action (bold, italic, save, insert picture, etc.).  
• Reflect current formatting state via `apply_text_format_states()`.  
• Maintain a registry of widget refs for dynamic updates.  

Signals:
--------
+-----------------------------+----------------------+------------------------------+
| Signal                      | Emitted on           | Payload                      |
+=============================+======================+==============================+
| boldClicked()               | Bold button clicked  | None                         |
| italicClicked()             | Italic button clicked| None                         |
| highlightClicked()          | Highlight clicked    | None                         |
| fontSizeChanged(int)        | Size dropdown change | New font size               |
| fontStyleChanged(str)       | Style dropdown change| "Normal" or "Heading"       |
| fontColorClicked()          | Color button clicked | None                         |
| saveClicked()               | Save button clicked  | None                         |
| refreshClicked()            | Refresh clicked      | None                         |
| insertPictureClicked()      | Insert picture btn   | None                         |
| bulletsClicked()            | Bullets clicked      | None                         |
| numberingClicked()          | Numbering clicked    | None                         |
| alignChanged(Qt.Alignment)  | Alignment selected   | Alignment flag              |
| insertTableClicked()        | Insert table clicked | None                         |
| insertColumnLeftClicked()   | Insert col left      | None                         |
| insertColumnRightClicked()  | Insert col right     | None                         |
| insertRowAboveClicked()     | Insert row above     | None                         |
| insertRowBelowClicked()     | Insert row below     | None                         |
| deleteRowClicked()          | Delete row clicked   | None                         |
| deleteColumnClicked()       | Delete col clicked   | None                         |
+-----------------------------+----------------------+------------------------------+
"""

import logging
from typing import Dict, Tuple, Optional

from PyQt5.QtWidgets import (
    QToolBar, QWidget, QLabel, QToolButton, QSizePolicy,
    QComboBox, QMenu, QPushButton, QWidgetAction, QFrame, QHBoxLayout
)
from PyQt5.QtGui    import QIcon
from PyQt5.QtCore   import Qt, QSize, pyqtSignal

import utils.file_utils as files
import styles.toolbar_style as toolbar_style

logger = logging.getLogger(__name__)

class DescriptionToolbar(QToolBar):
    """
    A rich text toolbar for editing the description section.
    """
    boldClicked               = pyqtSignal()
    italicClicked             = pyqtSignal()
    highlightClicked          = pyqtSignal()
    fontSizeChanged           = pyqtSignal(int)
    fontStyleChanged          = pyqtSignal(str)
    fontColorClicked          = pyqtSignal()
    saveClicked               = pyqtSignal()
    refreshClicked            = pyqtSignal()
    insertPictureClicked      = pyqtSignal()
    bulletsClicked            = pyqtSignal()
    numberingClicked          = pyqtSignal()
    alignChanged              = pyqtSignal(Qt.Alignment)
    insertTableClicked        = pyqtSignal()
    insertColumnLeftClicked   = pyqtSignal()
    insertColumnRightClicked  = pyqtSignal()
    insertRowAboveClicked     = pyqtSignal()
    insertRowBelowClicked     = pyqtSignal()
    deleteRowClicked          = pyqtSignal()
    deleteColumnClicked       = pyqtSignal()

    def __init__(
        self,
        heading_text: str,
        buttons: Dict[str, Tuple[str, str]],
        parent: Optional[QWidget] = None
    ) -> None:
        """
        Initialize the toolbar.

        Args:
            heading_text: Title text next to the back-arrow.
            buttons:      Map of button names to (icon_path, tooltip).
            parent:       Optional parent widget.

        Returns:
            None
        """
        super().__init__(parent)
        self.setMovable(False)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(toolbar_style.toolbar_style)

        self.buttons = buttons
        self.refs: Dict[str, QWidget] = {}
        self._build_toolbar(heading_text)

    def _build_toolbar(self, heading_text: str) -> None:
        """
        Construct all toolbar widgets.

        Args:
            heading_text: The label text to show after the arrow icon.

        Returns:
            None
        """
        def add_spacer(width: int = 5) -> None:
            spacer = QWidget()
            spacer.setFixedWidth(width)
            spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
            self.addWidget(spacer)

        def add_tool_button(name: str, signal=None, checkable: bool = False) -> None:
            btn = QToolButton()
            btn.setIcon(QIcon(self.buttons[name][0]))
            btn.setToolTip(self.buttons[name][1])
            btn.setIconSize(QSize(20, 20))
            btn.setStyleSheet(toolbar_style.toolbar_button_style)
            btn.setCheckable(checkable)
            if signal:
                btn.clicked.connect(signal)
            self.addWidget(btn)
            key = name.lower().replace(" ", "_") + "_button"
            self.refs[key] = btn

        # Back-arrow + heading
        arrow = QToolButton()
        arrow.setIcon(QIcon(files.path_arrow_icon))
        arrow.setIconSize(QSize(18, 18))
        arrow.setStyleSheet(toolbar_style.toolbar_arrow_style)
        self.addWidget(arrow)

        title_label = QLabel(heading_text)
        title_label.setStyleSheet(toolbar_style.toolbar_label_style)
        self.addWidget(title_label)

        expanding = QWidget()
        expanding.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        expanding.setStyleSheet(toolbar_style.toolbar_spacer_style)
        self.addWidget(expanding)

        # Save / Refresh
        add_tool_button("Save",    signal=self.saveClicked.emit)
        add_spacer()
        add_tool_button("Refresh", signal=self.refreshClicked.emit)
        add_spacer()
        self.addSeparator()

        # Font style dropdown
        font_style = QComboBox()
        font_style.addItems(["Normal", "Heading"])
        font_style.setFixedSize(QSize(120, 35))
        font_style.setStyleSheet(toolbar_style.toolbar_combobox_style)
        font_style.currentTextChanged.connect(self.fontStyleChanged.emit)
        self.addWidget(font_style)
        self.refs["font_style_combo"] = font_style

        add_spacer()

        # Font size dropdown
        font_size = QComboBox()
        for size in range(8, 32, 2):
            font_size.addItem(str(size))
        font_size.setFixedSize(QSize(50, 35))
        font_size.setStyleSheet(toolbar_style.toolbar_combobox_style)
        font_size.currentTextChanged.connect(lambda txt: self.fontSizeChanged.emit(int(txt)))
        self.addWidget(font_size)
        self.refs["font_size_combo"] = font_size

        add_spacer()

        # Formatting buttons
        add_tool_button("Bold",       signal=self.boldClicked.emit,      checkable=True)
        add_spacer()
        add_tool_button("Font Color", signal=self.fontColorClicked.emit)
        add_spacer()
        add_tool_button("Highlight",  signal=self.highlightClicked.emit,  checkable=True)
        add_tool_button("Italic",     signal=self.italicClicked.emit,    checkable=True)

        add_spacer()
        add_tool_button("Insert Picture", signal=self.insertPictureClicked.emit)

        add_spacer()
        self.addSeparator()
        add_spacer()

        # List controls
        add_tool_button("Bullets",   signal=self.bulletsClicked.emit)
        add_spacer()
        add_tool_button("Numbering", signal=self.numberingClicked.emit)

        add_spacer()
        self.addSeparator()
        add_spacer(10)

        # Alignment dropdown
        align_btn = QToolButton()
        align_btn.setIcon(QIcon(self.buttons["Left Align"][0]))
        align_btn.setToolTip("Alignment")
        align_btn.setIconSize(QSize(20, 20))
        align_btn.setStyleSheet(toolbar_style.toolbar_dropdown_button_style)
        align_btn.setPopupMode(QToolButton.InstantPopup)
        self.refs["align_button"] = align_btn

        align_frame = QFrame()
        hl = QHBoxLayout(align_frame)
        hl.setContentsMargins(5, 5, 5, 5)
        hl.setSpacing(5)

        align_map = {
            "Left Align":   Qt.AlignLeft,
            "Center Align": Qt.AlignCenter,
            "Right Align":  Qt.AlignRight,
            "Justify":      Qt.AlignJustify
        }
        for label, flag in align_map.items():
            btn = QPushButton()
            btn.setIcon(QIcon(self.buttons[label][0]))
            btn.setToolTip(self.buttons[label][1])
            btn.setIconSize(QSize(20, 20))
            btn.setStyleSheet(toolbar_style.toolbar_dropdown_button_inner_style)
            btn.clicked.connect(lambda _, a=flag: self.alignChanged.emit(a))
            hl.addWidget(btn)
            self.refs[label.lower().replace(" ", "_") + "_button"] = btn

        menu = QMenu(align_btn)
        menu.setStyleSheet(toolbar_style.toolbar_dropdown_menu_style)
        action = QWidgetAction(menu)
        action.setDefaultWidget(align_frame)
        menu.addAction(action)
        align_btn.setMenu(menu)
        self.addWidget(align_btn)

        add_spacer(10)
        self.addSeparator()
        add_spacer()

        # Table and cell controls
        add_tool_button("Insert Table",       signal=self.insertTableClicked.emit)
        add_spacer()
        add_tool_button("Insert Column Left", signal=self.insertColumnLeftClicked.emit)
        add_spacer()
        add_tool_button("Insert Column Right",signal=self.insertColumnRightClicked.emit)
        add_spacer()
        add_tool_button("Insert Row Above",   signal=self.insertRowAboveClicked.emit)
        add_spacer()
        add_tool_button("Insert Row Below",   signal=self.insertRowBelowClicked.emit)
        add_spacer()
        add_tool_button("Delete Row",         signal=self.deleteRowClicked.emit)
        add_spacer()
        add_tool_button("Delete Column",      signal=self.deleteColumnClicked.emit)
        add_spacer(10)

    def apply_text_format_states(
        self,
        is_bold: bool,
        is_italic: bool,
        is_underline: bool,
        is_highlighted: bool,
        font_size: int,
        font_color: str,
        alignment: str
    ) -> None:
        """
        Update toolbar controls to reflect the current text formatting.

        Args:
            is_bold:         True if current text is bold.
            is_italic:       True if italic.
            is_underline:    True if underlined.
            is_highlighted:  True if highlighted.
            font_size:       Current font size (points).
            font_color:      Current font color in hex (e.g. "#000000").
            alignment:       One of "Left", "Center", "Right", "Justify".

        Returns:
            None
        """
        try:
            # Toggle buttons (use QToolButton as fallback so setChecked() exists)
            self.refs.get("bold_button",   QToolButton()).setChecked(is_bold)
            self.refs.get("italic_button", QToolButton()).setChecked(is_italic)
            self.refs.get("underline_button", QToolButton()).setChecked(is_underline)
            self.refs.get("highlight_button", QToolButton()).setChecked(is_highlighted)

            # Font size dropdown
            size_combo = self.refs.get("font_size_combo")
            if isinstance(size_combo, QComboBox):
                size_combo.blockSignals(True)
                size_combo.setCurrentText(str(font_size))
                size_combo.blockSignals(False)

            # Alignment icon update
            icon_map = {
                "Left":    self.buttons["Left Align"][0],
                "Center":  self.buttons["Center Align"][0],
                "Right":   self.buttons["Right Align"][0],
                "Justify": self.buttons["Justify"][0],
            }
            align_btn = self.refs.get("align_button")
            if isinstance(align_btn, QToolButton):
                align_btn.setIcon(QIcon(icon_map.get(alignment, icon_map["Left"])))

        except Exception as e:
            logger.error("❌ apply_text_format_states failed: %s", e)
