"""
Module: Table Panel   \n
File: table_panel.py    \n 
Layer: UI / Table Presentation Layer    \n 
Component ID: CY_CO_011     \n
Requirement IDs:     \n
Author: Vishnu Viswanath     \n
Created On: 2025-05-14     \n
Version: V 3.0   \n

Purpose:
--------
Provides a `QTableWidget`-based panel with built-in support for inline editing using a custom delegate.  
This enables dynamic user interaction with table data while preserving consistent styling, margins, and behavior.

Description:
------------
Provides a reusable table panel with inline editing using a custom single-line delegate.
Encapsulates layout, styling, and signal handling in a wrapper class for clean integration into PyQt5 UIs.

Responsibilities
----------------
- Set up a standardized table panel using `QTableWidget`
- Integrate inline editing using a custom `SingleLineDelegate`
- Apply consistent styling, spacing, and interaction signals

Signals
-------
+---------------------+----------------------------+-----------------------------+--------------------------+
| Trigger             | Signal Name                | Description                 | Payload Format           |
+=====================+============================+=============================+==========================+
| Row selected        | selectionChanged           | Emitted when row is clicked | Selected row index       |
+---------------------+----------------------------+-----------------------------+--------------------------+
| Cell changed        | itemChanged / cellClicked  | Emitted on cell interaction | Changed cell value       |
+---------------------+----------------------------+-----------------------------+--------------------------+


Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore)
- styles.table_style
- logging

Limitations
-----------
- No row sorting or filtering features built in
- Assumes parent widget handles signal processing externally
- Does not validate edited input values

Improvements
------------
- Add row validation or formatting hooks
- Support drag/drop or copy/paste interaction
- Modularize delegate to support other input types (e.g., dropdown)

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


import logging
from components.table.table_row_indicator import SidebarWidget as TableRowIndicator
from components.table.tree_row_indicator import SidebarWidget as TreeRowIndicator
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTableWidgetItem



logger = logging.getLogger(__name__)

try:
    from PyQt5.QtWidgets import (
        QTableWidget, QSizePolicy, QVBoxLayout, QStyledItemDelegate, QLineEdit
    )
    from PyQt5.QtCore import Qt
    from styles import table_style
except ImportError as import_error:
    logger.exception("Failed to import required modules in table_panel.py: %s", import_error)

from components.table.table_component import TableComponent

class SingleLineDelegate(QStyledItemDelegate):
    """
    Delegate to provide single-line editable text fields in table cells.
    Ensures uniform height and focus behavior for QLineEdit fields.
    """

    def create_editor(self, parent, _option, _index):  # pylint: disable=invalid-name
        """ 
        Create a QLineEdit as the editor widget for the cell.

        Args:
            parent (QWidget): The parent widget.

        Returns:
            QLineEdit: The created line edit editor.
        """
        try:
            return QLineEdit(parent)
        except RuntimeError:
            logger.exception("Failed to create editor")
            return None

    def set_editor_data(self, editor, index):  # pylint: disable=invalid-name
        """ 
        Set data from the model into the editor widget.

        Args:
            editor (QLineEdit): The editor widget to update.
            index (QModelIndex): The index to retrieve data from.

        Returns:
            None
        """
        try:
            value = index.model().data(index, Qt.EditRole)
            editor.setText(str(value if value is not None else ""))
            editor.selectAll()
        except Exception:
            logger.exception("Failed to set editor data")

    def set_model_data(self, editor, model, index):  # pylint: disable=invalid-name
        """ 
        Update model data based on editor contents.

        Args:
            editor (QLineEdit): The editor with user input.
            model (QAbstractItemModel): The model to update.
            index (QModelIndex): The index to set data at.

        Returns:
            None
        """
        try:
            model.setData(index, editor.text(), Qt.EditRole)
        except Exception:
            logger.exception("Failed to set model data")

    def update_editor_geometry(self, editor, option, _index):  # pylint: disable=invalid-name
        """ 
        Update the editor geometry to match the cell dimensions.

        Args:
            editor (QLineEdit): The editor widget to position.
            option (QStyleOptionViewItem): Contains the geometry information.
            _index (QModelIndex): Unused.

        Returns:
            None
        """
        try:
            editor.setGeometry(option.rect)
        except AttributeError:
            logger.exception("Failed to update editor geometry")

class TablePanelWrapper(QWidget):
    """
    A wrapper class for creating and managing a customizable QTableWidget panel with inline editing support.

    This class sets up a styled table using PyQt5's QTableWidget, including inline editing via a custom delegate,
    row selection handling, and layout management. The table is embedded within a QVBoxLayout with margins and is
    suitable for integration into a parent widget.

    Attributes:
        parent (QWidget): The parent widget that will host the table.
        table (QTableWidget): The table widget used for displaying and editing data.
        table_layout (QVBoxLayout): Layout managing the placement and margins of the table.
    """
    def __init__(self, use_row_indicator=True, use_tree_indicator=False, parent=None):
        super().__init__(parent)  # ✅ Important
        self.parent_module = parent
        self.use_row_indicator = use_row_indicator
        self.use_tree_indicator = use_tree_indicator
        self.container = self  # ✅ Now this object itself is the QWidget

    def create_table_panel(self):
        """ 
        Set up the table widget panel layout with delegate and scroll policies.

        Args:
            self (QWidget): The parent widget that will hold the table and layout.

        Returns:
            None
        """
        try:
            self.table = QTableWidget()
            self.table.setSelectionBehavior(QTableWidget.SelectRows)
            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
            self.table.itemChanged.connect(self.display_selected_row)
            self.table.cellClicked.connect(self.display_selected_row)
            self.table.setStyleSheet(table_style.table_style)
            self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Install the custom delegate for single-line editing.
            self.table.setItemDelegate(SingleLineDelegate(self.table))
            
            # Create a layout and add the table.
            self.table_layout = QVBoxLayout()
            self.table_layout.setContentsMargins(10, 10, 10, 10)  # Add 10px margin on all sides
            self.table_layout.addWidget(self.table)
            
            self.container = QWidget()                      # ✅ container to wrap the layout
            self.setLayout(self.table_layout)  # ✅ Since self is now a QWidget     # ✅ set layout on container
            
            
         

        except (AttributeError, TypeError):
            logger.exception("Failed to create table panel")


    def on_row_selection_changed(self, selected, deselected):
        """Placeholder row selection handler. Can be overridden externally."""
        pass

    
    def display_selected_row(self, item_or_row, column=None):
        """
        Placeholder method triggered when a cell is changed or clicked.
        Can be overridden by external logic.
        """
        pass



    def set_headers(self, table_key: str):
        """
        Sets headers for the internal table based on the registered header mappings.
        """
        component = TableComponent()
        header_list = component._table_column_mappings.get(table_key.lower(), [])
        component.setup_table_headers(
            table=self.table,
            column_count=len(header_list) + 1,
            header_list=header_list,
            table_key=table_key
        )

    def insert_row(self, data_list: list, row_index=None):
        """
        Insert a row with optional row or tree indicator in column 0.

        Args:
            data_list (list): List of cell values (excluding indicator)
            row_index (int): Optional index to insert at (default = append)
        """
        if row_index is None:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
        else:
            self.table.insertRow(row_index)

        # Set sidebar indicator if enabled
        if self.use_row_indicator:
            if self.use_tree_indicator:
                indicator = TreeRowIndicator(parent=self, index=row_index, tree_indicator=self.use_tree_indicator)
                self.table.setCellWidget(row_index, 0, indicator)
                indicator.tree_button_requested.connect(self.parent_module.open_tree)
            else:
                indicator = TreeRowIndicator(parent=self, index=row_index)
                self.table.setCellWidget(row_index, 0, indicator)
            # self.table.setCellWidget(row_index, 0, indicator)
        else:
            # if no indicator, leave it blank
            self.table.setItem(row_index, 0, QTableWidgetItem(""))

        for col_index, value in enumerate(data_list):
            item = QTableWidgetItem(str(value))
            self.table.setItem(row_index, col_index + 1, item)

        self.ensure_row_selection()

    def ensure_row_selection(self):
        if hasattr(self, "table") and self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 1)
