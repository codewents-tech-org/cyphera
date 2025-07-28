import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QPushButton,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem, QScrollArea, QListWidget,
    QListWidgetItem, QButtonGroup
)
from PyQt5.QtCore import Qt
from pathlib import Path
import qtawesome as qta
from controllers.database import get_engine_and_session
import models.ScrollBarStyle as SBS
import utils.interface_utils as interfaces
from models import helper
from styles import home_style
import models.Parameters as P
from utils.server_connection import connect_postgres_and_print_tables, get_sftp, list_cloud_folders_with_sftp, list_cloud_files_with_sftp
from urllib.parse import quote_plus
from Home.controller.Recent_file_database_creation import Recent_file_DB_creation
class MainOpen_Panel(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__()
        helper.homePanel_selector = 'OpenTab'
        self.storage_mode = "local"
        self.selected_cloud_folder = None
        self.selected_cloud_file = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignTop)

        # --- Card-like Content Wrapper (MATCH NEW PANEL) ---
        content_wrapper = QWidget()
        content_wrapper.setStyleSheet("background-color: #FFFFFF; border: 2px solid #E3E5EC; border-radius: 8px;")
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(15)
        content_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(content_wrapper)

        # --- Title
        self.label = QLabel("Open Project")
        self.label.setStyleSheet(home_style.main_label_stye)
        self.label.setAlignment(Qt.AlignLeft)
        content_layout.addWidget(self.label)

        # --- Toggle
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

        # --- Local File Browse Widget (WRAPPED) ---
        self.file_browse_widget = QWidget()
        file_browse_layout = QHBoxLayout(self.file_browse_widget)
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
        content_layout.addWidget(self.file_browse_widget)

        # --- Cloud folder/file areas ---
        self.cloud_folder_area = QScrollArea()
        self.cloud_folder_area.setFixedHeight(300)
        self.cloud_folder_area.setVisible(False)
        self.cloud_folder_area.setStyleSheet(
            "border: 1px solid #E3E5EC; border-radius: 8px; background: #fafbfc; padding:6px;" +
            SBS.Scrollbar_ScrollingBar_style
        )
        self.cloud_folder_list = QListWidget()
        self.cloud_folder_list.setStyleSheet("""
            border: none;
            font-size: 16px;
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
                background: transparent;
            }
        """)
        self.cloud_folder_list.itemClicked.connect(self.on_cloud_folder_clicked)
        self.cloud_folder_area.setWidgetResizable(True)
        self.cloud_folder_area.setWidget(self.cloud_folder_list)
        content_layout.addWidget(self.cloud_folder_area)

        self.cloud_file_area = QScrollArea()
        self.cloud_file_area.setFixedHeight(300)
        self.cloud_file_area.setVisible(False)
        self.cloud_file_area.setStyleSheet("""
            border: none;
            font-size: 16px;
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
                background: transparent;
            }
        """)

                # --- Selected Folder Label (above files list) ---
        self.selected_folder_label = QLabel("")
        self.selected_folder_label.setStyleSheet("font-weight: 600; font-size: 18px; color: #333; margin-bottom: 6px; color : #17CFCE;")
        self.selected_folder_label.setVisible(False)
        content_layout.addWidget(self.selected_folder_label)

        self.cloud_file_list = QListWidget()
        self.cloud_file_list.setStyleSheet("border: none; font-size: 16px;")
        self.cloud_file_list.itemClicked.connect(self.on_cloud_file_clicked)
        self.cloud_file_area.setWidgetResizable(True)
        self.cloud_file_area.setWidget(self.cloud_file_list)
        content_layout.addWidget(self.cloud_file_area)

        # --- Button Layout
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        self.open_button = QPushButton("Open")
        self.open_button.setStyleSheet(home_style.main_panel_button_style)
        self.open_button.setFixedWidth(200)
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self.Open_Project)
        button_layout.addWidget(self.open_button)
        content_layout.addLayout(button_layout)

        # Input field behavior
        self.file_input.textChanged.connect(self.check_input_fields)
        content_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def set_storage_mode(self, mode):
        self.storage_mode = mode
        self.update_toggle_button_styles()
        if mode == 'cloud':
            self.file_browse_widget.setVisible(False)
            self.cloud_folder_area.setVisible(True)
            self.cloud_file_area.setVisible(False)
            self.open_button.setEnabled(False)
            self.selected_folder_label.setVisible(False)   # <--- Add this
            self.load_cloud_folders()
        else:
            self.file_browse_widget.setVisible(True)
            self.cloud_folder_area.setVisible(False)
            self.cloud_file_area.setVisible(False)
            self.open_button.setEnabled(False)
            self.file_input.clear()
            self.selected_folder_label.setVisible(False)   # <--- Add this


    def update_toggle_button_styles(self):
        if self.storage_mode == 'local':
            self.local_button.setStyleSheet(home_style.toggle_button_active_style)
            self.cloud_button.setStyleSheet(home_style.toggle_button_inactive_style)
        else:
            self.local_button.setStyleSheet(home_style.toggle_button_inactive_style)
            self.cloud_button.setStyleSheet(home_style.toggle_button_active_style)

    def load_cloud_folders(self):
        self.cloud_folder_list.clear()
        try:
            transport, sftp = get_sftp()
            folders = list_cloud_folders_with_sftp(sftp)
            for folder in folders:
                item = QListWidgetItem(folder)
                icon = qta.icon('fa.folder')
                item.setIcon(icon)
                self.cloud_folder_list.addItem(item)
            sftp.close()
            transport.close()
        except Exception as e:
            print("[Cloud SFTP] Error loading folders:", e)

    def on_cloud_folder_clicked(self, item):
        folder = item.text()
        self.selected_cloud_folder = folder
        self.selected_folder_label.setText(f"{folder}")
        self.selected_folder_label.setVisible(True)
        self.load_cloud_files(folder)


    def load_cloud_files(self, folder):
        self.cloud_file_list.clear()
        self.cloud_file_area.setVisible(True)
        try:
            transport, sftp = get_sftp()
            files = list_cloud_files_with_sftp(sftp, folder)
            for file in files:
                item = QListWidgetItem(file)
                if '.' not in file:
                    icon = qta.icon('fa.folder')
                elif file.endswith('.tara'):
                    icon = qta.icon('fa.file')
                else:
                    icon = qta.icon('fa.file-o')
                item.setIcon(icon)
                self.cloud_file_list.addItem(item)
            sftp.close()
            transport.close()
        except Exception as e:
            print(f"[Cloud SFTP] Error loading files in {folder}:", e)

    def on_cloud_file_clicked(self, item):
        file = item.text()
        if file.endswith('.tara'):
            self.selected_cloud_file = file
            self.open_button.setEnabled(True)
        else:
            self.selected_cloud_file = None
            self.open_button.setEnabled(False)

    def check_input_fields(self):
        if self.storage_mode == "local":
            self.open_button.setEnabled(Path(self.file_input.text()).exists())
        # cloud mode: open button enabled only on valid .tara file select

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "TARA Project (*.tara);;Text Files (*.txt)")
        if file_path:
            self.file_input.setText(file_path)

    
    def Open_Project(self):
        if self.storage_mode == "local":
            self.open_local_project()
        else:
            self.open_cloud_project()

    def open_local_project(self):
        project_path = self.file_input.text()
        print(f"🔍 [DEBUG][LOCAL] Opening: {project_path}")

        # 1. Update recent file DB (if used)
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

        # 3. Get DB path and set SQLAlchemy URL
        database_path = self.get_database_file_path(config_file_path=project_path)
        P.database_file_path = database_path
        P.SQLALCHEMY_DATABASE_URL = f"sqlite:///{database_path}"
        print(f"🔗 [DEBUG][LOCAL] SQLite URL: {P.SQLALCHEMY_DATABASE_URL}")

        get_engine_and_session()  # Rebuild SQLAlchemy connection
        # initialize_database()  # If ORM tables needed

        # 4. Reset/activate all modules and panels for new project
        for module, module_data in interfaces.sub_modules.items():
            module_data["current_submodule"] = module_data["default_submodule"]
            module_data["module"].on_click()
            module_data["action"]()

        if hasattr(interfaces, "report_panel") and interfaces.report_panel:
            interfaces.report_panel.setHtml("")

        # 5. Store project path in global helpers
        helper.Panel_selector = 'ModuleTab'
        helper.modulePanel_Selector = 'TargetOfEvaluationTab'
        helper.submodulePanel_Selector = 'SystemDescriptionTab'
        interfaces.project_path = project_path

        # 6. Set first/default button as active by default
        interfaces.sub_modules[interfaces.default_modules["module"]["name"]]["current_submodule"] = interfaces.default_modules["submodule"]["name"]
        interfaces.default_modules["module"]["module_button"].on_click()
        interfaces.default_modules["module"]["module_action"]()
        interfaces.default_modules["submodule"]["submodule_button"].on_click()
        interfaces.default_modules["submodule"]["submodule_action"]()

        print("✅ [DEBUG][LOCAL] Local project fully opened and UI state reset.")


    def open_cloud_project(self):
        """Open a cloud project (.tara), set up PostgreSQL connection, and fully reset tool state."""
        try:
            # 1. Download .tara config from SFTP and parse
            transport, sftp = get_sftp()
            os.makedirs("cyphera/tmp", exist_ok=True)
            local_tmp_path = os.path.join("cyphera", "tmp", self.selected_cloud_file)
            remote_path = os.getenv("REMOTE_BASE_PATH") + f"/{self.selected_cloud_folder}/{self.selected_cloud_file}"
            print(f"🔍 [DEBUG][CLOUD] Downloading .tara from: {remote_path} -> {local_tmp_path}")
            sftp.get(remote_path, local_tmp_path)
            with open(local_tmp_path, "r") as f:
                tara_data = json.load(f)
                print(f"🔍 [DEBUG][CLOUD] .tara file contents: {tara_data}")
                db_name = tara_data.get("project_name") or tara_data.get("db_name")
                print(f"🔍 [DEBUG][CLOUD] Project/DB name read from .tara: {db_name}")
            sftp.close()
            transport.close()
        except Exception as e:
            print(f"❌ [DEBUG][CLOUD] Could not fetch/read cloud .tara: {e}")
            return

        if not db_name:
            print("❌ [DEBUG][CLOUD] Could not determine DB name from .tara.")
            return

        # 2. Build PostgreSQL DB URL
        from utils.server_connection import get_db_env_vars
        env_vars = get_db_env_vars()
        db_user = env_vars.get("DB_USER")
        db_password = env_vars.get("DB_PASSWORD")
        db_host = env_vars.get("DB_HOST")
        db_port = env_vars.get("DB_PORT", "5434")
        from urllib.parse import quote_plus
        password_encoded = quote_plus(db_password)
        db_url = f"postgresql://{db_user}:{password_encoded}@{db_host}:{db_port}/{db_name}"
        P.SQLALCHEMY_DATABASE_URL = db_url
        print(f"🔗 [DEBUG][CLOUD] Set SQLAlchemy URL: {P.SQLALCHEMY_DATABASE_URL}")

        # 3. Reset tool state, remove all tabs, panels, etc. (same as local)
   
        interfaces.tool_reset_enable = True
        for Tree, (tree_tab, instances) in interfaces.tree_tab_panel.items():
            for i in reversed(range(tree_tab.count())):
                instances.pop(f'{tree_tab.tabText(i)}', None)
                tree_tab.removeTab(i)
        interfaces.tool_reset_enable = False

        # 4. Establish SQLAlchemy/Postgres connection
        get_engine_and_session()

        # 5. Reset/activate all modules and panels for new project (just like local)
        for module, module_data in interfaces.sub_modules.items():
            module_data["current_submodule"] = module_data["default_submodule"]
            module_data["module"].on_click()
            module_data["action"]()

        if hasattr(interfaces, "report_panel") and interfaces.report_panel:
            interfaces.report_panel.setHtml("")

        # 6. Store project path in global helpers
        # You might want to store the cloud path or some cloud meta, up to you.
        helper.Panel_selector = 'ModuleTab'
        helper.modulePanel_Selector = 'TargetOfEvaluationTab'
        helper.submodulePanel_Selector = 'SystemDescriptionTab'
        interfaces.project_path = f"/cloud/{self.selected_cloud_folder}/{self.selected_cloud_file}"

        # 7. Set first/default button as active by default
        interfaces.sub_modules[interfaces.default_modules["module"]["name"]]["current_submodule"] = interfaces.default_modules["submodule"]["name"]
        interfaces.default_modules["module"]["module_button"].on_click()
        interfaces.default_modules["module"]["module_action"]()
        interfaces.default_modules["submodule"]["submodule_button"].on_click()
        interfaces.default_modules["submodule"]["submodule_action"]()

        print("✅ [DEBUG][CLOUD] Cloud project fully opened and UI state reset.")



    def get_database_file_path(self, config_file_path):
        # Read the configuration file to get the project name
        if not Path(config_file_path).exists():
            raise FileNotFoundError(f"Configuration file '{config_file_path}' not found.")
        
        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
        
        # Extract the project name from the config data
        project_name = config_data.get("project_name")
        author_name = config_data.get("author")
        client_name = config_data.get("client") if "client" in config_data else "client"
        supplier_name = config_data.get("supplier") if "supplier" in config_data else "supplier"
        methedology_used = config_data.get("methodology")
        if not project_name: raise ValueError("Project name not found in the configuration file.")
        if not author_name: raise ValueError("Author name not found in the configuration file.")
        if not client_name: raise ValueError("Client name not found in the configuration file.")
        if not supplier_name: raise ValueError("Supplier name not found in the configuration file.")
        if not methedology_used: raise ValueError("Methedology not found in the configuration file.")

        P.Project_name = project_name
        P.Author_name = author_name
        P.Client_name = client_name
        P.Supplier_name = supplier_name
        P.selected_methedology = methedology_used

        # Construct the path to the database file
        base_path = Path(config_file_path).parent
        db_file_path = base_path / 'config' / f"{project_name}.db"
        report_dir = base_path / 'report'
        report_dir.mkdir(parents=True, exist_ok=True)
        P.project_path = base_path
        P.GenerateReport_path = f"{report_dir}/{project_name}_word_Report.docx"
        P.GeneratePdfReport_path = f"{report_dir}/{project_name}_Report.pdf"
        
        return db_file_path

