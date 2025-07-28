from PyQt5.QtWidgets import QToolBar, QToolButton, QWidget, QSizePolicy,QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
import utils.file_utils as files
import styles.toolbar_style as toolbar_style

def create_toolbar(parent):
    # Create the toolbar
    toolbar = QToolBar("")
    toolbar.setMovable(False)
    toolbar.setContentsMargins(0, 0, 0, 0)
    toolbar.setStyleSheet(toolbar_style.toolbar_style)

    # Add an icon button
    icon_button = QToolButton()
    icon_button.setIcon(QIcon(files.path_arrow_icon))
    icon_button.setIconSize(QSize(18, 18))
    icon_button.setStyleSheet(toolbar_style.toolbar_arrow_style)
    toolbar.addWidget(icon_button)

    # Add a label with a unique objectName
    toolbar_label = QLabel("Profile Details")
    toolbar_label.setObjectName("toolbar_label")  # Assign objectName for dynamic updates
    toolbar_label.setStyleSheet(toolbar_style.toolbar_label_style)
    toolbar.addWidget(toolbar_label)

    # Add a spacer
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    toolbar.addWidget(spacer)

    return toolbar
