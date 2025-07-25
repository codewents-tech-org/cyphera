"""
Module Name   : riskassessment_TableRefreshRecord.py
Layer         : Presentation / Table UI Refresh
Component ID  : CY_TBL_005
Requirement ID: N/A
Version       : V 3.0
Created By    : Vishnu Viswanath
Created On    : 2025-05-22

Purpose:
--------
Refreshes table records for various risk assessment modules such as Security Claims,
Security Controls, and Risk Treatment. Ensures updated data from the database is
correctly rendered in the UI with appropriate widget bindings.

Description:
------------
This module re-fetches the latest saved records from the SQLite database and injects
them into their respective table widgets. It also handles formatting, widget instantiation
(e.g., combo boxes, line edits), and applies color-coding or restrictions based on
data conditions such as severity levels or attack feasibility.

Responsibilities:
-----------------
- Reload assumptions, responsible parties, TOE configuration, and other linked data
- Create multiselect combo boxes or styled QLineEdit widgets
- Style rows and columns based on predefined thresholds or metadata
- Handle complex relationships between threat scenarios, damage scenarios, and risk controls

Functions:
----------
+-------------------------------+-----------------------------------------------+
| Function                      | Purpose                                       |
+===============================+===============================================+
| SecurityClaims_refresh_data   | Reloads all Security Claims into the table    |
+-------------------------------+-----------------------------------------------+
| SecurityControls_refresh_data | Reloads all Security Controls into the table  |
+-------------------------------+-----------------------------------------------+
| risktreatement_refresh_data   | Rebuilds the Risk Treatment matrix view       |
+-------------------------------+-----------------------------------------------+

Dependencies:
-------------
- PyQt5
- sqlite3
- models.helper (for mappings and risk scales)
- components.table.multioption_selector
- components.table.table_row_indicator
- controllers.DatabaseCreator

Limitations:
------------
- Risk Treatment table structure is highly rigid and hardcoded
- Requires consistent table schema; lacks flexible column detection
- Visual styling is embedded directly in logic

Improvements:
-------------
- Refactor style rules into a separate theme/style manager
- Add exception handling for missing relationship records
- Support plugin-based table configurations

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
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import sqlite3
import sys
import models.Parameters as P
import controllers.DatabaseCreator as DB
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.table_row_indicator as TRI
import models.TableStyle as TS
import Analysis.controllers.analysis_TableValueLoad as TVL
from controllers.schema_manager import get_instances
from controllers.tablemodel import (SecurityClaims, Assumptions, TOEConfiguration, SecurityClaims,SecurityControls, SecurityGoals, DamageScenarios, ThreatScenarios, Threats,
    RiskControlTreeHome, RiskData)


def SecurityClaims_refresh_data(table):
    try:
        # 🔹 Load assumptions
        assumptions_rows = get_instances(Assumptions, {})
        assumptions_list = [
            f"{a.assumption_id}::{a.assumptions}"
            for a in assumptions_rows
            if a.assumption_id and a.assumptions
        ]

        # 🔹 Load TOE configurations
        toe_configuration_rows = get_instances(TOEConfiguration, {})
        toe_configuration_list = [
            f"{t.toe_configuration_id}::{t.toe_configuration_name}"
            for t in toe_configuration_rows
            if t.toe_configuration_id and t.toe_configuration_name
        ]

        # 🔹 Load responsible org/client/supplier
        project_rows = get_instances(SecurityClaims, {})
        responsible_list = []
        for row in project_rows:
            for field in ['organization', 'client', 'supplier']:
                raw = getattr(row, field, None)
                if raw:
                    for val in raw.split(","):
                        val = val.strip()
                        if val and val not in responsible_list:
                            responsible_list.append(val)

        # 🔹 Clear table
        table.setRowCount(0)

        # 🔹 Load SecurityClaims entries
        records = get_instances(SecurityClaims, {'is_deleted': False})
        for row_idx, row in enumerate(records):
            table.insertRow(row_idx)

            # Column 0: Sidebar
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)

            # Column 1: ID (read-only)
            id_item = QTableWidgetItem(row.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 1, id_item)

            # Column 2: Name
            name_item = QTableWidgetItem(row.name or "")
            table.setItem(row_idx, 2, name_item)

            # Column 3: Assumptions (multi-select)
            assumptions_selected = [a.strip() for a in (row.assumption_id or "").split(",") if a.strip()]
            mapped_assumptions = [x for x in assumptions_list if any(f"{a}::" in x for a in assumptions_selected)]
            assumptions_widget = MOS.TSMultiSelectComboBox(assumptions_list)
            assumptions_widget.set_text(mapped_assumptions)
            table.setCellWidget(row_idx, 3, assumptions_widget)

            # Column 4: Responsible (multi-select)
            responsibles_selected = [r.strip() for r in (row.responsible or "").split(",") if r.strip()]
            responsible_widget = MOS.MultiSelectComboBox(responsible_list)
            responsible_widget.set_text(responsibles_selected)
            table.setCellWidget(row_idx, 4, responsible_widget)

            # Column 5: TOE Configuration (multi-select)
            toe_selected = [t.strip() for t in (row.toe_configuration_id or "").split(",") if t.strip()]
            mapped_toe = [x for x in toe_configuration_list if any(f"{t}::" in x for t in toe_selected)]
            toe_widget = MOS.TSMultiSelectComboBox(toe_configuration_list)
            toe_widget.set_text(mapped_toe)
            table.setCellWidget(row_idx, 5, toe_widget)

            # Column 6: Description
            desc_item = QTableWidgetItem(row.description or "")
            table.setItem(row_idx, 6, desc_item)

            # Column 7: Comments
            comments_item = QTableWidgetItem(row.comments or "")
            table.setItem(row_idx, 7, comments_item)

        # Set first row selected
        if table.rowCount() > 0:
            table.setCurrentCell(0, 1)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

def SecurityControls_refresh_data(table):
    try:
        # 🔹 Clear table
        table.setRowCount(0)

        # 🔹 Load SecurityControls records
        records = get_instances(SecurityControls, {'is_deleted': False})

        # 🔹 Load SecurityGoals for combo box options
        securitygoal_rows = get_instances(SecurityGoals, {'is_deleted': False})
        security_property_list = [
            f"{sg.sg_id}::{sg.name}"
            for sg in securitygoal_rows
            if sg.sg_id and sg.name
        ]

        for row_idx, row in enumerate(records):
            table.insertRow(row_idx)

            # Column 0: Sidebar
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)

            # Column 1: ID (read-only)
            id_item = QTableWidgetItem(row.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 1, id_item)

            # Column 2: Name
            table.setItem(row_idx, 2, QTableWidgetItem(row.name or ""))

            # Column 3: Security Goal multi-select
            sg_ids = [s.strip() for s in (row.security_goal_id or "").split(",") if s.strip()]
            matched_sg_values = [x for x in security_property_list if any(f"{sid}::" in x for sid in sg_ids)]

            sg_widget = MOS.TSMultiSelectComboBox(security_property_list)
            sg_widget.set_text(matched_sg_values)
            table.setCellWidget(row_idx, 3, sg_widget)

            # Column 4: Control Type
            table.setItem(row_idx, 4, QTableWidgetItem(row.control_type or ""))

            # Column 5: Description
            table.setItem(row_idx, 5, QTableWidgetItem(row.description or ""))

        # Focus on first row if exists
        if table.rowCount() > 0:
            table.setCurrentCell(0, 1)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

def risktreatement_refresh_data(table):
    try:
        table.setRowCount(0)

        # ORM Fetches
        damage_rows = get_instances(DamageScenarios, {'is_deleted': False})
        threat_rows = get_instances(ThreatScenarios, {'is_deleted': False})
        toe_configuration_rows = get_instances(TOEConfiguration, {'is_deleted': False})
        security_goals = get_instances(SecurityGoals, {'is_deleted': False})
        security_claims = get_instances(SecurityClaims, {'is_deleted': False})
        attacktree_rows = get_instances(Threats, {'is_deleted': False})
        mitigate_rows = get_instances(RiskControlTreeHome, {})
        riskdata_rows = get_instances(RiskData, {})

        # Preprocess for lookups
        toe_configuration_list = [
            f"{t.toe_configuration_id}::{t.toe_configuration_name}"
            for t in toe_configuration_rows
            if t.toe_configuration_id and t.toe_configuration_name
        ]

        attacktree_values = {
            f"{t.threat_id} - {t.name}": (t.initia_afr, t.resid_afr)
            for t in attacktree_rows if t.threat_id and t.name
        }
        attacktree_keys = list(attacktree_values.keys())

        # Mitigation mapping
        mitigate_datas = {}
        for ts in threat_rows:
            threat_id = ts.threat_id
            if not threat_id:
                continue
            matched = []
            for rc in mitigate_rows:
                if not rc.mitigates:
                    continue
                if threat_id in rc.mitigates.split(','):
                    matched.append(rc.rc_id)
            mitigate_datas[threat_id] = ', '.join(matched)

        # Risk ID mapping
        risk_id_dict = {
            (ts.ds_id, ts.threat_id): ts.ts_id for ts in threat_rows
        }

        for dmg in damage_rows:
            ds_id = dmg.ds_id
            impact = dmg.impact
            damage_scenario_value = f"{ds_id} - {dmg.name}"
            related_threats = [ts for ts in threat_rows if ts.ds_id == ds_id]

            for ts in related_threats:
                threat = ts.threat_id
                row_idx = table.rowCount()
                table.insertRow(row_idx)

                # Risk ID
                risk_id = str(risk_id_dict.get((ds_id, threat), "N/A"))
                item = QTableWidgetItem(risk_id)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_idx, 1, item)

                # Damage Scenario
                dmg_item = QTableWidgetItem(damage_scenario_value)
                dmg_item.setFlags(dmg_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_idx, 2, dmg_item)

                # Impact
                impact_item = QLineEdit(impact)
                impact_item.setReadOnly(True)
                impact_item.setAlignment(Qt.AlignCenter)
                table.setCellWidget(row_idx, 3, impact_item)

                if impact == 'Severe':
                    impact_item.setStyleSheet("background-color: #921A40; font-size: 14px;")
                elif impact == 'Major':
                    impact_item.setStyleSheet("background-color: #C75B7A; font-size: 14px;")
                elif impact == 'Moderate':
                    impact_item.setStyleSheet("background-color: #D9ABAB; font-size: 14px;")
                elif impact == 'Negligible':
                    impact_item.setStyleSheet("background-color:#F4D9D0; font-size: 14px;")

                # Threat
                threat_item = QTableWidgetItem(threat)
                threat_item.setFlags(threat_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_idx, 4, threat_item)

                # AFR levels
                Init_AFR = attacktree_values.get(f"{threat} - {next((t.name for t in attacktree_rows if t.threat_id == threat), '')}", ('', ''))[0]
                Init_AFR_item = QLineEdit(Init_AFR)
                Init_AFR_item.setReadOnly(True)
                Init_AFR_item.setAlignment(Qt.AlignCenter)
                table.setCellWidget(row_idx, 5, Init_AFR_item)

                # AFR value
                Init_AFR_value = str(helper.risk_map.get((impact, Init_AFR))) if Init_AFR else ''
                afr_val_item = QLineEdit(Init_AFR_value)
                afr_val_item.setReadOnly(True)
                afr_val_item.setAlignment(Qt.AlignCenter)
                table.setCellWidget(row_idx, 6, afr_val_item)

                # Residual AFR
                Resid_AFR = attacktree_values.get(f"{threat} - {next((t.name for t in attacktree_rows if t.threat_id == threat), '')}", ('', ''))[1]
                Resid_AFR_item = QLineEdit(Resid_AFR)
                Resid_AFR_item.setReadOnly(True)
                Resid_AFR_item.setAlignment(Qt.AlignCenter)
                table.setCellWidget(row_idx, 7, Resid_AFR_item)

                # Residual AFR value
                Resid_AFR_value = str(helper.risk_map.get((impact, Resid_AFR))) if Resid_AFR else ''
                resid_val_item = QLineEdit(Resid_AFR_value)
                resid_val_item.setReadOnly(True)
                resid_val_item.setAlignment(Qt.AlignCenter)
                table.setCellWidget(row_idx, 8, resid_val_item)

                # Mitigation
                mitigation_text = mitigate_datas.get(threat, 'N/A')
                mitigate_item = QLineEdit(mitigation_text)
                mitigate_item.setReadOnly(True)
                mitigate_item.setAlignment(Qt.AlignCenter)
                table.setCellWidget(row_idx, 9, mitigate_item)

                # TOE Configuration dropdown
                toe_value = ts.toe_configuration_id or ""
                toe_combo = QComboBox()
                toe_combo.addItems(toe_configuration_list)
                toe_combo.setCurrentText(toe_value)
                table.setCellWidget(row_idx, 10, toe_combo)

    except Exception as e:
        print(f"An error occurred: {e}")

