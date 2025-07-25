
from PyQt5.QtWidgets import QToolTip, QPushButton
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QSize
import models.update_svg as update_svg

import styles.main_module_style as main_module_style

class ModuleTabButton(QPushButton):
    active_button = None  # Class-level variable to track the active tab

    def __init__(self, icon_path, tooltip_text, action, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.inactive_icon_path = self.icon_path  # Default path for the inactive state
        self.active_icon_path = icon_path  # Default path for the active state

        # Set initial icon and style
        self.setIcon(QIcon(self.inactive_icon_path))
        self.setIconSize(QSize(24, 24))
        self.setFixedHeight(70)
        self.setCursor(QCursor(Qt.PointingHandCursor))  # Change the cursor to pointing hand
        self.setToolTip(tooltip_text)  # Set the tooltip text
        QToolTip.setFont(main_module_style.main_module_tooltip_style)

        # Update inactive state initially
        self.update_icon_and_style(active=False)

        # Connect signals
        self.clicked.connect(self.on_click)
        self.clicked.connect(action)

    def on_click(self):
        # Reset the previous active button's icon and style
        if ModuleTabButton.active_button and ModuleTabButton.active_button != self:
            ModuleTabButton.active_button.update_icon_and_style(active=False)

        # Set this button as the active button
        ModuleTabButton.active_button = self
        self.update_icon_and_style(active=True)

    def update_icon_and_style(self, active: bool):
        # Update the SVG color, icon, and style based on active state
        if active:
            # Change icon for active state
            update_svg.change_svg_stroke_color(self.icon_path, main_module_style.Module_active_fg)
            self.setIcon(QIcon(self.icon_path))
            self.setStyleSheet(main_module_style.main_module_active_style)
        else:
            # Reset icon for inactive state
            update_svg.change_svg_stroke_color(self.icon_path, main_module_style.Module_inactive_fg)
            self.setIcon(QIcon(self.icon_path))
            self.setStyleSheet(main_module_style.main_module_inactive_style)

