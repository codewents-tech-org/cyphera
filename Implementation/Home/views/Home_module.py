from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QStackedWidget, QSpacerItem
from PyQt5.QtCore import Qt
import components.sub_module_panel as sub_module_panel
import styles.sub_module_style as submodule_style
import utils.interface_utils as interfaces

class HomeModule(QWidget):
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

        sidebar_label = QLabel("Home")
        sidebar_label.setAlignment(Qt.AlignLeft) 
        sidebar_label.setStyleSheet(submodule_style.sub_module_label_style)
        # Add the label to the layout
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addItem(QSpacerItem(0, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # # Optionally, set size policies to make panels adjustable
        # self.create_Home_buttons(sidebar_layout)
        # sidebar_layout.addStretch()
        # self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
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