
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QScrollArea
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import styles.property_panel_style as property_style
import utils.file_utils as files

def create_selection_panel(self):
    self.switch_selection_panel = QWidget()
    self.switch_selection_panel.setContentsMargins(2, 12, 0, 0)
    self.switch_selection_panel.setFixedWidth(30)
    self.switch_selection_panel.setStyleSheet(property_style.switch_property_panel_style)
    
    # Layout for the switch property panel
    switch_panel_layout = QVBoxLayout(self.switch_selection_panel)
    switch_panel_layout.setContentsMargins(0, 0, 0, 0)
    switch_panel_layout.setSpacing(0) 

    # Add icon button to the top
    self.toggle_button = QPushButton()
    self.toggle_button.setIcon(QIcon(files.path_arrow_icon))
    self.toggle_button.setIconSize(QSize(30, 30))
    self.toggle_button.setFixedSize(40, 40) 
    self.toggle_button.setStyleSheet(property_style.switch_button_style)
    self.toggle_button.setToolTip('hide selection panel')
    self.toggle_button.clicked.connect(lambda: toggle_right_panel(self))

    switch_panel_layout.addWidget(self.toggle_button, alignment=Qt.AlignTop)

    # Add a spacer to push other elements down, if needed in the future
    spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
    switch_panel_layout.addSpacerItem(spacer)

    # Create the right-side property panel
    self.selection_panel = QWidget()
    self.selection_panel.setContentsMargins(0, 20, 0, 20)  # Remove margins for the scrollable area
    self.selection_panel.setFixedWidth(250)
    self.selection_panel.setStyleSheet(property_style.property_panel_style)

    # Create a scrollable area
    self.selection_scroll_area = QScrollArea()
    self.selection_scroll_area.setWidgetResizable(True)  # Ensure the content resizes with the scroll area
    self.selection_scroll_area.setStyleSheet(property_style.Scroll_area_style)  # Optional: Remove border around the scroll area

    # Create a container widget to hold the layout
    self.scrollable_content = QWidget()
    self.scrollable_content.setContentsMargins(0, 0, 10, 0)  # Add inner margins for spacing
    self.selection_layout = QVBoxLayout(self.scrollable_content)
    self.selection_layout.setContentsMargins(0, 0, 0, 0)  # Layout margins inside the scrollable content
    self.selection_layout.setSpacing(0)

    # Set up the content of the scroll area
    self.selection_scroll_area.setWidget(self.scrollable_content)

    # Add the scroll area to the main property panel layout
    selection_panel_layout = QVBoxLayout(self.selection_panel)
    selection_panel_layout.addWidget(self.selection_scroll_area)
    selection_panel_layout.setContentsMargins(0, 0, 0, 0)
    selection_panel_layout.setSpacing(0)

    # Add heading
    self.selection_heading = QLabel("Report")
    self.selection_heading.setStyleSheet(property_style.property_heading_label_style)
    self.selection_heading.setAlignment(Qt.AlignLeft)
    selection_panel_layout.addWidget(self.selection_heading)

    # Add spacer
    spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)  # 20px vertical space
    selection_panel_layout.addItem(spacer)

    selection_panel_layout.addWidget(self.selection_scroll_area)


def toggle_right_panel(self):
    """Toggle the visibility of the right property panel."""
    if not self.selection_panel.isVisible():
        self.selection_panel.setVisible(True)
        self.toggle_button.setToolTip('hide propert panel')
    else:
        self.selection_panel.setVisible(False)
        self.toggle_button.setToolTip('show propert panel')
