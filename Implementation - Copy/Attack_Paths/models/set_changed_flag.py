

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def set_node_gate_changed(self, target_node_id: str) -> bool:
    """
    Recursively traverses self.tree_nodes and sets 'is_gate_changed' flag on the node with matching ID.

    Args:
        target_node_id (str): The ID of the node whose gate has changed.

    Returns:
        bool: True if the node was found and updated, False otherwise.
    """
    def recurse(tree: dict) -> bool:
        if tree.get("node_id") == target_node_id:
            tree["is_gate_changed"] = True
            logger.info(f"Flagged gate changed for node: {target_node_id}")
            return True
        for child in tree.get("childrens", []):
            if recurse(child):
                return True
        return False

    tree_nodes = recurse(self.tree_nodes)
    self._tree_data_modified = True
    return tree_nodes

def set_node_text_changed(self, target_node_id: str) -> bool:
    """
    Recursively traverses self.tree_nodes and sets 'is_text_changed' flag on the node with matching ID.

    Args:
        target_node_id (str): The ID of the node whose text has changed.

    Returns:
        bool: True if the node was found and updated, False otherwise.
    """
    def recurse(tree: dict) -> bool:
        if tree.get("node_id") == target_node_id:
            tree["is_text_changed"] = True
            logger.info(f"Flagged text changed for node: {target_node_id}")
            return True
        for child in tree.get("childrens", []):
            if recurse(child):
                return True
        return False

    tree_nodes = recurse(self.tree_nodes)
    self._tree_data_modified = True
    return tree_nodes

def set_node_value_changed(self, target_node_id: str) -> bool:
    """
    Recursively traverses self.tree_nodes and sets 'is_values_changed' flag on the node with matching ID.

    Args:
        target_node_id (str): The ID of the node whose values has changed.

    Returns:
        bool: True if the node was found and updated, False otherwise.
    """
    def recurse(tree: dict) -> bool:
        if tree.get("node_id") == target_node_id:
            tree["is_values_changed"] = True
            logger.info(f"Flagged values changed for node: {target_node_id}")
            return True
        for child in tree.get("childrens", []):
            if recurse(child):
                return True
        return False

    tree_nodes = recurse(self.tree_nodes)
    self._tree_data_modified = True
    return tree_nodes

def set_node_latest(self, target_node_id: str) -> bool:
    """
    Recursively traverses self.tree_nodes and sets 'is_values_changed' flag on the node with matching ID.

    Args:
        target_node_id (str): The ID of the node whose values has changed.

    Returns:
        bool: True if the node was found and updated, False otherwise.
    """
    def recurse(tree: dict) -> bool:
        if tree.get("node_id") == target_node_id:
            tree["is_new"] = True
            logger.info(f"Flagged values changed for node: {target_node_id}")
            return True
        for child in tree.get("childrens", []):
            if recurse(child):
                return True
        return False

    tree_nodes = recurse(self.tree_nodes)
    self._tree_data_modified = True
    return tree_nodes

