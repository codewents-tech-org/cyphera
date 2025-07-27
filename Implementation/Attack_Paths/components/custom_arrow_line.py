"""
Module: custom arrow line      \n 
File: custom_arrow_line.py      \n
Layer: UI / Tree layer    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-06-27     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Provides a custom implementation of QGraphicsLineItem used to visually
represent segments of directional arrows between node items in a 
QGraphicsScene-based layout, such as tree diagrams, graphs, or flow editors.

Description:
------------
This module defines the `CustomArrowLine` class, a subclass of 
QGraphicsLineItem, which encapsulates styling and layering behavior 
for lines that represent arrows in a graphics scene. It allows setting 
color and style for better visual clarity and separation from node elements.

Responsibilities
----------------
- Draw a line segment between two points with a specified color.
- Maintain visual layering (rendered below node elements).
- Serve as a building block for complex arrows in hierarchical or 
  graph-based views.

Dependencies:
-------------
- PyQt5.QtWidgets.QGraphicsLineItem
- PyQt5.QtGui.QPen, QColor
- PyQt5.QtCore.Qt (for line styles and z-order)

Classes:
- CustomArrowLine: A stylized line item with configurable color and 
  rendering priority (z-value).

Limitations
-----------
- No built-in support for interactivity (hover, click, animation).
- Does not include arrowheads (use alongside DynamicArrow for full arrows).
- Color and style are fixed at creation (no dynamic styling methods yet).

Improvements
------------
- Add support for dynamic hover or selection styles.
- Provide runtime methods to update color or width.
- Integrate animation for progressive drawing or transition effects.
- Support dashed or highlighted stroke variants for temporary states.
- Introduce signal emitting for debugging or tracing path interaction.

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-06-27           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""


from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtGui import QPen, QColor


class CustomArrowLine(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, selected_color="#000000"):
        super().__init__(x1, y1, x2, y2)
        pen = QPen(QColor(selected_color), 2)
        self.setPen(pen)
