from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QToolBar,
    QToolButton,
    QSizePolicy,
    QComboBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

import utils.file_utils as files
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidgetAction


import styles.toolbar_style as toolbar_style
import logging

logger = logging.getLogger(__name__)


def create_toolbar(self, buttons):
    logger.info("Toolbar creation")
    # Create a toolbar and add it to the left panel layout
    self.toolbar = QToolBar("")
    self.toolbar.setMovable(False)
    self.toolbar.setContentsMargins(0, 0, 0, 0)
    self.toolbar.setStyleSheet(toolbar_style.toolbar_style)

    # Add icon button to toolbar (without dropdown arrow)
    # self.icon_button = QToolButton()
    # self.icon_button.setIcon(QIcon(files.path_arrow_icon))
    # self.icon_button.setIconSize(QSize(18, 18))
    # self.icon_button.setStyleSheet(toolbar_style.toolbar_arrow_style)
    # self.toolbar.addWidget(self.icon_button)

    # # Create a stylish text label
    # self.toolbar_label = QLabel("System Description")
    # self.toolbar_label.setStyleSheet(toolbar_style.toolbar_label_style)
    # self.toolbar.addWidget(self.toolbar_label)

    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(spacer)

    self.save_button = QToolButton()
    self.save_button.setIcon(QIcon(buttons["Save"][0]))
    self.save_button.setIconSize(QSize(20, 20))
    self.save_button.setToolTip(buttons["Save"][1])
    self.save_button.clicked.connect(buttons["Save"][2])
    self.save_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.save_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.reload_button = QToolButton()
    self.reload_button.setIcon(QIcon(buttons["Refresh"][0]))
    self.reload_button.setIconSize(QSize(20, 20))
    self.reload_button.setToolTip(buttons["Refresh"][1])
    self.reload_button.clicked.connect(buttons["Refresh"][2])
    self.reload_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.reload_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.toolbar.addSeparator()

    # Create a QComboBox for font selection
    self.font_combo = QComboBox()
    self.font_combo.addItems(["Normal", "Heading"])
    self.font_combo.setFixedSize(QSize(120, 35))
    self.font_combo.setStyleSheet(toolbar_style.toolbar_combobox_style)
    self.font_combo.currentIndexChanged.connect(lambda: self.change_font())
    self.font_combo.currentTextChanged.connect(lambda: self.change_font())
    self.toolbar.addWidget(self.font_combo)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    # Define the font size combo box before referencing it
    self.font_size_combo = QComboBox()
    self.font_size_combo.addItems(
        [str(size) for size in range(8, 31, 2)]
    )  # Add font sizes 8 to 30 in steps of 2
    self.font_size_combo.setFixedSize(QSize(50, 35))
    self.font_size_combo.setStyleSheet(toolbar_style.toolbar_combobox_style)
    self.font_size_combo.currentIndexChanged.connect(lambda: self.change_font_size())
    self.toolbar.addWidget(self.font_size_combo)

    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.bold_button = QToolButton()
    self.bold_button.setIcon(QIcon("assets/Images/bold.svg"))  # Path to your bold icon
    self.bold_button.setIconSize(QSize(20, 20))
    self.bold_button.setToolTip("Bold")
    self.bold_button.setCheckable(True)  # Make it toggleable
    self.bold_button.clicked.connect(
        lambda: self.toggle_bold()
    )
    self.bold_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.bold_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.font_color_button = QToolButton()
    self.font_color_button.setIcon(QIcon(buttons["Font Color"][0]))
    self.font_color_button.setIconSize(QSize(20, 20))
    self.font_color_button.setToolTip(buttons["Font Color"][1])
    self.font_color_button.clicked.connect(lambda: buttons["Font Color"][2]())
    self.font_color_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.font_color_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.highlight_button = QToolButton()
    self.highlight_button.setIcon(QIcon(buttons["Highlight"][0]))
    self.highlight_button.setIconSize(QSize(20, 20))
    self.highlight_button.setToolTip(buttons["Highlight"][1])
    self.highlight_button.clicked.connect(lambda: buttons["Highlight"][2]())
    self.highlight_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.highlight_button.setCheckable(True) 
    self.toolbar.addWidget(self.highlight_button)

    self.italic_button = QToolButton()
    self.italic_button.setIcon(QIcon(buttons["Italic"][0]))
    self.italic_button.setIconSize(QSize(20, 20))
    self.italic_button.setToolTip(buttons["Italic"][1])
    self.italic_button.clicked.connect(lambda: buttons["Italic"][2]())
    self.italic_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.italic_button.setCheckable(True)
    self.toolbar.addWidget(self.italic_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the 
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.image_button = QToolButton()
    self.image_button.setIcon(QIcon(buttons["Insert Picture"][0]))
    self.image_button.setIconSize(QSize(20, 20))
    self.image_button.setToolTip(buttons["Insert Picture"][1])
    self.image_button.clicked.connect(lambda: buttons["Insert Picture"][2]())
    self.image_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.image_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.toolbar.addSeparator()

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.bullet_button = QToolButton()
    self.bullet_button.setIcon(QIcon(buttons["Bullets"][0]))
    self.bullet_button.setIconSize(QSize(20, 20))
    self.bullet_button.setToolTip(buttons["Bullets"][1])
    self.bullet_button.clicked.connect(lambda: buttons["Bullets"][2]())
    self.bullet_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.bullet_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.numeric_button = QToolButton()
    self.numeric_button.setIcon(QIcon(buttons["Numbering"][0]))
    self.numeric_button.setIconSize(QSize(20, 20))
    self.numeric_button.setToolTip(buttons["Numbering"][1])
    self.numeric_button.clicked.connect(lambda: buttons["Numbering"][2]())
    self.numeric_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.numeric_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.toolbar.addSeparator()

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(10)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    # Create the alignment button with a dropdown menu
    self.align_button = QToolButton()
    self.align_button.setIcon(
        QIcon("assets/images/left_align.png")
    )  # Path to your align_justified.svg file
    self.align_button.setIconSize(QSize(20, 20))
    self.align_button.setToolTip("Alignment")
    self.align_button.setStyleSheet(toolbar_style.toolbar_button_style)

    # **Ensure there is spacing between the icon and dropdown arrow**
    self.align_button.setToolButtonStyle(
        Qt.ToolButtonTextBesideIcon
    )  # Ensures proper spacing
    self.align_button.setPopupMode(
        QToolButton.InstantPopup
    )  # Prevents the arrow from colliding

    # **FIX: Add right padding for dropdown arrow**
    self.align_button.setStyleSheet(
        """
    QToolButton {
        padding-right: 4px;  /* Reduce space between icon and dropdown */
        padding-bottom: 0px; /* Ensure no downward misalignment */
        border: none; /* Ensure no unwanted border */
    }
    QToolButton::menu-indicator {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        padding-right: 2px;  /* Adjust right spacing */
        padding-bottom: 0px;  /* Align properly */
    }
"""
    )

    # Create a custom QWidget to act as the dropdown content
    align_dropdown_widget = QFrame()
    align_dropdown_layout = QHBoxLayout(align_dropdown_widget)
    align_dropdown_layout.setSpacing(5)  # Space between icons
    align_dropdown_layout.setContentsMargins(5, 5, 5, 5)  # Add padding

    # Create buttons for Left Align, Center Align, and Right Align
    left_align_button = QPushButton()
    left_align_button.setIcon(QIcon(buttons["Left Align"][0]))
    left_align_button.setIconSize(QSize(20, 20))
    left_align_button.setToolTip(buttons["Left Align"][1])
    left_align_button.clicked.connect(lambda: buttons["Left Align"][2]())
    left_align_button.setStyleSheet("border: none; background: white;")

    center_align_button = QPushButton()
    center_align_button.setIcon(QIcon(buttons["Center Align"][0]))
    center_align_button.setIconSize(QSize(20, 20))
    center_align_button.setToolTip(buttons["Center Align"][1])
    center_align_button.clicked.connect(lambda: buttons["Center Align"][2]())
    center_align_button.setStyleSheet("border: none; background: white;")

    right_align_button = QPushButton()
    right_align_button.setIcon(QIcon(buttons["Right Align"][0]))
    right_align_button.setIconSize(QSize(20, 20))
    right_align_button.setToolTip(buttons["Right Align"][1])
    right_align_button.clicked.connect(lambda: buttons["Right Align"][2]())
    right_align_button.setStyleSheet("border: none; background: white;")

    justify_button = QPushButton()
    justify_button.setIcon(QIcon(buttons["Justify"][0]))
    justify_button.setIconSize(QSize(20, 20))
    justify_button.setToolTip(buttons["Justify"][1])
    justify_button.clicked.connect(lambda: buttons["Justify"][2]())
    justify_button.setStyleSheet("border: none; background: white;")

    # Add the buttons to the layout
    align_dropdown_layout.addWidget(left_align_button)
    align_dropdown_layout.addWidget(center_align_button)
    align_dropdown_layout.addWidget(right_align_button)
    align_dropdown_layout.addWidget(justify_button)

    # Create a QMenu and add the custom widget
    align_menu = QMenu(self.align_button)
    align_menu.setStyleSheet(
        "QMenu { background-color: white; border: 1px solid #ccc; }"
    )  # Optional styling
    action = QWidgetAction(align_menu)
    action.setDefaultWidget(align_dropdown_widget)
    align_menu.addAction(action)

    # Set the menu to the align button
    self.align_button.setMenu(align_menu)
    self.align_button.setPopupMode(QToolButton.InstantPopup)

    # Add the alignment button to the toolbar
    self.toolbar.addWidget(self.align_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(10)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    self.toolbar.addSeparator()

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    # # Add Insert Table button
    
    self.table_button = QToolButton()
    self.table_button.setIcon(QIcon(buttons["Insert Table"][0]))
    self.table_button.setIconSize(QSize(20, 20))
    self.table_button.setToolTip(buttons["Insert Table"][1])
    self.table_button.clicked.connect(buttons["Insert Table"][2])
    self.table_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.table_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    # Create a QToolButton for the Insert Options dropdown
    self.insert_dropdown_button = QToolButton()
    self.insert_dropdown_button.setIcon(
        QIcon(buttons["Insert Column Left"][0])
    )  # Use Column Left icon
    self.insert_dropdown_button.setIconSize(QSize(20, 20))
    self.insert_dropdown_button.setToolTip("Insert Options")
    self.insert_dropdown_button.setPopupMode(
        QToolButton.InstantPopup
    )  # Ensure instant dropdown

    # **Fix: Properly align the dropdown arrow beside the icon**
    self.insert_dropdown_button.setStyleSheet(
        """
    QToolButton {
        padding-right: 6px;  /* Increase space between icon and dropdown arrow */
        padding-bottom: 1px; /* Slightly move the dropdown arrow up */
        border: none; /* Remove the grey border issue */
        background-color: transparent; /* Ensure no unwanted background color */
        vertical-align: middle; /* Ensure vertical alignment */
    }
    QToolButton::menu-indicator {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        padding-right: 4px;  /* Slightly move the arrow to the right */
        padding-bottom: 1px; /* Adjust vertical centering */
    }
"""
    )

    # **Add proper spacing to separate dropdown from adjacent icons**
    small_spacer = QWidget()
    small_spacer.setFixedWidth(7)  # Adjusted for better balance
    self.toolbar.addWidget(small_spacer)

    # # Create a custom QWidget for the dropdown content
    insert_dropdown_widget = QFrame()
    insert_dropdown_layout = QHBoxLayout(insert_dropdown_widget)
    insert_dropdown_layout.setSpacing(5)  # Space between icons
    insert_dropdown_layout.setContentsMargins(5, 5, 5, 5)  # Add padding

    # # Add actions as icons in the dropdown
    insert_column_left_button = QPushButton()
    insert_column_left_button.setIcon(QIcon(buttons["Insert Column Left"][0]))
    insert_column_left_button.setIconSize(QSize(20, 20))
    insert_column_left_button.setToolTip("Insert Column Left")
    insert_column_left_button.clicked.connect(
         lambda: buttons["Insert Column Left"][2]()
     )
    insert_column_left_button.setStyleSheet("border: none; background: white;")

    insert_column_right_button = QPushButton()
    insert_column_right_button.setIcon(QIcon(buttons["Insert Column Right"][0]))
    insert_column_right_button.setIconSize(QSize(20, 20))
    insert_column_right_button.setToolTip("Insert Column Right")
    insert_column_right_button.clicked.connect(
         lambda: buttons["Insert Column Right"][2]()
     )
    insert_column_right_button.setStyleSheet("border: none; background: white;")

    insert_row_above_button = QPushButton()
    insert_row_above_button.setIcon(QIcon(buttons["Insert Row Above"][0]))
    insert_row_above_button.setIconSize(QSize(20, 20))
    insert_row_above_button.setToolTip("Insert Row Above")
    insert_row_above_button.clicked.connect(lambda: buttons["Insert Row Above"][2]())
    insert_row_above_button.setStyleSheet("border: none; background: white;")

    insert_row_below_button = QPushButton()
    insert_row_below_button.setIcon(QIcon(buttons["Insert Row Below"][0]))
    insert_row_below_button.setIconSize(QSize(20, 20))
    insert_row_below_button.setToolTip("Insert Row Below")
    insert_row_below_button.clicked.connect(lambda: buttons["Insert Row Below"][2]())
    insert_row_below_button.setStyleSheet("border: none; background: white;")

    # # Add buttons to the layout
    insert_dropdown_layout.addWidget(insert_column_left_button)
    insert_dropdown_layout.addWidget(insert_column_right_button)
    insert_dropdown_layout.addWidget(insert_row_above_button)
    insert_dropdown_layout.addWidget(insert_row_below_button)

    # # Create a QMenu and add the custom widget
    insert_menu = QMenu(self.insert_dropdown_button)
    insert_menu.setStyleSheet(
         "QMenu { background-color: white; border: 1px solid #ccc; }"
     )
    insert_action = QWidgetAction(insert_menu)
    insert_action.setDefaultWidget(insert_dropdown_widget)
    insert_menu.addAction(insert_action)

    # # Set the menu to the dropdown button
    self.insert_dropdown_button.setMenu(insert_menu)

    # # Add the dropdown button to the toolbar
    self.toolbar.addWidget(self.insert_dropdown_button)

    # **Fix: Add proper spacing to avoid collision with next button**
    large_spacer = QWidget()
    large_spacer.setFixedWidth(10)  # Adjust width as needed
    self.toolbar.addWidget(large_spacer)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    # Add Delete Row button to the toolbar
    self.delete_row_button = QToolButton()
    self.delete_row_button.setIcon(QIcon(buttons["Delete Row"][0]))
    self.delete_row_button.setIconSize(QSize(20, 20))
    self.delete_row_button.setToolTip(buttons["Delete Row"][1])
    self.delete_row_button.clicked.connect(lambda: buttons["Delete Row"][2]())
    self.delete_row_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.delete_row_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(5)
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)

    # Add Delete Column button to the toolbar
    self.delete_column_button = QToolButton()
    self.delete_column_button.setIcon(QIcon(buttons["Delete Column"][0]))
    self.delete_column_button.setIconSize(QSize(20, 20))
    self.delete_column_button.setToolTip(buttons["Delete Column"][1])
    self.delete_column_button.clicked.connect(lambda: buttons["Delete Column"][2]())
    self.delete_column_button.setStyleSheet(toolbar_style.toolbar_button_style)
    self.toolbar.addWidget(self.delete_column_button)

    # Add a small spacer between buttons
    small_spacer = QWidget()
    small_spacer.setFixedWidth(10)  # Adjust the width as needed
    small_spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(small_spacer)
