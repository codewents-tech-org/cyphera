import sys
from Home.views.NameLabel import NameLabel
from Home.views.PathLabel import PathLabel
from Home.views.MainOpenPanel import MainOpen_Panel
from PyQt5.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import  QFontMetrics
from PyQt5.QtCore import QTimer, Qt, QSize
import models.Parameters as P
import models.helper as helper
from pathlib import Path


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

class MainHome_Panel(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Remove all margins to ensure full white panel
        main_layout.setSpacing(0)

        # Wrapper to add padding around the content
        content_wrapper = QWidget()
        content_wrapper.setStyleSheet(""" background-color: #FFFFFF; border: 2px solid #E3E5EC; border-radius: 8px;""")
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(40, 30, 40, 30)  # Add uniform padding inside
        content_layout.setSpacing(15)
        content_layout.setAlignment(Qt.AlignTop)

        # Image in place of subtitle (moved up slightly and increased size)
        self.subtitle_image = QLabel()
        self.subtitle_image.setPixmap(QPixmap(files.home_panel_icon).scaled(280, 80, 2, True))  # Slightly increase image size
        self.subtitle_image.setAlignment(Qt.AlignLeft)
        
        self.subtitle_image.setStyleSheet("border: none;")  # No borders
        content_layout.addWidget(self.subtitle_image)

        # Description (With 3 lines fixed height and no scrollbars)
         # Description
        # Description (Non-editable, static text)
        self.description = QLabel()
        self.description.setText(
            """Cyphera offers an intelligent, model-based approach for conducting Threat Analysis and Risk Assessment (TARA), enabling systematic, efficient, and ISO 21434 standards-aligned cybersecurity evaluations."""
        )
        self.description.setWordWrap(True)
        self.description.setFixedWidth(300)
        self.description.setStyleSheet(home_style.description_label_style)
        self.description.setAlignment(Qt.AlignLeft)  # Align text to the left
        content_layout.addWidget(self.description)


        # Start section (increased size and bold)
        self.start_label = QLabel("Start")
        self.start_label.setStyleSheet(home_style.start_label_style)
        content_layout.addWidget(self.start_label)

        # Actions (keeping the rest of the layout)
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        # New Project
        new_project_layout = QHBoxLayout()
        new_project_layout.setSpacing(10)
        new_project_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # New Project custom SVG icon (from assets/Icons/Folder_add.svg)
        new_project_icon = QSvgWidget(files.home_panel_new)
        new_project_icon.setFixedWidth(20)  # Set the size to match previous size
        new_project_icon.setFixedHeight(20)
        new_project_icon.setStyleSheet(home_style.home_panel_icon_style)  # Slightly moved up
        new_project_layout.addWidget(new_project_icon)

        new_project_label = QLabel("New Project")
        new_project_label.setStyleSheet(home_style.home_panel_label_style)
        new_project_label.setCursor(Qt.PointingHandCursor)  # Use setCursor to apply a pointer cursor
        new_project_label.mousePressEvent = self.show_Newpanel
        new_project_layout.addWidget(new_project_label)

        button_layout.addLayout(new_project_layout)

        # Open Project
        open_project_layout = QHBoxLayout()
        open_project_layout.setSpacing(10)
        open_project_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Open Project custom SVG icon (from assets/Icons/Folder_line_light.svg)
        open_project_icon = QSvgWidget(files.home_panel_open)
        open_project_icon.setFixedWidth(20)  # Set the size to match previous size
        open_project_icon.setFixedHeight(20)
        open_project_icon.setStyleSheet(home_style.home_panel_icon_style)  # Slightly moved up
        open_project_layout.addWidget(open_project_icon)

        open_project_label = QLabel("Open Project")
        open_project_label.setStyleSheet(home_style.home_panel_label_style)
        open_project_label.setCursor(Qt.PointingHandCursor)  # Use setCursor to apply a pointer cursor
        open_project_label.mousePressEvent = self.show_Openpanel
        open_project_layout.addWidget(open_project_label)

        button_layout.addLayout(open_project_layout)

        content_layout.addLayout(button_layout)

        spacer_between = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)
        content_layout.addItem(spacer_between)

        self.recent_label = QLabel("Recents")
        self.recent_label.setStyleSheet(home_style.start_label_style)  # Reuse style
        content_layout.addWidget(self.recent_label)

        # Layout for displaying recent projects
        self.recent_projects_layout = QVBoxLayout()
        content_layout.addLayout(self.recent_projects_layout)

        # Fetch and display recent projects
        self.load_recent_projects()

        spacer_item = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        content_layout.addItem(spacer_item)

        main_layout.addWidget(content_wrapper)

    # Ensure these functions are correctly implemented
    def show_Newpanel(self, event):
        helper.homePanel_selector = 'NewTab'
        interfaces.home_sub_modules[2].on_click()
        # self.main_window.show_homeframe('MainNew_Panel') 

    def show_Openpanel(self, event):
        helper.homePanel_selector = 'OpenTab'
        interfaces.home_sub_modules[3].on_click()
        # self.main_window.show_homeframe('MainOpen_Panel')

    def open_project_from_recent(self, project_path):
        if not Path(project_path).exists():
            reply = QMessageBox.warning(
                None, "Information",
                "Project Not Found",
                QMessageBox.Ok 
            )

            if reply == QMessageBox.Ok:
                # Delete project from database
                recent_db = Recent_file_DB_creation()
                recent_db.delete_project(project_path)

                # Refresh the recent projects list
                self.load_recent_projects()
            return 
        recent_db = Recent_file_DB_creation()
        recent_db.update_project_timestamp(project_path)

        open_panel = MainOpen_Panel(self)  # Create an instance of MainOpen_Panel
        open_panel.file_input.setText(project_path)  # Set the project path in the input field
        open_panel.Open_Project()  # Call the method to open the project 
        self.load_recent_projects()   

    def elide_text(text, max_width, font):
        """Truncate text with '...' if it exceeds max_width"""
        metrics = QFontMetrics(font)  # Use the provided font instead of QLabel instance
        return metrics.elidedText(text, Qt.ElideRight, max_width)    

    def load_recent_projects(self):
        while self.recent_projects_layout.count():
            item = self.recent_projects_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Fetch recent projects
        recent_db = Recent_file_DB_creation()
        recent_projects = recent_db.fetch_recent_projects()
        recent_db.close_db()

        if recent_projects:
            for name, path in recent_projects:
                # Create a separate frame for each project
                project_widget = QWidget()
                project_layout = QHBoxLayout(project_widget)
                project_layout.setSpacing(10)
                project_layout.setContentsMargins(10, 5, 10, 5)  # Add some padding

                # Name Label (Fixed Width + Tooltip)
                name_label = NameLabel(name)
                name_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
                name_label.setStyleSheet("border: none; padding: 0px; margin: 0px; color: #009D9C;")
                name_label.setToolTip(name)

                # Path Label (Expandable + Truncated with Tooltip)
                path_label = PathLabel(path.strip(), width=700)  # Adjust width as needed
                path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                path_label.setStyleSheet("border: none; padding: 0px; margin: 0px; color: #607182;")
                path_label.setCursor(Qt.PointingHandCursor)
                path_label.setContentsMargins(0, 0, 0, 0)
                path_label.setToolTip(path.strip())  # Show full path on hover
                path_label.mousePressEvent = lambda event, p=path: self.open_project_from_recent(p)

                # Add widgets to the project layout
                project_layout.addWidget(name_label)
                project_layout.addWidget(path_label)

                # Ensure the widget is properly enclosed
                project_widget.setLayout(project_layout)
                project_widget.setStyleSheet("border: 0px;")  # Optional styling

                # Add project_widget to the main layout
                self.recent_projects_layout.addWidget(project_widget)

        else:
            no_projects_label = QLabel("")
            no_projects_label.setStyleSheet(home_style.description_label_style)
            self.recent_projects_layout.addWidget(no_projects_label)


