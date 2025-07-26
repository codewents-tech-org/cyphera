from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QSpacerItem, QTextEdit, QPushButton, QGridLayout, QFileDialog, QLineEdit
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize

import components.action_panel as action_panel
from Settings.views.settings_toolbar_panel import create_toolbar
import styles.sub_module_style as submodule_style
import styles.action_panel_style as actionpanel_style
import utils.file_utils as files
from Settings.views.controller import Report_input_submit as Report_Input_Submit
from utils import interface_utils as interfaces 
from PyQt5.QtCore import pyqtSignal
import os
from datetime import datetime

class Settings(QWidget):
    autosave_toggled = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.general_visible = False
        self.heading_full_path = ""
        self.header_full_path = ""
        self.footer_logo_full_path = ""
        
        # Main layout for the Settings Frame
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # Main Content Area (Right Panel)
        self.content_area = QWidget()
        self.content_area.setStyleSheet(actionpanel_style.action_panel_style)  # Background styling
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0,0,0,0)
        #content_layout.setSpacing(0)

        # Add Toolbar at the top of the content area
        self.toolbar = create_toolbar(self)
        content_layout.addWidget(self.toolbar)

        # Add Action Panel with Logo
        self.action_panel = QWidget()
        self.action_panel.setStyleSheet(actionpanel_style.settings_panel_style)  # Example styling with padding
        #self.action_panel.setContentsMargins(10,10,10,10)
        action_panel_layout = QVBoxLayout(self.action_panel)
        action_panel_layout.setContentsMargins(10,10,10,10)

        top_panel = QWidget()
        top_panel_layout = QVBoxLayout(top_panel)
        top_panel_layout.setContentsMargins(0, 0, 0, 0)

        logo_image_path = files.home_panel_icon
        logo_label = QLabel()
        pixmap = QPixmap(logo_image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("Logo not found")
        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        logo_label.setStyleSheet("padding-left: 20px; padding-top: 20px;")

        top_panel_layout.addWidget(logo_label, alignment=Qt.AlignLeft | Qt.AlignTop)
        action_panel_layout.addWidget(top_panel)

        # ---------- Bottom Panel: Placeholder "hai" ----------
        bottom_panel = QWidget()
        bottom_panel_layout = QHBoxLayout(bottom_panel)
        bottom_panel_layout.setContentsMargins(0, 10, 10, 10)

        # --- Right Panel (Declare First) ---
        right_panel = QWidget()
        self.right_panel_layout = QVBoxLayout(right_panel)  # Declare first
        self.right_panel_layout.setContentsMargins(10, 10, 10, 10)
        self.right_panel = right_panel  # Store reference
        self.right_panel_layout.setSpacing(0)

        # --- Left Panel ---
        left_panel = QWidget()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 10, 10, 10)
        left_panel_layout.setAlignment(Qt.AlignLeft)
        left_panel.setFixedWidth(250)

        # Add "General" Button
        self.general_button = QPushButton("General")
        self.general_button.setFixedSize(120, 40)
        self.general_button.setStyleSheet("font-size: 16px; font-weight: bold; text-align: left;  padding-left: 0px;")
        self.general_button.clicked.connect(self.show_general_panel)
        left_panel_layout.addWidget(self.general_button)

        # Add "Report" Button
        self.report_button = QPushButton("Report")
        self.report_button.setFixedSize(120, 40)
        self.report_button.setStyleSheet("font-size: 16px; font-weight: bold; text-align: left; padding-left: 0px;")
        self.report_button.clicked.connect(self.show_report_panel)
        left_panel_layout.addWidget(self.report_button)

        left_panel_layout.addStretch()

        # Add Left and Right Panels to Bottom Panel
        bottom_panel_layout.addWidget(left_panel)
        spacer = QSpacerItem(30, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)
        bottom_panel_layout.addItem(spacer)
        bottom_panel_layout.addWidget(right_panel)

        # Add Bottom Panel to Action Panel
        action_panel_layout.addWidget(bottom_panel)

        # Spacer at bottom
        action_panel_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add to main layout
        content_layout.addWidget(self.action_panel)
        main_layout.addWidget(self.content_area)

        self.show_general_panel()

    def load_data(self): pass

    def show_report_panel(self):

        self.general_button.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        self.report_button.setStyleSheet("font-size: 18px; font-weight: bold; color: #009D9C;") 
        # Clear Right Panel
        self.clear_layout(self.right_panel_layout)
        self.right_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.right_panel_layout.setSpacing(0)

        # Add Report Heading Label
        report_label = QLabel("Report Heading Logo")
        report_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 0px;")
        report_label.setAlignment(Qt.AlignLeft)
        self.right_panel_layout.addWidget(report_label)
        

        description_label = QLabel("Provide logo for Report Heading. Recommended image size is 330x165px")
        description_label.setStyleSheet("font-size: 12px; color: gray; padding: 0px;")
        description_label.setWordWrap(True)  # Optional: wrap text if needed
        description_label.setAlignment(Qt.AlignLeft)
        self.right_panel_layout.addWidget(description_label)
        
        footer_db = Report_Input_Submit.FooterDatabase()  # Create an instance
        report_heading_logo_path = footer_db.fetch_heading_image_path()
        if not report_heading_logo_path or not os.path.isfile(report_heading_logo_path):
            report_heading_logo_path = "No file selected"
        else:
            report_heading_logo_path = os.path.basename(report_heading_logo_path)    

        self.report_heading_logo_path = QLineEdit()
        self.report_heading_logo_path.setText(report_heading_logo_path)
        self.report_heading_logo_path.setReadOnly(True)
        self.report_heading_logo_path.setFixedWidth(600)
        self.report_heading_logo_path.setStyleSheet("""QLineEdit {border: 1px solid gray; padding: 2px; color: #A0A0A0;}""")
        self.report_heading_logo_path.setAlignment(Qt.AlignLeft)
        self.right_panel_layout.addWidget(self.report_heading_logo_path)
        self.right_panel_layout.addStretch()  

        browse_heading_button = QPushButton("Browse")
        browse_heading_button.setFixedWidth(80)
        browse_heading_button.setStyleSheet(self.get_browse_button_style())
        browse_heading_button.clicked.connect(self.browse_heading_image)
        self.right_panel_layout.addWidget(browse_heading_button, alignment=Qt.AlignLeft)
        spacer = QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.right_panel_layout.addItem(spacer)


        report_header_label = QLabel("Report Header Logo")
        report_header_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 0px;")
        report_header_label.setAlignment(Qt.AlignLeft)

        self.right_panel_layout.addWidget(report_header_label, alignment=Qt.AlignLeft)

        header_description_label = QLabel("Provide logo for Report Header. Recommended image size is 330x100px")
        header_description_label.setStyleSheet("font-size: 12px; color: gray; padding: 0px;")
        header_description_label.setWordWrap(True)  # Optional: wrap text if needed
        header_description_label.setAlignment(Qt.AlignLeft)
        self.right_panel_layout.addWidget(header_description_label)
        self.right_panel_layout.addStretch()  

        report_header_logo_path = footer_db.fetch_header_logo_path()
        if not report_header_logo_path or not os.path.isfile(report_header_logo_path):
            report_header_logo_path = "No file selected"
        else:
            report_header_logo_path = os.path.basename(report_header_logo_path)    

        self.report_header_logo_path = QLineEdit()
        self.report_header_logo_path.setText(report_header_logo_path)
        self.report_header_logo_path.setReadOnly(True)
        self.report_header_logo_path.setFixedWidth(600)
        self.report_header_logo_path.setStyleSheet("""QLineEdit {border: 1px solid gray; padding: 2px; color: #A0A0A0;}""")
        self.right_panel_layout.addWidget(self.report_header_logo_path)
        self.right_panel_layout.addStretch()

        browse_header_button = QPushButton("Browse")
        browse_header_button.setFixedWidth(80)
        browse_header_button.setStyleSheet(self.get_browse_button_style())
        browse_header_button.clicked.connect(self.browse_header_image)
        self.right_panel_layout.addWidget(browse_header_button, alignment=Qt.AlignLeft)
        spacer = QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.right_panel_layout.addItem(spacer)

        report_footer_label = QLabel("Report Footer Logo")
        report_footer_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 0px;")
        report_footer_label.setAlignment(Qt.AlignLeft)

        self.right_panel_layout.addWidget(report_footer_label)

        footer_description_label = QLabel("Provide logo for Report Footer. Recommended image size is 42x55px")
        footer_description_label.setStyleSheet("font-size: 12px; color: gray; padding: 0px;")
        footer_description_label.setWordWrap(True)  # Optional: wrap text if needed
        footer_description_label.setAlignment(Qt.AlignLeft)
        self.right_panel_layout.addWidget(footer_description_label)
        self.right_panel_layout.addStretch()  

        report_footer_logo_path = footer_db.fetch_logo_path()
        if not report_footer_logo_path or not os.path.isfile(report_footer_logo_path):
            report_footer_logo_path = "No file selected"
        else:
            report_footer_logo_path = os.path.basename(report_footer_logo_path)    

        self.report_footer_logo_path = QLineEdit()
        self.report_footer_logo_path.setText(report_footer_logo_path)
        self.report_footer_logo_path.setReadOnly(True)
        self.report_footer_logo_path.setFixedWidth(600)
        self.report_footer_logo_path.setStyleSheet("""QLineEdit {border: 1px solid gray; padding: 2px; color: #A0A0A0;}""")
        self.right_panel_layout.addWidget(self.report_footer_logo_path)
        self.right_panel_layout.addStretch()

        browse_footer_button = QPushButton("Browse")
        browse_footer_button.setFixedWidth(80)
        browse_footer_button.setStyleSheet(self.get_browse_button_style())
        browse_footer_button.clicked.connect(self.browse_footer_logo_image)
        self.right_panel_layout.addWidget(browse_footer_button, alignment=Qt.AlignLeft)
        spacer = QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.right_panel_layout.addItem(spacer)

        report_footer_text_label = QLabel("Report Footer Text")
        report_footer_text_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 0px;")
        report_footer_text_label.setAlignment(Qt.AlignLeft)
        self.right_panel_layout.addWidget(report_footer_text_label)

        footer_text_description_label = QLabel("Provide text for Report Footer")
        footer_text_description_label.setStyleSheet("font-size: 12px; color: gray; padding: 0px;")
        footer_text_description_label.setWordWrap(True)  # Optional: wrap text if needed
        footer_description_label.setAlignment(Qt.AlignLeft)
        self.right_panel_layout.addWidget(footer_text_description_label)
        self.right_panel_layout.addStretch()  

        footer_db = Report_Input_Submit.FooterDatabase()
        footer_text = footer_db.fetch_footer_text()
        current_year = datetime.now().year
        next_year_short = str(current_year + 1)[-2:]
        if not footer_text:
            footer_text = f" © Copyright {current_year}-{next_year_short} | Your Organisation name | All Rights Reserved"

        self.report_footer_edit = QLineEdit()
        self.report_footer_edit.setFixedWidth(600)  # Adjust width as needed
        self.report_footer_edit.setStyleSheet("""QLineEdit {color: #A0A0A0; border: 1px solid gray; padding: 2px;}""")
        self.report_footer_edit.setText(footer_text)
        self.report_footer_edit.setToolTip(self.report_footer_edit.text())
        self.report_footer_edit.textChanged.connect(lambda: self.report_footer_edit.setToolTip(self.report_footer_edit.text()))
        self.right_panel_layout.addWidget( self.report_footer_edit)
        self.right_panel_layout.addStretch()  

        save_button = QPushButton("Save")
        save_button.setFixedWidth(80)
        save_button.setStyleSheet(self.get_browse_button_style())
        save_button.clicked.connect(self.save_settings)
        self.right_panel_layout.addWidget(save_button, alignment=Qt.AlignLeft)


    def show_general_panel(self):
        self.clear_layout(self.right_panel_layout)

        self.general_button.setStyleSheet("font-size: 18px; font-weight: bold; color: #009D9C;")
        self.report_button.setStyleSheet("font-size: 16px; font-weight: bold; color: black;") 

        # ========== AutoSave Section ==========
        auto_save_layout = QHBoxLayout()
        auto_save_layout.setContentsMargins(10, 0, 10, 0)
        auto_save_layout.setSpacing(0)

        auto_save_label = QLabel("AutoSave")
        auto_save_label.setAlignment(Qt.AlignLeft)
        auto_save_label.setStyleSheet("font-size: 16px;")
        auto_save_layout.addWidget(auto_save_label)

        self.auto_save_button = QPushButton('')
        self.auto_save_button.setIcon(QIcon(files.turnoff_barbutton_icon))
        self.auto_save_button.setIconSize(QSize(60, 20))
        self.auto_save_button.setFixedSize(70, 30)
        self.auto_save_button.clicked.connect(self.toggle_autosave)
        auto_save_layout.addWidget(self.auto_save_button)

        auto_save_layout.addStretch()
        self.right_panel_layout.addLayout(auto_save_layout)

        autosave_label = QLabel("  When Autosave is enabled, the changes made will get automatically saved")
        autosave_label.setStyleSheet("font-size: 12px; color: gray;")
        autosave_label.setWordWrap(True)  # Optional: wrap text if needed
        autosave_label.setAlignment(Qt.AlignLeft)
        self.right_panel_layout.addWidget(autosave_label)
        

        # # ========== Guidelines Section ==========
        # guidelines_layout = QHBoxLayout()
        # guidelines_layout.setContentsMargins(10, 10, 10, 0)
        # guidelines_layout.setSpacing(10)

        # guidelines_label = QLabel("Guidelines")
        # guidelines_label.setAlignment(Qt.AlignLeft)
        # guidelines_label.setStyleSheet("font-size: 16px;")
        # guidelines_layout.addWidget(guidelines_label)

        # guidelines_button = QPushButton('')
        # guidelines_icon = QIcon(files.toggle_button_icon)
        # guidelines_button.setIcon(guidelines_icon)
        # guidelines_button.setIconSize(QSize(40, 40))
        # guidelines_button.setFixedSize(50, 50)
        # guidelines_layout.addWidget(guidelines_button)

        # guidelines_layout.addStretch()
        # self.right_panel_layout.addLayout(guidelines_layout)

        # guide_lines_label = QLabel("  Will act as a Guide")
        # guide_lines_label.setStyleSheet("font-size: 12px; color: gray;")
        # guide_lines_label.setWordWrap(True)  # Optional: wrap text if needed
        # guide_lines_label.setAlignment(Qt.AlignLeft)
        # self.right_panel_layout.addWidget(guide_lines_label)

        # # Add Stretch
        # self.right_panel_layout.addStretch()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)    

        
    def toggle_autosave(self):
        """Toggle the AutoSave setting."""
        if not interfaces.autosave_enabled:
            interfaces.autosave_enabled = True
            self.auto_save_button.setIcon(QIcon(files.turnon_barbutton_icon))
        else:
            interfaces.autosave_enabled = False
            self.auto_save_button.setIcon(QIcon(files.turnoff_barbutton_icon))
        self.autosave_toggled.emit()    

    def update_autosave_button(self):
        """Update Auto Save button based on global state."""
        if interfaces.autosave_enabled:
            self.auto_save_button.setIcon(QIcon(files.turnon_barbutton_icon))
        else:
            self.auto_save_button.setIcon(QIcon(files.turnoff_barbutton_icon))

    def browse_heading_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Heading Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.heading_full_path = file_path
            self.set_path_with_tooltip(self.report_heading_logo_path, file_name, file_path)
            self.save_settings()

    def browse_header_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Header Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.header_full_path = file_path
            self.set_path_with_tooltip(self.report_header_logo_path, file_name, file_path)
            self.save_settings()

    def browse_footer_logo_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Footer Logo Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.footer_logo_full_path = file_path
            self.set_path_with_tooltip(self.report_footer_logo_path, file_name, file_path)
            self.save_settings()
        

    def set_path_with_tooltip(self, line_edit: QLineEdit, file_name: str, full_path: str):
        line_edit.setText(file_name)
        line_edit.setToolTip(full_path)
        line_edit.setCursorPosition(0)  # Optional: show start of path
        
    def save_settings(self):
        # Get paths from line edits
        heading_path = self.heading_full_path
        header_path = self.header_full_path
        footer_logo_path = self.footer_logo_full_path
        
        # Call external function to save files
        Report_Input_Submit.save_browsed_files(heading_path, header_path, footer_logo_path)

        footer_text = self.report_footer_edit.text()

        footer_db = Report_Input_Submit.FooterDatabase()
        footer_db.save_footer_text(footer_text)
        footer_db.close_connection()

    def get_browse_button_style(self):
        return """
            QPushButton {
                background-color: #17cfce;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #007F7E;
            }
        """        
    
