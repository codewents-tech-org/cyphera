

import os
import json
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QSpacerItem, QSizePolicy, QFrame, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QIcon
import importlib

from controllers.database import get_engine_and_session
from utils import file_utils as files
from styles import main_module_style
from styles import sub_module_style
import components.main_module_panel as main_module_window
import components.sub_module_panel as sub_module_panel
import utils.interface_utils as interfaces

def load_modules(self):
    """
    Loads modules and their submodules from the JSON file
    and dynamically creates corresponding UI labels and buttons.

    - Only 'enabled' and 'licensed' modules/submodules are shown.
    - Widget classes are NOT instantiated until user clicks.
    """
    import importlib
    if not os.path.exists(self.module_json_path):
        print(f"[Sidebar] JSON not found: {self.module_json_path}")
        return

    try:
        with open(self.module_json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"[Sidebar] JSON error: {e}")
        return

    try:
        # Add Home tab/button
        button = main_module_window.ModuleTabButton(
            "assets/Images/Home.svg", "Home",
            lambda test=True, m="Home": self.emit_module_signal(test, m)
        )
        button.setIconSize(QSize(40, 40))
        self.module_sidebar.addWidget(button, alignment=Qt.AlignTop)
       

        # Dict to track instantiated widget per submodule name
        if not hasattr(self, "_widget_instances"):
            self._widget_instances = {}

        for idx, module in enumerate(data.get("modules", [])):
            if module.get("enabled") and module.get("licensed"):
                module_name = module.get("name", "").strip()
                module_icon = module.get("icon", "").strip()
                button = main_module_window.ModuleTabButton(
                    module_icon, module_name,
                    lambda test=True, m=module_name: self.emit_module_signal(test, m)
                )
                button.setIconSize(QSize(40, 40))
                self.module_sidebar.addWidget(button, alignment=Qt.AlignTop)

                # Module container (sidebar left)
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
                if idx == 0:
                    interfaces.default_modules["module"] = {
                        "name": module_name,
                        "module_button": button,
                        "module_action": lambda test=True, m=module_name: self.emit_module_signal(test, m)
                    }

                for index, sub in enumerate(module.get("submodules", [])):
                    if sub.get("enabled") and sub.get("licensed"):
                        name = sub.get("name", "").strip()
                        if not name:
                            print(f"[Sidebar] Skipping submodule with missing or empty name in module '{module['name']}'")
                            continue

                        try:
                            module_path = sub.get("file", "").strip()
                            class_name = sub.get("class", "").strip()
                            module_file = importlib.import_module(module_path)
                            module_class = getattr(module_file, class_name)
                            self.frames[name] = module_class  # store class, not instance

                            # Submodule button click handler
                            def submodule_click_handler(test=True, m=module_name, s=sub, n=name):
                                # Lazy instantiate widget on first click
                                if n not in self._widget_instances:
                                    self._widget_instances[n] = self.frames[n]()  # Create instance
                                    self.action.addWidget(self._widget_instances[n])
                                widget = self._widget_instances[n]
                                self.action.setCurrentWidget(widget)  # Switch to this widget

                                # Always call load_data (even if re-clicking same tab) for refresh
                                if hasattr(widget, "load_data") and callable(widget.load_data):
                                    try:
                                        widget.load_data()
                                        print(f"[Sidebar] load_data() called for submodule: {n}")
                                    except Exception as e:
                                        print(f"[Sidebar] Failed to load submodule data for {n}: {e}")

                                # Update current submodule pointer (if used)
                                interfaces.sub_modules[m]["current_submodule"] = n


                            sub_btn = sub_module_panel.SubModuleTabButton(name, submodule_click_handler)
                            module_layout.addWidget(sub_btn, alignment=Qt.AlignLeft)

                            # Add to interface dict (use click handler, not lambda with frame)
                            interfaces.sub_modules[module["name"]]['submodules'][name] = {
                                "name": name,
                                "button": sub_btn,
                                "action": submodule_click_handler,  # updated
                                "frame": None   # instance set at runtime
                            }
                            if interfaces.sub_modules[module["name"]]["default_submodule"] is None:
                                interfaces.sub_modules[module["name"]]["current_submodule"] = name
                                interfaces.sub_modules[module["name"]]["default_submodule"] = name

                                if idx == 0:
                                    interfaces.default_modules["submodule"] = {
                                        "name": name,
                                        "submodule_button": sub_btn,
                                        "submodule_action": submodule_click_handler
                                    }

                            print(f"[Sidebar] Adding submodule: {name} in module: {module_name}")

                        except (ImportError, AttributeError) as e:
                            print(f"[Sidebar] Error loading submodule '{name}' in module '{module_name}': {e}")
                            continue
    
        # Add spacer to fill vertical space
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        spacer.setStyleSheet(main_module_style.spacer_style)
        self.module_sidebar.addWidget(spacer)

    except Exception as e:
        print(f"[Sidebar] Error loading modules: {e}")
        QMessageBox.critical(self, "Error", f"Failed to load modules:\n{str(e)}")
