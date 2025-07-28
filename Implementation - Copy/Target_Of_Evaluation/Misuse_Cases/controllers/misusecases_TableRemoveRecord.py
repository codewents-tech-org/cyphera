
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
import components.table.table_row_indicator as TRI
import logging
logger = logging.getLogger(__name__)


def misusecases_delete_entry(table):
    logger.info("deletion of Missuse case")
    try:
        replay = QMessageBox.warning(None, "Warning", "Delete selected row.", QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Ok)
        if replay == QMessageBox.Ok:
            selected_row = table.currentRow()
            if selected_row < 0:
                QMessageBox.warning("Warning", "Please select a row to delete.")
                return
            id_item = table.item(selected_row, 1).text()
            DB.update_db("DELETE FROM misuse_cases WHERE misuse_cases_id = ?", (id_item,))
            DB.update_db("INSERT INTO misusecases_trash (id) VALUES (?)", (id_item,))
            table.removeRow(selected_row)
            row_count = table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                table.selectRow(next_row)
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")
