"""
Module Name   : riskassessment_TableAddRecord.py
Layer         : Presentation / Table UI Action
Component ID  : CY_TBL_003
Requirement ID: N/A
Version       : V 3.0
Created By    : Vishnu Viswanath
Created On    : 2025-05-20

Purpose:
--------
Defines functions to handle the creation of new entries for Security Claims, Security Goals,
and Security Controls in their respective tables in the TARA tool.

Description:
------------
This module adds structured rows to the UI table widgets for Security Claims, Security Goals,
and Security Controls. Each function dynamically generates table content with prefilled values,
fetches related options (e.g., Responsible, Assumptions, TOE Config) from the database,
and applies appropriate styling and signal connections.

Responsibilities:
-----------------
- Generate unique IDs for each new record
- Create and insert a new table row with editable and non-editable fields
- Fetch dynamic combo box options from the SQLite database
- Attach sidebars and placeholder widgets
- Perform duplicate detection and text tracking

Functions:
----------
+-------------------------------+-----------------------------------------------+
| Function                      | Purpose                                       |
+===============================+===============================================+
| SecurityClaims_add_new_entry | Adds a new row for a Security Claim           |
+-------------------------------+-----------------------------------------------+
| SecurityGoals_add_new_entry  | Adds a new row for a Security Goal            |
+-------------------------------+-----------------------------------------------+
| SecurityControls_add_new_entry | Adds a new row for a Security Control       |
+-------------------------------+-----------------------------------------------+

Dependencies:
-------------
- PyQt5 (widgets, core, GUI)
- components.table.multioption_selector (for combo boxes)
- components.table.table_row_indicator (for sidebar widget)
- models.helper (ID generation and duplication check)
- controllers.DatabaseCreator (DB connection handler)

Limitations:
------------
- Column indexes are hardcoded; changes to table structure require code update
- No inline validation of combo box selections or empty fields

Improvements:
-------------
- Introduce layout-aware field mapping to reduce index dependency
- Abstract database queries into a utility for better reuse and testing
- Enable undo/redo support for table row additions

Change History:
---------------
+---------+------------+--------------------------------------------------------+----------------------+
| Version | Date       | Change                                                 | Author               |
+=========+============+========================================================+======================+
| V 3.0   | 2025-06-04 | Dynamic Responsible field loading from project_info    | Vishnu Viswanath     |
+---------+------------+--------------------------------------------------------+----------------------+
|         |            |                                                        |                      |
+---------+------------+--------------------------------------------------------+----------------------+
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QApplication, QPushButton, QStyledItemDelegate,
                             QMessageBox, QToolBar, QMainWindow, QLineEdit, QLabel, QComboBox,
                             QToolTip, QGridLayout, QFileDialog, QFrame, QStackedWidget, QButtonGroup, 
                             QSpacerItem, QSizePolicy, QTextEdit, QAction, QMenu, QToolButton, QStyle
                             )
from PyQt5.QtGui import QIcon, QPainter, QCursor, QFont, QColor, QBrush
from PyQt5.QtCore import QTimer, Qt, QSize, QRect, QRectF
import sqlite3
import sys
import models.Parameters as P
import controllers.DatabaseCreator as DB
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.table_row_indicator as TRI
from controllers.schema_manager import get_instances
from controllers.tablemodel import Assumptions, TOEConfiguration, SecurityClaims, SecurityGoals
import models.helper as helper

import logging
logger = logging.getLogger(__name__)

def SecurityClaims_add_new_entry(table, self):
    logger.info("Added new entry in Security Claims")

    row_idx = table.rowCount()
    table.insertRow(row_idx)
    table.setRowHeight(row_idx, 40)

    # 🔹 Generate SC ID
    sc_id = helper.securityclaims_generate_id(table)
    id_item = QTableWidgetItem(sc_id)
    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
    table.setItem(row_idx, 1, id_item)

    # 🔹 Load assumptions from ORM
    assumptions_rows = get_instances(Assumptions, {})
    assumptions_list = [
        f"{a.assumption_id}::{a.assumptions}"
        for a in assumptions_rows
        if a.assumption_id and a.assumptions
    ]

    # 🔹 Load TOE configuration from ORM
    toe_configuration_rows = get_instances(TOEConfiguration, {})
    toe_configuration_list = [
        f"{t.toe_configuration_id}::{t.toe_configuration_name}"
        for t in toe_configuration_rows
        if t.toe_configuration_id and t.toe_configuration_name
    ]

    # 🔹 Load responsible parties from ORM
    responsible_list = []
    try:
        project_rows = get_instances(SecurityClaims, {})
        for row in project_rows:
            for field in ['organization', 'client', 'supplier']:
                raw = getattr(row, field, None)
                if raw:
                    for value in raw.split(","):
                        value = value.strip()
                        if value and value not in responsible_list:
                            responsible_list.append(value)
    except Exception as e:
        logger.warning(f"Could not load SecurityClaims entries: {e}")
        responsible_list = ["DefaultORG", "Customer", "Supplier"]

    # 🔹 Sidebar cell
    sidebar = TRI.SidebarWidget()
    table.setCellWidget(row_idx, 0, sidebar)

    # 🔹 Auto-fill name
    sc_name = f"Secruity Claim {sc_id.split('-')[-1]}"
    name_item = QTableWidgetItem(sc_name)
    table.setItem(row_idx, 2, name_item)
    table.setCurrentCell(row_idx, 2)

    self.find_duplicates(name_item)
    self.previous_text = name_item.text()
    self.existing_entries.add(name_item.text())

    # 🔹 Assumptions combo
    assum_widget = MOS.TSMultiSelectComboBox(assumptions_list)
    assum_widget.set_text("")
    table.setCellWidget(row_idx, 3, assum_widget)

    # 🔹 Responsible combo
    resp_widget = MOS.TSMultiSelectComboBox(responsible_list)
    resp_widget.set_text("")
    table.setCellWidget(row_idx, 4, resp_widget)

    # 🔹 TOE Configuration combo
    toe_widget = MOS.TSMultiSelectComboBox(toe_configuration_list)
    toe_widget.set_text("")
    table.setCellWidget(row_idx, 5, toe_widget)

    # 🔹 Description and Comments
    table.setItem(row_idx, 6, QTableWidgetItem(""))
    table.setItem(row_idx, 7, QTableWidgetItem(""))

    # Finalize focus
    table.setCurrentCell(row_idx, 1)

    return sc_id, sc_name

def SecurityGoals_add_new_entry(table, self):
    logger.info("Added new entry in Security Goals")

    row_idx = table.rowCount()
    table.insertRow(row_idx)
    table.setRowHeight(row_idx, 40)

    # 🔹 Generate SG ID
    sg_id = helper.securitygoals_generate_id(table)
    id_item = QTableWidgetItem(sg_id)
    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
    table.setItem(row_idx, 1, id_item)

    # 🔹 Load TOE configuration from ORM
    toe_configuration_list = []
    try:
        toe_configuration_rows = get_instances(TOEConfiguration, {})
        toe_configuration_list = [
            f"{t.toe_configuration_id}::{t.toe_configuration_name}"
            for t in toe_configuration_rows
            if t.toe_configuration_id and t.toe_configuration_name
        ]
    except Exception as e:
        logger.warning(f"Error loading TOE Configuration: {e}")

    # 🔹 Load responsible parties from ORM
    responsible_list = []
    try:
        project_rows = get_instances(SecurityClaims, {})
        for row in project_rows:
            for field in ['organization', 'client', 'supplier']:
                raw = getattr(row, field, None)
                if raw:
                    for value in raw.split(","):
                        value = value.strip()
                        if value and value not in responsible_list:
                            responsible_list.append(value)
    except Exception as e:
        logger.warning(f"Could not load SecurityClaims entries: {e}")
        responsible_list = ["DefaultORG", "Customer", "Supplier"]

    # 🔹 Sidebar
    sidebar = TRI.SidebarWidget()
    table.setCellWidget(row_idx, 0, sidebar)

    # 🔹 Generate default name
    sg_name = f"Secruity Goal {sg_id.split('-')[-1]}"

    # 🔁 Populate columns
    for col_idx in range(2, table.columnCount()):
        if col_idx == 2:
            item = QTableWidgetItem(sg_name)
            table.setItem(row_idx, 2, item)
            table.setCurrentCell(row_idx, 2)
            self.find_duplicates(item)
            self.previous_text = item.text()
            self.existing_entries.add(item.text())
        elif col_idx == 3:
            widget = MOS.TSMultiSelectComboBox(responsible_list)
            widget.set_text('')
            table.setCellWidget(row_idx, col_idx, widget)
        elif col_idx == 4:
            widget = MOS.TSMultiSelectComboBox(toe_configuration_list)
            widget.set_text('')
            table.setCellWidget(row_idx, col_idx, widget)
        else:
            item = QTableWidgetItem("")
            table.setItem(row_idx, col_idx, item)

    table.setCurrentCell(row_idx, 1)

    return sg_id, sg_name

def SecurityControls_add_new_entry(table, self):
    logger.info("Added New entry in Security Controls")

    # ✅ Load security goals via ORM
    security_property_list = []
    try:
        securitygoal_rows = get_instances(SecurityGoals, {'is_deleted': False})
        security_property_list = [
            f"{sg.sg_id}::{sg.name}"
            for sg in securitygoal_rows
            if sg.sg_id and sg.name
        ]
    except Exception as e:
        logger.warning(f"Could not load SecurityGoals: {e}")

    # ✅ Create a new row in the table
    row_idx = table.rowCount()
    table.insertRow(row_idx)
    table.setRowHeight(row_idx, 40)

    security_ctrl_id = helper.securitycontrols_generate_id(table)
    id_item = QTableWidgetItem(security_ctrl_id)
    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
    table.setItem(row_idx, 1, id_item)

    sidebar = TRI.SidebarWidget()
    table.setCellWidget(row_idx, 0, sidebar)

    security_ctrl_name = f"Secruity Control {security_ctrl_id.split('-')[-1]}"

    # ✅ Populate table cells
    for col_idx in range(2, table.columnCount()):
        if col_idx == 2:
            item = QTableWidgetItem(security_ctrl_name)
            table.setItem(row_idx, 2, item)
            table.setCurrentCell(row_idx, 2)
            self.find_duplicates(item)
            self.previous_text = item.text()
            self.existing_entries.add(item.text())

        elif col_idx == 3:
            widget = MOS.TSMultiSelectComboBox(security_property_list)
            widget.set_text('')
            table.setCellWidget(row_idx, col_idx, widget)
        else:
            item = QTableWidgetItem("")
            table.setItem(row_idx, col_idx, item)

    table.setCurrentCell(row_idx, 1)

    return security_ctrl_id, security_ctrl_name


