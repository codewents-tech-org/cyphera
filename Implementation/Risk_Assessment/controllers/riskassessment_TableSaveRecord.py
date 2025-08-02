
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
import logging
from controllers.schema_manager import delete_all_instance, bulk_insert_instances
from controllers.tablemodel import SecurityClaims, SecurityGoals, SecurityControls, RiskData
import uuid
logger = logging.getLogger(__name__)

def SecurityClaims_submit_changes(table):
    logger.info("Submitting changes for Security Claims")

    try:
        # 1️⃣ Delete all existing SecurityClaims (soft delete optional if needed)
        delete_all_instance(SecurityClaims, {})

        # 2️⃣ Prepare new entries
        new_instances = []

        for row in range(table.rowCount()):
            values = []

            for col in range(table.columnCount() - 1):  # exclude last column if reserved
                widget = table.cellWidget(row, col + 1)

                if col in [2, 4]:  # Assumptions or TOE configuration
                    if widget:
                        selected = widget.selected_items()
                        ids = [item.split("::")[0] for item in selected]
                        values.append(", ".join(ids))
                    else:
                        values.append("")
                elif col == 3:  # Responsible
                    if widget:
                        selected = widget.selected_items()
                        values.append(", ".join(selected))
                    else:
                        values.append("")
                else:
                    item = table.item(row, col + 1)
                    values.append(item.text() if item else "")

            # 3️⃣ Build SecurityClaims instance
            claim = SecurityClaims(
                id=values[0],
                name=values[1],
                assumption_id=values[2],
                responsible=values[3],
                toe_configuration_id=values[4],
                description=values[5],
                comments=values[6],
                uuid=str(uuid.uuid4()),
                is_deleted=False
            )

            new_instances.append(claim)

        # 4️⃣ Insert all instances via ORM
        bulk_insert_instances(new_instances)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error submitting changes: {e}")
            # item = table.item(row, col+1)
            # if item is not None:
            #     row_data.append(item.text())
            # else:
            #     widget = table.cellWidget(row, col+1)
            #     if widget is not None:
            #         if isinstance(widget, MOS.MultiSelectComboBox):
            #             row_data.append(", ".join(widget.selected_items()))
            #         elif isinstance(widget, MOS.TSMultiSelectComboBox):
            #             row_data.append(", ".join(widget.selected_items()))
            #         else:
            #             row_data.append(widget.selected_items())
    # QMessageBox.information(None,"Success","Data submitted successfully!")

def SecurityGoals_submit_changes(table):
    logger.info("Submitting changes for Security Goals")

    try:
        # 1️⃣ Clear all existing SecurityGoals (soft delete can be used if needed)
        delete_all_instance(SecurityGoals, {})

        new_instances = []

        for row in range(table.rowCount()):
            values = []

            for col in range(table.columnCount() - 1):  # Skipping final UI-only column
                item = table.item(row, col + 1)

                if item is not None:
                    values.append(item.text())
                else:
                    widget = table.cellWidget(row, col + 1)
                    if widget:
                        if hasattr(widget, 'selected_items'):
                            selected = widget.selected_items()
                            if selected and isinstance(selected[0], str) and "::" in selected[0]:
                                # Combo with ID::Name format
                                ids = [x.split("::")[0] for x in selected]
                                values.append(", ".join(ids))
                            else:
                                values.append(", ".join(selected))
                        else:
                            values.append("")
                    else:
                        values.append("")

            # 2️⃣ Construct ORM instance
            goal = SecurityGoals(
                id=values[0],
                name=values[1],
                security_goal_id=values[2],
                control_type=values[3],
                description=values[4],
                comments=values[5],
                uuid=str(uuid.uuid4()),
                is_deleted=False
            )

            new_instances.append(goal)

        # 3️⃣ Insert all records in bulk
        bulk_insert_instances(new_instances)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error submitting Security Goals: {e}")

def SecurityControls_submit_changes(table):

    logger.info("Submitting changes for Security Controls")

    try:
        # 1️⃣ Delete all existing records
        delete_all_instance(SecurityControls, {})

        new_instances = []

        for row in range(table.rowCount()):
            row_data = []

            for col in range(table.columnCount() - 1):  # skip UI-only column if any
                item = table.item(row, col + 1)

                if item is not None:
                    row_data.append(item.text())
                else:
                    widget = table.cellWidget(row, col + 1)
                    if widget and hasattr(widget, 'selected_items'):
                        selected = widget.selected_items()
                        row_data.append(", ".join(selected))
                    else:
                        row_data.append("")

            # 2️⃣ Map to ORM model
            control = SecurityControls(
                id=row_data[0],
                name=row_data[1],
                security_goal_id=row_data[2],
                control_type=row_data[3],
                description=row_data[4],
                uuid=str(uuid.uuid4()),
                is_deleted=False
            )

            new_instances.append(control)

        # 3️⃣ Insert all
        bulk_insert_instances(new_instances)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error submitting Security Controls: {e}")

def risktreatment_submit_changes(table):
    logger.info("Submitting Changes for Risk treatment")

    try:
        # 1️⃣ Clear existing RiskData
        delete_all_instance(RiskData, {})

        new_instances = []

        for row in range(table.rowCount()):
            row_data = []

            for col in range(table.columnCount() - 1):
                widget = table.cellWidget(row, col + 1)

                # TSMultiSelectComboBox with :: separator (columns 8, 10, 11)
                if col in [8, 10, 11]:
                    if widget and hasattr(widget, "selected_items"):
                        selected = widget.selected_items()
                        ids = [s.split("::")[0] for s in selected if "::" in s]
                        row_data.append(", ".join(ids))
                    else:
                        row_data.append("")

                # QComboBox (column 9)
                elif col == 9:
                    row_data.append(widget.currentText() if widget else "")

                # QLineEdit widgets (columns 2, 4–7)
                elif col in [2, 4, 5, 6, 7]:
                    row_data.append(widget.text() if widget else "")

                # Plain text from table
                else:
                    item = table.item(row, col + 1)
                    row_data.append(item.text() if item else "")

            # 2️⃣ Create RiskData ORM instance
            record = RiskData(
                rd_id=row_data[0],
                ds_id=row_data[1],
                impact=row_data[2],
                threat_id=row_data[3],
                init_afr_level=row_data[4],
                init_afr_value=row_data[5],
                resid_afr_level=row_data[6],
                resid_afr_value=row_data[7],
                mitigated_by=row_data[8],
                toe_configuration_id=row_data[9],
                risk_treatment=row_data[10],
                security_claims_id=row_data[11],
                security_goal_id=row_data[12],
                uuid=str(uuid.uuid4())
            )


            new_instances.append(record)

        # 3️⃣ Bulk insert
        bulk_insert_instances(new_instances)

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error submitting Risk Treatment: {e}")
