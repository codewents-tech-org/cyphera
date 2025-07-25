from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QLabel, QFrame, QGridLayout, QScrollArea
from PyQt5.QtGui import QPainter, QFont, QPen, QPainterPath, QColor
from PyQt5.QtCore import Qt, QPointF
import models.Parameters as P



class CustomScrollContent(QWidget):
    def __init__(self):
        super().__init__()
        self.lines_to_draw = []
        self.line_seen = {}  # To store the lines with color

    def add_line(self, start_box, end_box, color=QColor(P.shadeGray)):
        self.lines_to_draw.append((start_box, end_box))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw each line with its respective color
        for line_info in self.line_seen.values():
            start_box = line_info['start_box']
            end_box = line_info['end_box']
            color = line_info['color']
            painter.setPen(QPen(color, 2))  # Set the line color and width
            start_center = start_box.mapTo(self, start_box.rect().center())
            end_center = end_box.mapTo(self, end_box.rect().center())

            # Calculate half sizes of each box
            start_half_width = start_box.rect().width() / 2
            end_half_width = end_box.rect().width() / 2

            # Set the start point to the right edge center of the start_box
            start_edge_x = start_center.x() + start_half_width
            start_edge_y = start_center.y()

            # Set the end point to the left edge center of the end_box
            end_edge_x = end_center.x() - end_half_width
            end_edge_y = end_center.y()

            # Create a QPainterPath for the curved line
            path = QPainterPath(QPointF(start_edge_x, start_edge_y))

            # Define control points to create a smooth curve
            control_point_1 = QPointF((start_edge_x + end_edge_x) / 2, start_edge_y)
            control_point_2 = QPointF((start_edge_x + end_edge_x) / 2, end_edge_y)

            # Draw the curved path
            path.cubicTo(control_point_1, control_point_2, QPointF(end_edge_x, end_edge_y))

            # Draw the path
            painter.drawPath(path)

        painter.end()
