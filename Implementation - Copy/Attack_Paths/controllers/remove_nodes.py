
from PyQt5.QtWidgets import QGraphicsScene

class TreeNodeRemover:
    """
    Utility class to remove a node and all its descendants from a tree-based QGraphicsScene,
    including graphics items and ArrowRenderer connections.
    """

    def __init__(self, scene: QGraphicsScene, tree: dict, renderer, extracted_tree: dict):
        """
        Args:
            scene (QGraphicsScene): The graphics scene.
            tree (dict): The root node of the tree (self.tree_nodes).
            renderer (ArrowRenderer): ArrowRenderer instance with arrows and node references.
            extracted_tree (dict): Flattened node lookup used for arrows.
        """
        self.scene = scene
        self.tree = tree
        self.renderer = renderer
        self.extracted_tree = extracted_tree

    def remove_node_and_subtree(self, node_id: str) -> bool:
        """
        Removes the specified node and its subtree from the scene and internal structures.

        Args:
            node_id (str): The ID of the node to remove.

        Returns:
            bool: True if the node was found and removed, False otherwise.
        """
        to_remove_ids = []

        def collect_subtree_ids(node):
            to_remove_ids.append(node["node_id"])
            for child in node.get("childrens", []):
                collect_subtree_ids(child)

        def find_and_prune(node):
            if node["node_id"] == node_id:
                collect_subtree_ids(node)
                return True
            for child in node.get("childrens", []):
                if find_and_prune(child):
                    node["childrens"] = [c for c in node["childrens"] if c["node_id"] != node_id]
                    return True
            return False

        found = find_and_prune(self.tree)
        if not found:
            print(f"[TreeNodeRemover] Node '{node_id}' not found.")
            return False

        for nid in to_remove_ids:
            # Remove arrows
            for arrow in self.renderer.nodes.get(nid, {}).get("arrows", []):
                arrow.remove_from_scene()
                if arrow in self.renderer.arrows:
                    self.renderer.arrows.remove(arrow)

            # Remove graphics item
            node_obj = self.renderer.nodes.get(nid, {}).get("node")
            if node_obj:
                self.scene.removeItem(node_obj)

            # Clean up references
            self.renderer.nodes.pop(nid, None)
            self.extracted_tree.pop(nid, None)

        return True
