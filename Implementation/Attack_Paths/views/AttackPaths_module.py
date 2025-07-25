# module_action.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolTip, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy, QStackedWidget, QSpacerItem, QMessageBox
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtCore import QTimer, Qt, QSize
import models.Parameters as P
import Attack_Paths.views.AttackPaths_action as AttackPaths_action
import Attack_Paths.Attack_Tree.views.AttackTree_action as AttackTree_action
import Attack_Paths.RiskControl_Tree.views.RiskControlTree_action as RiskControlTree_action
import Attack_Paths.Technical_Attack_Tree.views.technicaltree_action as technicaltree_action
import Attack_Paths.Attack_Leaves.views.AttackLeaves_action as AttackLeaves_action
import models.helper as helper

import components.submodulehighlight as SMH
import components.sub_module_panel as sub_module_panel
import styles.sub_module_style as submodule_style
import utils.interface_utils as interfaces



class AttackPaths(QWidget):
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

        sidebar_label = QLabel("Attack paths")
        sidebar_label.setAlignment(Qt.AlignLeft)
        sidebar_label.setStyleSheet(submodule_style.sub_module_label_style)
        # Add the label to the layout
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addItem(QSpacerItem(0, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))
        
        # Optionally, set size policies to make panels adjustable
        self.create_AttackPaths_buttons(sidebar_layout)
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
        content_layout.setSpacing(0)
        content_layout.addWidget(self.action)
        
        main_layout.addLayout(content_layout)

        # Set size policies to make panels adjustable
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.frames = {  'Attack Tree': AttackTree_action.Attack_Tree(),
                    'Technical Attack Tree': technicaltree_action.Technical_Tree(),
                    'Risk Control Tree': RiskControlTree_action.RiskControl_Tree(),
                    'Attack Leaves': AttackLeaves_action.Attack_Leaves()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)

    # Add more frames as needed
    def create_AttackPaths_buttons(self, layout):
        buttons = [('Attack Tree', lambda: self.show_frame('Attack Tree')),
            ('Technical Attack Tree', lambda: self.show_frame('Technical Attack Tree')),
            ('Risk Control Tree', lambda: self.show_frame('Risk Control Tree')),
            ('Attack Leaves', lambda: self.show_frame('Attack Leaves'))
        ]
        
        # Add module buttons
        for index, (name, action) in enumerate(buttons):
            button = sub_module_panel.SubModuleTabButton(name, action)
            layout.addWidget(button, alignment=Qt.AlignLeft)

            interfaces.attackpaths_sub_modules.append([name, button, action])

            if index == 0:
                interfaces.default_attackpaths_sub_module = interfaces.attackpaths_sub_modules[0]

    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)

        # # Handle autosave before switching
        # if interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
        #     if interfaces.previous_module:
            
        #         if hasattr(interfaces.previous_module, "Submit_Changes"):
        #             interfaces.previous_module.Submit_Changes()
             
        #         elif hasattr(interfaces.previous_module, "submit_changes"):
        #             interfaces.previous_module.submit_changes()
            
        #     if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
        #         interfaces.previous_tree.Save_Tree()

        # elif not interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
        #     # Show a popup to confirm if the user wants to discard changes
        #     reply = QMessageBox.question(
        #         None, 'Unsaved Changes',
        #         "You have unsaved changes. Do you want to save them before switching?",
        #         QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        #     )

        #     # Handle user's choice
        #     if reply == QMessageBox.Yes:
        #         if interfaces.previous_module:
                   
        #             if hasattr(interfaces.previous_module, "Submit_Changes"):
        #                 interfaces.previous_module.Submit_Changes()
                 
        #             elif hasattr(interfaces.previous_module, "submit_changes"):
        #                 interfaces.previous_module.submit_changes()
                
        #         if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
        #             interfaces.previous_tree.Save_Tree()
            
        #     elif reply == QMessageBox.No:
        #         interfaces.unsaved_changes = False 

        # # Switch frame logic
        # if frame:
        #     if self.action.indexOf(frame) == -1:
        #         self.action.addWidget(frame)
        #     self.action.setCurrentWidget(frame)
        #     interfaces.previous_module = frame  # Track last opened module


        #     if frame_name == 'Attack Tree':
        #         interfaces.default_attackpaths_sub_module = interfaces.attackpaths_sub_modules[0]
        #         frame.Load_data()
        #         frame.tab_container.setCurrentIndex(0)
        #     elif frame_name == 'Technical Attack Tree':
        #         interfaces.default_attackpaths_sub_module = interfaces.attackpaths_sub_modules[1]
        #         frame.Load_data()
        #         frame.tab_container.setCurrentIndex(0)
        #     elif frame_name == 'Risk Control Tree':
        #         interfaces.default_attackpaths_sub_module = interfaces.attackpaths_sub_modules[2]
        #         frame.Load_data()
        #         frame.tab_container.setCurrentIndex(0)
        #     elif frame_name == 'Attack Leaves':
        #         interfaces.default_attackpaths_sub_module = interfaces.attackpaths_sub_modules[3]
        #         frame.Load_data()

