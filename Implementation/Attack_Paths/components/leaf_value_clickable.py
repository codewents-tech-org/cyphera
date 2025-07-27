"""
Module: Leaf Value Selection      \n 
File: leaf_value_clickable.py      \n
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
This module provides a UI component that allows users to interactively
select one of several predefined leaf-level attribute values (e.g., Time, Expertise, Access).

Description:
------------
The `ClickableLabel` class extends `QLabel` to show a context menu with predefined
values when clicked. Each instance corresponds to one value field (by index), and emits
the selected value as a signal for integration with parent logic.

Responsibilities
----------------
- Handle left-click only if the click occurs inside the label bounds
- Display a context menu with the correct value mapping for the current index
- Emit a signal when the user selects a new value

Dependencies:
-------------
- PyQt5.QtWidgets (QLabel, QMenu)
- PyQt5.QtCore (pyqtSignal, Qt, QPoint)
- PyQt5.QtGui (QFont)
- functools.partial

Classes:
-------------
- ClickableLabel(QLabel)
    - Shows a context menu of predefined values on click
    - Emits a valueSelected signal when an item is picked

Signals:
-------------
- valueSelected(str): emitted with the selected code value from the menu

Limitations
-----------
- Emits only the code, not the full label (can be expanded)
- No hover styling or visual feedback
- Menu only triggered via left-click; no keyboard navigation

Improvements
------------
- Add support for tooltips or value descriptions
- Allow label-to-code mapping back from text display
- Emit both code and label in valueSelected signal
- Add hover effect or focus indication for accessibility

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

from PyQt5.QtWidgets import QLabel, QMenu
from PyQt5.QtCore import pyqtSignal, Qt, QPoint
from PyQt5.QtGui import QFont
from functools import partial


AP_leaf_values_menu = [ 
                    {"0": "(<= One day)",   "1": "(<= one week)",   "4": "(<= one month)",  "17": "(<= six months)",        "19": "(> six months)"},
                    {"0": "(Layman)",       "3": "(Proficient)",    "6": "(Expert)",        "8": "(Multiple expert)"},
                    {"0": "(Public)",       "3": "(Restricted)",    "7": "(Confidential)",  "11": "(Strictly Confidential)"},
                    {"0": "(Unlimited)",    "1": "(Easy)",          "4": "(Moderate)",      "10": "(Difficult/none)"},
                    {"0": "(Standard)",     "4": "(Specialized)",   "7": "(Bespoke)",       "9": "(Multiple Bespoke)"}
                    ]


class ClickableLabel(QLabel):
    """
    A clickable QLabel that displays a context menu of predefined values.
    Emits the selected value code on user selection.

    Attributes:
        index (int): Index into AP_leaf_values_menu to determine which set of values to show.
    """
    valueSelected = pyqtSignal(str)  # Emits selected value code (e.g., "4")

    def __init__(self, index: int=0, parent=None):
        """
        Initializes the clickable label.

        Args:
            index (int): Index in the AP_leaf_values_menu.
            parent (QWidget): Optional parent widget.
        """
        super().__init__(parent)
        self.index = index
        self.setStyleSheet("QLabel { color: black; background: transparent; }")
        self.setAlignment(Qt.AlignCenter)
    
    def mousePressEvent(self, event):
        """
        Intercepts left-clicks and displays the value selection menu.
        Only triggers if click is inside label bounds.
        """
        if event.button() == Qt.LeftButton:
            if self.rect().contains(event.pos()):  # Strict containment check
                self.show_context_menu(event.globalPos())

    def show_context_menu(self, global_pos: QPoint):
        """
        Displays a context menu with predefined values for the label's index.

        Args:
            global_pos (QPoint): Global screen coordinates for menu placement.
        """
        menu = QMenu()
        menu.setFont(QFont('Roboto', 8, QFont.Normal))
        for code, label in AP_leaf_values_menu[self.index].items():
            action = menu.addAction(f"{code} {label}")
            action.triggered.connect(partial(self.emit_selected, code, label))
        menu.exec_(global_pos)

    def emit_selected(self, code: str, label: str):
        """
        Updates the label text and emits the selected code.

        Args:
            code (str): Selected internal code.
            label (str): Display label (unused in signal).
        """
        self.setText(code)
        self.valueSelected.emit(code)