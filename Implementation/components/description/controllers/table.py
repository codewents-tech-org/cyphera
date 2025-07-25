# pylint: disable=E0611,E0401,W0718
"""
Module: Table Controller
File: table.py
Layer: UI / Controller Layer
Component ID: 
Requirement IDs: 
Author: Vijaya Ragavan
Created On: 2025-06-27
Version: 

Purpose:
--------
Provides `TableController`, which handles insertion and modification
(rows/columns) of tables in a `QTextEdit`.

Responsibilities:
-----------------
• Prompt for table size via a dialog.  
• Insert new tables with default styling.  
• Add/remove rows and columns at or around the current cell.  
• Safely no‐op when there’s no table.  
• Restore document edit blocks to allow undo/redo.

Public API:
-----------
class TableController
  __init__(text_edit: QTextEdit, toolbar) -> None  
    • Connects toolbar signals for table actions.  

  insert_table() -> None  
    • Prompts user for rows/columns and inserts the table.

  _add_row(above: bool) -> None  
    • Inserts a row above or below the current row.

  _delete_row() -> None  
    • Deletes the current row if more than one.

  _add_column(left: bool) -> None  
    • Inserts a column to the left or right of the current column.

  _delete_column() -> None  
    • Deletes the current column if more than one.

Helper Methods:
---------------
  _current_table() -> Optional[QTextTable]  
    • Returns the table at cursor or None.
"""

import logging
import os
from typing import Optional, Tuple

from PyQt5.QtWidgets import (
    QDialog, QGridLayout, QLabel, QSpinBox, QPushButton, QTextEdit
)
from PyQt5.QtGui     import (
    QTextTableFormat, QTextCharFormat, QColor, QTextCursor
)
from PyQt5.QtCore    import Qt

from ..image_editor_dialog import ResizableImageDialog

logger = logging.getLogger(__name__)

class TableDialog(QDialog):
    """
    Dialog to get the number of rows and columns for table creation.
    """
    def __init__(self, parent=None) -> None:
        """
        Args:
            parent: The parent widget for the dialog.
        """
        super().__init__(parent)
        self.setWindowTitle("Insert Table")
        self.setFixedSize(300, 150)

        layout = QGridLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Number of Rows:"), 0, 0)
        self.rows_spinbox = QSpinBox(self)
        self.rows_spinbox.setRange(1, 100)
        layout.addWidget(self.rows_spinbox, 0, 1)

        layout.addWidget(QLabel("Number of Columns:"), 1, 0)
        self.columns_spinbox = QSpinBox(self)
        self.columns_spinbox.setRange(1, 20)
        layout.addWidget(self.columns_spinbox, 1, 1)

        insert_btn = QPushButton("Insert Table", self)
        insert_btn.clicked.connect(self.accept)
        layout.addWidget(insert_btn, 2, 0)

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn, 2, 1)

    def get_table_size(self) -> Tuple[int, int]:
        """
        Returns:
            A tuple (rows, columns) selected by the user.
        """
        return self.rows_spinbox.value(), self.columns_spinbox.value()


class TableController:
    """
    Handles insertion and manipulation of tables in a QTextEdit.
    """

    def __init__(self, text_edit: QTextEdit, toolbar) -> None:
        """
        Connects toolbar signals to controller methods.

        Args:
            text_edit: The QTextEdit to operate on.
            toolbar:   Toolbar emitting table-related signals.

        Returns:
            None
        """
        self.text_edit = text_edit
        self.toolbar   = toolbar

        toolbar.insertTableClicked.connect(self.insert_table)
        toolbar.insertRowAboveClicked.connect(lambda: self._add_row(above=True))
        toolbar.insertRowBelowClicked.connect(lambda: self._add_row(above=False))
        toolbar.deleteRowClicked.connect(self._delete_row)
        toolbar.insertColumnLeftClicked.connect(lambda: self._add_column(left=True))
        toolbar.insertColumnRightClicked.connect(lambda: self._add_column(left=False))
        toolbar.deleteColumnClicked.connect(self._delete_column)

    def insert_table(self) -> None:
        """
        Prompt for rows/columns and insert a new table with default styling.

        Returns:
            None
        """
        dialog = TableDialog(self.text_edit)
        if dialog.exec_() != QDialog.Accepted:
            return

        rows, cols = dialog.get_table_size()
        cursor = self.text_edit.textCursor()
        fmt = QTextTableFormat()
        fmt.setBorder(1)
        fmt.setCellPadding(4)
        fmt.setCellSpacing(0)

        cursor.beginEditBlock()
        table = cursor.insertTable(rows, cols, fmt)

        # Default formatting: 8pt Arial, black on white
        cell_fmt = QTextCharFormat()
        cell_fmt.setFontFamily("Arial")
        cell_fmt.setFontPointSize(8)
        cell_fmt.setForeground(QColor("black"))
        cell_fmt.setBackground(QColor("white"))

        for r in range(rows):
            for c in range(cols):
                cell = table.cellAt(r, c)
                cell_cursor = cell.firstCursorPosition()
                cell_cursor.mergeCharFormat(cell_fmt)

        cursor.endEditBlock()
        logger.info("Inserted %dx%d table", rows, cols)

    def _add_row(self, above: bool = True) -> None:
        """
        Insert a row above or below the current cell.

        Args:
            above: True to insert above; False to insert below.

        Returns:
            None
        """
        table = self._current_table()
        if not table:
            return
        cursor = self.text_edit.textCursor()
        row = table.cellAt(cursor).row()
        table.insertRows(row if above else row + 1, 1)
        logger.info("Added row %s current row %d", "above" if above else "below", row)

    def _delete_row(self) -> None:
        """
        Delete the current row if table exists and has more than one.

        Returns:
            None
        """
        table = self._current_table()
        if not table or table.rows() <= 1:
            return
        cursor = self.text_edit.textCursor()
        row = table.cellAt(cursor).row()
        table.removeRows(row, 1)
        logger.info("Deleted row %d", row)

    def _add_column(self, left: bool = True) -> None:
        """
        Insert a column to the left or right of the current cell.

        Args:
            left: True to insert left; False to insert right.

        Returns:
            None
        """
        table = self._current_table()
        if not table:
            return
        cursor = self.text_edit.textCursor()
        col = table.cellAt(cursor).column()
        table.insertColumns(col if left else col + 1, 1)
        logger.info("Added column %s current column %d", "left" if left else "right", col)

    def _delete_column(self) -> None:
        """
        Delete the current column if table exists and has more than one.

        Returns:
            None
        """
        table = self._current_table()
        if not table or table.columns() <= 1:
            return
        cursor = self.text_edit.textCursor()
        col = table.cellAt(cursor).column()
        table.removeColumns(col, 1)
        logger.info("Deleted column %d", col)

    def _current_table(self):
        """
        Return:
            The QTextTable at the current cursor, or None if not in a table.
        """
        return self.text_edit.textCursor().currentTable()
