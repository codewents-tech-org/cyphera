"""
Module: Technical Tree Scene      \n 
File: technicaltree_scene.py      \n
Layer: UI / Graphics Scene Management      \n
Component ID:          \n
Requirement IDs:       \n
Author: Vijaya karagi  \n
Created On: 2025-07-08     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Defines the `TechnicalTreeScene` class for managing and rendering a dynamic technical attack tree 
structure using PyQt5. This scene class encapsulates logic for adding, positioning, linking, and 
removing visual tree nodes, and integrates AFR path highlighting and tree persistence support.

Description:
------------
The `TechnicalTreeScene` class extends `QGraphicsScene` to support visual construction of 
hierarchical tree-based data models. It manages the creation of head, intermediate, and leaf 
nodes, auto-generates directional arrows between nodes, applies layout algorithms, and computes 
AFR paths. This scene is designed for integration with a `QGraphicsView` to support interactive 
tree building, risk visualization, and analysis.

Responsibilities
----------------
- Maintain a consistent internal tree structure (`self.tree_nodes`)
- Create and visually layout QGraphicsItems for head/intermediate/leaf nodes
- Automatically link nodes with arrows using `ArrowRenderer`
- Dynamically update AFR paths based on tree structure and values
- Support tree loading via `TreeLoader` and removal via `TreeNodeRemover`
- Apply spatial layout through `TreeLayout` based on hierarchy
- Serialize tree to dictionary format for saving/exporting
- Recompute and re-render arrows and layout on user interaction

Dependencies:
-------------
- PyQt5.QtWidgets.QGraphicsScene
- Attack_Paths.controllers:
    - head_node_creator.headNodeBox
    - intermediate_node_creator.IntermediateNodeBox
    - leaf_node_creator.LeafNodeBox
    - arrow_line_creator.ArrowRenderer
    - remove_nodes.TreeNodeRemover
    - tree_loader.TreeLoader
    - tree_layout.TreeLayout
    - highlight_afr_path (arrow + path utilities)
    - root_afr_data_update
    - auto_leafs_update / auto_intermediates_update
    - get_node_label

Limitations
-----------
- Tree assumes a single root node (no forest support)
- Does not support undo/redo stack for node operations
- Layout is fixed vertically with static spacing
- AFR value computation is assumed to be externally delegated
- View zoom/scroll behavior is managed outside this class
- Node `node_id` auto-generation is tightly coupled to internal counter

Improvements
------------
- Add undo/redo functionality for interactive editing
- Support node type customization (e.g., decorators or strategies)
- Implement zoom-aware layout adjustments and responsive spacing
- Add drag-and-drop support for node repositioning
- Export/save tree to JSON/YAML file via QFileDialog
- Integrate animation transitions for better UX during node insertion/removal

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-08           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

import hashlib
import json
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QRectF
from Attack_Paths.controllers.head_node_creator import headNodeBox
from Attack_Paths.controllers.intermediate_node_creator import IntermediateNodeBox
from Attack_Paths.controllers.leaf_node_creator import LeafNodeBox
from Attack_Paths.controllers.tree_layout import TreeLayout
from Attack_Paths.controllers.arrow_line_creator import ArrowRenderer
from Attack_Paths.controllers.remove_nodes import TreeNodeRemover
from Attack_Paths.controllers.tree_loader import TreeLoader
from Attack_Paths.controllers.root_afr_data_update import head_node_afr_update
from Attack_Paths.controllers.auto_leafs_update import update_auto_leafs
from Attack_Paths.controllers.auto_intermediates_update import update_auto_intermediates
from Attack_Paths.controllers.get_node_label import get_intermediate_node_id, get_leaf_node_id
from Attack_Paths.controllers.highlight_afr_path import create_arrow_for_nodes, update_arrow_lines
from Attack_Paths.controllers.load_tree import load_tree_items_with_data
from Attack_Paths.controllers.get_tree_details import get_tree_data
from Attack_Paths.controllers.save_tree_into_db import save_tree_in_database
from Attack_Paths.components.make_tree_center_view import center_tree_in_view
from Attack_Paths.models.set_changed_flag import set_node_gate_changed, set_node_text_changed, set_node_value_changed, set_node_latest
from Attack_Paths.controllers.backend_afr_calculator import update_afr_values

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TechnicalTreeScene(QGraphicsScene):
    """
    Manages the rendering and interaction of a Technical Attack Tree using QGraphicsScene.

    This class handles creation, linking, layout, highlighting, and data update
    operations for technical attack tree nodes such as head, intermediate, and leaf types.
    """
    def __init__(self, tat_id):
        """
        Initializes a new technical attack tree scene.

        Args:
            tat_id (str): Unique identifier for the tree instance.
        """
        super().__init__()
        self.tat_id = tat_id
        self._cached_tree_hash = None  # 🔐 added
        self._tree_modified = False
        self._tree_data_modified = False
        self.last_intermediate_node_id = 0
        self.last_leaf_node_id = 0
        self.updated_leaf_list = []
        self.initialize_parameters()

    def _hash_tree(self, tree_dict: dict) -> str:
        """
        Generates a stable hash from the tree structure for comparison.
        
        Args:
            tree_dict (dict): Tree structure.

        Returns:
            str: Hash string for tree comparison.
        """
        normalized = json.dumps(tree_dict, sort_keys=True).encode("utf-8")
        return hashlib.sha256(normalized).hexdigest()

    def initialize_parameters(self) -> None:
        """
        Clears all scene state and reinitializes tree structure, layout, and arrow renderer.
        """
        view = self.views()[0] if self.views() else None
        if view:
            view.setUpdatesEnabled(False)
        try:
            self.clear()
            self.view = view
            self.tree_nodes = {}
            self.node_counter = 0
            self.tree_layout = TreeLayout(self.tree_nodes)
            self.renderer = ArrowRenderer(self, {}, [])
            self.extracted_tree = {}
            self.selectedPath = []
            self.updated_leaf_list = []
            self.rootnode_id = f"{self.tat_id}_node_{self.node_counter}"
            self._tree_modified = False
            self._tree_data_modified = False
        finally:
            if view:
                view.setUpdatesEnabled(True)

    def add_head_node(self, tree_id: str="unknown", label: str="unknown", text: str="unknown", 
                      x: int=0, y: int=0, af_value: str='0', af_level: str='High', rf_value: str='', rf_level: str='', gate: str='AND') -> None:
        """
        Adds the root (head) node to the tree.

        Args:
            tree_id (str): Unique node ID.
            label (str): Display label.
            text (str): Description text.
            x (int): X position.
            y (int): Y position.
            af_value (str): Attack Frequency value.
            af_level (str): Risk level.
            gate (str): Gate type ("AND" or "OR").
        """
        head_node = {   "tree_id": tree_id, "node_label": label, "node_Text": text, "af_value": af_value, "af_level": af_level, "x": x, "y": y, "gate_type": gate}
        node = headNodeBox(head_node, tree_type="TechnicalTree")
        self.addItem(node)
        node.addIntermediateRequested.connect(self.Add_IntermediateNode_Request)
        node.addLeafRequested.connect(self.Add_LeafNode_Request)
        node.gateSwitchRequested.connect(self.data_process_operation)
        self.tree_nodes = {"node_type": "head", "node_id": tree_id, "node": node, "is_gate_changed": False, "is_new": False}
        node.gateSwitchRequested.connect(lambda: set_node_gate_changed(self=self, target_node_id=node.tree_id))
        tree_nodes = self.tree_nodes
        tree_nodes["parent_id"] = None
        self.renderer.nodes[tree_id] = tree_nodes
        self.extracted_tree[tree_id] = tree_nodes

    def add_intermediate_node(self, tree_id: str="unknown", label: str="unknown", text: str="unknown", 
                              x: int=0, y: int=0, gate: str='AND', parent_id: str=None)-> dict:
        """
        Adds an intermediate node under a given parent.

        Args:
            tree_id (str): Unique ID for the intermediate node.
            label (str): Node label.
            text (str): Node description.
            x (int): X position.
            y (int): Y position.
            gate (str): Logical gate type.
            parent_id (str): ID of the parent node.

        Returns:
            dict: Serialized intermediate node dictionary.
        """
        intermediate_node = {   "tree_id": tree_id, "node_label": label, "node_Text": text, "x": x, "y": y, "gate_type": gate}
        node = IntermediateNodeBox(intermediate_node, tree_type="TechnicalTree")
        self.addItem(node)
        node.addIntermediateRequested.connect(self.Add_IntermediateNode_Request)
        node.addLeafRequested.connect(self.Add_LeafNode_Request)
        node.textEditedRequested.connect(self.Update_IntermediateNode_Request)
        node.gateSwitchRequested.connect(self.data_process_operation)
        node.removeRequested.connect(self.remove_node_Request)
        child_node = {"node_type": "intermediate", "node_id": tree_id, "node": node, "is_gate_changed": False, "is_text_changed": False, "is_new": False}
        self.update_tree_json(self.tree_nodes, parent_id, child_node)
        node.gateSwitchRequested.connect(lambda: set_node_gate_changed(self=self, target_node_id=node.tree_id))
        node.textEditedRequested.connect(lambda: set_node_text_changed(self=self, target_node_id=tree_id))
        return child_node
    
    def add_leaf_node(self, tree_id: str="unknown", label: str="unknown", text: str="unknown", 
                      x: int=0, y: int=0, af_value: str='0', af_level: str='High', 
                      values: list[str]=['0', '0', '0', '0', '0'], parent_id: str=None) -> dict:
        """
        Adds a leaf node under a parent.

        Args:
            tree_id (str): Node ID.
            label (str): Node label.
            text (str): Description.
            x (int): X coordinate.
            y (int): Y coordinate.
            af_value (str): Attack Frequency value.
            af_level (str): Risk level string.
            values (list[str]): List of AFR data values.
            parent_id (str): Parent node ID.

        Returns:
            dict: Serialized leaf node dictionary.
        """
        leaf_node = {   "tree_id": tree_id, "node_label": label, "node_Text": text, "af_value": af_value, "af_level": af_level, "x": x, "y": y, "values": values}
        node = LeafNodeBox(leaf_node, tree_type="TechnicalTree")
        self.addItem(node)
        node.textEditedRequested.connect(self.Update_LeafNode_Request)
        node.valueChangedRequested.connect(self.Update_LeafNode_Request)
        node.removeRequested.connect(self.remove_node_Request)
        child_node = {"node_type": "leaf", "node_id": tree_id, "node": node, "is_text_changed": False, "is_values_changed": False, "is_new": False}
        self.update_tree_json(self.tree_nodes, parent_id, child_node)
        node.textEditedRequested.connect(lambda: set_node_text_changed(self=self, target_node_id=node.tree_id))
        node.valueChangedRequested.connect(lambda: set_node_value_changed(self=self, target_node_id=node.tree_id))
        return child_node
    
    def Add_IntermediateNode_Request(self, node_data:dict) -> None:
        """
        Slot for handling intermediate node creation requests.

        Args:
            node_data (dict): Contains `node_id` and `node` keys for the parent.
        """
        self.node_counter += 1
        tree_id = f"{self.tat_id}_node_{self.node_counter}"
        node_label = get_intermediate_node_id(self, self.last_intermediate_node_id)
        tree_node = self.add_intermediate_node(tree_id, node_label, "Node Text", 0, 200, "AND", node_data["node_id"])
        set_node_latest(self=self, target_node_id=tree_id)
        self.tree_layout.apply_layout_positions(self.tree_nodes)
        extracted_node = create_arrow_for_nodes(self.renderer, tree_node, node_data["node_id"], node_data["node"])
        self.extracted_tree[tree_id] = extracted_node
        update_arrow_lines(self.renderer, self.selectedPath, self.extracted_tree)

    def Add_LeafNode_Request(self, node_info:dict) -> None:
        """
        Slot for handling leaf node creation requests.

        Args:
            node_info (dict): Contains `node_id` and `node` for the parent.
        """
        self.node_counter += 1
        tree_id = f"{self.tat_id}_node_{self.node_counter}"
        node_data = get_leaf_node_id(self, self.last_leaf_node_id, node_info["leaf_id"])
        tree_node = self.add_leaf_node(tree_id, node_data["node_label"], node_data["node_Text"], 350, 200, node_data["af_value"], node_data["af_level"], node_data["values"], node_info["node_id"])
        set_node_latest(self=self, target_node_id=tree_id)
        self.tree_layout.apply_layout_positions(self.tree_nodes)
        extracted_node = create_arrow_for_nodes(self.renderer, tree_node, node_info["node_id"], node_info["node"])
        self.extracted_tree[tree_id] = extracted_node
        self.data_process_operation()

    def Update_IntermediateNode_Request(self, node_data:dict) -> None:
        """
        Slot for updating intermediate node content.

        Args:
            node_data (dict): Contains updated label and text.
        """
        update_auto_intermediates(tree=self.tree_nodes, node_label=node_data["node_label"], node_text=node_data["text"])

    def Update_LeafNode_Request(self, node_data:dict) -> None:
        """
        Slot for updating leaf node content or AFR values.

        Args:
            node_data (dict): Dict containing updated text or AFR data.
        """
        if "text" in node_data:
            update_auto_leafs(tree=self.tree_nodes, node_label=node_data["node_label"], node_text=node_data["text"])
        if "afr_data" in node_data:
            update_auto_leafs(tree=self.tree_nodes, node_label=node_data["node_label"], afr_data=node_data["afr_data"])
            if node_data["node_label"] not in self.updated_leaf_list:
                self.updated_leaf_list.append(node_data["node_label"])

        self.data_process_operation()
    
    def data_process_operation(self) -> None:
        """
        Recalculates root AFR path and updates arrow highlights.
        """
        output = head_node_afr_update(self.tree_nodes, "technical_tree")
        self.selectedPath = output["init_afr"]["path"]
        update_arrow_lines(self.renderer, self.selectedPath, self.extracted_tree)

    def update_tree_json(self, tree: dict, parent_id: str, new_child: dict) -> bool:
        """
        Recursively adds a new child node to the parent node in tree JSON structure.

        Args:
            tree (dict): Tree structure to update.
            parent_id (str): ID of the parent node.
            new_child (dict): New child node data.

        Returns:
            bool: True if successfully inserted, else False.
        """
        if tree.get("node_id") == parent_id:
            tree.setdefault("childrens", []).append(new_child)
            return True
        for child in tree.get("childrens", []):
            if self.update_tree_json(child, parent_id, new_child):
                return True
        return False

    def load_tree(self, tree_dict: dict) -> None:
        """
        Loads a tree structure into the scene using TreeLoader.

        Args:
            tree_dict (dict): Nested tree definition to render.
        """
        load_tree_items_with_data(self=self, tree_dict=tree_dict, tree_type="technical_tree")

    def remove_node_Request(self, node_id: str) -> None:
        """
        Removes a node and all its children from the scene and data structures.

        Args:
            node_id (str): ID of the node to remove.
        """
        remover = TreeNodeRemover(scene=self, tree=self.tree_nodes, renderer=self.renderer, extracted_tree=self.extracted_tree)
        removed = remover.remove_node_and_subtree(node_id)
        if removed:
            self.tree_layout.apply_layout_positions(self.tree_nodes)
            self.data_process_operation()
        center_tree_in_view(self)
        self._tree_modified = True

    def save_tree(self) -> dict:
        """
        Recursively serializes the tree into a nested dictionary.

        Returns:
            dict: Serialized representation of the current tree.
        """
        tree_data = get_tree_data({"tree":self.tree_nodes, "tree_type":"technical_tree"})
        save_tree_in_database(self.tat_id, tree_data, "technical_tree")

        update_status = update_afr_values(self.updated_leaf_list, self.tat_id, "technical_tree")
        if update_status:
            self.updated_leaf_list = []
