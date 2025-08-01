"""
Module: Table Component   \n
File: table_component.py     \n
Layer: UI Component Layer     \n
Component ID: CO_010     \n
Requirement IDs: None     \n
Author: Vishnu Viswanath     \n
Created On: 2025-05-14     \n
Version: V 3.0   \n

Purpose:
--------
Provides reusable functions for managing `QTableWidget` behavior, focusing on
configuring column headers and dynamically adjusting column widths based on header content.

Description:
------------
Defines reusable UI components for dynamic property panels, supporting various input types
(QLineEdit, QTextEdit, MultiSelectComboBox) with standardized styling and signal handling.

Responsibilities:
-----------------
- Define default column header mappings for various domains.
- Setup table headers and icons with proper alignment and styling.
- Dynamically adjust column widths using `QFontMetrics` for optimal fit.

Signals
-------
+---------------------+----------------------+-----------------------------+----------------------+
| Trigger             | Signal Origin        | Description                 | Payload Format       |
+=====================+======================+=============================+======================+
| N/A (internal)      | N/A                  | No external signals emitted | N/A                  |
+---------------------+----------------------+-----------------------------+----------------------+


Dependencies:
-------------
- PyQt5 (QtCore, QtWidgets)
- models.helper

Limitations:
------------
- Hardcoded padding values may need tweaking per use case.
- Header mapping assumes pre-defined keys and lists from `helper`.

Improvements:
-------------
- Add support for dynamic header data via config or metadata.
- Abstract font/padding logic for more flexibility.
- Add accessibility hints for screen reader compliance.

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

from PyQt5.QtGui import QFontMetrics ,QColor, QBrush # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem,QStyledItemDelegate  # pylint: disable=no-name-in-module
from PyQt5.QtCore import Qt, QSize 
# pylint: disable=no-name-in-module

from models import helper  # pylint: disable=import-error

logger = logging.getLogger(__name__)


class TableComponent:
    def __init__(self):
        # Configuration values moved here
        self.sidebar_column_width = 70
        self.header_text_padding = 140
        self.header_item_height = 50
        self.header_item_size = QSize(28, 28)

        self._table_column_mappings = {
            'scope': helper.scope_header,
            'asset': helper.asset_header,
            'damage_scenarios': helper.DS_header,
            'threats': helper.threat_header,
            'threat_scenarios': helper.TS_header,
            'securitycontrols': helper.securitycontrols_header,
            'attacktree': helper.attacktree_header,
            'riskcontroltree': helper.RiskControlTree_header,
            'attackleaves': helper.attackleaves_header,
            'technicaltree': helper.technicaltree_header,
            'securityclaims': helper.securityclaims_header,
            'securitygoals': helper.securitygoals_header,
            'risktreatment': helper.risktreatement_header,
            'assumptions': helper.assumptions_header,
            'toe_configuration': helper.toe_configuration_header,
            'misuse_case': helper.misusecases_header
        }


    def auto_adjust_column_width(self, table: QTableWidget, table_key: str):
        """ 
        Adjust the column widths of a QTableWidget based on the header text length.

        Args:
            table (QTableWidget): The table widget whose columns are to be resized.
            table_key (str): A key identifying which header list to use for column resizing.

        Returns:
            None
        """
        try:
            font_metrics = QFontMetrics(table.font())
            col_count = table.columnCount()
            headers = self._table_column_mappings.get(table_key.lower(), [])

            for col in range(col_count):
                if col == 0:
                    table.setColumnWidth(col, self.sidebar_column_width)
                    continue

                header_text = headers[col - 1] if col - 1 < len(headers) else ""
                width = font_metrics.boundingRect(header_text).width() + self.header_text_padding
                table.setColumnWidth(col, width)
        except Exception:  # noqa: E722
            logger.exception("Failed to auto adjust column widths")


    def setup_table_headers(self, table: QTableWidget, column_count: int, header_list: list, table_key: str):
        """ 
        Set up the table headers for a QTableWidget, including sidebar and title columns.

        Args:
            table (QTableWidget): The table widget to configure.
            column_count (int): Total number of columns to be added to the table.
            header_list (list): List of strings to be used as column headers (excluding sidebar).
            table_key (str): A key used to identify the appropriate header mapping.

        Returns:
            None
        """
        try:
            table.setColumnCount(column_count)
            table.verticalHeader().setVisible(False)

            header_item = QTableWidgetItem('')
            header_item.setTextAlignment(Qt.AlignLeft)
            header_item.setSizeHint(self.header_item_size)
            table.setHorizontalHeaderItem(0, header_item)
            table.horizontalHeader().setFirstSectionMovable(False)

            for index, header in enumerate(header_list):
                item = QTableWidgetItem(header)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setSizeHint(self.header_item_size)
                table.setHorizontalHeaderItem(index + 1, item)

            table.horizontalHeader().setFixedHeight(self.header_item_height)
            self.auto_adjust_column_width(table, table_key=table_key)
            table.horizontalHeader().setStretchLastSection(True)
        except Exception:  # noqa: E722
            logger.exception("Failed to setup table headers")
            
