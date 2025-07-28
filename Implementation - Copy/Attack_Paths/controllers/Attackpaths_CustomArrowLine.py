
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsPolygonItem, QStyle
from PyQt5.QtGui import QColor, QBrush, QPen, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QLineF
import math

import logging
logger = logging.getLogger(__name__)

class CustomArrowLine(QGraphicsLineItem):
    def __init__(self, *args, selected_color="black", **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_color = selected_color
        self.linesize = 2 if selected_color=='black' else 3
        self.setPen(QPen(QColor(self.selected_color), self.linesize))  # Default line color: black
        # self.setFlags(QGraphicsLineItem.ItemIsSelectable)  # Make the line selectable
        # self.set

    def paint(self, painter, option, widget=None):
        pen = QPen(QColor(self.selected_color), self.linesize)
        painter.setPen(pen)
        painter.drawLine(self.line())  # Draw the arrow line


