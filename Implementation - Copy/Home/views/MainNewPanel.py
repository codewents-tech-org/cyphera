import os
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

from dotenv import dotenv_values
from utils.server_connection import check_server_and_license
import os
from utils.server_connection import create_remote_project_folder
from models import Parameters as P
from dotenv import dotenv_values
from utils.server_connection import check_server_and_license, create_remote_project_folder, create_remote_config_structure, create_postgres_database_for_project, write_remote_tara_config
from controllers.database import get_engine_and_session, initialize_database
import os, json
import os
from dotenv import load_dotenv


# Load .env from the current directory (or specify path as needed)
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    print("[WARN] .env file not found; using default/fallback values.")
class MainNew_Panel(QWidget):
    def __init__(self):
        super().__init__()
        helper.homePanel_selector = 'NewTab'
        self.storage_mode = 'local'  # default to local, updated by button clicks
        self.base_path = os.getenv("REMOTE_BASE_PATH")
        print("base path1111111111111111------------",self.base_path)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignTop)

        content_wrapper = QWidget()
        content_wrapper.setStyleSheet(""" background-color: #FFFFFF; border: 2px solid #E3E5EC; border-radius: 8px;""")
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(15)
        content_layout.setAlignment(Qt.AlignTop)

        self.label = QLabel("Create New Project")
        self.label.setStyleSheet(home_style.main_label_stye)
        self.label.setAlignment(Qt.AlignLeft)
        content_layout.addWidget(self.label)

        # Cloud / Local toggle buttons
        toggle_layout = QHBoxLayout()
        self.local_button = QPushButton("Local PC")
        self.cloud_button = QPushButton("Cloud")
        self.local_button.setCheckable(True)
        self.cloud_button.setCheckable(True)
        self.local_button.setChecked(True)

        toggle_group = QButtonGroup(self)
        toggle_group.addButton(self.local_button)
        toggle_group.addButton(self.cloud_button)
        self.local_button.clicked.connect(lambda: self.set_storage_mode('local'))
        self.cloud_button.clicked.connect(lambda: self.set_storage_mode('cloud'))
        self.update_toggle_button_styles()


        toggle_layout.addWidget(self.local_button)
        toggle_layout.addWidget(self.cloud_button)
        content_layout.addLayout(toggle_layout)

        # File path input layout
        file_browse_layout = QHBoxLayout()
        file_browse_layout.setSpacing(10)

        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Enter file path here")
        self.file_input.setStyleSheet(home_style.main_panel_input_style)
        self.file_input.setFixedHeight(40)
        file_browse_layout.addWidget(self.file_input)

        self.browse_button = QPushButton("Browse File")
        self.browse_button.setStyleSheet(home_style.main_panel_button_style)
        self.browse_button.setFixedWidth(200)
        self.browse_button.clicked.connect(self.browse_file)
        file_browse_layout.addWidget(self.browse_button)

        content_layout.addLayout(file_browse_layout)

        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Enter Project Name Here")
        self.project_name_input.setStyleSheet(home_style.main_panel_input_style)
        self.project_name_input.setFixedHeight(40)
        content_layout.addWidget(self.project_name_input)

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Enter Author Name Here")
        self.author_input.setStyleSheet(home_style.main_panel_input_style)
        self.author_input.setFixedHeight(40)
        content_layout.addWidget(self.author_input)

        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("Enter Client Name Here")
        self.client_input.setStyleSheet(home_style.main_panel_input_style)
        self.client_input.setFixedHeight(40)
        content_layout.addWidget(self.client_input)

        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Enter Supplier Name Here")
        self.supplier_input.setStyleSheet(home_style.main_panel_input_style)
        self.supplier_input.setFixedHeight(40)
        content_layout.addWidget(self.supplier_input)

        self.dropdown = QComboBox()
        self.dropdown.addItems(["Attack Potential"])
        self.dropdown.setStyleSheet(home_style.main_panel_input_style)
        self.dropdown.setFixedHeight(40)
        content_layout.addWidget(self.dropdown)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)

        self.new_button = QPushButton("Create")
        self.new_button.setStyleSheet(home_style.main_panel_button_style)
        self.new_button.setFixedWidth(200)
        self.new_button.setEnabled(False)
        self.new_button.clicked.connect(self.Create_New_Project)
        button_layout.addWidget(self.new_button)

        content_layout.addLayout(button_layout)

        self.file_input.textChanged.connect(self.check_input_fields)
        self.author_input.textChanged.connect(self.check_input_fields)

        spacer_item = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        content_layout.addItem(spacer_item)
        main_layout.addWidget(content_wrapper)
     


    def set_storage_mode(self, mode):
        self.storage_mode = mode
        self.update_toggle_button_styles()
        if mode == 'cloud':
            print("base path22222222222222------------",self.base_path)
            self.file_input.setText(self.base_path)
            self.file_input.setEnabled(False)
            self.browse_button.setEnabled(False)
        else:
            self.file_input.clear()
            self.file_input.setEnabled(True)
            self.browse_button.setEnabled(True)

    def check_input_fields(self):
        if self.file_input.text() and self.author_input.text():
            self.new_button.setEnabled(True)
        else:
            self.new_button.setEnabled(False)

    def browse_file(self):
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory_path:
            self.file_input.setText(directory_path)

    def Create_New_Project(self):
        if self.storage_mode == 'cloud':
            self.create_remote_project()
        else:
            from pathlib import Path
            self.create_project_with_config_file(Path(self.file_input.text()))

    def create_remote_project(self):


        print("\n🔄 [TARA] Starting remote project creation...\n")
        project_name = self.project_name_input.text().strip()
        author = self.author_input.text().strip()
        client = self.client_input.text().strip()
        supplier = self.supplier_input.text().strip()
        methodology = self.dropdown.currentText()

        success, message = check_server_and_license()
        if not success:
            print("❌ Server connection failed. Project creation aborted.")
            return

        local_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../cyphera/.env"))
        env_vars = dotenv_values(local_env_path)
        if not env_vars:
            print("❌ Failed to parse .env.")
            return

        print("🌍 Remote .env loaded:")
        for k, v in env_vars.items():
            print(f"   {k} = {v}")

        if not create_remote_project_folder(project_name):
            print("❌ Remote project folder creation failed.")
            return

        create_remote_config_structure(project_name)
        db_url = create_postgres_database_for_project(project_name, env_vars)
        if not db_url:
            print("❌ Postgres DB creation failed. Aborting.")
            return

        print(f"✅ Postgres DB initialized: {db_url}")
        from models import Parameters as P
        P.SQLALCHEMY_DATABASE_URL = db_url
        get_engine_and_session()
        initialize_database()

        tara_config = {
            "project_name": project_name,
            "version": "1.0",
            "author": author,
            "client": client,
            "supplier": supplier,
            "methodology": methodology,
            "dependencies": []
        }
        write_remote_tara_config(project_name, tara_config)
        print(f"📦 Project '{project_name}' fully initialized in remote server.")
        self.clear_fields()

    def create_project_with_config_file(self, selected_base_path, config_extension=".tara", config_data=None):
        """
        Creates local project structure using SQLite and initializes database using tablemodels.py.
        
        Folder structure:
        └── <selected_base_path>/<project_name>/
            ├── config/
            │   └── <project_name>.db
            ├── <project_name>.tara
            ├── README.md
            └── requirements.txt
        """

        from controllers.database import get_engine_and_session, initialize_database
        from models import Parameters as P
        import json
        from pathlib import Path

        # 📁 Compose final project path
        project_name = self.project_name_input.text().strip()
        final_path = Path(selected_base_path) / project_name

        # 🛠 Create folder structure
        final_path.mkdir(parents=True, exist_ok=True)
        (final_path / 'config').mkdir(exist_ok=True)
        (final_path / 'README.md').touch()
        (final_path / 'requirements.txt').touch()

        # 🗂️ Define SQLite DB file path and URL
        db_file_path = final_path / 'config' / f"{project_name}.db"
        P.database_file_path = db_file_path
        P.SQLALCHEMY_DATABASE_URL = f"sqlite:///{str(db_file_path)}"

        if db_file_path.exists():
            os.chmod(db_file_path, 0o666)  # Read & write permission for all
            os.chmod(db_file_path.parent, 0o775)  # Ensure /config folder is writable
            
        # ⚙️ Initialize SQLAlchemy engine and models
        get_engine_and_session()
        initialize_database()

        # 📝 Build project metadata config
        if config_data is None:
            config_data = {
                "project_name": project_name,
                "version": "1.0",
                "author": self.author_input.text(),
                "client": self.client_input.text(),
                "supplier": self.supplier_input.text(),
                "methodology": self.dropdown.currentText(),
                "dependencies": []
            }

        # 💾 Write .tara config file
        config_file_path = final_path / f"{project_name}{config_extension}"
        with config_file_path.open('w') as config_file:
            json.dump(config_data, config_file, indent=4)

        # 🔁 Store metadata
        P.project_path = final_path
        P.Project_name = config_data['project_name']
        P.Client_name = config_data['client']
        P.Supplier_name = config_data['supplier']
        P.selected_methodology = config_data['methodology']
        interfaces.project_path = config_file_path

        print(f"✅ Project '{project_name}' created with configuration file at '{config_file_path}'.")
        
        # 🧹 Clear inputs
        self.clear_fields()

    def clear_fields(self):
        self.file_input.clear()
        self.project_name_input.clear()
        self.author_input.clear()
        self.client_input.clear()
        self.supplier_input.clear()

        if interfaces.main_sub_modules:
            interfaces.main_sub_modules[1][1].on_click()
            interfaces.main_sub_modules[1][0]()

        if interfaces.default_sub_module:
            interfaces.default_sub_module[0].on_click()
            interfaces.default_sub_module[1]()

        helper.Panel_selector = 'ModuleTab'
        helper.modulePanel_Selector = 'HomeTab'
        helper.submodulePanel_Selector = 'HomeTab'
        interfaces.home_sub_modules[0].setHidden(False)

    def show_project_exists_warning(self):
        warning_msg = QMessageBox()
        warning_msg.setIcon(QMessageBox.Warning)
        warning_msg.setWindowTitle("Project Exists")
        warning_msg.setText("A project with this name already exists. Please enter a different project name.")
        warning_msg.setStandardButtons(QMessageBox.Ok)
        warning_msg.exec_()

    def update_toggle_button_styles(self):
        if self.storage_mode == 'local':
            self.local_button.setStyleSheet(home_style.toggle_button_active_style)
            self.cloud_button.setStyleSheet(home_style.toggle_button_inactive_style)
        else:
            self.local_button.setStyleSheet(home_style.toggle_button_inactive_style)
            self.cloud_button.setStyleSheet(home_style.toggle_button_active_style)
