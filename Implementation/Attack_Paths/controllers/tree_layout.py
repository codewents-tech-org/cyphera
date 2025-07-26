"""
Module: Tree Nodes Alignment      \n 
File: tree_layout.py      \n
Layer: UI / Tree layer    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-06-24     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
TreeLayout - A hierarchical tree parser and layout engine using anytree and custom positional logic.

Description:
------------
This module defines a layout utility for hierarchical node structures represented as nested
dictionaries. It flattens the structure, constructs a tree using `anytree`, computes visual
layout positions using a Reingold–Tilford-style algorithm, and optionally associates these
positions with graphical nodes.

Responsibilities
----------------
- Parse a nested dictionary-based tree structure and flatten it.
- Track node relationships using parent/child hierarchy.
- Build a tree using `anytree` with unique node identifiers.
- Compute 2D positional layout for each node using depth and sibling ordering.
- Return a dictionary of computed positions suitable for UI or diagram rendering.
- Provide extensibility for linking nodes to visual elements (e.g., QGraphicsItem).

Dependencies:
-------------
- anytree >= 2.8.0
- typing (standard library)

Classes:
- TreeNode: A custom tree node with positional attributes.
- TreeLayout: A layout engine to parse a JSON tree and compute node positions.

Limitations
-----------
- Assumes the tree is well-formed (i.e., no cycles, each node has a single parent).
- Does not validate uniqueness of node IDs — duplicate node keys may result in undefined behavior.
- Only one root node is supported; multiple roots are not currently handled.
- Layout computation is strictly 2D and vertical — no support for radial or horizontal trees.
- `node` field in the input is assumed to be a string or object — positional updates must be implemented externally.
- No built-in rendering or drawing; integration with UI frameworks must be handled externally (e.g., Qt, matplotlib).
- Tree size scaling or spacing customization (dx, dy) is static and must be tuned manually.

Improvements
------------
- Add support for forest (multi-rooted) trees.
- Implement node ID uniqueness validation with descriptive error messages.
- Allow customizable layout direction (top-down, left-right, radial).
- Enable dynamic spacing based on subtree size or label length.
- Add hooks for UI binding, e.g., a callback for setting position on actual graphic nodes.
- Export layout to common graph formats (e.g., DOT, GEXF, JSON).
- Integrate bounding box or tree canvas size estimation.
- Add automated unit tests for tree flattening and layout position correctness.

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-06-24           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from anytree import NodeMixin, RenderTree
from typing import Dict, Tuple, Any, List, Optional
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TreeNode(NodeMixin):
    """
    Represents a node in the tree. Inherits from anytree.NodeMixin to enable tree behavior.
    Stores position data used in layout computations.
    """
    def __init__(self, name, parent=None, node=None):
        self.name = name                # Unique identifier of the node
        self.parent = parent            # Parent TreeNode (established during tree construction)
        self.node = parent            # Parent TreeNode (established during tree construction)
        self.pos = (0, 0)               # (x, y) position to be computed later

class TreeLayout():
    """
    Parses a JSON-style tree structure, builds a tree using anytree, and computes
    2D layout positions for rendering or UI usage.
    """
    def __init__(self, json_tree: Dict[str, Any]):
        """
        Initialize the TreeLayout with a hierarchical dictionary structure.
        Builds internal tree structure and computes layout positions.
        """
        self.json_tree = json_tree          # The raw input tree dictionary
        self.tree_nodes = {}                # Dictionary of TreeNode instances keyed by node_id

    def apply_layout_positions(self, json_tree):
        node_positions = self.get_node_positions(json_tree)
        self.set_node_positions(json_tree, node_positions)

    def get_node_positions(self, json_tree):
        self.tree_nodes = {}
        self.json_tree = json_tree
        # Flatten the tree and collect all nodes with parent references
        tree_nodes_list = self.get_treenodes_list(self.json_tree)

        # First pass: Create all TreeNode instances
        for node in tree_nodes_list:
            self.tree_nodes[node["node_id"]] = TreeNode(node["node_id"])

        # Second pass: Establish parent-child relationships
        for node in tree_nodes_list:
            if node["parent_node"] is not None:
                self.tree_nodes[node["node_id"]].parent = self.tree_nodes[node["parent_node"]]
                self.tree_nodes[node["node_id"]].node = node["node"]

        # Find the root node (must be exactly one)
        root = [n for n in self.tree_nodes.values() if n.is_root][0]

        # Compute layout positions for all nodes
        positions = self.compute_layout(root)

        return positions

    def get_treenodes_list(self, tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recursively traverses a nested dictionary tree structure and flattens it.
        Returns a list of node dictionaries including node_id and parent_node info.

        Args:
            tree (Dict[str, Any]): The nested tree dictionary.

        Returns:
            List[Dict[str, Any]]: Flattened list of nodes with hierarchy info.
        """
        flat_nodes: List[Dict[str, Any]] = []

        def traverse(node_data: Dict[str, Any], parent_node: Optional[str] = None):
            node_id = node_data.get("node_id")
            if not node_id:
                logger.debug(f"Node is missing 'node_id': {node_data}")
                raise ValueError("Node is missing 'node_id':", node_data)
            node = node_data.get("node")
            if not node:
                logger.debug(f"Node is missing 'node': {node_data}")
                raise ValueError("Node is missing 'node':", node_data)

            # Create a flat record excluding 'childrens'
            flat_node = {
                "node_id": node_id,
                "parent_node": parent_node,
                "node": node
            }
            flat_nodes.append(flat_node)

            # Recursively handle children
            for child in node_data.get("childrens", []):
                traverse(child, node_id)

        traverse(tree)

        return flat_nodes

    def compute_layout(self, root: TreeNode, dx: int = 320, dy: int = 200) -> Dict[str, Tuple[int, int]]:
        """
        Computes a Reingold–Tilford-like layout for the tree, assigning 2D positions to each node.

        Args:
            root (TreeNode): Root of the tree.
            dx (int): Horizontal spacing between sibling nodes.
            dy (int): Vertical spacing between levels.

        Returns:
            Dict[str, Tuple[int, int]]: Mapping of node_id to (x, y) screen coordinates.
        """
        def _layout(node, depth=0, offset=0):
            """
            Recursive layout helper that walks the tree in depth-first order.

            Args:
                node (TreeNode): Current node being processed.
                depth (int): Depth level in the tree.
                offset (int): Horizontal offset for current subtree.

            Returns:
                int: The updated offset after placing this node and all its children.
            """
            children = list(node.children)
            if not children:
                # Leaf node: assign current offset and increment
                node.pos = (offset, depth)
                return offset + 1
            
            start = offset
            for child in children:
                offset = _layout(child, depth + 1, offset)

            # Center parent node between its children
            mid = (start + offset - 1) / 2
            # if depth == 0:      # Optional tweak for root centering
            #     mid = (start + offset) / 2
            node.pos = (mid, depth)
            return offset

        # Begin layout from root node
        _layout(root)

        # Scale computed logical positions to actual coordinates
        return {n.name: (n.pos[0] * dx, n.pos[1] * dy) for n in root.descendants + (root,)}

    def set_node_positions(self, tree: dict, positions: dict) -> None:
        """
        Recursively sets .setPos(x, y) for all nodes in the tree based on their node_id.

        Args:
            tree (dict): Root node of the tree.
            positions (dict): node_id → (x, y) coordinates.
        """
        node_id = tree.get("node_id")
        node_obj = tree.get("node")
        if node_id in positions and node_obj:
            x, y = positions[node_id]
            node_obj.setPos(x, y)
        for child in tree.get("childrens", []):
            self.set_node_positions(child, positions)

