
import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QToolTip, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy, QStackedWidget, QButtonGroup
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtCore import QTimer, Qt, QSize
import models.Parameters as P
import views.module_action as M
import Home.views.Home_action as H
import models.helper as helper
import models.update_svg as update_svg



class HighlightToolbarButton(QPushButton):
    def __init__(self, icon_path, tooltip_text, action, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        self.setStyleSheet("background: none; border: none;")
        self.clicked.connect(action)
        self.setCursor(QCursor(Qt.PointingHandCursor))  # Change the cursor to pointing hand
        self.setToolTip(tooltip_text)  # Set the tooltip text

        # Optional: Set custom font and style for the tooltip
        QToolTip.setFont(QFont('SansSerif', 8))
        self.setStyleSheet("""
            QToolTip {
                background-color: #f0f0f0;
                color: #000;
                border: 1px solid black;
            }
            QPushButton {
                background: none;
                border: none;
            }
            QPushButton:hover {
                background-color: lightgray;
            }            
            QPushButton:clicked {
                background-color: blue;
                border: 2px solid blue;
            }
        """)

    def enterEvent(self, event):
        self.setStyleSheet("""
            QPushButton {
                background-color: lightgray;
                border: none;
            }
            QPushButton:pressed {
                background-color: #dcdcdc;
                border: none;
                padding-left: 2px;
                padding-top: 0px;
            }
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
            }
            QPushButton:hover {
                background-color: lightgray;
            }
            QPushButton:pressed {
                background-color: #dcdcdc;
                border: none;
                padding-left: 2px;
                padding-top: 0px;
            }
        """)
        super().leaveEvent(event)

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
                background-color: {P.ModuleHighlight_bg};
                color: #000;
                border: 1px solid black;
            }}
            QPushButton {{
                background: none;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {P.ModuleHighlight_bg};
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

# class ModuleTabButton(QPushButton):
#     active_button = None  # Class-level variable to track the active tab

#     def __init__(self, icon_path, tooltip_text, action, parent=None):
#         super().__init__(parent)
#         self.icon_path = icon_path
#         self.setIcon(QIcon(icon_path))
#         self.setIconSize(QSize(24, 24))
#         self.setFixedHeight(70)
#         self.setStyleSheet("background: none; border: none; padding: 20px 10px 20px 10px;")
#         self.setStyleSheet(self.inactive_style())  # Set the initial style as inactive
#         self.clicked.connect(self.on_click)
#         self.clicked.connect(action)
#         self.setCursor(QCursor(Qt.PointingHandCursor))  # Change the cursor to pointing hand
#         self.setToolTip(tooltip_text)  # Set the tooltip text

#         # Optional: Set custom font and style for the tooltip
#         QToolTip.setFont(QFont('SansSerif', 10))
#         self.setStyleSheet(f"""
#             QToolTip {{
#                 background-color: {P.ModuleHighlightColor};
#                 color: #000;
#                 border: 1px solid black;
#             }}
#             QPushButton {{
#                 background: none;
#                 border: none;
#             }}
#             QPushButton:hover {{
#                 background-color: {P.ModuleHighlight_bg};
#             }}
#         """)
#         update_svg.change_svg_stroke_color(self.icon_path, self.icon_path, P.Gray, P.Gray)
    
#     def on_click(self):
#         # Reset the background color of the previous active button
#         if ModuleTabButton.active_button and ModuleTabButton.active_button != self:
#             ModuleTabButton.active_button.setStyleSheet(self.inactive_style())
#             # update_svg.change_svg_stroke_color(self.icon_path, self.icon_path, P.Gray, P.Gray)
#             # self.setIcon(QIcon(self.icon_path))
            

#         # Set the current button as the active one and change its background color
#         ModuleTabButton.active_button = self
#         self.setStyleSheet(self.active_style())
        

#     def active_style(self):
#         update_svg.change_svg_stroke_color(self.icon_path, self.icon_path, P.Gray, P.ModuleHighlightColor)
#         self.setIcon(QIcon(self.icon_path))
#         return f"""
#             QToolTip {{
#                 background-color: {P.ModuleHighlightColor};
#                 color: #000;
#                 border: 1px solid black;
#             }}
#             QPushButton {{
#                 background-color: {P.SubModuleSidebar_bg};
#                 border: none;
#                 border-left: 6px solid {P.HighlightColor};
#             }}
#         """
        

#     def inactive_style(self):
#         update_svg.change_svg_stroke_color(self.icon_path, self.icon_path, P.ModuleHighlightColor, P.Gray)
#         self.setIcon(QIcon(self.icon_path))
#         return f"""
#             QToolTip {{
#                 background-color: {P.ModuleHighlightColor};
#                 color: #000;
#                 border: 1px solid black;
#             }}
#             QPushButton {{
#                 background: none;
#                 border: none;
                
#             }}
#             QPushButton:hover {{
#                 background-color: {P.ModuleHighlight_bg};
#             }}
#         """

# class ModuleTabButton(QPushButton):
#     active_button = None  # Class-level variable to track the active tab

#     def __init__(self, icon_path, tooltip_text, action, parent=None):
#         super().__init__(parent)
#         self.icon_path = icon_path
#         self.inactive_icon_path = self.icon_path  # Default path for the inactive state
#         self.active_icon_path = icon_path  # Default path for the active state

#         # Set initial icon and style
#         self.setIcon(QIcon(self.inactive_icon_path))
#         self.setIconSize(QSize(24, 24))
#         self.setFixedHeight(70)
#         self.setCursor(QCursor(Qt.PointingHandCursor))  # Change the cursor to pointing hand
#         self.setToolTip(tooltip_text)  # Set the tooltip text
#         QToolTip.setFont(QFont('SansSerif', 10))

#         # Update inactive state initially
#         self.update_icon_and_style(active=False)

#         # Connect signals
#         self.clicked.connect(self.on_click)
#         self.clicked.connect(action)

#     def on_click(self):
#         # Reset the previous active button's icon and style
#         if ModuleTabButton.active_button and ModuleTabButton.active_button != self:
#             ModuleTabButton.active_button.update_icon_and_style(active=False)

#         # Set this button as the active button
#         ModuleTabButton.active_button = self
#         self.update_icon_and_style(active=True)

#     def update_icon_and_style(self, active: bool):
#         # Update the SVG color, icon, and style based on active state
#         if active:
#             # Change icon for active state
#             update_svg.change_svg_stroke_color(
#                 self.icon_path, self.icon_path, P.Gray, P.ModuleHighlightColor
#             )
#             self.setIcon(QIcon(self.icon_path))
#             self.setStyleSheet(self.active_style())
#         else:
#             # Reset icon for inactive state
#             update_svg.change_svg_stroke_color(
#                 self.icon_path, self.icon_path, P.ModuleHighlightColor, P.Gray
#             )
#             self.setIcon(QIcon(self.icon_path))
#             self.setStyleSheet(self.inactive_style())

#     def active_style(self):
#         return f"""
#             QToolTip {{
#                 color: #000;
#                 border: px solid black;
#             }}
#             QPushButton {{
#                 border: none;
#                 border-left: 6px solid {P.HighlightColor};
#             }}
#         """

#     def inactive_style(self):
#         return f"""
#             QToolTip {{
#                 color: #000;
#                 border: 1px solid black;
#             }}
#             QPushButton {{
#                 background: none;
#                 border: none;
#             }}
#         """


class HomeTabButton(QPushButton):
    active_button = None  # Class-level variable to track the active tab

    def __init__(self, icon_path, tooltip_text, action, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        self.setFixedWidth(180)
        self.setFixedHeight(30)
        self.setStyleSheet("background: none; border: none;")
        self.setStyleSheet(self.inactive_style())  # Set the initial style as inactive
        self.clicked.connect(self.on_click)
        self.clicked.connect(action)
        # helper.homePanel_selector
        self.setCursor(QCursor(Qt.PointingHandCursor))  # Change the cursor to pointing hand
        self.setToolTip(tooltip_text)  # Set the tooltip text

        # Optional: Set custom font and style for the tooltip
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setStyleSheet(f"""
            QToolTip {{
                background-color: {P.ModuleHighlightColor};
                color: #000;
                border: 1px solid black;
                text-align: left;
            }}
            QPushButton {{
                background: none;
                border: none;
                text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{
                background-color: {P.ModuleHighlight_bg};
                text-align: left;
            }}
        """)
    
    def on_click(self):
        # Reset the background color of the previous active button
        if HomeTabButton.active_button and HomeTabButton.active_button != self:
            HomeTabButton.active_button.setStyleSheet(self.inactive_style())

        # Set the current button as the active one and change its background color
        HomeTabButton.active_button = self
        self.setStyleSheet(self.active_style())

    def active_style(self):
        return f"""
            QToolTip {{
                background-color: {P.ModuleHighlightColor};
                color: #000;
                border: 1px solid black;
                text-align: left;
            }}
            QPushButton {{
                background-color: {P.SubModuleSidebar_bg};
                border: none;
                text-align: left;
                border-left: 6px solid {P.HighlightColor};
                padding-left: 20px;
            }}
        """

    def inactive_style(self):
        return f"""
            QToolTip {{
                background-color: {P.ModuleHighlightColor};
                color: #000;
                border: 1px solid black;
                text-align: left;
            }}
            QPushButton {{
                background: none;
                border: none;
                text-align: left;
                padding-left: 20px;
                
            }}
            QPushButton:hover {{
                background-color: {P.ModuleHighlight_bg};
                text-align: left;
            }}
        """




