
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolTip, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy, QStackedWidget, QSpacerItem
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
import models.Parameters as P
import Reports.Generate_Reports.views.GenerateReport_action as GenerateReport_action
import Reports.PEN_Testcases_Report.views.PENTestcasesReport_action as PENTestcasesReport_action
import Reports.views.Report_action as Report_action
import models.helper as helper

import components.submodulehighlight as SMH
import components.sub_module_panel as sub_module_panel

import styles.sub_module_style as submodule_style

import utils.interface_utils as interfaces



class Report(QWidget):
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

        sidebar_label = QLabel("Report") 
        sidebar_label.setAlignment(Qt.AlignLeft) 
        sidebar_label.setStyleSheet(submodule_style.sub_module_label_style)
        # Add the label to the layout
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addItem(QSpacerItem(0, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))
        
        # Optionally, set size policies to make panels adjustable
        self.create_Report_buttons(sidebar_layout)
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

        self.frames = {  'Generate_Report': GenerateReport_action.GenerateReport_module(),
                    'Generate_Pen_Test_Report': PENTestcasesReport_action.PenTestReportModule()
                }
        # Add frames to the stacked widget
        for frame in self.frames.values():
            self.action.addWidget(frame)


    # Add more frames as needed
    def create_Report_buttons(self, layout):
        buttons = [ 
                    ('Generate Report', lambda: self.show_frame('Generate_Report')),
                    ('PEN Test Cases Report', lambda: self.show_frame('Generate_Pen_Test_Report'))
                    ]
        
        # Add module buttons
        for index, (name, action) in enumerate(buttons):
            button = sub_module_panel.SubModuleTabButton(name, action)
            layout.addWidget(button, alignment=Qt.AlignLeft)
            
            interfaces.report_sub_modules.append([name, button, action])

            if index == 0:
                interfaces.default_report_sub_module = interfaces.report_sub_modules[0]
    
    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)
    #     if frame:
    #         if self.action.indexOf(frame) == -1:
    #             self.action.addWidget(frame)
    #         self.action.setCurrentWidget(frame)

            
    #         if frame_name == 'Generate_Report':
    #             interfaces.default_report_sub_module = interfaces.report_sub_modules[0]
    #         elif frame_name == 'Generate_Pen_Test_Report':
    #             interfaces.default_report_sub_module = interfaces.report_sub_modules[1]
    #             # frame.graphics_scene.clear()
    #             frame.Update_Testcases()
