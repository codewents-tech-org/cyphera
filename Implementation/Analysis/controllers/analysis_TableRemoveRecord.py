
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
import Target_Of_Evaluation.Scope.controllers.scope_synchronizations as TSS

import logging
logger = logging.getLogger(__name__)
def asset_delete_entry(table):
    logger.info("Deleted Asset entry")
    try:
        replay = QMessageBox.warning(None, "Warning", "Delete selected row.", QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Ok)
        if replay == QMessageBox.Ok:
            selected_row = table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(None, "Warning", "Please select a row to delete.")
                return
            id_item = table.item(selected_row, 1).text()
            DB.update_db("DELETE FROM assets WHERE asset_id = ?", (id_item,))
            DB.update_db("INSERT INTO asset_trash (id) VALUES (?)", (id_item,))
            table.removeRow(selected_row)
            row_count = table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                table.selectRow(next_row)
            
            AS.sync_threats_with_assets()
            AS.update_threatscenario_from_threat()
            AS.update_risktreatement_data()
            AS.remove_orphaned_attack_tree_rows()
            AS.remove_nonexistent_threat_scenarios_from_Risk_data()
            TSS.update_scope_assets()

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")

def DS_delete_entry(table):
    logger.info("Deleted Damage Scenarios entry")
    try:
        replay = QMessageBox.warning(None, "Warning", "Delete selected row.", QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Ok)
        if replay == QMessageBox.Ok:
            selected_row = table.currentRow()
            if selected_row < 0:
                QMessageBox.warning("Warning", "Please select a row to delete.")
                return
            id_item = table.item(selected_row, 1).text()
            DB.update_db("DELETE FROM damage_scenarios WHERE ds_id = ?", (id_item,))
            DB.update_db("INSERT INTO ds_trash (id) VALUES (?)", (id_item,))
            table.removeRow(selected_row)
            row_count = table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                table.selectRow(next_row)
            
            AS.update_threat_TS_from_DS()
            AS.update_risktreatement_data()

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")


