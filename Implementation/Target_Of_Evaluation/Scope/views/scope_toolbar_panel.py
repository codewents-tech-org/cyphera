
from PyQt5.QtWidgets import QWidget, QLabel, QToolBar, QToolButton, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

import utils.file_utils as files
import styles.toolbar_style as toolbar_style
import logging
logger = logging.getLogger(__name__)

def create_toolbar(self):
    logger.info("Toolbar panel creation")
    # Create a toolbar and add it to the left panel layout
    self.toolbar = QToolBar("")
    self.toolbar.setMovable(False)
    self.toolbar.setContentsMargins(0,0,0,0)
    self.toolbar.setStyleSheet(toolbar_style.toolbar_style)

    # Add icon button to toolbar (without dropdown arrow)
    self.icon_button = QToolButton()
    self.icon_button.setIcon(QIcon(files.path_arrow_icon))
    self.icon_button.setIconSize(QSize(18, 18))
    self.icon_button.setStyleSheet(toolbar_style.toolbar_arrow_style)
    self.toolbar.addWidget(self.icon_button)

    # Create a stylish text label
    self.toolbar_label = QLabel("Scope")
    self.toolbar_label.setStyleSheet(toolbar_style.toolbar_label_style)
    self.toolbar.addWidget(self.toolbar_label)

    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(spacer)

    self.add_button = QToolButton()
    self.add_button.setIcon(QIcon(files.add_icon)) 
    self.add_button.setText(' Add')            
    self.add_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    self.add_button.setStyleSheet(toolbar_style.toolbar_button_style) 
    self.toolbar.addWidget(self.add_button)
    
    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(10)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)
    
    self.submit_button = QToolButton()
    self.submit_button.setIcon(QIcon(files.submit_icon))   
    self.submit_button.setText(' Submit')           
    self.submit_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon) 
    self.submit_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.submit_button)
    
    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(10)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)
    
    self.delete_button = QToolButton()
    self.delete_button.setIcon(QIcon(files.delete_icon)) 
    self.delete_button.setText(' Delete')       
    self.delete_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon) 
    self.delete_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.delete_button)
    
    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(10)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.refresh_button = QToolButton()
    self.refresh_button.setIcon(QIcon(files.refresh_icon))
    self.refresh_button.setText(' Refresh')
    self.refresh_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    self.refresh_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.refresh_button)

    # Add a final spacer if needed
    small_spacer = QWidget()
    small_spacer.setFixedWidth(10)
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)
