import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QStackedWidget, QSpacerItem
)
from PyQt5.QtCore import Qt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import models.Parameters as P
import models.helper as helper
import components.submodulehighlight as SMH
import components.sub_module_panel as sub_module_panel
import styles.sub_module_style as submodule_style
import utils.interface_utils as interfaces
from Profile.views.profile_toolbar_panel import create_toolbar

from Profile.Profilesupport.views.profile_support import ProfileSupport
from Profile.Profilebillingdetails.views.profile_billing import ProfileBilling
from Profile.Profiledetails.Views.profile_details import ProfileDetails
class Profile(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout for the Frame1
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar (Left Panel)
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setStyleSheet(submodule_style.sub_module_style)
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        sidebar_label = QLabel("Profile")
        sidebar_label.setAlignment(Qt.AlignLeft)
        sidebar_label.setStyleSheet(submodule_style.sub_module_label_style)
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addItem(QSpacerItem(0, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.create_profile_buttons(sidebar_layout)
        sidebar_layout.addStretch()
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        main_layout.addWidget(self.sidebar)

        # Content Layout (Remaining area)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Add the toolbar at the top
        self.toolbar = create_toolbar(self)
        content_layout.addWidget(self.toolbar)

        # Action (Center Panel)
        self.action = QStackedWidget()
        self.action.setFrameShape(QFrame.StyledPanel)
        self.action.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.action)

        main_layout.addLayout(content_layout)

        # Set size policies to make panels adjustable
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.frames = {
            'Profile': self.create_profile_details_frame(),
            'Billing and Purchase': ProfileBilling(),
            'Support': ProfileSupport()
        }

        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)

    def create_profile_details_frame(self):
        """Create the ProfileDetails frame."""
        profile_details_widget = QWidget()
        profile_details_layout = QVBoxLayout(profile_details_widget)
        profile_details_layout.setContentsMargins(0, 0, 0, 0)
        profile_details_layout.setSpacing(10)

        # Add the rest of the ProfileDetails content
        profile_details_content = ProfileDetails()
        profile_details_layout.addWidget(profile_details_content)

        return profile_details_widget

    def create_profile_buttons(self, layout):
        buttons = [
            ('Profile', lambda: self.show_frame('Profile')),
            ('Billing and Purchase', lambda: self.show_frame('Billing and Purchase')),
            ('Support', lambda: self.show_frame('Support')),
        ]

        # Add module buttons
        for index, (name, action) in enumerate(buttons):
            button = sub_module_panel.SubModuleTabButton(name, action)
            layout.addWidget(button, alignment=Qt.AlignLeft)

            interfaces.profile_sub_modules.append([name, button])

            if index == 0:
                interfaces.default_profile_sub_module = interfaces.profile_sub_modules[0]

    def show_frame(self, frame_name):
        """Switch frames and update the toolbar label."""
        frame = self.frames.get(frame_name)
        if frame:
            if self.action.indexOf(frame) == -1:
                self.action.addWidget(frame)
            self.action.setCurrentWidget(frame)

            # Update the toolbar label dynamically
            toolbar_label = self.toolbar.findChild(QLabel, "toolbar_label")
            if toolbar_label:
                # Set the toolbar label text based on the selected frame
                if frame_name == "Profile":
                    interfaces.default_profile_sub_module = interfaces.profile_sub_modules[0]
                    toolbar_label.setText("Profile Details")
                elif frame_name == "Billing and Purchase":
                    interfaces.default_profile_sub_module = interfaces.profile_sub_modules[1]
                    toolbar_label.setText("Billing and Purchase")
                elif frame_name == "Support":
                    interfaces.default_profile_sub_module = interfaces.profile_sub_modules[2]
                    toolbar_label.setText("Support")
