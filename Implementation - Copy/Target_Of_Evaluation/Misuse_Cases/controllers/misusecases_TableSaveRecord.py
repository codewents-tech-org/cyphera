
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

def misusecases_submit_changes(table):
    logger.info("Save Missuse case")
    DB.execute_db("DELETE FROM misuse_cases")
    for row in range(table.rowCount()):
        misusecases_id_item = table.item(row, 1)
        name_item = table.item(row, 2)
        comments_item = table.item(row, 3)

        if misusecases_id_item and name_item and comments_item:
            misusecases_id = misusecases_id_item.text()
            name = name_item.text()
            comments = comments_item.text()

            DB.update_db("""
            INSERT INTO misuse_cases (misuse_cases_id, misuse_cases_name, misuse_cases_comments)
            VALUES (?, ?, ?)
            """, (misusecases_id, name, comments))
    