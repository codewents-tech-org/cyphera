
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

import styles.sub_module_style as sub_module_style

class HomeTabButton(QPushButton):
    active_button = None  # Class-level variable to track the active tab

    def __init__(self, name, action, parent=None):
        super().__init__(parent)
        self.name = name  # Store name to use as button text

        self.setFixedWidth(190)
        self.setFixedHeight(35)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setText(self.name)
        self.update_style(active=False)
        self.clicked.connect(self.on_click)
        self.clicked.connect(action)

    def on_click(self):
        # Reset the previous active button's style
        if HomeTabButton.active_button and HomeTabButton.active_button != self:
            HomeTabButton.active_button.update_style(active=False)

        # Set this button as the active button
        HomeTabButton.active_button = self
        self.update_style(active=True)

    def update_style(self, active: bool):
        if active:
            self.setStyleSheet(sub_module_style.sub_module_active_style)
        else:
            self.setStyleSheet(sub_module_style.sub_module_inactive_style)

