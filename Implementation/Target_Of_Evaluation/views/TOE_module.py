
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QStackedWidget, QSpacerItem, QMessageBox
from PyQt5.QtCore import Qt

import Implementation.Target_Of_Evaluation.System_Description.views.System_description_action as System_description_action
import Target_Of_Evaluation.Scope_Description.views.Scope_description_action as Scope_description_action
import Target_Of_Evaluation.Scope.views.Scope_action as Scope_action
import Target_Of_Evaluation.Assumptions.views.Assumptions_action as Assumptions_action
import Target_Of_Evaluation.Misuse_Cases.views.Misusecase_action as Misusecase_action
import Target_Of_Evaluation.TOE_Configuration.views.TOE_Configuration_action as TOE_Configuration_action

import components.sub_module_panel as sub_module_panel
import styles.sub_module_style as submodule_style
import utils.interface_utils as interfaces
import logging
logger = logging.getLogger(__name__)
class TargetOfEvaluation(QWidget):
    def __init__(self):
        super().__init__()
        logger.info("Target of Evaluation class")
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

        sidebar_label = QLabel("Target Of evaluation")
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
        content_layout.setSpacing(0)
        content_layout.addWidget(self.action)
        
        main_layout.addLayout(content_layout)

        # Set size policies to make panels adjustable
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.frames = {  'System Description': System_description_action.TOEDescription(),
                    'Scope Description': Scope_description_action.ScopeDescriptionWidget(),
                    'Scope': Scope_action.ScopeModule(),
                    'Assumptions': Assumptions_action.Assumptions(),
                    'Misuse cases': Misusecase_action.MisuseCases(),
                    'TOE Configuration' : TOE_Configuration_action.TOEConfiguration()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)

    # Add more frames as needed
    def create_TargetOfEvaluation_buttons(self, layout):
        buttons = [ ('System Description', lambda: self.show_frame('System Description')),
                    ('Scope Description', lambda: self.show_frame('Scope Description')),
                    ('Scope', lambda: self.show_frame('Scope')),
                    ('Assumptions', lambda: self.show_frame('Assumptions')),
                    ('Misuse cases', lambda: self.show_frame('Misuse cases')),
                    ('TOE Configuration', lambda: self.show_frame('TOE Configuration'))
                    ]
        
        # Add module buttons
        for index, (name, action) in enumerate(buttons):
            button = sub_module_panel.SubModuleTabButton(name, action)
            layout.addWidget(button, alignment=Qt.AlignLeft)

            interfaces.toe_sub_modules.append([name, button, action])

            if index == 0:
                interfaces.default_sub_module = [button, action]
                interfaces.default_toe_sub_module = interfaces.toe_sub_modules[0]
    
    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)

        # # Autosave logic before switching frames
        # if interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
        #     if interfaces.previous_module:
        #         # ✅ Check for 'Submit_Changes()' (Camel Case)
        #         if hasattr(interfaces.previous_module, "Submit_Changes"):
        #             interfaces.previous_module.Submit_Changes()
        #         # ✅ Check for 'submit_changes()' (Lowercase)
        #         elif hasattr(interfaces.previous_module, "submit_changes"):
        #             interfaces.previous_module.submit_changes()
            
        #     if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
        #         interfaces.previous_tree.Save_Tree()

        # elif not interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
        #     reply = QMessageBox.question(
        #         None, 'Unsaved Changes',
        #         "You have unsaved changes. Do you want to save them before switching?",
        #         QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        #     )

        #     if reply == QMessageBox.Yes:
        #         if interfaces.previous_module:
        #             # ✅ Check for 'Submit_Changes()' (Camel Case)
        #             if hasattr(interfaces.previous_module, "Submit_Changes"):
        #                 interfaces.previous_module.Submit_Changes()
        #             # ✅ Check for 'submit_changes()' (Lowercase)
        #             elif hasattr(interfaces.previous_module, "submit_changes"):
        #                 interfaces.previous_module.submit_changes()
                
        #         if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
        #             interfaces.previous_tree.Save_Tree()
            
        #     elif reply == QMessageBox.No:
        #         interfaces.unsaved_changes = False  

        # Frame switching logic
        # if frame:
        #     if self.action.indexOf(frame) == -1:
        #         self.action.addWidget(frame)
        #     self.action.setCurrentWidget(frame)
        #     interfaces.previous_module = frame  # Track last opened module


            # if frame_name == 'System Description':
            #     interfaces.default_toe_sub_module = interfaces.toe_sub_modules[0]
            #     frame.load_from_database(1)
            # elif frame_name == 'Scope Description':
            #     interfaces.default_toe_sub_module = interfaces.toe_sub_modules[1]
            #     frame.load_from_database(1)
            # elif frame_name == 'Scope':
            #     interfaces.default_toe_sub_module = interfaces.toe_sub_modules[2]
            #     frame.Load_data()
            #     frame.tab_container.setCurrentIndex(0)
            # elif frame_name == 'Assumptions':
            #     interfaces.default_toe_sub_module = interfaces.toe_sub_modules[3]
            #     frame.handle_menu_action()
            # elif frame_name =="Misuse cases":
            #     interfaces.default_toe_sub_module = interfaces.toe_sub_modules[4]
            #     frame.handle_menu_action()
            # elif frame_name == 'TOE Configuration':
            #     interfaces.default_toe_sub_module = interfaces.toe_sub_modules[5]
            #     frame.handle_menu_action()


