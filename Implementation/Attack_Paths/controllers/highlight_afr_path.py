"""
Module: arrow line tree utils      \n 
File: highlight_afr_path.py      \n
Layer: UI / Tree Arrow Management    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-04     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Provides utility functions for rendering and managing arrows between tree nodes
in a QGraphicsScene. This includes flattening nested node structures, creating
arrow lines between parent and child nodes, and updating arrow styles based on
logical path selection.

Description:
------------
The module integrates with the ArrowRenderer class to visually connect nodes
with directional arrows in tree or graph structures. It flattens nested data
representations into a renderable node map and establishes correct parent-child
relationships for arrow creation. The utilities also support updating arrow
styles dynamically during interaction.

Responsibilities
----------------
- Flatten hierarchical node structures to flat maps keyed by node_id.
- Automatically generate directional arrows between parent and child items.
- Configure update callbacks for node movement to update arrows.
- Dynamically update visual paths during selection changes.

Dependencies:
-------------
- PyQt5.QtWidgets.QGraphicsScene
- ArrowRenderer (Attack_Paths.controllers.arrow_line_creator)

Classes/Functions:
-------------
- create_arrow_lines(scene, nodes, rootnode_id, selected_nodes)
- update_arrow_lines(renderer, selected_nodes)
- flatten_tree(tree_node, parent_id, result)
- create_arrows_for_tree(renderer, parent_node)

Limitations
-----------
- Assumes nodes have 'node_id', 'node', 'childrens'.
- 'node' must be a QGraphicsObject with arrow_update_callback and node_id.
- Flat map construction does not validate uniqueness of node_ids.

Improvements
------------
- Add schema validation for tree input structure.
- Extract to class-based builder pattern.
- Support dynamic registration of per-node metadata.
- Add debug logging support.

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-04           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from typing import Dict, Optional, Tuple, Set
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsObject
from Attack_Paths.controllers.arrow_line_creator import ArrowRenderer
import styles.tree_style as TS

NodeMap = Dict[str, dict]  # node_id -> node info dict


def create_arrow_lines(scene: QGraphicsScene, nodes: dict, rootnode_id: str, selected_nodes: Set[str]) -> Tuple[ArrowRenderer, NodeMap]:
    """
    Entry point to render arrow lines for a nested tree node structure.

    Args:
        scene (QGraphicsScene): Scene to draw arrows in.
        nodes (dict): Nested tree structure (with children).
        rootnode_id (str): ID of the root node.
        selected_nodes (set): Node IDs to highlight.

    Returns:
        Tuple[ArrowRenderer, dict]: The renderer and flattened node dictionary.
    """
    extracted_tree: NodeMap = flatten_tree(nodes, rootnode_id)

    renderer = ArrowRenderer(scene, extracted_tree, selected_nodes)

    create_arrows_for_tree(renderer, nodes)

    for node_id, node_data in extracted_tree.items():
        node_data["node"].arrow_update_callback = renderer.update_arrow_position
        if node_data["node_type"]=="leaf" and node_id in selected_nodes:
            node_data["node"].highlight_box_border(TS.selectedleafnode_color)

    return renderer, extracted_tree

def update_arrow_lines(renderer: ArrowRenderer, selected_nodes: Set[str], nodes) -> None:
    """
    Update the renderer with a new selected path set.

    Args:
        renderer (ArrowRenderer): The existing renderer.
        selected_nodes (set): Updated path to highlight.
    """
    renderer.set_selected_path(selected_nodes)
    for node_id, node_data in nodes.items():
        if node_data["node_type"]=="leaf":
            if node_id in selected_nodes:
                node_data["node"].highlight_box_border(TS.leafnode_sidebar_color)
            else:
                node_data["node"].highlight_box_border(TS.node_border_color)


def flatten_tree(tree_node: dict, parent_id: Optional[str] = None, result: Optional[NodeMap] = None) -> NodeMap:
    """
    Recursively flattens a nested tree into a dict with parent_id linkage.

    Args:
        tree_node (dict): Current node.
        parent_id (Optional[str]): Parent ID.
        result (Optional[dict]): Accumulator.

    Returns:
        dict: Flattened map of node_id → node info.
    """
    if result is None:
        result = {}

    node_id = tree_node.get("node_id")
    if not node_id or "node" not in tree_node:
        raise ValueError(f"Invalid tree_node: {tree_node}")

    result[node_id] = {
        "node_type": tree_node.get("node_type", "unknown"),
        "node": tree_node["node"],
        "node_id": node_id,
        "parent_id": parent_id
    }

    for child in tree_node.get("childrens", []):
        flatten_tree(child, node_id, result)

    return result


def create_arrows_for_tree(renderer: ArrowRenderer, parent_node: dict) -> None:
    """
    Create arrows recursively from a parent node to its children.

    Args:
        renderer (ArrowRenderer): Renderer object for creating arrows.
        parent_node (dict): Current parent node in tree.
    """
    parent_id = parent_node["node_id"]
    parent_item = parent_node["node"]

    for child in parent_node.get("childrens", []):
        child_id = child["node_id"]
        child_item = child["node"]
        renderer.create_arrow(parent_item, child_item, parent_id, child_id)

        create_arrows_for_tree(renderer, child)

def create_arrow_for_nodes(renderer: ArrowRenderer, tree_node: dict, parent_id: str, parent_node: QGraphicsObject) -> None:
    tree_node["parent_id"] = parent_id
    renderer.nodes[tree_node["node_id"]] = tree_node
    renderer.create_arrow(parent_node, tree_node["node"], parent_id, tree_node["node_id"])
    return tree_node
