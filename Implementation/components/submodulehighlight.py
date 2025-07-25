
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolTip, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy, QStackedWidget, QButtonGroup
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtCore import QTimer, Qt, QSize
import models.Parameters as P


class HighlightButton(QPushButton):
    def __init__(self, icon_path, tooltip_text, action, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        self.setStyleSheet("background: none; border: none;")
        self.clicked.connect(action)
        self.setCursor(QCursor(Qt.PointingHandCursor))  # Change the cursor to pointing hand
        self.setToolTip(tooltip_text)  # Set the tooltip text

        # Optional: Set custom font and style for the tooltip
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setStyleSheet(f"""
            QToolTip {{
                background-color: {P.Module_bg};
                color: #000;
                border: none;;
            }}
            QPushButton {{
                background: none;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {P.Module_bg};
            }}
        """)

    def enterEvent(self, event):
        # Additional highlighting if needed when the mouse enters
        self.setStyleSheet(f"background-color: {P.ModuleHighlight_bg}; border: none;")
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        # Revert highlight when the mouse leaves
        self.setStyleSheet("border: none;")
        super().leaveEvent(event)

class TabButton(QPushButton):
    active_button = None  # Class-level variable to track the active tab

    def __init__(self, name, action, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: none; border: none; color: {P.SubModuleIAText_fg};")
        self.setFixedWidth(200)
        # self.setFixedHeight(30)
        self.setStyleSheet(self.inactive_style())  # Set the initial style as inactive
        self.clicked.connect(self.on_click)
        self.clicked.connect(action)
        self.setCursor(QCursor(Qt.PointingHandCursor))  # Change the cursor to pointing hand
        self.setToolTip(name)

        # Optional: Set custom font and style for the tooltip
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setStyleSheet(f"""
            QToolTip {{
                background-color: {P.Module_bg};
                color: #000;
                border: none;
                text-align: left;
            }}
            QPushButton {{
                background: none;
                border: none;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {P.Module_bg};
                text-align: left;
            }}
        """)
    
    def set_active(self, active):
        if active:
            TabButton.active_button = self
            self.setStyleSheet(self.active_style())
        else:
            self.setStyleSheet(self.inactive_style())
    
    def on_click(self):
        # Reset the background color of the previous active button
        if TabButton.active_button and TabButton.active_button != self:
            TabButton.active_button.setStyleSheet(self.inactive_style())

        # Set the current button as the active one and change its background color
        TabButton.active_button = self
        self.setStyleSheet(self.active_style())

    def active_style(self):
        return f"""
            QToolTip {{
                background-color: {P.Gray};
                color: #000;
                border: none;
                text-align: left;
            }}
            QPushButton {{
                background-color: {P.Module_bg};
                font-weight: bold;
                color: {P.SubModuleAText_fg};
                border: none;
                text-align: left;
                
            }}
            QPushButton:hover {{
                background-color: {P.Module_bg};
                text-align: left;
            }}
        """

    def inactive_style(self):
        return f"""
            QToolTip {{
                background-color: {P.Gray};
                color: #000;
                border: none;
                text-align: left;
            }}
            QPushButton {{
                background: none;
                color: {P.SubModuleIAText_fg};
                border: none;
                text-align: left;
                
            }}
            QPushButton:hover {{
                background-color: {P.Module_bg};
                text-align: left;
            }}
        """




