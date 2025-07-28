

import os
import json
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QSpacerItem, QSizePolicy, QFrame, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QIcon
import importlib

from utils import file_utils as files
from styles import main_module_style
from styles import sub_module_style
import components.main_module_panel as main_module_window
import components.sub_module_panel as sub_module_panel
import utils.interface_utils as interfaces

def load_profile(self):
    """
    Loads profile and their submodules from the JSON file
    and dynamically creates corresponding UI labels and buttons.

    Behavior:
        - Only 'enabled' and 'licensed' modules/submodules are shown.
        - Icons are set using attributes from file_utils.

    Assumptions:
        - JSON must contain valid keys like 'name', 'enabled', 'licensed', 'icon', 'file', 'class'.
        - Icons referenced must be defined in file_utils.

    Limitations:
        - No JSON schema validation
        - No support for dynamic module refresh
    """
    if not os.path.exists(self.profile_json_path):
        print(f"[Sidebar] JSON not found: {self.profile_json_path}")
        return

    try:
        with open(self.profile_json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"[Sidebar] JSON error: {e}")
        return

    try:
        for idx, module in enumerate(data.get("Profile", [])):
            if module.get("enabled") and module.get("licensed"):
                module_name = module.get("name", "").strip()
                module_icon = module.get("icon", "").strip()
                button = main_module_window.ModuleTabButton(module_icon, module_name, lambda test=True, m=module_name: self.emit_module_signal(test, m))
                button.setIconSize(QSize(40, 40))  # Adjust icon size if needed
                self.module_sidebar.addWidget(button, alignment=Qt.AlignTop)

                # 🔲 Create a container frame for each module
                module_frame = QFrame()
                module_frame.setStyleSheet("border: None;")
                module_layout = QVBoxLayout(module_frame)
                module_layout.setContentsMargins(0, 0, 0, 0)
                module_layout.setSpacing(0)

                mod_label = QLabel(module_name)
                mod_label.setAlignment(Qt.AlignLeft)
                mod_label.setStyleSheet(sub_module_style.sub_module_label_style)
                module_layout.addWidget(mod_label)
                self.submodule_sidebar.addWidget(module_frame)

                interfaces.sub_modules[module_name] = {
                    "name": module_name,
                    "module": button,
                    "action": lambda test=True, m=module_name: self.emit_module_signal(test, m),
                    "label": mod_label,
                    "frame": module_frame,
                    "submodules": {},
                    "default_submodule": None,
                    "current_submodule": None
                }
                
                for index, sub in enumerate(module.get("submodules", [])):
                    if sub.get("enabled") and sub.get("licensed"):
                        name = sub.get("name", "").strip()
                        if not name:
                            print(f"[Sidebar] Skipping submodule with missing or empty name in module '{module['name']}'")
                            continue

                        try:
                            # Check if the submodule already exists in frames
                            # Dynamically import the module and class
                            module_path = sub.get("file", "").strip()
                            class_name = sub.get("class", "").strip()
                            module_file = importlib.import_module(module_path)
                            module_class = getattr(module_file, class_name)
                            self.frames[name] = module_class()
                            sub_btn = sub_module_panel.SubModuleTabButton(name, lambda test=True, m=module_name, s=sub, f=self.frames[name]: self.emit_submodule_signal(test, m, s, f))
                            module_layout.addWidget(sub_btn, alignment=Qt.AlignLeft)
                            self.action.addWidget(self.frames[name])

                            # Add submodule to interfaces
                            interfaces.sub_modules[module["name"]]['submodules'][name] = {
                                "name": name,
                                "button": sub_btn,
                                "action": lambda test=True, m=module_name, s=sub, f=self.frames[name]: self.emit_submodule_signal(test, m, s, f),
                                "frame": self.frames[name]
                            }
                            if index == 0: 
                                interfaces.sub_modules[module["name"]]["current_submodule"] = name
                                interfaces.sub_modules[module["name"]]["default_submodule"] = name
                                
                            print(f'''[Sidebar] Adding submodule: {name} in module: {module_name}''')

                        except (ImportError, AttributeError) as e:
                            print(f"[Sidebar] Error loading submodule '{name}' in module '{module_name}': {e}")
                            continue

    except Exception as e:
        print(f"[Sidebar] Error loading profile: {e}")
        QMessageBox.critical(None, "Error", f"Failed to load profile:\n{str(e)}")