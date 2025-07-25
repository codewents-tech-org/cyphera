import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QToolTip, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QFileDialog, QPushButton, QComboBox, QLabel, QFrame, QLineEdit, QSizePolicy, QStackedWidget, QButtonGroup
from PyQt5.QtGui import QIcon, QCursor, QFont, QPainter, QFontMetrics
from PyQt5.QtCore import QTimer, Qt, QSize
import models.Parameters as P
import models.helper as helper
from pathlib import Path
import json
import controllers.DatabaseCreator as DB
import styles.property_panel_style as property_panel_style
import styles.action_panel_style as action_panel_style
import styles.action_background_panel_style as action_panel_style
import styles.Tool_style as tool_style
import styles.main_module_style as main_module_style
import styles.tool_footer_style as footer_style
import styles.home_style as home_style
import utils.file_utils as files
import sqlite3
from PyQt5.QtSvg import QSvgWidget
import datetime
from Home.controller.Recent_file_database_creation import Recent_file_DB_creation
import models.Parameters as P
import utils.interface_utils as interfaces
from PyQt5.QtGui import QPixmap

import qtawesome as qta  # Ensure qtawesome is installed: pip install qtawesome
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,QSpacerItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QTextOption  # For font and text options
from PyQt5.QtWidgets import QTextEdit, QSizePolicy  # For QTextEdit widget and size policies
from PyQt5.QtGui import QPixmap  # Import QPixmap for handling images


import qtawesome as qta  # Ensure qtawesome is installed
from PyQt5.QtGui import QPixmap  # Ensure QPixmap is imported
from controllers.database import get_engine_and_session, initialize_database
from PyQt5.QtGui import QPixmap, QFont, QTextOption  # Import necessary classes
from PyQt5.QtWidgets import QTextEdit, QSizePolicy  # For QTextEdit widget and size policies
import styles.Tool_style as Tool_style



class NameLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setFixedWidth(180)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.setWordWrap(False) 
        self.setToolTip(text)  # Set tooltip to show full name
        
    def paintEvent(self, event):
        """Custom paint event to elide text when it overflows."""
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided_text = metrics.elidedText(self.text(), Qt.ElideRight, self.width())  # Truncate with "..."
        painter.drawText(self.rect(), Qt.AlignLeft | Qt.AlignVCenter, elided_text)

    def sizeHint(self):
        """Override sizeHint to ensure correct label sizing."""
        metrics = QFontMetrics(self.font())
        return QSize(metrics.width(self.text()), metrics.height())        

    def enterEvent(self, event):
        """ Show tooltip dynamically when mouse enters if text is clipped """
        if self.fontMetrics().width(self.text()) > self.width():
            QToolTip.showText(event.globalPos(), self.text(), self)
        super().enterEvent(event)
