# module_action.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QStackedWidget, QSpacerItem, QMessageBox
from PyQt5.QtCore import Qt

import Analysis.Asset.views.Asset_action as Asset_action
import Analysis.Damage_Scenarios.views.DamageScenarios_action as DamageScenarios_action
import Analysis.Threats.views.Threat_action as Threat_action
import Analysis.Threat_Scenarios.views.ThreatScenarios_action as ThreatScenarios_action

import components.sub_module_panel as sub_module_panel
import styles.sub_module_style as submodule_style
import utils.interface_utils as interfaces

class Analysis(QWidget):
    def __init__(self):
        super().__init__()
        # Main layout for the Frame1
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Optional: Adjust margins
        main_layout.setSpacing(0)  # Optional: Adjust spacing

        # Sidebar (Left Panel)
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setStyleSheet(submodule_style.sub_module_style)
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0) 
        sidebar_layout.setSpacing(0) 
        sidebar_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        sidebar_label = QLabel("Analysis")
        sidebar_label.setAlignment(Qt.AlignLeft) 
        sidebar_label.setStyleSheet(submodule_style.sub_module_label_style)
        # Add the label to the layout
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addItem(QSpacerItem(0, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))
        
        # Optionally, set size policies to make panels adjustable
        self.create_Analysis_buttons(sidebar_layout)
        sidebar_layout.addStretch()
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        main_layout.addWidget(self.sidebar)
        
        # Content Layout (Remaining area)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)

        # Action (Center Panel)
        self.action = QStackedWidget()
        self.action.setFrameShape(QFrame.StyledPanel)
        self.action.setContentsMargins(0,0,0,0)
        content_layout.addWidget(self.action)
        
        main_layout.addLayout(content_layout)

        # Set size policies to make panels adjustable
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.frames = {  'Assets': Asset_action.Asset_Module(),
                    'Damage Scenarios': DamageScenarios_action.DS_Module(),
                    'Threats': Threat_action.Threat_Module(),
                    'Threat Scenarios': ThreatScenarios_action.TS_Module()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)

    # Add more frames as needed
    def create_Analysis_buttons(self, layout):
        buttons = [ ('Assets', lambda: self.show_frame('Assets')),
                    ('Damage Scenarios', lambda: self.show_frame('Damage Scenarios')),
                    ('Threats', lambda: self.show_frame('Threats')),
                    ('Threat Scenarios', lambda: self.show_frame('Threat Scenarios'))
                    ]
        
        # Add module buttons
        for index, (name, action) in enumerate(buttons):
            button = sub_module_panel.SubModuleTabButton(name, action)
            layout.addWidget(button, alignment=Qt.AlignLeft)

            interfaces.analysis_sub_modules.append([name, button, action])

            if index == 0:
                interfaces.default_analysis_sub_module = interfaces.analysis_sub_modules[0]

    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)

        # # 🔹 Autosave logic before switching
        # if interfaces.autosave_enabled and interfaces.previous_module and interfaces.unsaved_changes:
           
        #     if hasattr(interfaces.previous_module, "Submit_Changes"):
        #         interfaces.previous_module.Submit_Changes()
          
        #     elif hasattr(interfaces.previous_module, "submit_changes"):
        #         interfaces.previous_module.submit_changes()

        # elif not interfaces.autosave_enabled and interfaces.previous_module and interfaces.unsaved_changes:
        #     # Show a popup to confirm if the user wants to discard changes
        #     reply = QMessageBox.question(
        #         None, 'Unsaved Changes',
        #         "You have unsaved changes. Do you want to save them before switching?",
        #         QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        #     )

        #     # Handle user's choice
        #     if reply == QMessageBox.Yes:
               
        #         if hasattr(interfaces.previous_module, "Submit_Changes"):
        #             interfaces.previous_module.Submit_Changes()
               
        #         elif hasattr(interfaces.previous_module, "submit_changes"):
        #             interfaces.previous_module.submit_changes()
        #     elif reply == QMessageBox.No:
        #         interfaces.unsaved_changes = False  # Reset unsaved changes flag

        # 🔹 Frame switching logic
        # if frame:
        #     if self.action.indexOf(frame) == -1:
        #         self.action.addWidget(frame)
        #     self.action.setCurrentWidget(frame)
        #     interfaces.previous_module = frame  # Track last opened module

        #     if frame_name == 'Assets':
        #         interfaces.default_analysis_sub_module = interfaces.analysis_sub_modules[0]
        #         frame.handle_menu_action()
        #     elif frame_name == 'Damage Scenarios':
        #         interfaces.default_analysis_sub_module = interfaces.analysis_sub_modules[1]
        #         frame.handle_menu_action()
        #     elif frame_name == 'Threats':
        #         interfaces.default_analysis_sub_module = interfaces.analysis_sub_modules[2]
        #         frame.handle_menu_action()
        #     elif frame_name == 'Threat Scenarios':
        #         interfaces.default_analysis_sub_module = interfaces.analysis_sub_modules[3]
        #         frame.handle_menu_action()



