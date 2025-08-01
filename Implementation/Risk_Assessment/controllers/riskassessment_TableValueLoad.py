"""
Module Name   : riskassessment_TableValueLoad.py
Layer         : Presentation / Table Data Loader
Component ID  : CY_TBL_004
Requirement ID: N/A
Version       : V 3.0
Created By    : Vishnu Viswanath
Created On    : 2025-05-21

Purpose:
--------
Provides functions to load persisted Security Claims, Security Goals, Security Controls,
and Risk Treatment data into their respective table views in the TARA tool. This allows
users to resume work from previously saved states and view/edit existing entries.

Description:
------------
Each function loads data from the relevant SQLite database tables, dynamically creates the
appropriate row widgets (e.g., editable text fields, multiselect combo boxes), and injects
them into the PyQt5 table UI. Also connects signal slots to track user changes and update
property panels accordingly.

Responsibilities:
-----------------
- Retrieve records from SQLite tables
- Dynamically create table rows with appropriate widgets
- Handle database relationships (e.g., claims → goals)
- Maintain UI consistency (e.g., styling, sizing)
- Gracefully handle missing or malformed data

Functions:
----------
+----------------------------+-----------------------------------------------+
| Function                   | Purpose                                       |
+============================+===============================================+
| load_securityclaims        | Load all saved security claim entries         |
+----------------------------+-----------------------------------------------+
| load_securitygoals         | Load all saved security goal entries          |
+----------------------------+-----------------------------------------------+
| load_securitycontrols      | Load all saved security control entries       |
+----------------------------+-----------------------------------------------+
| load_risktreatement        | Load risk treatment table from RiskData       |
+----------------------------+-----------------------------------------------+

Dependencies:
-------------
- PyQt5
- sqlite3
- helper (header lists, column names)
- DatabaseCreator (database connection abstraction)
- MultiOptionSelector, TableRowIndicator (custom UI components)

Limitations:
------------
- Hardcoded column indices: tightly coupled to table schema
- Lacks exception handling for UI rendering failures
- Manual string parsing for relationships like "claim_id::claim_name"

Improvements:
-------------
- Replace manual widget wiring with a layout-agnostic config
- Centralize dropdown data queries in helper or DB layer
- Implement sorting, filtering, and search within tables

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


from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QHeaderView,
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

from controllers.schema_manager import get_instances,safe_get_instances
from controllers.tablemodel import SecurityClaims, Assumptions, TOEConfiguration, SecurityGoals,SecurityControls, RiskData, ThreatCatalog
import models.helper as helper

import logging
logger = logging.getLogger(__name__)

def load_securityclaims(self, table, property_panel, toggle_button):
    logger.info("Loading Security Claims")
    try:
        table.setColumnCount(8)
        table.verticalHeader().setVisible(False)

        header_item = QTableWidgetItem('')
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28, 28))
        table.setHorizontalHeaderItem(0, header_item)
        table.horizontalHeader().setFirstSectionMovable(False)

        for index, header in enumerate(helper.securityclaims_header):
            header_item = QTableWidgetItem(header)
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28, 28))
            table.setHorizontalHeaderItem(index + 1, header_item)
        table.horizontalHeader().setFixedHeight(50)
        table.horizontalHeader().setStretchLastSection(True)

        helper.adjust_table_column('SecurityClaims', table)

        # ✅ Load reference data via ORM
        assumptions_rows = get_instances(Assumptions, {})
        assumptions_list = [
            f"{a.assumption_id}::{a.assumptions}"
            for a in assumptions_rows if a.assumption_id and a.assumptions
        ]

        toe_rows = get_instances(TOEConfiguration, {})
        toe_configuration_list = [
            f"{t.toe_configuration_id}::{t.toe_configuration_name}"
            for t in toe_rows if t.toe_configuration_id and t.toe_configuration_name
        ]

        project_rows = get_instances(SecurityClaims, {})
        responsible_list = []
        for row in project_rows:
            for field in ['organization', 'client', 'supplier']:
                val = getattr(row, field, "")
                if val:
                    for entry in val.split(","):
                        entry = entry.strip()
                        if entry and entry not in responsible_list:
                            responsible_list.append(entry)

        # ✅ Load SecurityClaims entries
        table.setRowCount(0)
        rows = get_instances(SecurityClaims, {'is_deleted': False})

        if not rows:
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
            return

        for row_idx, row_data in enumerate(rows):
            table.insertRow(row_idx)
            table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row_data.id)

            # Column 0: Sidebar
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)

            # Column 1: ID (read-only)
            id_item = QTableWidgetItem(row_data.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 1, id_item)

            # Column 2: Name
            name_item = QTableWidgetItem(row_data.name or "")
            table.setItem(row_idx, 2, name_item)

            # Column 3: Assumptions (multi-select)
            assumption_ids = [a.strip() for a in (row_data.assumption_id or "").split(",")]
            mapped_assumptions = [x for x in assumptions_list if any(f"{aid}::" in x for aid in assumption_ids)]
            assum_widget = MOS.TSMultiSelectComboBox(assumptions_list)
            assum_widget.set_text(mapped_assumptions)
            assum_widget.currentTextChanged.connect(self.set_unsaved_changes)
            table.setCellWidget(row_idx, 3, assum_widget)

            # Column 4: Responsible (multi-select)
            responsibles = [r.strip() for r in (row_data.responsible or "").split(",")]
            resp_widget = MOS.MultiSelectComboBox(responsible_list)
            resp_widget.set_text(responsibles)
            resp_widget.currentTextChanged.connect(self.set_unsaved_changes)
            table.setCellWidget(row_idx, 4, resp_widget)

            # Column 5: TOE Configurations (multi-select)
            toe_ids = [t.strip() for t in (row_data.toe_configuration_id or "").split(",")]
            mapped_toes = [x for x in toe_configuration_list if any(f"{tid}::" in x for tid in toe_ids)]
            toe_widget = MOS.TSMultiSelectComboBox(toe_configuration_list)
            toe_widget.set_text(mapped_toes)
            toe_widget.currentTextChanged.connect(self.set_unsaved_changes)
            table.setCellWidget(row_idx, 5, toe_widget)

            # Column 6: Description
            desc_item = QTableWidgetItem(row_data.description or "")
            table.setItem(row_idx, 6, desc_item)

            # Column 7: Comments
            comments_item = QTableWidgetItem(row_data.comments or "")
            table.setItem(row_idx, 7, comments_item)

        if table.rowCount() > 0:
            table.setCurrentCell(0, 1)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

def load_securitygoals(self, table, property_panel, toggle_button):
    logger.info("Loading Security Goals")
    try:
        table.setColumnCount(7)
        table.verticalHeader().setVisible(False)

        header_item = QTableWidgetItem('')
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28, 28))
        table.setHorizontalHeaderItem(0, header_item)
        table.horizontalHeader().setFirstSectionMovable(False)

        for index, header in enumerate(helper.securitygoals_header):
            header_item = QTableWidgetItem(header)
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28, 28))
            table.setHorizontalHeaderItem(index + 1, header_item)
        table.horizontalHeader().setFixedHeight(50)

        helper.adjust_table_column('SecurityClaims', table)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        table.horizontalHeader().setStretchLastSection(True)

        # ✅ Load TOE configurations
        toe_rows = get_instances(TOEConfiguration, {})
        toe_configuration_list = [
            f"{t.toe_configuration_id}::{t.toe_configuration_name}"
            for t in toe_rows if t.toe_configuration_id and t.toe_configuration_name
        ]

        # ✅ Load organization/client/supplier
        project_rows = get_instances(SecurityClaims, {})
        responsible_list = []
        for row in project_rows:
            for field in ['organization', 'client', 'supplier']:
                raw = getattr(row, field, "")
                if raw:
                    for entry in raw.split(","):
                        entry = entry.strip()
                        if entry and entry not in responsible_list:
                            responsible_list.append(entry)

        # ✅ Load SecurityGoals records
        table.setRowCount(0)
        rows = get_instances(SecurityGoals, {'is_deleted': False})

        if not rows:
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
            return

        for row_idx, row in enumerate(rows):
            table.insertRow(row_idx)
            table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row.id)

            # Column 0: Sidebar
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)

            # Column 1: ID (read-only)
            id_item = QTableWidgetItem(row.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 1, id_item)

            # Column 2: Name
            table.setItem(row_idx, 2, QTableWidgetItem(row.name or ""))

            # Column 3: Responsible
            responsible_vals = [v.strip() for v in (row.security_goal_id or "").split(",") if v.strip()]
            responsible_widget = MOS.TSMultiSelectComboBox(responsible_list)
            responsible_widget.set_text(responsible_vals)
            responsible_widget.currentTextChanged.connect(self.set_unsaved_changes)
            table.setCellWidget(row_idx, 3, responsible_widget)

            # Column 4: TOE Configuration
            toe_ids = [t.strip() for t in (row.control_type or "").split(",") if t.strip()]
            matched_toes = [x for x in toe_configuration_list if any(f"{t}::" in x for t in toe_ids)]
            toe_widget = MOS.TSMultiSelectComboBox(toe_configuration_list)
            toe_widget.set_text(matched_toes)
            toe_widget.currentTextChanged.connect(self.set_unsaved_changes)
            table.setCellWidget(row_idx, 4, toe_widget)

            # Column 5: Description
            table.setItem(row_idx, 5, QTableWidgetItem(row.description or ""))

            # Column 6: Comments
            table.setItem(row_idx, 6, QTableWidgetItem(row.comments or ""))

        if table.rowCount() > 0:
            table.setCurrentCell(0, 1)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

def load_securitycontrols(self, table, property_panel, toggle_button):
    logger.info("Loading Security Controls")
    try:
        table.setColumnCount(6)
        table.verticalHeader().setVisible(False)

        header_item = QTableWidgetItem('')
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28, 28))
        table.setHorizontalHeaderItem(0, header_item)
        table.horizontalHeader().setFirstSectionMovable(False)

        for index, header in enumerate(helper.securitycontrols_header):
            header_item = QTableWidgetItem(header)
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28, 28))
            table.setHorizontalHeaderItem(index + 1, header_item)
        table.horizontalHeader().setFixedHeight(50)

        helper.adjust_table_column('SecurityClaims', table)
        table.horizontalHeader().setStretchLastSection(True)

        # ORM Fetches
        rows = get_instances(SecurityControls, {'is_deleted': False})
        securitygoal_rows = get_instances(SecurityGoals, {'is_deleted': False})
        # -------- Change: Get mitigations directly from ThreatCatalog
        catalog_rows = get_instances(ThreatCatalog, {})
        threat_controls = {
            getattr(row, 'mitigation_checkbox').strip()
            for row in catalog_rows
            if getattr(row, 'mitigation_checkbox', None)
        }

        # Convert goals to display format
        security_property_list = [
            f"{sg.sg_id}::{sg.name}"
            for sg in securitygoal_rows if sg.sg_id and sg.name
        ]

        # If no data found
        if not rows:
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
            return

        # Populate the table
        table.setRowCount(0)
        for row_idx, row in enumerate(rows):
            table.insertRow(row_idx)
            table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row.id)

            # Column 0: Sidebar
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)

            # Column 1: ID
            id_item = QTableWidgetItem(row.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 1, id_item)

            # Column 2: Name (editable unless referenced in ThreatCatalog)
            name_item = QTableWidgetItem(row.name or "")
            # --- Now: If the control's name is present as a mitigation in ThreatCatalog, make it readonly
            if row.name in threat_controls:
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 2, name_item)

            # Column 3: Security Goal multi-select
            sg_widget = MOS.TSMultiSelectComboBox(security_property_list)
            selected_goals = [g.strip() for g in (row.security_goal_id or "").split(",") if g.strip()]
            matched_sgs = [x for x in security_property_list if any(f"{g}::" in x for g in selected_goals)]
            sg_widget.set_text(matched_sgs)
            sg_widget.currentTextChanged.connect(self.set_unsaved_changes)
            table.setCellWidget(row_idx, 3, sg_widget)

            # Column 4: Control Type
            control_type_item = QTableWidgetItem(row.control_type or "")
            table.setItem(row_idx, 4, control_type_item)

            # Column 5: Description
            desc_item = QTableWidgetItem(row.description or "")
            table.setItem(row_idx, 5, desc_item)

        if table.rowCount() > 0:
            table.setCurrentCell(0, 1)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")


def load_risktreatement(self, table, property_panel, toggle_button):
    logger.info("Loading Risk Treatment Data")
    try:
        table.setColumnCount(14)
        table.verticalHeader().setVisible(False)

        header_item = QTableWidgetItem('')
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28, 28))
        table.setHorizontalHeaderItem(0, header_item)

        for index, header in enumerate(helper.risktreatement_header):
            header_item = QTableWidgetItem(header)
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28, 28))
            table.setHorizontalHeaderItem(index + 1, header_item)
        table.horizontalHeader().setFixedHeight(50)

        helper.adjust_table_column('RiskTreatment', table)
        table.horizontalHeader().setStretchLastSection(True)

        # ORM Fetches
        risk_data_rows = safe_get_instances(RiskData, {'is_deleted': False})
        security_claims = get_instances(SecurityClaims, {'is_deleted': False})
        security_goals = get_instances(SecurityGoals, {'is_deleted': False})
        toe_configuration = get_instances(TOEConfiguration, {'is_deleted': False})

        if not risk_data_rows:
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
            return

        SC_list = [f"{sc.id}::{sc.name}" for sc in security_claims if sc.id and sc.name]
        SG_list = [f"{sg.id}::{sg.name}" for sg in security_goals if sg.id and sg.name]
        TOEC_list = [f"{t.toe_configuration_id}::{t.toe_configuration_name}" for t in toe_configuration if t.toe_configuration_id and t.toe_configuration_name]

        table.setRowCount(0)

        for row_idx, row in enumerate(risk_data_rows):
            table.insertRow(row_idx)
            table.setRowHeight(row_idx, 40)

            # ID
            id_item = QTableWidgetItem(row.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 1, id_item)

            # Damage Scenario
            damage_item = QTableWidgetItem(row.damage or "")
            damage_item.setFlags(damage_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 2, damage_item)

            # Impact
            impact = QLineEdit(row.impact or "")
            impact.setReadOnly(True)
            impact.setAlignment(Qt.AlignCenter)
            table.setCellWidget(row_idx, 3, impact)

            # Color styling
            impact_colors = {
                'Severe': "#921A40",
                'Major': "#C75B7A",
                'Moderate': "#D9ABAB",
                'Negligible': "#F4D9D0"
            }
            if row.impact in impact_colors:
                impact.setStyleSheet(f"background-color: {impact_colors[row.impact]}; font-size: 14px;")

            # Threat
            threat_item = QTableWidgetItem(row.threat or "")
            threat_item.setFlags(threat_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 4, threat_item)

            # Init AFR Level
            init_afr = QLineEdit(row.initial_afr or "")
            init_afr.setReadOnly(True)
            init_afr.setAlignment(Qt.AlignCenter)
            table.setCellWidget(row_idx, 5, init_afr)

            afr_colors = {
                'High': "#0097b2",
                'Medium': "#0cc0df",
                'Low': "#5ce1e6",
                'Very Low': "#cefdff"
            }
            if row.initial_afr in afr_colors:
                init_afr.setStyleSheet(f"background-color: {afr_colors[row.initial_afr]}; font-size: 14px;")

            # Init AFR Value
            afr_val = QLineEdit(str(row.afr_val or ""))
            afr_val.setReadOnly(True)
            afr_val.setAlignment(Qt.AlignCenter)
            table.setCellWidget(row_idx, 6, afr_val)

            afr_val_colors = {
                '5': "#a80000",
                '4': "#ff3131",
                '3': "#ff914d",
                '2': "#ffde59",
                '1': "#7ed957"
            }
            if str(row.afr_val) in afr_val_colors:
                afr_val.setStyleSheet(f"background-color: {afr_val_colors[str(row.afr_val)]}; font-size: 14px;")

            # Resid AFR Level
            resid_afr = QLineEdit(row.residual_afr or "")
            resid_afr.setReadOnly(True)
            resid_afr.setAlignment(Qt.AlignCenter)
            table.setCellWidget(row_idx, 7, resid_afr)
            if row.residual_afr in afr_colors:
                resid_afr.setStyleSheet(f"background-color: {afr_colors[row.residual_afr]}; font-size: 14px;")

            # Resid AFR Value
            resid_val = QLineEdit(str(row.residual_afr_val or ""))
            resid_val.setReadOnly(True)
            resid_val.setAlignment(Qt.AlignCenter)
            table.setCellWidget(row_idx, 8, resid_val)
            if str(row.residual_afr_val) in afr_val_colors:
                resid_val.setStyleSheet(f"background-color: {afr_val_colors[str(row.residual_afr_val)]}; font-size: 14px;")

            # TOE Configuration
            toe_combo = MOS.ReadOnlyMultiSelectComboBox(TOEC_list)
            toe_ids = [id.strip() for id in (row.toe_configuration or "").split(",")]
            selected_toe = [x for x in TOEC_list if any(f"{tid}::" in x for tid in toe_ids)]
            toe_combo.set_text(selected_toe)
            table.setCellWidget(row_idx, 9, toe_combo)

            # Risk Treatment
            rt_combo = MOS.MultiSelectComboBox(helper.risktreatement)
            rt_combo.set_text(row.risk_treatment or "")
            rt_combo.currentTextChanged.connect(self.set_unsaved_changes)
            table.setCellWidget(row_idx, 10, rt_combo)

            # Security Claims
            sc_combo = MOS.TSMultiSelectComboBox(SC_list)
            sc_ids = [id.strip() for id in (row.security_claims or "").split(",")]
            selected_sc = [x for x in SC_list if any(f"{sid}::" in x for sid in sc_ids)]
            sc_combo.set_text(selected_sc)
            sc_combo.currentTextChanged.connect(self.set_unsaved_changes)
            table.setCellWidget(row_idx, 11, sc_combo)

            # Security Goals
            sg_combo = MOS.TSMultiSelectComboBox(SG_list)
            sg_ids = [id.strip() for id in (row.security_goals or "").split(",")]
            selected_sg = [x for x in SG_list if any(f"{sid}::" in x for sid in sg_ids)]
            sg_combo.set_text(selected_sg)
            sg_combo.currentTextChanged.connect(self.set_unsaved_changes)
            table.setCellWidget(row_idx, 12, sg_combo)

            # Mitigated By
            mitigated_by_item = QTableWidgetItem(row.mitigated_by or "")
            mitigated_by_item.setFlags(mitigated_by_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 13, mitigated_by_item)

            # Sidebar
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)

        if table.rowCount() > 0:
            table.setCurrentCell(0, 1)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")




