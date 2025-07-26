from PyQt5.QtWidgets import QWidget, QLabel, QToolBar, QToolButton, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

import utils.file_utils as files
import styles.toolbar_style as toolbar_style

def create_toolbar(self):
    # Create a toolbar and add it to the left panel layout
    toolbar = QToolBar("")
    toolbar.setMovable(False)
    toolbar.setContentsMargins(0, 0, 0, 0)
    toolbar.setStyleSheet(toolbar_style.toolbar_style)

    # Add icon button to toolbar (without dropdown arrow)
    icon_button = QToolButton()
    icon_button.setIcon(QIcon(files.path_arrow_icon))
    icon_button.setIconSize(QSize(18, 18))
    icon_button.setStyleSheet(toolbar_style.toolbar_arrow_style)
    toolbar.addWidget(icon_button)

    # Create a stylish text label
    toolbar_label = QLabel("Configure settings")
    toolbar_label.setStyleSheet(toolbar_style.toolbar_label_style)
    toolbar.addWidget(toolbar_label)

    # Add a spacer for alignment
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    toolbar.addWidget(spacer)

    # Return the created toolbar
    return toolbar
