
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

def on_property_multiline_changed(table, col_idx, input_control):
    # logger.info("property multiline changed")
    try:
        if table.selectedIndexes():
            if table.currentRow() < 0:
                QMessageBox.warning("Warning", "Please select a row to update.")
                return
            if input_control.toPlainText() != None and table.item(table.currentRow(), col_idx) != None: 
                cursor = input_control.textCursor()
                current_position = cursor.position()
                table.item(table.currentRow(), col_idx).setText(input_control.toPlainText())
                cursor.setPosition(current_position)
                input_control.setTextCursor(cursor)
    except Exception as e:
        pass

def display_selected_row(table, property_controls, property_panel, toggle_button):
    logger.info("Displays selected row")
    try:
        if table.selectedIndexes():  # Check if any row is selected
            selected_row = table.currentRow()
            if selected_row < 0:  # No valid row selected
                property_panel.setEnabled(False)
                property_panel.setVisible(False)
                toggle_button.setEnabled(False)
                return

            # Enable and show the property panel when a row is selected
            property_panel.setEnabled(True)
            property_panel.setVisible(True)
            toggle_button.setEnabled(True)

            # Display selected row data
            assum_display(table, selected_row, property_controls)
        else:
            # Disable and hide property panel when no row is selected
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)

            # Reset property panel controls
            assum_display_reset(property_controls)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error loading data: {e}")  # Show error message to the user

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
