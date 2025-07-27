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
        self.row_idx = row_idx
        self.tree_indicator = tree_indicator

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 0, 0)

        # ✅ Row selection indicator (dot)
        self.dot_label = QLabel()
        self.update_dot_color(selected)
        layout.addWidget(self.dot_label)

        # ✅ Optional Tree icon
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

    def update_dot_color(self, selected):
        """Re-color the same SVG icon dynamically."""
        color = "#009D9C" if selected else "#FFFFFF00"  # Green when selected
        pixmap = QPixmap(P.selectedraw_icon).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color))
        painter.end()
        self.dot_label.setPixmap(pixmap)

    def set_selected(self, selected):
        """Call this to dynamically recolor the row indicator."""
        self.update_dot_color(selected)

    def emit_tree_clicked(self):
        print("tree signal...........................")
        if self.row_idx is not None:
            self.tree_button_clicked.emit(self.row_idx)
