"""
Module: Tree Importer

Purpose:
--------
Handles dynamic importing of a technical tree into a parent node within another tree scene.

Description:
------------
This module allows subtree data (e.g., from a technical tree) to be imported under a given node
of a parent tree (such as in a RiskControl tree). It recursively walks the input structure and
adds intermediate/leaf nodes to the scene, linking them visually and logically.

Author: Vijaya Karagi
Version: V 2.0
Created On: 2025-07-08
"""

from Attack_Paths.controllers.highlight_afr_path import create_arrow_for_nodes
from Attack_Paths.controllers.get_node_label import get_import_tree


class TreeImporter:
    """
    Imports a tree structure into a parent node by manually adding nodes recursively to the scene.
    """

    def __init__(self, scene):
        """
        Initializes the importer.

        Args:
            scene (QGraphicsScene): Target scene to import into.
        """
        self.scene = scene

    def import_tree(self, parent_info: dict, tree_type: str) -> None:
        """
        Imports a subtree and attaches it under the specified parent node.

        Args:
            parent_info (dict): Contains keys:
                - 'node_id': str, ID of parent node
                - 'node': QGraphicsObject, instance of parent node
                - 'tat_id': str, used to fetch import data
            tree_type (str): Type of tree to import (e.g., 'TechnicalTree')
        """
        # Get the external subtree
        imported_tree = get_import_tree(tree_type=tree_type, tree_id=parent_info["tat_id"])
        if not imported_tree:
            print("⚠ No import tree selected or returned.")
            return

        self._recursive_insert(imported_tree, parent_info["node_id"], parent_info["node"], tree_type)

        # Reposition everything and recalculate AFR
        self.scene.tree_layout.apply_layout_positions(self.scene.tree_nodes)
        self.scene.data_process_operation()

    def _recursive_insert(self, node_data: dict, parent_id: str, parent_node, tree_type:str) -> None:
        self.scene.node_counter += 1
        tree_id = f"{self.scene.tat_id}_node_{self.scene.node_counter}"
        node_type = node_data.get("node_type")

        if node_type == "intermediate":
            new_node = self.scene.add_intermediate_node(
                tree_id=tree_id,
                label=node_data.get("node_label", f"Nd-{self.scene.node_counter}"),
                text=node_data.get("node_Text", ""),
                x=node_data.get("x", 0),
                y=node_data.get("y", 0),
                gate=node_data.get("gate", "AND"),
                parent_id=parent_id
            )

        elif node_type == "leaf":
            new_node = self.scene.add_leaf_node(
                tree_id=tree_id,
                label=node_data.get("node_label", f"Lf-{self.scene.node_counter}"),
                text=node_data.get("node_Text", ""),
                x=node_data.get("x", 0),
                y=node_data.get("y", 0),
                af_value=node_data.get("af_value", "0"),
                af_level=node_data.get("af_level", "High"),
                values=node_data.get("values", ['0', '0', '0', '0', '0']),
                parent_id=parent_id
            )
        else:
            new_node = self.scene.add_treehead_node(
                tree_id=tree_id,
                label=node_data.get("node_label", "SubtreeRoot"),
                text=node_data.get("node_Text", ""),
                x=node_data.get("x", 0),
                y=node_data.get("y", 0),
                gate=node_data.get("gate", "AND"),
                parent_id=parent_id, tree_type = tree_type
            )

        # ✅ Disable interaction (selection, editing, signals, context menu etc.)
        node_item = new_node["node"]
        node_item_type = new_node["node_type"]
        if node_item_type in ["intermediate", "leaf"]:
            node_item.setEnabled(False)
            node_item.setFlag(node_item.ItemIsSelectable, False)
            node_item.setAcceptHoverEvents(False)
            if hasattr(node_item, "gate_button"):
                node_item.gate_button.setEnabled(False)

        self.scene.extracted_tree[tree_id] = create_arrow_for_nodes(
            self.scene.renderer,
            new_node,
            parent_id,
            parent_node
        )

        # Recursively insert children
        for child in node_data.get("childrens", []):
            self._recursive_insert(child, tree_id, node_item, tree_type)
