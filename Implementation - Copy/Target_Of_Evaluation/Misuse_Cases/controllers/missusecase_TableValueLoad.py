
import os
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
import components.table.table_row_indicator as TRI
import logging
logger = logging.getLogger(__name__)

def load_misusecases(self, table,  property_panel, toggle_button):
    logger.info("Load Missuse cases")
    try:
        table.setColumnCount(4)
        table.verticalHeader().setVisible(False)
        header_item = QTableWidgetItem('') 
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28,28))
        table.setHorizontalHeaderItem(0, header_item)
        table.horizontalHeader().setFirstSectionMovable(False)
        for index, header in enumerate(helper.misusecases_header):
            header_item = QTableWidgetItem(header) 
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28,28))
            table.setHorizontalHeaderItem(index+1, header_item)
            table.horizontalHeader().setFixedHeight(50)

        
        helper.adjust_table_column('Misuse cases', table)
        table.horizontalHeader().setSectionResizeMode(3,QHeaderView.Stretch)
        table.horizontalHeader().setStretchLastSection(True)
        
        table.setRowCount(0)
        rows = DB.execute_db("SELECT misuse_cases_id, misuse_cases_name, misuse_cases_comments FROM misuse_cases")
        if not rows:
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
        for row_data in rows:
            row_idx = table.rowCount()
            table.insertRow(row_idx)
            table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row_data[1])

            assumption_id_item = QTableWidgetItem(row_data[0])
            assumptions_item = QTableWidgetItem(row_data[1])
            comments_item = QTableWidgetItem(row_data[2])
            
            assumption_id_item.setFlags(assumption_id_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 1, assumption_id_item)
            table.setItem(row_idx, 2, assumptions_item)
            table.setItem(row_idx, 3, comments_item)

            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)
        if table.rowCount() > 0: table.setCurrentCell(0, 1)
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

