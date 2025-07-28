"""
Module: Module Toolbar Panel     \n  
File: module_toolbar.py      \n  
Layer: UI / Toolbar Component Layer       \n 
Component ID: CY_CO_017       \n  
Requirement IDs:        \n 
Author: Vijay         \n
Created On: 2025-05-22        \n 
Updated By: Vishnu Viswanath  \n
Updated On: 2025-05-28  \n
Version: V 3.0       \n

Purpose:
--------
Provides a reusable top toolbar component for all modules in the TARA Tool, supporting standardized buttons and emitting structured signals for centralized event handling.

Description:
------------
Encapsulates toolbar construction using `QToolBar` and `QToolButton` to ensure consistent layout and behavior across modules. 
Supports dynamic button addition and event emission using a shared signal bus.

Responsibilities
----------------
- Generate and style a toolbar per module
- Attach button signals for centralized action dispatch
- Assign button instances dynamically to the parent UI for external control

Signals
-------
+---------------------+-------------------+-----------------------------+-------------------------------------------------------------------------+
| Trigger             | Signal Name       | Description                 | Payload Format                                                          |
+=====================+===================+=============================+=========================================================================+
| Button clicked      | action_triggered  | Triggered by toolbar button | {"sender": "Toolbar", "event": "<type>", "data": {"target": "current"}} |
+---------------------+-------------------+-----------------------------+-------------------------------------------------------------------------+


Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore, QtGui)
- styles.toolbar_style
- utils.file_utils
- logging

Limitations
-----------
- Toolbar does not yet support runtime button visibility toggling
- Requires parent widget to support `setattr()` for attaching button references
- Assumes existence of valid icon/style keys in external modules

Improvements
------------
- Add runtime enable/disable functionality for buttons
- Support alignment customization (left/center/right)
- Allow dynamic tooltip updates
- Extend signal payload with contextual metadata

Change History:
---------------
+----------------+----------------------+---------------------------------------------------+----------------------+
| Version        | Date                 | Change                                            | Author               |
+================+======================+===================================================+======================+
| V 3.0          | 2025-05-28           | Moved module_toolbar to components/submodule/     | Vishnu Viswanath     |
+----------------+----------------------+---------------------------------------------------+----------------------+
| V 3.0          | 2025-05-22           | Initial version created                           | Vijay                |
+----------------+----------------------+---------------------------------------------------+----------------------+
|                |                      |                                                   |                      |
+----------------+----------------------+---------------------------------------------------+----------------------+
|                |                      |                                                   |                      |
+----------------+----------------------+---------------------------------------------------+----------------------+
"""


import logging
from PyQt5.QtCore import Qt, QSize, QObject, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QToolBar, QToolButton, QSizePolicy

from styles import toolbar_style
from utils import file_utils as files

logger = logging.getLogger(__name__)


class ToolbarEventBus(QObject):
    """
    Global signal bus for emitting toolbar actions.

    Signals:
        action_triggered (dict): Structured signal triggered on any toolbar button click.
            Payload includes:
                - sender (str): always "Toolbar"
                - event (str): button type like "add", "submit"
                - data (dict): optional metadata (e.g., target="current")
    """
    action_triggered = pyqtSignal(dict)


# Shared instance of the event bus
toolbar_signals = ToolbarEventBus()

class ModuleToolbarBuilder:
    """
    Builder class for constructing standardized toolbars for modules.
    """

    @staticmethod
    def create_toolbar(parent: QWidget, label_text: str, buttons: list = None) -> QToolBar:
        """
        Creates a reusable and styled toolbar.

        Args:
            parent (QWidget): Parent widget (module UI container).
            label_text (str): Label displayed on the toolbar's left.
            buttons (list, optional): List of button types to include.

        Returns:
            QToolBar: The fully functional toolbar instance.
        """
        logger.info("Creating toolbar for: %s with buttons: %s", label_text, buttons)
        print(f"[TOOLBAR INIT] '{label_text}' with buttons: {buttons}")
        
        buttons = buttons or ['add', 'submit', 'delete']
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setStyleSheet(toolbar_style.toolbar_style)

        # Navigation Icon (left arrow)
        icon_button = QToolButton()
        icon_button.setIcon(QIcon(files.path_arrow_icon))
        icon_button.setIconSize(QSize(18, 18))
        icon_button.setStyleSheet(toolbar_style.toolbar_arrow_style)
        toolbar.addWidget(icon_button)

        # Toolbar label
        label = QLabel(label_text)
        label.setStyleSheet(toolbar_style.toolbar_label_style)
        toolbar.addWidget(label)

        # Spacer between label and buttons
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
        toolbar.addWidget(spacer)

        # Button type map
        button_map = {
            "add":      ("add_icon", " Add", "add_button"),
            "submit":   ("submit_icon", " Submit", "submit_button", "tree_submit_button"),
            "delete":   ("delete_icon", " Delete", "delete_button"),
            "generate": ("submit_icon", " Generate", "generate_button"),
            "download": ("download_icon", " Download", "download_button"),
        }

        # Create each button
        for btn_key in buttons:
            if btn_key not in button_map:
                logger.warning("Unsupported toolbar button: %s", btn_key)
                continue

            icon_name, btn_text, *attr_names = button_map[btn_key]

            button = QToolButton()
            button.setIcon(QIcon(getattr(files, icon_name)))
            button.setText(btn_text)
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            button.setStyleSheet(toolbar_style.toolbar_button_style)

            # Attach button reference to parent
            for attr in attr_names:
                setattr(parent, attr, button)

            # Emit signal on button click
            def emit_toolbar_signal(_checked=False, action=btn_key):
                payload = {
                    "sender": "Toolbar",
                    "event": action,
                    "data": {"target": "current"}
                }
                print(f"[SIGNAL EMIT] {payload}")
                toolbar_signals.action_triggered.emit(payload)

            button.clicked.connect(emit_toolbar_signal)
            toolbar.addWidget(button)
            toolbar.addWidget(ModuleToolbarBuilder._create_small_spacer())

        return toolbar


    def _create_small_spacer() -> QWidget:
        """
         Adds spacing between toolbar buttons.

        Returns:
            QWidget: Spacer widget with fixed width.
        """
        spacer = QWidget()
        spacer.setFixedWidth(10)
        spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
        return spacer
