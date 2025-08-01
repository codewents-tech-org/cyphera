from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QColor, QBrush

class TransparentBackgroundDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.backgroundBrush = QBrush(QColor(255, 255, 255, 0))  # fully transparent
        super().paint(painter, option, index)
