from PyQt5.QtWidgets import (
    QWidget, QLabel, QToolBar, QToolButton, QSizePolicy, QComboBox, QMenu,
    QFrame, QHBoxLayout, QPushButton, QWidgetAction
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
import utils.file_utils as files
import styles.toolbar_style as toolbar_style
import logging

logger = logging.getLogger(__name__)

def create_toolbar(self, buttons, heading_text):
    """
    Create a styled, interactive toolbar with formatting and table controls.

    Args:
        self: The parent class or UI instance where this toolbar is used.
        buttons (dict): Dictionary of button configurations with structure:
            {
                'Button Name': (icon_path: str, tooltip: str, callback: callable)
            }
        heading_text (str): Heading label to show beside the toolbar icon.

    Returns:
        tuple: (QToolBar instance, dict of QPushButton/QToolButton/QComboBox refs)
    """
    logger.info("Toolbar creation")
    refs = {}

    # Toolbar setup
    self.toolbar = QToolBar("")
    self.toolbar.setMovable(False)
    self.toolbar.setContentsMargins(0, 0, 0, 0)
    self.toolbar.setStyleSheet(toolbar_style.toolbar_style)

    # Toolbar icon
    self.icon_button = QToolButton()
    self.icon_button.setIcon(QIcon(files.path_arrow_icon))
    self.icon_button.setIconSize(QSize(18, 18))
    self.icon_button.setStyleSheet(toolbar_style.toolbar_arrow_style)
    self.toolbar.addWidget(self.icon_button)

    # Toolbar heading
    self.toolbar_label = QLabel(heading_text)
    self.toolbar_label.setStyleSheet(toolbar_style.toolbar_label_style)
    self.toolbar.addWidget(self.toolbar_label)

    # Expandable spacer
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
    self.toolbar.addWidget(spacer)

    def add_spacer(width=5):
        """Add a fixed-width spacer widget to the toolbar."""
        spacer = QWidget()
        spacer.setFixedWidth(width)
        spacer.setStyleSheet(toolbar_style.toolbar_spacer_style)
        self.toolbar.addWidget(spacer)

    def add_tool_button(name, checkable=False):
        """
        Add a single tool button to the toolbar.

        Args:
            name (str): Button name key from the buttons dict.
            checkable (bool): If True, makes the button toggleable.
        """
        btn = QToolButton()
        btn.setIcon(QIcon(buttons[name][0]))
        btn.setIconSize(QSize(20, 20))
        btn.setToolTip(buttons[name][1])
        btn.clicked.connect(lambda: buttons[name][2]())
        btn.setStyleSheet(toolbar_style.toolbar_button_style)
        btn.setCheckable(checkable)
        self.toolbar.addWidget(btn)
        refs[f"{name.lower().replace(' ', '_')}_button"] = btn

    # Core buttons
    add_tool_button("Save")
    add_spacer()
    add_tool_button("Refresh")
    add_spacer()
    self.toolbar.addSeparator()

    # Font family combo
    self.font_combo = QComboBox()
    self.font_combo.addItems(["Normal", "Heading"])
    self.font_combo.setFixedSize(QSize(120, 35))
    self.font_combo.setStyleSheet(toolbar_style.toolbar_combobox_style)
    self.toolbar.addWidget(self.font_combo)
    refs["font_combo"] = self.font_combo

    add_spacer()

    # Font size combo
    self.font_size_combo = QComboBox()
    self.font_size_combo.addItems([str(size) for size in range(8, 31, 2)])
    self.font_size_combo.setFixedSize(QSize(50, 35))
    self.font_size_combo.setStyleSheet(toolbar_style.toolbar_combobox_style)
    self.toolbar.addWidget(self.font_size_combo)
    refs["font_size_combo"] = self.font_size_combo

    add_spacer()
    add_tool_button("Bold", checkable=True)
    add_spacer()
    add_tool_button("Font Color")
    add_spacer()
    add_tool_button("Highlight", checkable=True)
    add_tool_button("Italic", checkable=True)
    add_spacer()
    add_tool_button("Insert Picture")
    add_spacer()
    self.toolbar.addSeparator()
    add_spacer()
    add_tool_button("Bullets")
    add_spacer()
    add_tool_button("Numbering")
    add_spacer()
    self.toolbar.addSeparator()
    add_spacer(10)

    # Alignment dropdown
    self.align_button = QToolButton()
    self.align_button.setIcon(QIcon("assets/images/left_align.png"))
    self.align_button.setIconSize(QSize(20, 20))
    self.align_button.setToolTip("Alignment")
    self.align_button.setStyleSheet(toolbar_style.toolbar_dropdown_button_style)
    self.align_button.setPopupMode(QToolButton.InstantPopup)

    align_widget = QFrame()
    align_layout = QHBoxLayout(align_widget)
    align_layout.setSpacing(5)
    align_layout.setContentsMargins(5, 5, 5, 5)

    for key in ["Left Align", "Center Align", "Right Align", "Justify"]:
        btn = QPushButton()
        btn.setIcon(QIcon(buttons[key][0]))
        btn.setIconSize(QSize(20, 20))
        btn.setToolTip(buttons[key][1])
        btn.clicked.connect(lambda _, k=key: buttons[k][2]())
        btn.setStyleSheet(toolbar_style.toolbar_dropdown_button_inner_style)
        align_layout.addWidget(btn)
        refs[f"{key.lower().replace(' ', '_')}_button"] = btn

    align_menu = QMenu(self.align_button)
    align_menu.setStyleSheet(toolbar_style.toolbar_dropdown_menu_style)
    action = QWidgetAction(align_menu)
    action.setDefaultWidget(align_widget)
    align_menu.addAction(action)
    self.align_button.setMenu(align_menu)
    self.toolbar.addWidget(self.align_button)

    add_spacer(10)
    self.toolbar.addSeparator()
    add_spacer()

    # Insert Table
    add_tool_button("Insert Table")
    add_spacer()

    # Insert dropdown
    self.insert_dropdown_button = QToolButton()
    self.insert_dropdown_button.setIcon(QIcon(buttons["Insert Column Left"][0]))
    self.insert_dropdown_button.setIconSize(QSize(20, 20))
    self.insert_dropdown_button.setToolTip("Insert Options")
    self.insert_dropdown_button.setPopupMode(QToolButton.InstantPopup)
    self.insert_dropdown_button.setStyleSheet(toolbar_style.toolbar_dropdown_button_style)

    insert_widget = QFrame()
    insert_layout = QHBoxLayout(insert_widget)
    insert_layout.setSpacing(5)
    insert_layout.setContentsMargins(5, 5, 5, 5)

    for key in ["Insert Column Left", "Insert Column Right", "Insert Row Above", "Insert Row Below"]:
        btn = QPushButton()
        btn.setIcon(QIcon(buttons[key][0]))
        btn.setIconSize(QSize(20, 20))
        btn.setToolTip(buttons[key][1])
        btn.clicked.connect(lambda _, k=key: buttons[k][2]())
        btn.setStyleSheet(toolbar_style.toolbar_dropdown_button_inner_style)
        insert_layout.addWidget(btn)
        refs[f"{key.lower().replace(' ', '_')}_button"] = btn

    insert_menu = QMenu(self.insert_dropdown_button)
    insert_menu.setStyleSheet(toolbar_style.toolbar_dropdown_menu_style)
    insert_action = QWidgetAction(insert_menu)
    insert_action.setDefaultWidget(insert_widget)
    insert_menu.addAction(insert_action)
    self.insert_dropdown_button.setMenu(insert_menu)
    self.toolbar.addWidget(self.insert_dropdown_button)

    add_spacer(10)
    add_spacer()

    # Delete buttons
    add_tool_button("Delete Row")
    add_spacer()
    add_tool_button("Delete Column")
    add_spacer(10)

    return self.toolbar, refs