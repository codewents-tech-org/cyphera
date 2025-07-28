"""
Module: arrow line creator      \n 
File: arrow_line_creator.py      \n
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
Defines the ArrowRenderer class which manages the creation, update, and
visual rendering of arrows between dynamically positioned nodes in a 
QGraphicsScene. It acts as the coordination layer between nodes and arrows.

Description:
------------
The ArrowRenderer class maintains a collection of arrows (`DynamicArrow`)
between parent and child nodes. It handles:
  - Initial arrow creation
  - Redrawing arrows when nodes move
  - Updating arrow styles dynamically based on logical path selection
    
Arrows are visualized using a combination of line segments and arrowheads,
styled via `selected_path` highlighting logic.

Responsibilities
----------------
- Link two nodes with a dynamically styled and positioned arrow.
- Redraw arrows when node geometry changes (drag/move/etc.).
- Track and apply highlighting using `selected_path`.
- Coordinate with `DynamicArrow` for visual line + arrowhead rendering.

Dependencies:
-------------
- Project Modules:
    - Attack_Paths.controllers.dynamic_arrow.DynamicArrow
- PyQt5:
    - QGraphicsScene (indirectly via scene)

Classes:
- ArrowRenderer:
    Manages arrows between nodes and updates them in sync with node changes.

    Constructor:
        ArrowRenderer(scene, nodes, selected_path, threat_id)
            - scene: QGraphicsScene that holds all visual items
            - nodes: dict mapping node_id to QGraphicsObject and arrow references
            - selected_path: set of node_ids to visually highlight
            - threat_id: logical identifier for path group or session context

    Public Methods:
    - create_arrow(start_item, end_item, parent_id, child_id):
        Creates and renders an arrow from parent to child.

    - update_arrow_position(node_id: str):
        Recalculates the geometry of all arrows connected to the node.

    - set_selected_path(new_path: set):
        Updates the active `selected_path` set and refreshes arrow styles.

Limitations
-----------
- Does not remove arrows (only supports creation and update).
- Assumes the node dictionary (`nodes`) is correctly maintained externally.
- Assumes all arrows are directed (parent → child).

Improvements
------------
- Add support for arrow deletion (e.g., when a node is removed).
- Encapsulate node/arrow cleanup logic within this manager.
- Support bidirectional arrows or different arrow types.
- Allow per-arrow style overrides (e.g. dashed, weighted).

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

from Attack_Paths.controllers.dynamic_arrow import DynamicArrow


class ArrowRenderer:
    def __init__(self, scene, nodes: dict, selected_path: set):
        self.scene = scene
        self.nodes = nodes
        self.selected_path = selected_path
        self.arrows = []

    def create_arrow(self, start_item, end_item, parent_id, child_id):
        arrow = DynamicArrow(start_item, end_item, self.scene, parent_id, child_id, self.selected_path)
        self.arrows.append(arrow)
        self.nodes[child_id].setdefault("arrows", []).append(arrow)

    def update_arrow_position(self, node_id: str):
        for arrow in self.nodes[node_id].get("arrows", []):
            arrow.update_position()

    def set_selected_path(self, new_path: set):
        """Update selected path and redraw all arrows."""
        self.selected_path = new_path
        for arrow in self.arrows:
            arrow.selected_path = new_path
            arrow.update_position()
