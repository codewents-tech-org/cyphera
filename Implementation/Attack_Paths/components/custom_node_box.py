"""
Module: Custom Node Box      \n 
File: custom_node_box.py      \n
Layer: UI / Graphics Items    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-02     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Provides a reusable background graphics item for visualizing node containers in
hierarchical tree visualizations such as Attack Trees, Risk Control Trees, etc.

Description:
------------
This module defines a stylized rectangular graphics item with rounded corners
and an optional colored left sidebar. It is typically used as a visual background
for composite node elements such as intermediate nodes, leaves, or control gates.

Responsibilities
----------------
- Render a node background with:
   - Rounded rectangular main area
   - Colored left sidebar with curved corners
- Maintain consistent z-index for visual layering
- Support customization of size and sidebar color

Dependencies:
-------------
- PyQt5.QtWidgets.QGraphicsItem
- PyQt5.QtGui (QPainter, QPen, QBrush, QColor, QPainterPath)
- PyQt5.QtCore (QRectF, Qt)
- styles.tree_style (custom style variables for node background/border)

Classes:
-------------
- NodeBackgroundItem(QGraphicsItem):
    - Parameters:
        - width (int)
        - height (int)
        - sidebar_width (int)
        - sidebar_color (str)

Limitations
-----------
- No dynamic resizing or scaling support
- Static radius for rounded corners
- Not interactive (doesn't respond to events like hover/click)

Improvements
------------
- Add support for hover/selection state coloring
- Animate sidebar or corner radius on state change
- Add click and focus signals for interaction
- Parameterize corner radius and shadow styling

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-02           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor
from PyQt5.QtCore import QRectF, Qt
import styles.tree_style as TS


class NodeBackgroundItem(QGraphicsItem):
    """
    A reusable background component with rounded corners and a left-colored sidebar.
    Used as the base background for tree nodes (e.g., AttackTree, RiskControlTree).

    Attributes:
        width (int): Total width of the node box.
        height (int): Total height of the node box.
        sidebar_width (int): Width of the left-colored sidebar.
        sidebar_color (str): Hex color code for the sidebar background.
    """

    def __init__(self, width: int, height: int, sidebar_width: int = 10, sidebar_color="#ffffff", parent=None):
        """
        Initializes the background with specified dimensions and sidebar color.

        Args:
            width (int): Width of the box.
            height (int): Height of the box.
            sidebar_width (int): Width of the sidebar area.
            sidebar_color (str): Sidebar fill color (hex).
            parent (QGraphicsItem, optional): Optional parent graphics item.
        """
        super().__init__(parent)
        self.width = width
        self.height = height
        self.sidebar_width = sidebar_width
        self.sidebar_color = sidebar_color
        self.border_color = TS.node_border_color  # Main box background color
        self.setZValue(-1)  # Ensure it's drawn behind text/items

    def boundingRect(self) -> QRectF:
        """
        Returns the bounding rectangle of the background item.

        Returns:
            QRectF: The drawing area boundary.
        """
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None):
        """
        Paints the background box with rounded corners and a left sidebar.

        Args:
            painter (QPainter): Painter used to draw the item.
            option (QStyleOptionGraphicsItem): Not used.
            widget (QWidget): Not used.
        """
        # --- Main Rounded Box ---
        box_rect = QRectF(0, 0, self.width - self.sidebar_width, self.height)
        box_path = QPainterPath()
        box_path.addRoundedRect(box_rect, 10, 10)

        painter.setBrush(QBrush(QColor(TS.node_bg)))
        painter.setPen(QPen(QColor(self.border_color), 2))
        painter.drawPath(box_path)

        # --- Left Sidebar with rounded left corners ---
        sidebar_path = QPainterPath()
        sidebar_path.moveTo(0, 10)
        sidebar_path.quadTo(0, 0, 10, 0)
        sidebar_path.lineTo(10, self.height)
        sidebar_path.quadTo(0, self.height, 0, self.height - 10)
        sidebar_path.closeSubpath()

        painter.setBrush(QBrush(QColor(self.sidebar_color)))
        painter.setPen(Qt.NoPen)
        painter.drawPath(sidebar_path)
    
    def set_border_color(self, color: str) -> None:
        """
        Dynamically updates the border color of the box.

        Args:
            color (str): Hex color code (e.g., "#FF0000")
        """
        self.border_color = color
        self.update()  # Schedule repaint
