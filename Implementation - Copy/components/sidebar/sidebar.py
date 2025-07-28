"""
Module: Sidebar Module Selector      \n 
File: sidebar.py      \n
Layer: UI / Sidebar Navigation Layer      \n
Component ID: CY_CO_016      \n
Requirement IDs:      \n
Author: Vijay      \n
Created On: 2025-05-21     \n
Updated By: Vishnu Viswanath  \n
Updated On: 2025-05-28   \n
Version: V 3.0      \n

Purpose:
--------
Provides a dynamic sidebar UI for navigating between application modules and submodules,
leveraging JSON configuration for rendering structure and permissions.

Description:
------------
This module defines the `Sidebar` widget using PyQt5, capable of:
- Loading a hierarchical module-submodule structure from a JSON file
- Filtering based on 'enabled' and 'licensed' flags
- Displaying modules with customizable labels and icons
- Emitting structured signals when a submodule is selected

Responsibilities
----------------
- Load and parse sidebar navigation data from a JSON source
- Dynamically render buttons for each submodule with associated icons
- Emit selection events with structured payloads for integration with parent components

Signals
-------
+---------------------+----------------------+-----------------------------+--------------------------+
| Trigger             | Signal Origin        | Description                 | Payload Format           |
+=====================+======================+=============================+==========================+
| Submodule clicked   | emit_submodule_signal| Sends submodule info        | Dict with sender, data   |
+---------------------+----------------------+-----------------------------+--------------------------+

Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore, QtGui)
- utils.file_utils
- styles.sub_module_style
- JSON for sidebar structure

Limitations
-----------
- No live reloading of sidebar from updated JSON
- No deep validation of JSON format
- No user role-based filtering

Improvements
------------
- Add live refresh capability for JSON updates
- Introduce user-role specific access control
- Allow sorting or reordering of modules/submodules via config

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-05-28           | Moved sidebar to components/submodule/ | Vishnu Viswanath     |
+----------------+----------------------+----------------------------------------+----------------------+
| V 3.0          | 2025-05-21           | Initial version created                | Vijay                |
+----------------+----------------------+----------------------------------------+----------------------+
| V 3.0          | 2025-06-12           | Implemented load                       | Vijaya Karagi        |
|                |                      | modules/submodules/profile/settings    |                      |
|                |                      | from JSON file and integrated          |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

import os
import json
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QSpacerItem, QSizePolicy, QFrame, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QIcon

import utils.interface_utils as interfaces
import components.sidebar.views.load_modules as load_modules_view
import components.sidebar.views.load_profile as load_profile_view
import components.sidebar.views.load_settings as load_settings_view


class Sidebar(QWidget):
    """
    Sidebar widget that loads a module/submodule tree from a JSON file
    and emits a structured signal when a submodule button is clicked.

    Attributes:
        module_selected (pyqtSignal): Signal emitted with a dictionary payload 
            when a module is selected. Used for inter-module communication.
        submodule_selected (pyqtSignal): Signal emitted with a dictionary payload 
            when a submodule is selected. Used for inter-module communication.
    """

    module_selected = pyqtSignal(dict)
    submodule_selected = pyqtSignal(dict)

    def __init__(self, module_json_path="data/modules.json", profile_json_path="data/profile.json", settings_json_path="data/settings.json", parent=None):
        """
        Initializes the Sidebar UI.

        Args:
            module_json_path (str): Path to the JSON file that defines the module structure.
            profile_json_path (str): Path to the JSON file that defines the module structure.
            settings_json_path (str): Path to the JSON file that defines the module structure.
        """
        super().__init__(parent)
        self.module_json_path = module_json_path
        self.profile_json_path = profile_json_path
        self.settings_json_path = settings_json_path
        self.frames = {}
        self.module_sidebar = self.parent().module_layout
        self.submodule_sidebar = self.parent().submodule_layout
        self.action = self.parent().Action_layer
        load_modules_view.load_modules(self)
        load_profile_view.load_profile(self)
        load_settings_view.load_settings(self)

    def emit_module_signal(self, test, module_name):
        current = interfaces.default_modules.get("module", {}).get("name")
        if current == module_name:
            print(f"[Sidebar] Module '{module_name}' already active – skipping emit.")
            return

        existing = interfaces.default_modules.get("module", {})
        interfaces.default_modules["module"] = {
            "name": module_name,
            "module_button": existing.get("module_button"),
            "module_action": existing.get("module_action")
        }


        payload = {
            "sender": "Sidebar",
            "event": "module_clicked",
            "data": {
                "type": "module",
                "module": module_name,
                "data": interfaces.sub_modules.get(module_name, {})
            }
        }

        self.module_selected.emit(payload)
        print(f"📂 Emitting signal for module: {module_name}")


    def emit_submodule_signal(self, test, module_name, sub, frame):
        submodule_name = sub.get("name")
        current = interfaces.sub_modules.get(module_name, {}).get("current_submodule")

        # Only call load_data if switching to a different submodule
        if current != submodule_name:
            # Show the new widget/frame
            self.action.setCurrentWidget(frame)
            
            # Only load data if this submodule was not already active
            if hasattr(frame, "load_data") and callable(frame.load_data):
                try:
                    frame.load_data()
                    print(f"[Sidebar] load_data() called for submodule: {submodule_name}")
                except Exception as e:
                    print(f"[Sidebar] Failed to load submodule data for {submodule_name}: {e}")

            # Update the current active submodule
            interfaces.sub_modules[module_name]["current_submodule"] = submodule_name
            print(f"📂 Emitting signal for submodule: {submodule_name} in module: {module_name}")
        else:
            # Still switch widget for UI consistency, but don't reload
            self.action.setCurrentWidget(frame)
            print(f"[Sidebar] Submodule '{submodule_name}' already active in module '{module_name}' – skipping emit and reload.")




