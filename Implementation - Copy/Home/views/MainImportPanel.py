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

class MainImport_Panel(QWidget):
    def __init__(self):
        super().__init__()
        helper.homePanel_selector = 'ImportTab'

        # Main vertical layout for the panel
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)  # Margins around the layout
        main_layout.setSpacing(20)  # Spacing between widgets
        main_layout.setAlignment(Qt.AlignTop)  # Align all widgets to the top

        # Create and configure the label as a heading
        self.label = QLabel("Import Project")
        self.label.setStyleSheet(home_style.main_panel_label_style)  # Padding and border for heading
        self.label.setAlignment(Qt.AlignLeft)  # Center alignment for the heading
        main_layout.addWidget(self.label)

        # Create and configure the grid layout for file input and browse button
        file_browse_layout = QGridLayout()
        file_browse_layout.setSpacing(10)  # Spacing in the grid layout
        file_browse_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for grid layout

        # Create and configure the input field for displaying the selected file path
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Enter file path here")
        self.file_input.setStyleSheet(home_style.main_panel_input_style)  # Padding, border, and rounded corners
        self.file_input.setFixedWidth(700)  
        self.file_input.setFixedHeight(40)  
        self.file_input.setContentsMargins(0,0,0,0)
        file_browse_layout.addWidget(self.file_input, 0, 0)  # Add to grid layout at row 0, column 0

        # Create and configure the Browse File button
        browse_button = QPushButton("Browse File")
        browse_button.setFixedWidth(200)
        browse_button.setStyleSheet(home_style.main_panel_button_style)  # Styled button
        browse_button.clicked.connect(self.browse_file)  # Connect to browse_file method
        file_browse_layout.addWidget(browse_button, 0, 1)
        
        # Add the file input and browse button grid layout to the main layout
        main_layout.addLayout(file_browse_layout)

        # Create and configure the grid layout for file input and browse button
        button_layout = QGridLayout()
        button_layout.setSpacing(10)  # Spacing in the grid layout
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for grid layout
        button_layout.setAlignment(Qt.AlignRight)

        # Create and configure the button for creating new projects
        import_button = QPushButton("Import")
        import_button.setStyleSheet(home_style.main_panel_button_style)
        import_button.setFixedWidth(200)  
        import_button.setFixedHeight(40)  
        import_button.setContentsMargins(0,0,0,0)
        import_button.clicked.connect(self.Import_Project)
        
        button_layout.addWidget(import_button, 0, 1)
        
        # Add the file input and browse button grid layout to the main layout
        main_layout.addLayout(button_layout)

        # Set the layout for this panel
        self.setLayout(main_layout)
        self.setStyleSheet(home_style.home_bg)  # Background color for the panel

    def browse_file(self):
        # Open a file dialog to select a file
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")
        if file_path:
            self.file_input.setText(file_path)  # Set the file path in the QLineEdit

    def Import_Project(self):
        helper.Panel_selector = 'ModuleTab'
        helper.modulePanel_Selector = 'HomeTab'
        # print("import project clicked)
