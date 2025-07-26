
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QStackedWidget, QSpacerItem,QMessageBox
from PyQt5.QtCore import Qt

import Security_Measurement.Security_Claims.views.SecurityClaims_action as SecurityClaims_action
import Security_Measurement.Security_Goals.views.SecurityGoals_action as SecurityGoals_action
import Security_Measurement.Security_Controls.views.SecurityControls_action as SecurityControls_action

import components.sub_module_panel as sub_module_panel
import styles.sub_module_style as submodule_style
import utils.interface_utils as interfaces
import logging
logger = logging.getLogger(__name__)
class SecurityControls(QWidget):
    def __init__(self):
        logger.info("Security Control module class")
        super().__init__()
        # Main layout for the Frame1
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Optional: Adjust margins
        main_layout.setSpacing(0)  # Optional: Adjust spacing

        # Sidebar (Left Panel)
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setStyleSheet(submodule_style.sub_module_style)
        self.sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0) 
        sidebar_layout.setSpacing(0)  
        sidebar_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        sidebar_label = QLabel("Security measurement") 
        sidebar_label.setAlignment(Qt.AlignLeft) 
        sidebar_label.setStyleSheet(submodule_style.sub_module_label_style)
        # Add the label to the layout
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addItem(QSpacerItem(0, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))
        
        # Optionally, set size policies to make panels adjustable
        self.create_TargetOfEvaluation_buttons(sidebar_layout)
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

        self.frames = {   'Security Claims': SecurityClaims_action.SecurityClaims_Module(),
                    'Security Goals': SecurityGoals_action.SecurityGoals_Module(),
                    'Security Controls': SecurityControls_action.SecurityControls_Module()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)


    # Add more frames as needed
    def create_TargetOfEvaluation_buttons(self, layout):
        logger.info("target of evaluation buttons")
        buttons = [ ('Security Claims', lambda: self.show_frame('Security Claims')),
                    ('Security Goals', lambda: self.show_frame('Security Goals')),
                    ('Security Controls', lambda: self.show_frame('Security Controls'))
                ]
        
        # Add module buttons
        for index, (name, action) in enumerate(buttons):
            button = sub_module_panel.SubModuleTabButton(name, action)
            layout.addWidget(button, alignment=Qt.AlignLeft)
            
            interfaces.securitymeasures_sub_modules.append([name, button, action])

            if index == 0:
                interfaces.default_securitymeasures_sub_module = interfaces.securitymeasures_sub_modules[0]
    
    def show_frame(self, frame_name):
        """Handles autosave logic before switching frames."""
        # logger.info("Show info")
        frame = self.frames.get(frame_name)

        # # 🔹 Autosave logic before switching
        # if interfaces.autosave_enabled and interfaces.previous_module and interfaces.unsaved_changes:
           
        #     if hasattr(interfaces.previous_module, "Submit_Changes"):
        #         interfaces.previous_module.Submit_Changes()
           
        #     elif hasattr(interfaces.previous_module, "submit_changes"):
        #         interfaces.previous_module.submit_changes()

        # elif not interfaces.autosave_enabled and interfaces.previous_module and interfaces.unsaved_changes:
        #     reply = QMessageBox.question(
        #         None, 'Unsaved Changes',
        #         "You have unsaved changes. Do you want to save them before switching?",
        #         QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        #     )
        #     if reply == QMessageBox.Yes:
               
        #         if hasattr(interfaces.previous_module, "Submit_Changes"):
        #             interfaces.previous_module.Submit_Changes()
               
        #         elif hasattr(interfaces.previous_module, "submit_changes"):
        #             interfaces.previous_module.submit_changes()

        # 🔹 Frame switching logic
        # if frame:
        #     if self.action.indexOf(frame) == -1:
        #         self.action.addWidget(frame)
        #     self.action.setCurrentWidget(frame)
        #     interfaces.previous_module = frame  # Track last opened module


        #     if frame_name == 'Security Claims':
        #         interfaces.default_securitymeasures_sub_module = interfaces.securitymeasures_sub_modules[0]
        #         frame.handle_menu_action()
        #     elif frame_name == 'Security Goals':
        #         interfaces.default_securitymeasures_sub_module = interfaces.securitymeasures_sub_modules[1]
        #         frame.handle_menu_action()
        #     elif frame_name == 'Security Controls':
        #         interfaces.default_securitymeasures_sub_module = interfaces.securitymeasures_sub_modules[2]
        #         frame.handle_menu_action()




