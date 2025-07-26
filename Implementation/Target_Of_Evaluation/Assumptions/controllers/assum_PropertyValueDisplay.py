
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
import logging
logger = logging.getLogger(__name__)


def on_property_line_changed(table, col_idx, input_control):
    logger.info("property line changed")
    try:
        if table.selectedIndexes():
            if table.currentRow() < 0:
                QMessageBox.warning("Warning", "Please select a row to update.")
                return
            table.item(table.currentRow(), col_idx).setText(input_control.text())
    except Exception as e:
        pass

def display_selected_row(table, property_controls):
    logger.info("Displays selected row")
    try:
        if table.selectedIndexes():
            selected_row = table.currentRow()        
            if selected_row < 0:
                return
            assum_display(table, selected_row, property_controls)
        else:
            assum_display_reset(property_controls)
    except Exception as e:
        pass
        # QMessageBox.critical(None, "Error", f"Error loading data: {e}")

def assum_display(table, selected_row, assum_property_controls):
    try:
        assum_property_controls[0][1].setText(table.item(selected_row, 1).text())
        assum_property_controls[1][1].setText(table.item(selected_row, 2).text())
        assum_property_controls[2][1].setText(table.item(selected_row, 3).text())
    except Exception as e:
        pass

def assum_display_reset(assum_property_controls):
    try:
        assum_property_controls[0][1].setText('')
        assum_property_controls[1][1].setText('')
        assum_property_controls[2][1].setText('')
    except Exception as e:
        pass
