
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

def assum_submit_changes(table):
    logger.info("Assumption Submission")
    DB.execute_db("DELETE FROM assumptions")
    for row in range(table.rowCount()):
        assumption_id_item = table.item(row, 1)
        assumptions_item = table.item(row, 2)
        comments_item = table.item(row, 3)

        if assumption_id_item and assumptions_item and comments_item:
            assumption_id = assumption_id_item.text()
            assumptions = assumptions_item.text()
            comments = comments_item.text()

            DB.update_db("""
            INSERT INTO assumptions (assumption_id, assumptions, comments)
            VALUES (?, ?, ?)
            """, (assumption_id, assumptions, comments))
    
    
def toec_submit_changes(table):
    logger.info("toec Submission")
    DB.execute_db("DELETE FROM toe_configuration")
    for row in range(table.rowCount()):
        toe_configuration_id_item = table.item(row, 1)
        toe_configuration_name_item = table.item(row, 2)
        toe_configuration_description_item = table.item(row,3)
        toe_configuration_comments_item = table.item(row, 4)

        # if toe_configuration_id_item and toe_configuration_name_item and toe_configuration_description_item and toe_configuration_comments_item:
        toe_configuration_id = toe_configuration_id_item.text()
        toe_configuration_name = toe_configuration_name_item.text()
        toe_configuration_description = toe_configuration_description_item.text()            
        toe_configuration_comments = toe_configuration_comments_item.text()

        DB.update_db("""
        INSERT INTO toe_configuration (toe_configuration_id, toe_configuration_name, toe_configuration_description, toe_configuration_comments)
            VALUES (?, ?, ?, ?)
            """, (toe_configuration_id, toe_configuration_name, toe_configuration_description, toe_configuration_comments))
            