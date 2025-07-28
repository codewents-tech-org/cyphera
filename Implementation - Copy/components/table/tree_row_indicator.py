from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt, pyqtSignal
import models.Parameters as P
import logging

logger = logging.getLogger(__name__)

ROUND_BUTTON_SIZE = 16
TREE_BUTTON_SIZE = 24
BUTTON_MARGIN_LEFT = 15


class SidebarWidget(QWidget):
    """
    Sidebar widget for table row indication (selection, expand).
    Used across modules like Security Goals, Assumptions, etc.

    Args:
        selected (bool): Whether this row is currently selected (green icon).
        parent (QWidget): Parent widget.
        index (int): Optional index if needed for tree expansion logic.
        tree_indicator (bool): Whether to include a tree expand button.
    """

    tree_button_requested = pyqtSignal(int)

    def __init__(self, selected=False, parent=None, index=None, tree_indicator=False):
        super().__init__(parent)
        self.selected = selected
        self.index = index

        layout = QHBoxLayout()
        layout.setContentsMargins(BUTTON_MARGIN_LEFT, 0, 0, 0)
        layout.setAlignment(Qt.AlignLeft)

        # Indicator Icon (selected/deselected)
        self.round_button = QPushButton()
        self.round_button.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.round_button.setIcon(QIcon(P.selectedrow_icon if selected else P.deselectedrow_icon))
        self.round_button.setIconSize(QSize(ROUND_BUTTON_SIZE, ROUND_BUTTON_SIZE))
        self.round_button.setFixedSize(ROUND_BUTTON_SIZE, ROUND_BUTTON_SIZE)
        self.round_button.clicked.connect(self.delete_row)
        layout.addWidget(self.round_button)

        # Optional Tree Expand Button
        if tree_indicator:
            self.tree_button = QPushButton()
            self.tree_button.setIcon(QIcon(P.selectedrow_icon))
            self.tree_button.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
            self.tree_button.setIconSize(QSize(TREE_BUTTON_SIZE, TREE_BUTTON_SIZE))
            self.tree_button.setFixedSize(TREE_BUTTON_SIZE, TREE_BUTTON_SIZE)
            self.tree_button.clicked.connect(self.open_tree)
            layout.addWidget(self.tree_button)

        layout.addStretch()
        self.setLayout(layout)

    def set_selected(self, selected: bool):
        """
        Updates the icon to show selected or not.
        """
        self.selected = selected
        icon = QIcon(P.selectedrow_icon if selected else P.deselectedrow_icon)
        self.round_button.setIcon(icon)

    def delete_row(self):
        logger.info("Delete placeholder clicked")

    def open_tree(self):
        self.tree_button_requested.emit(self.index)
