"""
Module: Tree Row Indicator   \n
File: tree_row_indicator.py     \n
Layer: UI / Widget Component Layer     \n
Component ID: CY_CO_013     \n
Requirement IDs:     \n
Author: Vishnu Viswanath     \n
Created On: 2025-05-14     \n
Version: V 3.0   \n

Purpose:
--------
Provides a sidebar widget for hierarchical tables that includes a row-level delete button  
and a tree-expansion toggle. This is used in complex views requiring interaction per row  
in a tree-structured data model.

Description:
------------
Defines a reusable sidebar widget for QTableWidget rows, featuring a compact, icon-based button interface.
Supports row-specific actions with standardized layout, icon styling, and signal handling for seamless UI interaction.

Responsibilities
----------------
- Display round and tree-expansion buttons within table/tree rows
- Handle click events for delete and open operations
- Maintain a fixed-size, margin-aligned layout per row

Signals
-------
+---------------------+-------------------------+-----------------------------+--------------------------+
| Trigger             | Signal Name             | Description                 | Payload Format           |
+=====================+=========================+=============================+==========================+
| Delete button       | round_button.clicked    |Triggered when delete pressed| N/A (logs only)          |
+---------------------+-------------------------+-----------------------------+--------------------------+
| Expand button       | tree_button.clicked     |Triggers tree expansion logic| Calls `open_tree()`      |
+---------------------+-------------------------+-----------------------------+--------------------------+


Dependencies:
-------------
- PyQt5 (QtWidgets, QtGui, QtCore)
- models.Parameters
- logging

Limitations
-----------
- No visual feedback for expanded/collapsed state
- Hardcoded icons and dimensions
- Delete and edit logic must be implemented externally


Improvements
------------
- Support dynamic icon switching on expand/collapse
- Add confirmation prompts for deletion
- Make layout fully adaptive to parent dimensions


Change History:
---------------
+----------------+----------------------+-----------------+----------------+
| Version        | Date                 | Change          | Author         |
+================+======================+=================+================+
| V 3.0          | 14/05/2025           | Initial Version |Vishnu Viswanath|
+----------------+----------------------+-----------------+----------------+
|                |                      |                 |                |
+----------------+----------------------+-----------------+----------------+
|                |                      |                 |                |
+----------------+----------------------+-----------------+----------------+
|                |                      |                 |                |
+----------------+----------------------+-----------------+----------------+
|                |                      |                 |                |
+----------------+----------------------+-----------------+----------------+
"""


from PyQt5.QtCore import pyqtSignal,Qt
import logging
try:
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import QSize
    import models.Parameters as P
except ImportError as e:
    print(f"ImportError in tree_row_indicator.py: {e}")

logger = logging.getLogger(__name__)


# Constants
ROUND_BUTTON_SIZE = 16
TREE_BUTTON_SIZE = 24
BUTTON_MARGIN_LEFT = 15


class SidebarWidget(QWidget):
    """
    Sidebar widget with a delete icon and a tree-expansion icon for each row.

    Args:
        parent (QWidget): The parent widget.
        index (int): Row index this widget is associated with.
    """

    tree_button_requested = pyqtSignal(int)

    def __init__(self, parent=None, index=None, tree_indicator=False):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        self.index = index

        layout = QHBoxLayout()
        layout.setContentsMargins(BUTTON_MARGIN_LEFT, 0, 0, 0)

        # Delete button
        self.round_button = QPushButton()
        self.round_button.setIcon(QIcon(P.deselectedrow_icon))
        self.round_button.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.round_button.setIconSize(QSize(ROUND_BUTTON_SIZE, ROUND_BUTTON_SIZE))
        self.round_button.setFixedSize(ROUND_BUTTON_SIZE, ROUND_BUTTON_SIZE)
        self.round_button.clicked.connect(self.delete_row)
        layout.addWidget(self.round_button)

        if tree_indicator:
            # Tree expansion button
            self.tree_button = QPushButton()
            self.tree_button.setIcon(QIcon(P.selectedrow_icon))
            self.tree_button.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
            self.tree_button.setIconSize(QSize(TREE_BUTTON_SIZE, TREE_BUTTON_SIZE))
            self.tree_button.setFixedSize(TREE_BUTTON_SIZE, TREE_BUTTON_SIZE)
            self.tree_button.clicked.connect(self.open_tree)
            layout.addWidget(self.tree_button)

        layout.addStretch()
        self.setLayout(layout)

    def delete_row(self):
        """
        Placeholder for delete row action.
        """
        logger.info("Delete placeholder")

    def add_row(self):
        """
        Placeholder for tree edit/add row action.
        """
        logger.info("Edit button clicked")

    def open_tree(self):
        self.tree_button_requested.emit(self.index)