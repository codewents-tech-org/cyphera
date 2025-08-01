from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QPainter, QColor
from PyQt5.QtCore import QSize, pyqtSignal, Qt
import models.Parameters as P
import logging

logger = logging.getLogger(__name__)


class SidebarWidget(QWidget):
    tree_button_clicked = pyqtSignal(int)  # row index

    def __init__(self, row_idx=None, selected=False, tree_indicator=False, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

        self.row_idx = row_idx
        self.tree_indicator = tree_indicator

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 0, 0)

        self.dot_label = QLabel()
        layout.addWidget(self.dot_label)

        if self.tree_indicator:
            self.tree_button = QPushButton()
            self.tree_button.setIcon(QIcon(P.subtask_icon))
            self.tree_button.setIconSize(QSize(24, 24))
            self.tree_button.setCursor(QCursor(Qt.PointingHandCursor))
            self.tree_button.setStyleSheet("QPushButton { background: transparent; border: none; }")
            self.tree_button.clicked.connect(self.emit_tree_clicked)
            layout.addWidget(self.tree_button)
        else:
            self.tree_button = None

        layout.addStretch()

        self.set_selected(selected)  # ✅ Set the correct initial icon

    def set_selected(self, selected):
        icon_path = P.selectedrow_icon if selected else P.deselectedrow_icon
        pixmap = QPixmap(icon_path).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        if selected:
            # Apply blue color overlay to selected icon
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor("#009D9C"))  # Use your desired blue
            painter.end()

        self.dot_label.setPixmap(pixmap)


    def emit_tree_clicked(self):
        if self.row_idx is not None:
            self.tree_button_clicked.emit(self.row_idx)
