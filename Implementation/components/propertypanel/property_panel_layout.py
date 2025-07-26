"""
Module Name   : property_panel_layout.py   \n
Layer         : Presentation / UI   \n
Component ID  : CY_CO_002   \n
Requirement ID: N/A   \n
Version       : V 3.0   \n
Created By    : Vishnu Viswanath   \n
Created On  : 2025-05-16   \n

Purpose:
--------
Provides a reusable class (`PropertyPanelManager`) for dynamically creating and managing 
the layout and behavior of a property panel in PyQt5-based interfaces. It encapsulates 
UI components like scrollable views, toggle panels, and headers while adhering to consistent 
styling and layout rules. This design avoids UI duplication and facilitates reuse across 
modules such as Assets, Threats, and other property-driven widgets.

Description:
------------
Manages the visual layout and behavior of the right-side property panel, including
toggle logic, scrollable view, and layout sections.

Responsibilities:
-----------------
- Toggle visibility of the panel
- Inject headings, scrolling layouts, and dynamic widgets
- Maintain layout consistency using style guidelines

Signals
-------
+----------------------------+-------------------------------+-------------------------------+-------------------------------+
| Trigger                    | Signal Name                   | Description                   | Payload Format                |
+============================+===============================+===============================+===============================+
| Property layout build      | create_property_layout_signal | Triggers property layout setup| None (emits a method call)    |
+----------------------------+-------------------------------+-------------------------------+-------------------------------+


Dependencies:
-------------
- PyQt5 (QtCore, QtGui, QtWidgets)
- styles.property_panel_style
- utils.file_utils

Limitations:
------------
- Limited to fixed-width layout
- Assumes external control of data injection and signal emissions
- Requires externally defined signal `create_property_layout_signal`

Improvements
------------
- Add row validation or formatting hooks
- Support drag/drop or copy/paste interaction
- Modularize delegate to support other input types (e.g., dropdown)

Change History:
---------------
+----------------+----------------------+-----------------------------+----------------------+
| Version        | Date                 | Change                      | Author               |
+================+======================+=============================+======================+
| V 3.0          | 2025-05-14           | Initial version created     | Vishnu Viswanath     |
+----------------+----------------------+-----------------------------+----------------------+
|                |                      |                             |                      |
+----------------+----------------------+-----------------------------+----------------------+
|                |                      |                             |                      |
+----------------+----------------------+-----------------------------+----------------------+
|                |                      |                             |                      |
+----------------+----------------------+-----------------------------+----------------------+
"""

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QScrollArea
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QIcon
    import styles.property_panel_style as property_style
    import utils.file_utils as files
except ImportError as import_error:
    logger.exception("Failed to import required modules in property_panel.py: %s", import_error)    

class PropertyPanelManager:
    """
    Manages the creation and behavior of a right-side property panel in PyQt5 interfaces.

    This class encapsulates layout setup, toggle functionality, and signal handling
    to ensure consistent UI structure across modules. It is designed to be initialized
    with a parent widget and provides methods to build and control the panel dynamically.
    """
    def __init__(self, parent_widget):
        self.parent = parent_widget

        # Constants as instance attributes
        self.TOGGLE_ICON_SIZE = QSize(30, 30)
        self.TOGGLE_BUTTON_WIDTH = 40
        self.TOGGLE_BUTTON_HEIGHT = 40
        self.SWITCH_PANEL_WIDTH = 30
        self.PROPERTY_PANEL_WIDTH = 330
        self.HEADING_SPACER_HEIGHT = 20
    def create_property_signal_handlers(self):
        """
        Connect the external `create_property_layout_signal` to the panel layout creation function.

        Parameters:
        -----------
        self : QWidget
            Main widget expected to define `create_property_layout_signal`.

        Emits:
        -------
        Signal connected to `create_property_panel(self)`.

        Usage:
        ------
        >>> self.create_property_layout_signal.emit()
        """
        self.create_property_layout_signal.connect(lambda: self.create_property_panel())


    def create_property_panel(self):
        """
        Build the complete property panel layout by composing sections.

        Parameters:
        -----------
        self : QWidget
            Parent widget.
        """
        self.create_switch_property_panel()
        self.create_property_scroll_panel()
        self.setup_property_panel_layout()


    def create_switch_property_panel(self):
        """
        Create left-side vertical switch panel with a toggle button.

        Parameters:
        -----------
        self : QWidget
            Container widget where the switch panel is created.
        """
        self.switch_property_panel = QWidget()
        self.switch_property_panel.setContentsMargins(2, 12, 0, 0)
        self.switch_property_panel.setFixedWidth(self.SWITCH_PANEL_WIDTH)
        self.switch_property_panel.setStyleSheet(property_style.switch_property_panel_style)

        switch_panel_layout = QVBoxLayout(self.switch_property_panel)
        switch_panel_layout.setContentsMargins(0, 0, 0, 0)
        switch_panel_layout.setSpacing(0)

        self.toggle_button = QPushButton()
        self.toggle_button.setIcon(QIcon(files.path_arrow_icon))
        self.toggle_button.setIconSize(self.TOGGLE_ICON_SIZE)
        self.toggle_button.setFixedSize(self.TOGGLE_BUTTON_WIDTH, self.TOGGLE_BUTTON_HEIGHT)
        self.toggle_button.setStyleSheet(property_style.switch_button_style)
        self.toggle_button.setToolTip('hide propert panel')
        self.toggle_button.clicked.connect(lambda: self.toggle_right_panel())

        switch_panel_layout.addWidget(self.toggle_button, alignment=Qt.AlignTop)
        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        switch_panel_layout.addSpacerItem(spacer)


    def create_property_scroll_panel(self):
        """
        Create scrollable container to hold the dynamic property inputs.

        Parameters:
        -----------
        self : QWidget
            Container widget where the scroll area is embedded.
        """
        self.property_panel = QWidget()
        self.property_panel.setContentsMargins(0, 20, 0, 20)
        self.property_panel.setFixedWidth(self.PROPERTY_PANEL_WIDTH)
        self.property_panel.setStyleSheet(property_style.property_panel_style)

        self.property_scroll_area = QScrollArea()
        self.property_scroll_area.setWidgetResizable(True)
        self.property_scroll_area.setStyleSheet(property_style.Scroll_area_style)

        self.scrollable_content = QWidget()
        self.scrollable_content.setContentsMargins(0, 0, 10, 0)
        self.property_layout = QVBoxLayout(self.scrollable_content)
        self.property_layout.setContentsMargins(0, 0, 0, 0)
        self.property_layout.setSpacing(0)

        self.property_scroll_area.setWidget(self.scrollable_content)


    def setup_property_panel_layout(self):
        """
        Attach title label and scroll view to the panel layout.

        Parameters:
        -----------
        self : QWidget
            Container widget.
        """
        property_panel_layout = QVBoxLayout(self.property_panel)
        property_panel_layout.setContentsMargins(0, 0, 0, 0)
        property_panel_layout.setSpacing(0)

        self.property_heading = QLabel("Property")
        self.property_heading.setStyleSheet(property_style.property_heading_label_style)
        self.property_heading.setAlignment(Qt.AlignLeft)
        property_panel_layout.addWidget(self.property_heading)

        spacer = QSpacerItem(0, self.HEADING_SPACER_HEIGHT, QSizePolicy.Minimum, QSizePolicy.Fixed)
        property_panel_layout.addItem(spacer)

        property_panel_layout.addWidget(self.property_scroll_area)



    def toggle_right_panel(self):
        """
        Show/hide the right-hand property panel.

        Parameters:
        -----------
        self : QWidget
            Widget controlling panel visibility.

        Raises:
        -------
        AttributeError
            If property panel or toggle button is not initialized.
        """
        try:
            if not self.property_panel.isVisible():
                self.property_panel.setVisible(True)
                self.toggle_button.setToolTip('hide propert panel')
                logger.info("Property panel shown.")
            else:
                self.property_panel.setVisible(False)
                self.toggle_button.setToolTip('show propert panel')
                logger.info("Property panel hidden.")
        except AttributeError as error:
            logger.error("Failed to toggle property panel: %s", error)        
