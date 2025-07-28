
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
import Analysis.models.analysis_synchronization as AS
from controllers.schema_manager import update_instance
from controllers.tablemodel import SecurityClaims, SecurityGoals,SecurityControls

import logging
logger = logging.getLogger(__name__)

def SecurityClaims_delete_entry(table):
    logger.info("Deleted entry in Security Claims")
    try:
        reply = QMessageBox.warning(
            None,
            "Warning",
            "Delete selected row.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Ok
        )
        if reply != QMessageBox.Ok:
            return

        selected_row = table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(None, "Warning", "Please select a row to delete.")
            return

        id_item = table.item(selected_row, 1)
        if not id_item:
            QMessageBox.warning(None, "Warning", "ID not found in selected row.")
            return

        sc_id = id_item.text()

        # 🔁 Soft-delete the record using schema_manager
        success = update_instance(
            model=SecurityClaims,
            filter_by={'id': sc_id},
            update_data={'is_deleted': True}
        )

        if success:
            table.removeRow(selected_row)
            row_count = table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                table.selectRow(next_row)
        else:
            QMessageBox.warning(None, "Warning", f"Could not delete Security Claim ID: {sc_id}")

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")

def SecurityGoals_delete_entry(table):
    logger.info("Deleted entry in Security Goals")
    try:
        reply = QMessageBox.warning(
            None,
            "Warning",
            "Delete selected row.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Ok
        )
        if reply != QMessageBox.Ok:
            return

        selected_row = table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(None, "Warning", "Please select a row to delete.")
            return

        id_item = table.item(selected_row, 1)
        if not id_item:
            QMessageBox.warning(None, "Warning", "No ID found in selected row.")
            return

        sg_id = id_item.text()

        # 🔁 Perform soft delete via ORM
        success = update_instance(
            model=SecurityGoals,
            filter_by={'id': sg_id},
            update_data={'is_deleted': True}
        )

        if success:
            table.removeRow(selected_row)
            row_count = table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                table.selectRow(next_row)
        else:
            QMessageBox.warning(None, "Warning", f"Could not delete Security Goal ID: {sg_id}")

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")

def SecurityControls_delete_entry(table):
    logger.info("Deleted entry in Security Controls")
    try:
        reply = QMessageBox.warning(
            None,
            "Warning",
            "Delete selected row.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Ok
        )
        if reply != QMessageBox.Ok:
            return

        selected_row = table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(None, "Warning", "Please select a row to delete.")
            return

        id_item = table.item(selected_row, 1)
        if not id_item:
            QMessageBox.warning(None, "Warning", "No ID found in selected row.")
            return

        ctrl_id = id_item.text()

        # ✅ Soft delete via ORM
        success = update_instance(
            model=SecurityControls,
            filter_by={'id': ctrl_id},
            update_data={'is_deleted': True}
        )

        if success:
            table.removeRow(selected_row)
            row_count = table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                table.selectRow(next_row)

            # ✅ Maintain dependent models
            AS.remove_from_riskcontrol_on_security_control_delete()
            AS.remove_SC_from_risk_data()
            AS.remove_riskcontrol_from_attack_tree_rows(ctrl_id)
        else:
            QMessageBox.warning(None, "Warning", f"Could not delete Security Control ID: {ctrl_id}")

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")
