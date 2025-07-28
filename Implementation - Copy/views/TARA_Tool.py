# TARA_Tool.py

import sys
import traceback
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QToolTip, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy, QStackedWidget, QButtonGroup, QSpacerItem
from PyQt5.QtGui import QIcon, QCursor, QFont, QPixmap, QFontDatabase
from PyQt5.QtCore import QTimer, Qt, QSize
import models.Parameters as P
import Home.views.Home_action as H
import models.helper as helper
import components.toolbarhighlight as TH
import styles.Tool_style as tool_style
import styles.main_module_style as main_module_style
import styles.tool_footer_style as footer_style

import utils.file_utils as files
import utils.interface_utils as interfaces

import components.main_module_panel as main_module_window
import components.home_module_panel as home_module_window
import styles.sub_module_style as sub_module_style
import styles.action_panel_style as action_panel_style
from components.sidebar.sidebar import Sidebar
import views.show_submodule_frame as show_submodule_frame
import views.show_module_frame as show_module_frame
from Home.views import NameLabel

import logging
logger = logging.getLogger(__name__)


def global_exception_handler(exctype, value, tb):
    """Handles all unhandled exceptions globally."""
    
    # Format the error message
    error_message = "".join(traceback.format_exception(exctype, value, tb))
    
    # Log error (optional)
    print("Unhandled Exception:", error_message)
    
    # Show error dialog
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Application Error")
    msg_box.setText("An unexpected error occurred!")
    msg_box.setDetailedText(error_message)
    msg_box.exec_()

# Set global exception handler
sys.excepthook = global_exception_handler

class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            font_id = QFontDatabase.addApplicationFont("styles/Poppins-Regular.ttf")
            if font_id == -1:
                print("Failed to load Poppins font.")
            else:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                tool_style.poppins_font = QFont(font_family, 12)
            self.setWindowTitle("CYPHERA")
            self.setWindowIcon(QIcon(files.logo_icon))
            self.setGeometry(100, 100, 1200, 600)
            self.setMinimumSize(1104, 1022)
            # self.toolbar_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            # Main layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            self.setStyleSheet(tool_style.tool_style)
            main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins around the main layout
            main_layout.setSpacing(0)  # Remove spacing between main layout elements
            central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Main Content Area
            self.content_area = QStackedWidget()
            self.content_area.setContentsMargins(0, 0, 0, 0)
            self.content_area.setFrameShape(QFrame.StyledPanel)
            main_layout.addWidget(self.content_area)

            # Tab 1 Content: Action Panel
            homecontent_layout = QHBoxLayout()
            homecontent_layout.setContentsMargins(0, 0, 0, 0)
            homecontent_layout.setSpacing(0)
            self.HomeTab_content = QWidget()
            self.HomeTab_content.setContentsMargins(0, 0, 0, 0)
            HomeTab_layout = QHBoxLayout(self.HomeTab_content)
            HomeTab_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins around the tab layout
            HomeTab_layout.setSpacing(0)  # Remove spacing between tab layout elements
            homecontent_widget = QWidget()
            homecontent_widget.setLayout(homecontent_layout)
            HomeTab_layout.addWidget(homecontent_widget)
            self.home_panel = QFrame()
            self.home_panel.setFrameShape(QFrame.NoFrame)
            self.home_panel.setStyleSheet(sub_module_style.sub_module_style)
            self.home_panel.setFixedWidth(200)
            home_layout = QVBoxLayout(self.home_panel)
            home_layout.setContentsMargins(0, 0, 0, 0)  # Margins for the panel itself
            home_layout.setSpacing(15)  # 1px spacing between buttons
            # Add icons and buttons
            self.create_Home_buttons(home_layout)
            home_layout.addStretch()
            homecontent_layout.addWidget(self.home_panel)

            self.action_panel = QStackedWidget()
            self.action_panel.setContentsMargins(0, 0, 0, 0)
            self.action_panel.setFrameShape(QFrame.StyledPanel)
            self.action_panel.setStyleSheet(action_panel_style.action_panel_style)
            HomeTab_layout.addWidget(self.action_panel)
            
            self.content_area.addWidget(self.HomeTab_content)

            # Tab 2 Content: Module Panel
            modulecontent_layout = QHBoxLayout()
            modulecontent_layout.setContentsMargins(0, 0, 0, 0)
            modulecontent_layout.setSpacing(0)
            self.ModuleTab_content = QWidget()
            self.ModuleTab_content.setContentsMargins(0, 0, 0, 0)
            ModuleTab_layout = QVBoxLayout(self.ModuleTab_content)
            ModuleTab_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins around the tab layout
            ModuleTab_layout.setSpacing(0)  # Remove spacing between tab layout elements
            self.module_panel = QFrame()
            self.module_panel.setFrameShape(QFrame.NoFrame)
            self.module_panel.setStyleSheet(main_module_style.main_module_style)
            self.module_panel.setFixedWidth(60)
            self.module_layout = QVBoxLayout(self.module_panel)
            self.module_layout.setContentsMargins(0, 0, 0, 0)  # Margins for the panel itself
            self.module_layout.setSpacing(0)  # 1px spacing between buttons
            self.module_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

            self.sub_module_panel = QFrame()
            self.sub_module_panel.setFrameShape(QFrame.StyledPanel)
            self.sub_module_panel.setStyleSheet(sub_module_style.sub_module_style)
            self.sub_module_panel.setFixedWidth(280)
            self.submodule_layout = QVBoxLayout(self.sub_module_panel)
            self.submodule_layout.setContentsMargins(0, 0, 0, 0)  # Margins for the panel itself
            self.submodule_layout.setSpacing(0)  # 1px spacing between buttons
            self.submodule_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
            self.module_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

            # module_layout.addStretch()
            modulecontent_layout.addWidget(self.module_panel)
            modulecontent_layout.addWidget(self.sub_module_panel)
            # Action Area of Tab 2 (Right)
            self.Action_layer = QStackedWidget()
            self.Action_layer.setFrameShape(QFrame.StyledPanel)
            self.Action_layer.setContentsMargins(0,0,0,0)
            modulecontent_layout.addWidget(self.Action_layer)

            modulecontent_widget = QWidget()
            modulecontent_widget.setLayout(modulecontent_layout)
            ModuleTab_layout.addWidget(modulecontent_widget)
            self.content_area.addWidget(self.ModuleTab_content)

            # Footer Panel
            footer_panel = QFrame()
            footer_panel.setFrameShape(QFrame.NoFrame)
            footer_panel.setStyleSheet(footer_style.footer_style)
            footer_layout = QHBoxLayout(footer_panel)
            footer_layout.setContentsMargins(10, 5, 10, 5)  # Margins for the panel itself
            footer_layout.addStretch()
            
            # Add footer labels
            footer_power_label  = QLabel("Powered by")
            footer_layout.addWidget(footer_power_label , alignment=Qt.AlignLeft)
            
            company_logo = QLabel()
            company_logo.setPixmap(QPixmap(files.footer_logo_icon).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            footer_layout.addWidget(company_logo, alignment=Qt.AlignLeft)
            
            footer_company_label = QLabel("Ettiksoft ")
            footer_layout.addWidget(footer_company_label, alignment=Qt.AlignLeft)
            
            # Add vertical line after the logo
            vertical_line = QFrame()
            vertical_line.setFrameShape(QFrame.VLine)
            vertical_line.setFrameShadow(QFrame.Sunken)
            vertical_line.setStyleSheet(footer_style.footer_line_style)
            footer_layout.addWidget(vertical_line)

            footer_version_label = QLabel("Version V3.0.1")
            footer_layout.addWidget(footer_version_label, alignment=Qt.AlignLeft)

            # Add vertical line after the logo
            vertical_line = QFrame()
            vertical_line.setFrameShape(QFrame.VLine)
            vertical_line.setFrameShadow(QFrame.Sunken)
            vertical_line.setStyleSheet(footer_style.footer_line_style)
            footer_layout.addWidget(vertical_line)

            self.footer_autosave_label = QLabel("Auto Save")
            footer_layout.addWidget(self.footer_autosave_label, alignment=Qt.AlignLeft)
            

            # Auto Save Toggle Button
            self.footer_autosave_button = QPushButton()
            self.footer_autosave_button.setIcon(QIcon(files.turnoff_barbutton_icon))
            self.footer_autosave_button.setIconSize(QSize(60, 20))
            self.footer_autosave_button.setFixedSize(70, 30)
            self.footer_autosave_button.clicked.connect(self.toggle_autosave)

            footer_layout.addWidget(self.footer_autosave_button, alignment=Qt.AlignLeft)
            self.footer_autosave_button.setStyleSheet(""" QPushButton { background-color: transparent; border: none;} """)

            footer_layout.addStretch(1)

            # Spacer size
            spacer_size = QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)

            self.footer_date_label = QLabel()
            footer_layout.addWidget(self.footer_date_label, alignment=Qt.AlignRight)
            footer_layout.addItem(spacer_size)

            # Add lock button
            lock_button = QPushButton()
            lock_button.setIcon(QIcon(files.footer_lock_icon))
            lock_button.setIconSize(QSize(16, 16))
            lock_button.setFlat(True)  # Makes it look like a label
            lock_button.setStyleSheet(footer_style.footer_button_style)
            footer_layout.addWidget(lock_button, alignment=Qt.AlignLeft)
            footer_layout.addItem(spacer_size)

            # Add check button
            check_button = QPushButton()
            check_button.setIcon(QIcon(files.footer_check_icon))
            check_button.setIconSize(QSize(16, 16))
            check_button.setFlat(True)
            check_button.setStyleSheet(footer_style.footer_button_style)
            footer_layout.addWidget(check_button, alignment=Qt.AlignLeft)
            footer_layout.addItem(spacer_size)

            # Add refresh button
            refresh_button = QPushButton()
            refresh_button.setIcon(QIcon(files.footer_refresh_icon))
            refresh_button.setIconSize(QSize(16, 16))
            refresh_button.setFlat(True)
            refresh_button.setStyleSheet(footer_style.footer_button_style)
            footer_layout.addWidget(refresh_button, alignment=Qt.AlignLeft)
            footer_layout.addItem(spacer_size)

            # Add database button
            database_button = QPushButton()
            database_button.setIcon(QIcon(files.footer_database_icon))
            database_button.setIconSize(QSize(16, 16))
            database_button.setFlat(True)
            database_button.setStyleSheet(footer_style.footer_button_style)
            footer_layout.addWidget(database_button, alignment=Qt.AlignLeft)
            footer_layout.addItem(spacer_size)

            # Add notification button
            notification_button = QPushButton()
            notification_button.setIcon(QIcon(files.footer_bell_icon))
            notification_button.setIconSize(QSize(16, 16))
            notification_button.setFlat(True)
            notification_button.setStyleSheet(footer_style.footer_button_style)
            footer_layout.addWidget(notification_button, alignment=Qt.AlignLeft)

            
            footer_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            main_layout.addWidget(footer_panel)

            # Timer for updating time
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_time)
            self.timer.start(1000)
            self.update_time()

            # Initialize frames and add to action panel
            self.homeframes = {
                'MainHome_Panel': H.MainHome_Panel(),
                'MainNew_Panel': H.MainNew_Panel(),
                'MainOpen_Panel': H.MainOpen_Panel(parent=self)
            }
            for frame in self.homeframes.values():
                self.action_panel.addWidget(frame)

            
            self.sidebar = Sidebar(module_json_path="data/modules.json", profile_json_path="data/profile.json", settings_json_path="data/settings.json", parent=self)
            self.sidebar.module_selected.connect(self.show_moduleframe)
            self.sidebar.submodule_selected.connect(self.show_submoduleframe)

            # Timer to check for Panel_selector changes
            self.panel_selector_timer = QTimer()
            self.panel_selector_timer.timeout.connect(self.check_panel_selector)
            self.panel_selector_timer.start(100)  # Check every 100 ms

            # Timer to check for Panel_selector changes
            self.homepanel_selector_timer = QTimer()
            self.homepanel_selector_timer.timeout.connect(self.check_homepanel_selector)
            self.homepanel_selector_timer.start(100)  # Check every 100 ms

            self.show_HomeTab_content()
            interfaces.home_sub_modules[1].on_click()

            helper.Panel_selector = 'HomeTab'
            helper.homePanel_selector = 'HomeTab'
            self.previousmodule = None
            self.activate_home_tab_button()
            self.update_footer()

        except Exception as e:
            logger.error(f"Failed to start main application: {e}")

    def create_Home_buttons(self, layout):
        # Add minimal top space
        spacer_top = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer_top)

        # Add heading
        self.heading = QLabel("Home")
        self.heading.setStyleSheet(sub_module_style.sub_module_label_style)
        self.heading.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.heading)

        # Add horizontal line (separator) below the "Home" button
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Add "New" and "Open" buttons below the separator line
        buttons = [
            ('Back to current project', lambda: self.BackTo_Opened_Project()),
            ('Home', lambda: self.show_homeframe('MainHome_Panel')),
            ('New Project', lambda: self.show_homeframe('MainNew_Panel')),
            ('Open Project', lambda: self.show_homeframe('MainOpen_Panel'))
        ]

        for name, action in buttons:
            button = home_module_window.HomeTabButton(name, action)
            button.setIconSize(QSize(40, 40))  # Adjust icon size if needed
            layout.addWidget(button, alignment=Qt.AlignTop)
            interfaces.home_sub_modules.append(button)
            if name == 'Back to current project':
                button.setHidden(True)

        layout.setSpacing(20)  # Uniform spacing between buttons
        layout.addStretch()  # Add stretch to align buttons at the top

    def show_homeframe(self, frame_name):
        frame = self.homeframes.get(frame_name)
        if frame:
            if self.action_panel.indexOf(frame) == -1: self.action_panel.addWidget(frame)
            self.action_panel.setCurrentWidget(frame)
            if frame_name == 'MainHome_Panel':
                helper.homePanel_selector = 'HomeTab' 
                frame.load_recent_projects()
            elif frame_name == 'MainNew_Panel': helper.homePanel_selector = 'NewTab'
            elif frame_name == 'MainOpen_Panel': helper.homePanel_selector = 'OpenTab'
            elif frame_name == 'MainImport_Panel': helper.homePanel_selector = 'ImportTab'
    
    def show_moduleframe(self, payload): show_module_frame.show_moduleframe(self, payload)
    def show_submoduleframe(self, payload): show_submodule_frame.show_submoduleframe(self, payload)
    
    def home_action(self):
        # print("Home clicked")
        helper.Panel_selector = 'HomeTab'
        helper.homePanel_selector = 'HomeTab'
        self.activate_home_tab_button()

        # Reset the active module button
        if main_module_window.ModuleTabButton.active_button:
            main_module_window.ModuleTabButton.active_button.setStyleSheet(main_module_window.ModuleTabButton.active_button.inactive_style())
            main_module_window.ModuleTabButton.active_button = None
    
    def update_time(self): self.footer_date_label.setText(f'{time.strftime("%d-%m-%Y %H:%M:%S")}')
    
    def show_HomeTab_content(self): self.content_area.setCurrentWidget(self.HomeTab_content)
    
    def BackTo_Opened_Project(self): 
        helper.Panel_selector = 'ModuleTab'
        interfaces.sub_modules[interfaces.previous_mainmodule]['module'].on_click()

    def show_ModuleTab_content(self):
        self.content_area.setCurrentWidget(self.ModuleTab_content)

    def check_panel_selector(self):
        if helper.Panel_selector == 'ModuleTab':
            self.show_ModuleTab_content()
        elif helper.Panel_selector == 'HomeTab':
            self.show_HomeTab_content()

    def check_homepanel_selector(self):
        if helper.homePanel_selector == 'HomeTab':
            for button in self.home_panel.findChildren(TH.HomeTabButton):
                if button.toolTip() == 'Home':
                    button.on_click()
            self.show_homeframe('MainHome_Panel')
        elif helper.homePanel_selector == 'NewTab':
            for button in self.home_panel.findChildren(TH.HomeTabButton):
                if button.toolTip() == 'New Project':
                    button.on_click()
            self.show_homeframe('MainNew_Panel')
        elif helper.homePanel_selector == 'OpenTab':
            for button in self.home_panel.findChildren(TH.HomeTabButton):
                if button.toolTip() == 'Open Project':
                    button.on_click()
            self.show_homeframe('MainOpen_Panel')
        elif helper.homePanel_selector == 'ImportTab':
            for button in self.home_panel.findChildren(TH.HomeTabButton):
                if button.toolTip() == 'Import Project':
                    button.on_click()
            self.show_homeframe('MainImport_Panel')

    def activate_home_tab_button(self):
        # Find the TH.HomeTabButton and set it as active
        for button in self.home_panel.findChildren(home_module_window.HomeTabButton):
            if button.toolTip() == 'Home':
                button.on_click()
                break

    def closeEvent(self, event):
        # Handle autosave before switching modules
        if interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
            # Check if submit_changes() or Submit_Changes() exists before calling
            if interfaces.previous_module and hasattr(interfaces.previous_module, "Submit_Changes"):
                interfaces.previous_module.Submit_Changes()
                interfaces.unsaved_changes = False
            elif interfaces.previous_module and hasattr(interfaces.previous_module, "submit_changes"):
                interfaces.previous_module.submit_changes()
                interfaces.unsaved_changes = False
            if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
                interfaces.previous_tree.Save_Tree()
                interfaces.unsaved_changes = False
        elif not interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
            # Show a popup to confirm if the user wants to discard changes
            reply = QMessageBox.question(
                None, 'Unsaved Changes',
                "You have unsaved changes. Do you want to save them before closing the application?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            # Handle user's choice
            if reply == QMessageBox.Yes:
                if interfaces.previous_module and hasattr(interfaces.previous_module, "Submit_Changes"):
                    interfaces.previous_module.Submit_Changes()
                    interfaces.unsaved_changes = False
                elif interfaces.previous_module and hasattr(interfaces.previous_module, "submit_changes"):
                    interfaces.previous_module.submit_changes()
                    interfaces.unsaved_changes = False
                if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
                    interfaces.previous_tree.Save_Tree()
                    interfaces.unsaved_changes = False
            elif reply == QMessageBox.No:
                interfaces.unsaved_changes = False

    def update_footer(self):
        """Update the footer Auto Save UI based on settings."""
        if interfaces.autosave_enabled:
            self.footer_autosave_label.setText("Auto Save")
            self.footer_autosave_button.setIcon(QIcon(files.turnon_barbutton_icon))
        else:
            self.footer_autosave_label.setText("Auto Save")
            self.footer_autosave_button.setIcon(QIcon(files.turnoff_barbutton_icon))
        # self.moduleframes['Settings'].update_autosave_button()
        interfaces.sub_modules['Settings']['submodules']['Settings']["frame"].update_autosave_button()

    def toggle_autosave(self):
        """Toggle Auto Save state and update footer UI."""
        if not interfaces.autosave_enabled:
            interfaces.autosave_enabled = True
            self.footer_autosave_button.setIcon(QIcon(files.turnon_barbutton_icon))
            self.footer_autosave_button.setStyleSheet(""" QPushButton { background-color: transparent; border: none;} """)
        else:
            interfaces.autosave_enabled = False
            self.footer_autosave_button.setIcon(QIcon(files.turnoff_barbutton_icon))
            self.footer_autosave_button.setStyleSheet(""" QPushButton { background-color: transparent; border: none;} """)
        
        # Emit the signal to notify the settings module
        # self.moduleframes['Settings'].autosave_toggled.emit()
        # self.moduleframes['Settings'].update_autosave_button()
        
        # Emit the signal to notify the settings module 
        interfaces.sub_modules['Settings']['submodules']['Settings']["frame"].autosave_toggled.emit()
        interfaces.sub_modules['Settings']['submodules']['Settings']["frame"].update_autosave_button()
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Application()
    window.resize(1200, 600)
    window.show()
    sys.exit(app.exec_())
