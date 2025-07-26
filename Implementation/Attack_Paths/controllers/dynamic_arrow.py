"""
Module: dynamic arrow line      \n 
File: dynamic_arrow.py      \n
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
This module renders a multi-segment arrow from a parent node to a child node.
The arrow starts from the bottom-center of the parent item and connects to
the top-center of the child item using an L-shaped or stepwise path
(vertical → horizontal → vertical), ending with a directional arrowhead.
    
The arrow supports dynamic styling based on whether the parent-child pair
is part of a selected/highlighted path. It can update in real-time when
the connected nodes move.

Responsibilities
----------------
- Calculate arrow geometry based on the positions and bounding boxes of nodes.
- Draw vertical and horizontal arrow segments with visual separation.
- Add and remove arrow components (lines and head) from the scene.
- Support dynamic updates when node positions change.
- Reflect visual path highlighting based on a given `selected_path`.

Dependencies:
-------------
- Python built-in: `math`
- PyQt5:
    - QtCore.QPointF
    - QtGui.QPolygonF, QBrush, QPen, QColor
    - QtWidgets.QGraphicsPolygonItem
- Project Modules:
    - Attack_Paths.components.custom_arrow_line.CustomArrowLine
    - styles.tree_style.arrow_color, arrow_highlight_color

Classes:
- DynamicArrow:
    Connects two QGraphicsItems (start and end) and draws an arrow between them.
    Manages line segments, an arrowhead, and dynamic redraws.

    Constructor Arguments:
    - start_item: QGraphicsItem, parent node
    - end_item: QGraphicsItem, child node
    - scene: QGraphicsScene to draw in
    - parent_id (str): logical parent node ID
    - child_id (str): logical child node ID
    - selected_path (set): logical path of nodes to highlight

    Public Methods:
    - update_position(): Recomputes and redraws arrow based on current node geometry.
    - remove_from_scene(): Removes all visual components from the scene.

Limitations
-----------
- Only supports step-style (right-angled) arrow layout; no curved or diagonal paths.
- Arrowhead orientation is limited to straight-line vector direction.
- Does not support animation or transitions between movements.
- Relies on node boundingRect() and scenePos() which assume rectangular nodes.

Improvements
------------
- Support Bezier or curved arrows for more natural layouts.
- Add animation when repositioning the arrow for smoother UX.
- Enable selection, highlighting, and user interaction with the arrow.
- Refactor to support custom arrowhead shapes or multiple styles.
- Abstract arrow style and layout as strategies (e.g. Strategy Pattern).

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

import math
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QGraphicsPolygonItem
from PyQt5.QtGui import QPolygonF, QBrush, QPen, QColor
from Attack_Paths.components.custom_arrow_line import CustomArrowLine
from styles.tree_style import arrow_highlight_color, arrow_color


class DynamicArrow:
    def __init__(self, start_item, end_item, scene, parent_id, child_id, selected_path):
        self.start_item = start_item
        self.end_item = end_item
        self.scene = scene
        self.parent_id = parent_id
        self.child_id = child_id
        self.selected_path = selected_path

        self.lines = []
        self.arrow_head = None
        self.update_position()

    def remove_from_scene(self):
        for line in self.lines:
            if line.scene():
                self.scene.removeItem(line)
        if self.arrow_head and self.arrow_head.scene():
            self.scene.removeItem(self.arrow_head)

    def update_position(self):
        self.remove_from_scene()
        self.lines.clear()

        parent_rect = self.start_item.boundingRect()
        child_rect = self.end_item.boundingRect()

        parent_pos = self.start_item.scenePos()
        child_pos = self.end_item.scenePos()

        # Bottom-center of parent
        start = QPointF(parent_pos.x() + parent_rect.width() / 2,
                        parent_pos.y() + parent_rect.height())

        # Top-center of child, slightly inset to ensure arrow touches node
        end = QPointF(child_pos.x() + child_rect.width() / 2, child_pos.y())

        mid_y = (start.y() + end.y()) / 2
        mid_v = QPointF(start.x(), mid_y)
        mid_h = QPointF(end.x(), mid_y)

        vc = arrow_highlight_color if self.parent_id in self.selected_path else arrow_color
        hc = arrow_highlight_color if (self.parent_id in self.selected_path and self.child_id in self.selected_path) else arrow_color

        v1 = CustomArrowLine(start.x(), start.y(), mid_v.x(), mid_v.y(), vc)
        h = CustomArrowLine(mid_v.x(), mid_v.y(), mid_h.x(), mid_h.y(), hc)
        v2 = CustomArrowLine(mid_h.x(), mid_h.y(), end.x(), end.y(), hc)

        for line in (v1, h, v2):
            self.scene.addItem(line)
            self.lines.append(line)

        angle = math.atan2(end.y() - mid_h.y(), end.x() - mid_h.x())
        size = 8
        arrowhead = QPolygonF([
            end,
            end + QPointF(math.sin(angle - math.pi / 3) * size, -math.cos(angle - math.pi / 3) * size),
            end + QPointF(math.sin(angle - math.pi + math.pi / 3) * size, -math.cos(angle - math.pi + math.pi / 3) * size),
        ])

        self.arrow_head = QGraphicsPolygonItem(arrowhead)
        self.arrow_head.setBrush(QBrush(QColor(hc)))
        self.arrow_head.setPen(QPen(QColor(hc), 2))
        self.scene.addItem(self.arrow_head)
