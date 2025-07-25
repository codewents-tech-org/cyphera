
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolTip, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy, QStackedWidget, QSpacerItem, QMessageBox
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtCore import QTimer, Qt, QSize
import models.Parameters as P
import Summary.Traceability_Graph.views.TraceabilityGraph_action as TraceabilityGraph_action
import Summary.Management_Summary.views.ManagementSummary_action as ManagementSummary_action
import Summary.views.Summary_action as Summary_action
import models.helper as helper

import components.submodulehighlight as SMH
import components.sub_module_panel as sub_module_panel

import styles.sub_module_style as submodule_style

import utils.interface_utils as interfaces



class Summary(QWidget):
    def __init__(self):
        super().__init__()
        helper.modulePanel_Selector = 'SummaryTab'

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

        sidebar_label = QLabel("Summary") 
        sidebar_label.setAlignment(Qt.AlignLeft) 
        sidebar_label.setStyleSheet(submodule_style.sub_module_label_style)
        # Add the label to the layout
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addItem(QSpacerItem(0, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))
        
        # Optionally, set size policies to make panels adjustable
        self.create_Summary_buttons(sidebar_layout)
        sidebar_layout.addStretch()
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        main_layout.addWidget(self.sidebar)
        
        # Content Layout (Remaining area)
        content_layout = QVBoxLayout()

        # Action (Center Panel)
        self.action = QStackedWidget()
        self.action.setFrameShape(QFrame.StyledPanel)
        self.action.setStyleSheet(f"background-color: {P.White}; border: none;")
        self.action.setContentsMargins(0,0,0,0)
        content_layout.addWidget(self.action)
        
        main_layout.addLayout(content_layout)

        # Set size policies to make panels adjustable
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.frames = {  'Traceability Graph': TraceabilityGraph_action.TraceabilityGraph_Module(),
                    'Management Summary': ManagementSummary_action.ManagementSummary_module()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)


    # Add more frames as needed
    def create_Summary_buttons(self, layout):
        buttons = [ ('Traceability Graph', lambda: self.show_frame('Traceability Graph')),
                    ('Management Summary', lambda: self.show_frame('Management Summary'))
                    ]
        
        # Add module buttons
        for index, (name, action) in enumerate(buttons):
            button = sub_module_panel.SubModuleTabButton(name, action)
            layout.addWidget(button, alignment=Qt.AlignLeft)
            
            interfaces.summary_sub_modules.append([name, button, action])

            if index == 0:
                interfaces.default_summary_sub_module = interfaces.summary_sub_modules[0]
            
    
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
        # if frame:
        #     if self.action.indexOf(frame) == -1:
        #         self.action.addWidget(frame)
        #     self.action.setCurrentWidget(frame)
        #     if frame_name == 'Traceability Graph':
        #         interfaces.default_summary_sub_module = interfaces.summary_sub_modules[0]
        #         frame.create_scroll_area()
        #     elif frame_name == 'Management Summary':
        #         interfaces.default_summary_sub_module = interfaces.summary_sub_modules[1]
        #         frame.refresh_data()

