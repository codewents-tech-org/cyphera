
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


def assum_add_new_entry(table, self):
    logger.info("Assumption new entry")
    row_idx = table.rowCount()
    table.insertRow(row_idx)
    table.setRowHeight(row_idx, 40)
    
    assum_id = helper.assum_generate_id(table)
    id_item = QTableWidgetItem(assum_id)
    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # ID column should remain non-editable
    table.setItem(row_idx, 1, id_item)

    sidebar = TRI.SidebarWidget()
    table.setCellWidget(row_idx, 0, sidebar)

    # Extract only the last part after the last '-'
    assumption_name = f"Assumption {assum_id.split('-')[-1]}"  # Pre-filled editable name

    for col_idx in range(2, table.columnCount()):
        if col_idx == 2:
            item = QTableWidgetItem(assumption_name)  # Set placeholder text
            table.setItem(row_idx, col_idx, item)
            table.setCurrentCell(row_idx, 2)
            # **DO NOT MAKE IT NON-EDITABLE** so the user can change it
            self.find_duplicates(item)
            self.previous_text = item.text()
            self.existing_entries.add(item.text())
        else:
            item = QTableWidgetItem("")
            table.setItem(row_idx, col_idx, item)

    table.setCurrentCell(row_idx, 1)

    return assum_id, assumption_name  # Returning both values for further use




def toec_add_new_entry(table, self):
    logger.info("TOE Config new entry")
    row_idx = table.rowCount()
    table.insertRow(row_idx)
    table.setRowHeight(row_idx, 40)
    
    toec_id = helper.toec_generate_id(table)
    id_item = QTableWidgetItem(toec_id)
    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # ID column should remain non-editable
    table.setItem(row_idx, 1, id_item)

    sidebar = TRI.SidebarWidget()
    table.setCellWidget(row_idx, 0, sidebar)

    # Extract only the last part after the last '-'
    toec_name = f"TOE Config {toec_id.split('-')[-1]}"  # Pre-filled editable name

    for col_idx in range(2, table.columnCount()):
        if col_idx == 2:
            item = QTableWidgetItem(toec_name)  # Set placeholder text
            table.setItem(row_idx, col_idx, item)
            table.setCurrentCell(row_idx, 2)
            # **DO NOT MAKE IT NON-EDITABLE** so the user can change it
            self.find_duplicates(item)
            self.previous_text = item.text()
            self.existing_entries.add(item.text())
        else:
            item = QTableWidgetItem("")
            table.setItem(row_idx, col_idx, item)

    table.setCurrentCell(row_idx, 1)

    return toec_id, toec_name  # Returning both values for further use
