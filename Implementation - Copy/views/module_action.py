# module_action.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolTip, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy, QStackedWidget, QButtonGroup
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtCore import QTimer, Qt, QSize
import models.Parameters as P
import Target_Of_Evaluation.views.TargetOfEvaluation_action as TargetOfEvaluation_action
import Attack_Paths.views.AttackPaths_action as AttackPaths_action
import Attack_Paths.Attack_Tree.views.AttackTree_action as AttackTree_action
import Attack_Paths.RiskControl_Tree.views.RiskControlTree_action as RiskControlTree_action
import Attack_Paths.Attack_Leaves.views.AttackLeaves_action as AttackLeaves_action
import Risk_Assessment.views.RiskAssessment_action as RiskAssessment_action
import Summary.views.Summary_action as Summary_action
import models.helper as helper
import components.submodulehighlight as SMH

import styles.sub_module_style as submodule_style

class Home(QWidget):
    def __init__(self):
        super().__init__()
        helper.modulePanel_Selector = 'HomeTab'

class TargetOfEvaluation(QWidget):
    def __init__(self):
        super().__init__()
        helper.modulePanel_Selector = 'TargetOfEvaluationTab'

        # Main layout for the Frame1
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Optional: Adjust margins
        main_layout.setSpacing(0)  # Optional: Adjust spacing

        # Sidebar (Left Panel)
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setStyleSheet(submodule_style.sub_module_style)  # Set background color for sidebar
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for a full-height layout
        # sidebar_layout.setSpacing(5)  # Remove spacing for full-height sections
        
        # Optionally, set size policies to make panels adjustable
        self.create_TargetOfEvaluation_buttons(sidebar_layout)
        sidebar_layout.addStretch()
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        main_layout.addWidget(self.sidebar)
        
        # Content Layout (Remaining area)
        content_layout = QVBoxLayout()

        # Action (Center Panel)
        self.action = QStackedWidget()
        self.action.setFrameShape(QFrame.StyledPanel)
        self.action.setStyleSheet(f"background-color: {P.Action_bg}; border: none;")
        content_layout.addWidget(self.action)
        
        main_layout.addLayout(content_layout)

        # Set size policies to make panels adjustable
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.property.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.frames = {  'Home': TargetOfEvaluation_action.Home(),
                       'TOE_Description': TargetOfEvaluation_action.TOE_Description(),
                    'Scope': TargetOfEvaluation_action.Scope(),
                    'Assumptions': TargetOfEvaluation_action.Assumptions(),
                    'Security_Controls': TargetOfEvaluation_action.Security_Controls()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)

    # Add more frames as needed
    def create_TargetOfEvaluation_buttons(self, layout):
        buttons = [ ('TOE Description', lambda: self.show_frame('TOE_Description')),
                    ('Scope', lambda: self.show_frame('Scope')),
                    ('Assumptions', lambda: self.show_frame('Assumptions')),
                    ('Security Controls', lambda: self.show_frame('Security_Controls'))
                    ]
        
        # Add module buttons
        for name, action in buttons:
            button = QPushButton()
            button = SMH.TabButton(name, action)
            button.setText(name)
            button.setFont(QFont('Anton', 10))
            button.setStyleSheet(f"""   
            QPushButton {{
                background: none;
                border: none;
                text-align: left;
                color: {P.SubModuleIAText_fg};
            }}
            QPushButton:hover {{
                background-color: {P.Module_bg};
            }}""")
            layout.addWidget(button, alignment=Qt.AlignLeft)
    
    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)
        if frame:
            self.action.setCurrentWidget(frame)

class AttackPaths(QWidget):
    def __init__(self):
        super().__init__()
        helper.modulePanel_Selector = 'AttackPathsTab'

        # Main layout for the Frame1
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Optional: Adjust margins
        main_layout.setSpacing(0)  # Optional: Adjust spacing

        # Sidebar (Left Panel)
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setStyleSheet(submodule_style.sub_module_style)  # Set background color for sidebar
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for a full-height layout
        sidebar_layout.setSpacing(5)  # Remove spacing for full-height sections
        
        # Optionally, set size policies to make panels adjustable
        self.create_AttackPaths_buttons(sidebar_layout)
        sidebar_layout.addStretch()
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        main_layout.addWidget(self.sidebar)
        
        # Content Layout (Remaining area)
        content_layout = QVBoxLayout()

        # Action (Center Panel)
        self.action = QStackedWidget()
        self.action.setFrameShape(QFrame.StyledPanel)
        self.action.setStyleSheet(f"background-color: {P.Action_bg};")
        content_layout.addWidget(self.action)
        
        main_layout.addLayout(content_layout)

        # Set size policies to make panels adjustable
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.frames = {  'Home': AttackPaths_action.Home(),
                       'Attack_Tree': AttackTree_action.Attack_Tree(),
                    'riskcontrol_tree': RiskControlTree_action.riskcontrol_tree(),
                    'Attack_Leaves': AttackLeaves_action.Attack_Leaves()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)
    
    # Add more frames as needed
    def create_AttackPaths_buttons(self, layout):
        buttons = [('Attack Tree', lambda: self.show_frame('Attack_Tree')),
            ('Risk Control Tree', lambda: self.show_frame('riskcontrol_tree')),
            ('Attack Leaves', lambda: self.show_frame('Attack_Leaves'))
        ]
        
        # Add module buttons
        for name, action in buttons:
            button = QPushButton()
            button = SMH.TabButton(name, action)
            button.setText(name)
            button.setFont(QFont('Anton', 10))
            button.setStyleSheet(f"""   
            QPushButton {{
                background: none;
                border: none;
                text-align: left;
                color: {P.SubModuleIAText_fg};
            }}
            QPushButton:hover {{
                background-color: {P.Module_bg};
            }}""")
            layout.addWidget(button, alignment=Qt.AlignLeft)

    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)
        if frame:
            self.action.setCurrentWidget(frame)

class RiskAssessment(QWidget):
    def __init__(self):
        super().__init__()
        helper.modulePanel_Selector = 'RiskAssessmentTab'

        # Main layout for the Frame1
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Optional: Adjust margins
        main_layout.setSpacing(0)  # Optional: Adjust spacing

        # Sidebar (Left Panel)
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setStyleSheet(submodule_style.sub_module_style)  # Set background color for sidebar
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for a full-height layout
        # sidebar_layout.setSpacing(5)  # Remove spacing for full-height sections
        
        # Optionally, set size policies to make panels adjustable
        self.create_RiskAssessment_buttons(sidebar_layout)
        sidebar_layout.addStretch()
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        main_layout.addWidget(self.sidebar)
        
        # Content Layout (Remaining area)
        content_layout = QVBoxLayout()

        # Action (Center Panel)
        self.action = QStackedWidget()
        self.action.setFrameShape(QFrame.StyledPanel)
        self.action.setStyleSheet(f"background-color: {P.Action_bg};")
        content_layout.addWidget(self.action)
        
        main_layout.addLayout(content_layout)

        # Set size policies to make panels adjustable
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.frames = {  'Home': RiskAssessment_action.Home(),
                       'Security_Claims': RiskAssessment_action.Security_Claims(),
                    'Security_Goals': RiskAssessment_action.Security_Goals(),
                    'Risk_Treatment': RiskAssessment_action.Risk_Treatment()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)
    
    # Add more frames as needed
    def create_RiskAssessment_buttons(self, layout):
        buttons = [
            ('Security Claims', lambda: self.show_frame('Security_Claims')),
            ('Security Goals', lambda: self.show_frame('Security_Goals')),
            ('Risk Treatment', lambda: self.show_frame('Risk_Treatment'))
        ]
        
        # Add module buttons
        for name, action in buttons:
            button = QPushButton()
            button = SMH.TabButton(name, action)
            button.setText(name)
            button.setFont(QFont('Anton', 10))
            button.setStyleSheet(f"""   
            QPushButton {{
                background: none;
                border: none;
                text-align: left;
                color: {P.SubModuleIAText_fg};
            }}
            QPushButton:hover {{
                background-color: {P.Module_bg};
            }}""")
            layout.addWidget(button, alignment=Qt.AlignLeft)

    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)
        if frame:
            self.action.setCurrentWidget(frame)

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
        self.sidebar.setStyleSheet(submodule_style.sub_module_style)  # Set background color for sidebar
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for a full-height layout
        # sidebar_layout.setSpacing(5)  # Remove spacing for full-height sections
        
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
        self.action.setStyleSheet(f"background-color: {P.Action_bg};")
        content_layout.addWidget(self.action)
        
        main_layout.addLayout(content_layout)

        # Set size policies to make panels adjustable
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.frames = {  'Home': Summary_action.Home(),
                       'Traceability_Graph': Summary_action.Traceability_Graph(),
                    'Management_Summary': Summary_action.Management_Summary(),
                    'Generate_Report': Summary_action.Generate_Report()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)
    
    # Add more frames as needed
    def create_Summary_buttons(self, layout):
        buttons = [
            ('Traceability Graph', lambda: self.show_frame('Traceability_Graph')),
            ('Management Summary', lambda: self.show_frame('Management_Summary')),
            ('Generate Report', lambda: self.show_frame('Generate_Report'))
        ]
        
        # Add module buttons
        for name, action in buttons:
            button = QPushButton()
            button = SMH.TabButton(name, action)
            button.setText(name)
            button.setFont(QFont('Anton', 10))
            button.setStyleSheet(f"""   
            QPushButton {{
                background: none;
                border: none;
                text-align: left;
                color: {P.SubModuleIAText_fg};
            }}
            QPushButton:hover {{
                background-color: {P.Module_bg};
            }}""")
            layout.addWidget(button, alignment=Qt.AlignLeft)

    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)
        if frame:
            self.action.setCurrentWidget(frame)
