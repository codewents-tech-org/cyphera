import os
import sys
from turtle import mode
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
from PyQt5.QtCore import QThread, pyqtSignal, QObject

from dotenv import dotenv_values
from utils.server_connection import check_server_and_license
import os
from utils.server_connection import create_remote_project_folder
from models import Parameters as P
from dotenv import dotenv_values
from utils.server_connection import check_server_and_license, create_remote_project_folder, create_remote_config_structure, create_postgres_database_for_project, write_remote_tara_config
from controllers.database import get_engine_and_session
import os, json
import os
from dotenv import load_dotenv
from components.loading_dialog import RoundLoader

# Load .env from the current directory (or specify path as needed)
from dotenv import load_dotenv
load_dotenv()  # ✅ Loads from current working dir by default

config_file_path = None  # Global project config path

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
        P.project_storage_mode = mode  # ✅ Set global mode
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
        self.loader = RoundLoader(self, label_text="Creating project...")
        self.loader.show()
        QApplication.processEvents()

        self.thread = QThread()
        self.worker = ProjectCreationWorker(self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.project_creation_complete)
        self.worker.failed.connect(self.project_creation_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    
    def create_remote_project(self):
        from models import Parameters as P
        from utils.server_connection import (
            fetch_env_from_server, get_db_env_vars,
            create_remote_project_folder, create_remote_config_structure,
            write_remote_tara_config
        )
        from controllers.database import get_engine_and_session, initialize_database
        from urllib.parse import quote_plus
        import json, os, psycopg2

        print("\n🔄 [TARA] Starting remote project creation...\n")

        # 📥 Step 0: Get user input
        project_name = self.project_name_input.text().strip()
        author = self.author_input.text().strip()
        client = self.client_input.text().strip()
        supplier = self.supplier_input.text().strip()
        methodology = self.dropdown.currentText()

        # 🛡️ Step 1: Ensure global .env is present
        local_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../cyphera/.env"))
        if not os.path.exists(local_env_path):
            if not fetch_env_from_server():
                print("❌ Server connection failed. Project creation aborted.")
                return
        env_vars = get_db_env_vars()
        if not env_vars:
            print("❌ Failed to parse .env.")
            return

        # 📁 Step 2: Create remote project structure
        if not create_remote_project_folder(project_name):
            print("❌ Remote project folder creation failed.")
            return
        create_remote_config_structure(project_name)

        # 🛢️ Step 3: Create PostgreSQL DB
        db_user = env_vars.get("DB_USER")
        db_password = env_vars.get("DB_PASSWORD")
        db_host = env_vars.get("DB_HOST")
        db_port = env_vars.get("DB_PORT", "5432")
        password_encoded = quote_plus(db_password)

        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (project_name,))
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE \"{project_name}\"")
                print(f"✅ Created PostgreSQL DB: {project_name}")
            else:
                print(f"ℹ️ Database '{project_name}' already exists.")
            cur.close()
            conn.close()
        except Exception as e:
            print(f"❌ PostgreSQL DB creation failed: {e}")
            return

        # 🧠 Step 4: Store connection info in Parameters
        db_url = f"postgresql://{db_user}:{password_encoded}@{db_host}:{db_port}/{project_name}"
        P.Project_name = project_name
        P.Author_name = author
        P.Client_name = client
        P.Supplier_name = supplier
        P.selected_methedology = methodology
        P.SQLALCHEMY_DATABASE_URL = db_url
        P.project_path = f"{os.getenv('REMOTE_BASE_PATH')}/{project_name}"

        # ⚙️ Step 5: Initialize ORM and session
        get_engine_and_session()
        initialize_database()

        # 📦 Step 6: Write remote .tara config
        tara_config = {
            "project_name": project_name,
            "version": "1.0",
            "author": author,
            "client": client,
            "supplier": supplier,
            "methodology": methodology,
            "dependencies": [],
            "db_url": db_url,
            "project_path": P.project_path
        }
        write_remote_tara_config(project_name, tara_config)

        # 🚀 Step 7: Auto-open newly created project
        local_tara_path = os.path.join("cyphera", "tmp", f"{project_name}.tara")
        self.file_input.setText(local_tara_path)
        # self.open_local_project(local_tara_path)
        self.latest_project_path = local_tara_path

    def open_local_project(self, project_path=None):
        global config_file_path
        project_path = project_path or str(config_file_path)
        print(f"🔍 [DEBUG][LOCAL] Opening: {project_path}")

        try:
            recent_db = Recent_file_DB_creation()
            recent_db.save_project(project_path=project_path)
        except Exception as e:
            print(f"⚠️ [DEBUG][LOCAL] Could not update recent files DB: {e}")

        interfaces.tool_reset_enable = True
        for Tree, (tree_tab, instances) in interfaces.tree_tab_panel.items():
            for i in reversed(range(tree_tab.count())):
                instances.pop(f'{tree_tab.tabText(i)}', None)
                tree_tab.removeTab(i)
        interfaces.tool_reset_enable = False

        database_path = self.get_database_file_path(config_file_path=project_path)
        if not P.SQLALCHEMY_DATABASE_URL:
            P.database_file_path = database_path
            P.SQLALCHEMY_DATABASE_URL = f"sqlite:///{database_path}"

        print(f"🔗 [DEBUG][LOCAL] SQLite URL: {P.SQLALCHEMY_DATABASE_URL}")

        get_engine_and_session()

        for module, module_data in interfaces.sub_modules.items():
            module_data["current_submodule"] = module_data["default_submodule"]
            module_data["module"].on_click()
            module_data["action"]()

        if hasattr(interfaces, "report_panel") and interfaces.report_panel:
            interfaces.report_panel.setHtml("")

        helper.Panel_selector = 'ModuleTab'
        helper.modulePanel_Selector = 'TargetOfEvaluationTab'
        helper.submodulePanel_Selector = 'SystemDescriptionTab'
        interfaces.project_path = project_path

        interfaces.sub_modules[interfaces.default_modules["module"]["name"]]["current_submodule"] = interfaces.default_modules["submodule"]["name"]
        interfaces.previous_mainmodule = interfaces.default_modules["module"]["name"]
        try:
            module_name = interfaces.default_modules["module"]["name"]
            submodule_name = interfaces.default_modules["submodule"]["name"]
            interfaces.previous_module = interfaces.sub_modules[module_name]["submodules"][submodule_name]["frame"]
            print("loader if starting insindie--------------------")

        except KeyError as e:
            print(f"[ERROR] Could not fetch previous_module frame: {e}")
            interfaces.previous_module = None


        interfaces.default_modules["module"]["module_button"].on_click()
        interfaces.default_modules["module"]["module_action"]()
        interfaces.default_modules["submodule"]["submodule_button"].on_click()
        interfaces.default_modules["submodule"]["submodule_action"]()

        print("✅ [DEBUG][LOCAL] Local project fully opened and UI state reset.")

    def create_project_with_config_file(self, selected_base_path, config_extension=".tara", config_data=None):
        from controllers.database import get_engine_and_session
        from models import Parameters as P
        import json
        from pathlib import Path

        project_name = self.project_name_input.text().strip()
        final_path = Path(selected_base_path) / project_name

        # Folder structure
        final_path.mkdir(parents=True, exist_ok=True)
        (final_path / 'config').mkdir(exist_ok=True)
        (final_path / 'README.md').touch()
        (final_path / 'requirements.txt').touch()

        # Database path
        db_file_path = final_path / 'config' / f"{project_name}.db"
        P.database_file_path = db_file_path
        P.SQLALCHEMY_DATABASE_URL = f"sqlite:///{str(db_file_path)}"

        if db_file_path.exists():
            os.chmod(db_file_path, 0o666)
            os.chmod(db_file_path.parent, 0o775)

        get_engine_and_session()
        initialize_database()

        # Config data
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

        config_file_path = final_path / f"{project_name}{config_extension}"
        with config_file_path.open('w') as config_file:
            json.dump(config_data, config_file, indent=4)

        # Store project metadata
        P.project_path = final_path
        P.Project_name = config_data['project_name']
        P.Client_name = config_data['client']
        P.Supplier_name = config_data['supplier']
        P.selected_methodology = config_data['methodology']
        interfaces.project_path = config_file_path

        print(f"✅ Project '{project_name}' created with configuration file at '{config_file_path}'.")

        # Open the project immediately
        self.file_input.setText(str(config_file_path))
        self.open_local_project(str(config_file_path))

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

    def switch_to_default_module(self):
        """
        Handles exact default loading like MainOpenPanel after module setup.
        """
        try:
            interfaces.sub_modules[interfaces.default_modules["module"]["name"]]["current_submodule"] = interfaces.default_modules["submodule"]["name"]
            interfaces.previous_mainmodule = interfaces.default_modules["module"]["name"]
            try:
                module_name = interfaces.default_modules["module"]["name"]
                submodule_name = interfaces.default_modules["submodule"]["name"]
                interfaces.previous_module = interfaces.sub_modules[module_name]["submodules"][submodule_name]["frame"]
            except KeyError as e:
                print(f"[ERROR] Could not fetch previous_module frame: {e}")
                interfaces.previous_module = None


            interfaces.default_modules["module"]["module_button"].on_click()
            interfaces.default_modules["module"]["module_action"]()
            interfaces.default_modules["submodule"]["submodule_button"].on_click()
            interfaces.default_modules["submodule"]["submodule_action"]()
        except Exception as e:
            print("[ERROR] Sidebar render failure (default switch):", e)

    def get_database_file_path(self, config_file_path):
        """
        Given a .tara config file path, locate the associated SQLite DB path.
        """
        try:
            with open(config_file_path, 'r') as f:
                config_data = json.load(f)
                project_name = config_data.get("project_name", "")
                project_root = os.path.dirname(config_file_path)
                return os.path.join(project_root, "config", f"{project_name}.db")
        except Exception as e:
            print(f"[ERROR] Failed to read config file for DB path: {e}")
            return ""

    def project_creation_complete(self):
        if hasattr(self, "loader") and self.loader:
            self.loader.hide()

        # ✅ Run open_local_project from here — in main thread!
        if hasattr(self, "latest_project_path") and self.latest_project_path:
            self.file_input.setText(self.latest_project_path)
            self.open_local_project(self.latest_project_path)


    def project_creation_failed(self, error_message):
        print(f"[ERROR] Project creation failed: {error_message}")
        if hasattr(self, "loader") and self.loader:
            self.loader.hide()
        QMessageBox.critical(self, "Error", f"Project creation failed:\n{error_message}")


class ProjectCreationWorker(QObject):
    finished = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, panel):
        super().__init__()
        self.panel = panel
        self.result_path = None  # store output path

    def run(self):
        try:
            if self.panel.storage_mode == 'cloud':
                from pathlib import Path
                project_name = self.panel.project_name_input.text().strip()
                self.panel.create_remote_project()  # 🔁 update to NOT touch UI inside
                self.result_path = os.path.join("cyphera", "tmp", f"{project_name}.tara")
            else:
                from pathlib import Path
                self.panel.create_project_with_config_file(Path(self.panel.file_input.text()))
                self.result_path = str(self.panel.file_input.text())
            self.finished.emit()
        except Exception as e:
            self.failed.emit(str(e))
