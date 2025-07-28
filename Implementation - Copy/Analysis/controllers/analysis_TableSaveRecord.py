
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
from controllers.schema_manager import create_instance, get_first_instance, update_instance
import models.Parameters as P
import controllers.DatabaseCreator as DB
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.table_row_indicator as TRI
import Analysis.models.analysis_synchronization as AS
import Target_Of_Evaluation.Scope.controllers.scope_synchronizations as TSS
from controllers.database_tables.analysis_tables import Threats
import logging
logger = logging.getLogger(__name__)
def asset_submit_changes(table):
    logger.info("Submitting changes for Assets")
    DB.execute_db("DELETE FROM assets")
    for row in range(table.rowCount()):
        row_data = []
        for col in range(table.columnCount()):
            item = table.item(row, col+1)
            if item is not None:
                row_data.append(item.text())
            else:
                widget = table.cellWidget(row, col+1)
                if widget is not None:
                    if isinstance(widget, MOS.MultiSelectComboBox):
                        row_data.append(", ".join(widget.selected_items()))
                    else:
                        row_data.append(widget.selected_items())
        DB.update_db("INSERT INTO assets VALUES (?, ?, ?, ?, ?)", tuple(row_data))
    # QMessageBox.information(None,"Success","Data submitted successfully!")
    
    AS.sync_threats_with_assets()
    AS.update_threatscenario_from_threat()
    AS.update_risktreatement_data()
    AS.remove_orphaned_attack_tree_rows()
    AS.update_attack_tree_text()
    AS.sync_attack_tree_with_threats()
    AS.remove_nonexistent_threat_scenarios_from_Risk_data()
    TSS.update_scope_threats()

def DS_submit_changes(table):
    logger.info("Submitting changes for Damage Scenarios")
    try:
        DB.execute_db("DELETE FROM damage_scenarios WHERE ds_id IN (SELECT ds_id FROM trash)")
        DB.conn.commit()
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col+1)
                if item is not None:
                    row_data.append(item.text())
                else:
                    widget = table.cellWidget(row, col+1)
                    if widget is not None:
                        if isinstance(widget, QComboBox):
                            row_data.append(widget.currentText())
                        else:
                            row_data.append("")
            print(row_data)
            if len(row_data) == 6:
                DB.cursor.execute(f"REPLACE INTO damage_scenarios VALUES (?, ?, ?, ?, ?, ?)", row_data)
        DB.conn.commit()
        # QMessageBox.information(None,"Success","Data submitted successfully!")
        
        AS.update_threat_TS_from_DS()
        AS.update_risktreatement_data()

    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error submitting data: {e}")

def threat_submit_changes(table):
    logger.info("Submitting changes for Threats (SQLAlchemy/ORM)")
    try:
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount() - 1):
                if col in [2, 3, 4]:  # MultiSelectComboBox columns
                    combo_box = table.cellWidget(row, col + 1)
                    if combo_box is not None:
                        selected_items = combo_box.selected_items()
                        new_selected_items = [data.split('::')[0] for data in selected_items]
                        row_data.append(", ".join(new_selected_items))
                    else:
                        row_data.append("")
                elif col in [5, 6]:
                    widget = table.cellWidget(row, col + 1)
                    if isinstance(widget, QLineEdit) and widget is not None:
                        row_data.append(widget.text())
                    else:
                        item = table.item(row, col + 1)
                        row_data.append(item.text() if item else "")
                else:
                    item = table.item(row, col + 1)
                    row_data.append(item.text() if item else "")

            # Logging and unpacking
            print("Row Data:", row_data)
            if len(row_data) == 11:
                (
                    id, name, damage_scenarios, toe_configuration, misuse_cases,
                    InitialAFR, ResidAFR, asset, security_properties, reasoning, comments
                ) = row_data

                # ORM-style upsert logic
                filters = {"threat_id": id}
                existing_threat = get_first_instance(Threats, filters=filters)

                if existing_threat:
                    # Update the threat
                    update_data = {
                        "name": name,
                        "damage_scenarios": damage_scenarios,
                        "toe_configuration": toe_configuration,
                        "misuse_cases": misuse_cases,
                        "InitialAFR": InitialAFR,
                        "ResidAFR": ResidAFR,
                        "asset": asset,
                        "security_properties": security_properties,
                        "reasoning": reasoning,
                        "comments": comments,
                    }
                    update_instance(Threats, {"threat_id": id}, update_data)
                else:
                    # Insert new threat
                    threat_instance = Threats(
                        threat_id=id,
                        name=name,
                        damage_scenarios=damage_scenarios,
                        toe_configuration=toe_configuration,
                        misuse_cases=misuse_cases,
                        InitialAFR=InitialAFR,
                        ResidAFR=ResidAFR,
                        asset=asset,
                        security_properties=security_properties,
                        reasoning=reasoning,
                        comments=comments,
                    )
                    create_instance(threat_instance)

                # Insert/Update threat_trash (simple upsert: always create, ignore if exists)
                # trash_instance = ThreatTrash(threat_id=id)
                # create_instance(trash_instance)

        # Run downstream sync logic
        AS.update_threatscenario_from_threat()
        AS.remove_threats_from_mitigation()
        AS.sync_attack_tree_with_threats()
        AS.update_risktreatement_data()
        AS.remove_nonexistent_threat_scenarios_from_Risk_data()

        # Optional: success message, or handle via logger/UI
        # QMessageBox.information(None, "Success", "Data submitted successfully.")

    except Exception as e:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Database Error", f"Error submitting data: {e}")
        logger.error(f"Error submitting threat data: {e}")


def TS_submit_changes(table):
    logger.info("Submitting changes for Threat Scenarios")
    try:
        rows = DB.execute_db("SELECT ts_id FROM threat_scenarios")
        existing_ids = {row[0] for row in rows}
        table_ids = set()
        row_count = table.rowCount()
        for row_idx in range(row_count):
            threat_id = table.item(row_idx, 1).text()
            table_ids.add(threat_id)

            threat_text = table.item(row_idx, 2).text()
            damage_scenario_text = table.item(row_idx, 3).text()
            toe_configuration_text = ""
            toe_configuration_combo = table.cellWidget(row_idx, 4)  # Assuming this is a custom multi-select combo box
            if toe_configuration_combo is not None:
                selected_toe_configurations = toe_configuration_combo.selected_items()  # Assuming `selected_items()` returns a list of selected items
                toe_configuration_text = ", ".join(selected_toe_configurations)  # Convert list to comma-separated string
            else:
                toe_configuration_text = ""
            reasoning = table.item(row_idx, 5).text() if table.item(row_idx, 5) else ""
            comment = table.item(row_idx, 6).text() if table.item(row_idx, 6) else ""

            # Extract ID from the damage_scenario_text
            # damage_scenario_id = damage_scenario_text.split(' - ')[0]

            # Insert or update data in the threat table
            DB.update_db("""
                INSERT OR REPLACE INTO threat_scenarios (ts_id, threat, damage_scenarios, toe_configuration, reasoning, comments)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (threat_id, threat_text, damage_scenario_text, toe_configuration_text, reasoning, comment))
            
            DB.update_db("INSERT INTO ts_trash (ts_id) VALUES (?)", (threat_id,))

        # Delete entries from the database that are not in the QTableWidget
        ids_to_delete = existing_ids - table_ids
        for threat_id in ids_to_delete:
            DB.update_db("DELETE FROM threat_scenarios WHERE ts_id = ?", (threat_id,))

        DB.conn.commit()
        # QMessageBox.information(None, "Success", "Data has been successfully submitted.")
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error submitting data: {e}")




