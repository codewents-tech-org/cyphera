"""
Module: Table Row Indicator   \n
File: table_row_indicator.py     \n
Layer: UI / Widget Component Layer     \n
Component ID: CO_012     \n
Requirement IDs: None     \n
Author: Vishnu Viswanath     \n
Created On: 2025-05-14     \n
Version: V 3.0   \n

Purpose:
--------
Defines the `SidebarWidget` used to display a compact, icon-based button interface  
on the left edge of each row in a `QTableWidget`. This widget facilitates row-specific actions  
and enhances interactivity with minimal visual footprint.

Description:
------------
Defines a reusable sidebar widget for QTableWidget rows, featuring a compact, icon-based button interface.
Supports row-specific actions with standardized layout, icon styling, and signal handling for seamless UI interaction.

Responsibilities
----------------
- Define a sidebar component that hosts action buttons per table row.
- Configure layout with margins, icon styles, and size constraints.
- Handle button click events to support row-specific actions (e.g., deletion).

Signals
-------
+---------------------+-------------------------+-----------------------------+--------------------------+
| Trigger             | Signal Name             | Description                 | Payload Format           |
+=====================+=========================+=============================+==========================+
| Button Click        | round_button.clicked    | Triggered on button press   | N/A (logging only)       |
+---------------------+-------------------------+-----------------------------+--------------------------+

Dependencies:
-------------
- PyQt5 (QtWidgets, QtGui, QtCore)
- models.Parameters
- logging

Limitations
-----------
- Currently hardcoded to one action button per row.
- Row deletion logic is a placeholder — must be implemented externally.
- Assumes valid icon path from `models.Parameters`.

Improvements
------------
- Add hover effects or tooltips for better UX.
- Support dynamic action binding (edit, duplicate, etc.).
- Integrate with model/view architecture for clean row operations.

Change History:
---------------
+----------------+----------------------+-----------------+----------------+
| Version        | Date                 | Change          | Author         |
+================+======================+=================+================+
| v 3.0          | 14/05/2025           | Initial Version |Vishnu Viswanath|
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


import logging

try:
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import QSize
    import models.Parameters as P
except ImportError as e:
    print(f"ImportError in table_row_indicator.py: {e}")

logger = logging.getLogger(__name__)



class SidebarWidget(QWidget):
    """
    Sidebar widget that displays a round button for each row in a table.
    Provides a consistent interface for row-level actions.

    Args:
        parent (QWidget, optional): The parent widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.button_size = 16
        self.button_margin_left = 15

        layout = QHBoxLayout()
        layout.setContentsMargins( self.button_margin_left, 0, 0, 0)

        self.round_button = QPushButton()
        try:
            self.round_button.setIcon(QIcon(P.deselectedrow_icon))
        except Exception as e:
            logger.warning(f"Failed to set icon: {e}")
        self.round_button.setStyleSheet(
            "QPushButton{background-color: transparent; border:none}"
        )
        self.round_button.setIconSize(QSize(self.button_size, self.button_size))
        self.round_button.setFixedSize(self.button_size, self.button_size)

        layout.addWidget(self.round_button)
        layout.addStretch()
        self.setLayout(layout)

        self.round_button.clicked.connect(self.delete_row)

    def delete_row(self):
        """
        Placeholder for row delete functionality.

        Returns:
            None
        """
        logger.info("Delete placeholder")
