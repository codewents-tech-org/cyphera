
from PyQt5.QtWidgets import QWidget, QHBoxLayout

import styles.action_panel_style as action_panel_style

def create_action_panel(self):
    self.action_panel = QWidget()
    self.action_panel_layout = QHBoxLayout()
    self.action_panel.setLayout(self.action_panel_layout)
    self.action_panel.setContentsMargins(0,0,0,0)
    self.action_panel_layout.setContentsMargins(0,0,0,0)
    self.action_panel_layout.setSpacing(0)
    self.action_panel.setStyleSheet(action_panel_style.action_panel_style)



