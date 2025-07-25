
from PyQt5.QtWidgets import QWidget, QLabel, QToolBar, QToolButton, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

import utils.file_utils as files
import styles.toolbar_style as toolbar_style

def create_toolbar(self):
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
    self.toolbar_label = QLabel("Management Summary")
    self.toolbar_label.setStyleSheet(toolbar_style.toolbar_label_style)
    self.toolbar.addWidget(self.toolbar_label)

    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(spacer)

    