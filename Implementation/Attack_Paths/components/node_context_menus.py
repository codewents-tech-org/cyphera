"""
Module: Node Context Menu Builder      \n 
File: node_context_menus.py      \n
Layer: UI / Menu Components    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-02     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Dynamically build context menus for `GraphicsGroupBox` nodes, supporting creation
and attachment of child nodes such as leaf, intermediate, technical, and control trees.

Description:
------------
Provides a utility function that creates and returns a fully populated `QMenu`
customized per node’s state and type. Menu actions emit appropriate signals for
integration with scene controllers.

Responsibilities
----------------
- Generate consistent right-click menus for tree nodes
- Allow nested submenus for new and existing leaf nodes
- Support dynamic menu population from `available_*` dictionaries
- Respect the type of tree for filtering valid actions

Dependencies:
-------------
- PyQt5.QtWidgets.QMenu

Functions:
-------------
- build_graphics_node_context_menu(node, insert_enable=True) → QMenu

Parameters:
-------------
- node: GraphicsGroupBox instance that exposes:
      - font
      - tree_type (e.g., "AttackTree")
      - tree_id (str)
      - available_leaf_nodes, available_technical_trees, available_control_trees
      - appropriate signals like: addLeafRequested, removeRequested, etc.
- insert_enable (bool): Whether to include "add node" actions

Limitations
-----------
- Tightly coupled to GraphicsGroupBox structure and signal names
- No keyboard or accessibility integration
- Menu localization (i18n) not supported

Improvements
------------
- Decouple signal names or use signal mapping via interface/protocol
- Add icons or tooltips for each menu action
- Add keyboard shortcut support or hover previews
- Cache menus to improve performance if reused frequently

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

from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QFont
import styles.tree_style as TS

def build_graphics_node_context_menu(node, insert_enable=True, is_rootnode=False):
    """
    Builds and returns a context menu for a GraphicsGroupBox node.

    Args:
        node: The GraphicsGroupBox instance (expected to expose signals & tree_type).
        insert_enable (bool): Whether to include node-insertion actions.

    Returns:
        QMenu: The constructed context menu.
    """
    menu = QMenu()
    menu.setFont(node.font)
    menu.setFont((QFont(TS.node_font_family, 8, QFont.Normal)))

    if insert_enable:
        # Add intermediate node
        action_add_intermediate = menu.addAction("Add Intermediate Node")
        action_add_intermediate.triggered.connect(lambda: node.addIntermediateRequested.emit({"node": node, "node_id": node.tree_id}))

        # Add Leaf Node
        leaf_menu = QMenu("Add Leaf Node", menu)
        leaf_menu.setFont(node.font)
        leaf_menu.setFont((QFont(TS.node_font_family, 8, QFont.Normal)))
        action_add_new_leaf = leaf_menu.addAction("New Leaf")
        action_add_new_leaf.triggered.connect(lambda: node.addLeafRequested.emit({"node": node, "node_id": node.tree_id, "leaf_id": None}))

        menu_existing_leaf = QMenu("Existing Leaf", leaf_menu)
        menu_existing_leaf.setFont((QFont(TS.node_font_family, 8, QFont.Normal)))
        if node.available_leaf_nodes:
            for leaf_id, leaf_name in node.available_leaf_nodes.items():
                action = menu_existing_leaf.addAction(f"{leaf_id}::{leaf_name}")
                action.triggered.connect(lambda checked, id=leaf_id, name=leaf_name: node.addLeafRequested.emit({"node": node, "node_id": node.tree_id, "leaf_id": id, "leaf_name": name}))
        else:
            no_leaf = menu_existing_leaf.addAction("Leaf Nodes not available")
            no_leaf.setEnabled(False)

        leaf_menu.addMenu(menu_existing_leaf)
        menu.addMenu(leaf_menu)

        # Risk Control Tree
        if node.tree_type == "AttackTree":
            rc_menu = QMenu("Add Risk Control Tree", menu)
            rc_menu.setFont((QFont(TS.node_font_family, 8, QFont.Normal)))
            print(f"Available Risk Control Trees: {node.available_control_trees}")
            if node.available_control_trees:
                for cid, cname in node.available_control_trees.items():
                    action = rc_menu.addAction(f"{cid}::{cname}")
                    action.triggered.connect(lambda checked, id=cid, name=cname: node.addRiskControlTreeRequested.emit({"node_id": node.tree_id, 
                                                                                                                        "node": node, "tat_id": id}, "RiskControlTree"))
            else:
                no_rc = rc_menu.addAction("Risk Control Trees not available")
                no_rc.setEnabled(False)
            menu.addMenu(rc_menu)

        # Technical Tree
        if node.tree_type in {"AttackTree", "RiskControlTree"}:
            tech_menu = QMenu("Add Technical Tree", menu)
            tech_menu.setFont((QFont(TS.node_font_family, 8, QFont.Normal)))
            if node.available_technical_trees:
                for tid, tname in node.available_technical_trees.items():
                    action = tech_menu.addAction(f"{tid}::{tname}")
                    action.triggered.connect(lambda checked, id=tid, name=tname: node.addTechnicalTreeRequested.emit({"node_id": node.tree_id, 
                                                                                                                      "node": node, "tat_id": id}, "TechnicalTree"))
            else:
                no_tt = tech_menu.addAction("Technical Trees not available")
                no_tt.setEnabled(False)
            menu.addMenu(tech_menu)

    if not is_rootnode:
        # Remove Node
        action_remove = menu.addAction("Remove Node")
        action_remove.triggered.connect(lambda: node.removeRequested.emit(node.tree_id))

    return menu
