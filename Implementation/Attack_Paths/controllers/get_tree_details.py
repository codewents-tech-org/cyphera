
import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_tree_data(emitted: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(emitted, dict):
        raise ValueError("Expected 'emitted' to be a dictionary.")

    tree = emitted.get("tree")
    tree_type = emitted.get("tree_type")

    if not tree or not tree_type:
        raise ValueError("Both 'tree' and 'tree_type' must be provided in emitted data.")

    node_info = {}
    node_info = extract_node_info(tree, tree_type)
    return node_info

def extract_node_info(node_dict, tree_type) -> Dict[str, Any]:
    """
    Recursively extracts gate or value information from a node.

    Args:
        node_dict (Dict[str, Any]): A node and its metadata/children.

    Returns:
        Dict[str, Any]: Simplified dictionary containing node_type, values, gate, and children.
    """
    node_id = node_dict["node_id"]
    node_type = node_dict["node_type"]
    node_obj = node_dict["node"]

    info = {
        "node_type": node_type,
        "node_label": node_obj.title.text(),
        "node_text": node_obj.node_text.toPlainText(),
        "x": int(node_obj.pos().x()),
        "y": int(node_obj.pos().y()),
    }

    if node_type in {"head", "intermediate", "control head", "technical head"}:
        info["gate"] = node_obj.gate_button.text()
        if node_type == "head":
            info["af_value"] = node_obj.af_value.text()
            info["af_level"] = node_obj.af_level.toPlainText()
            if tree_type == "attack_tree":
                info["rf_value"] = node_obj.rf_value.text()
                info["rf_level"] = node_obj.rf_level.toPlainText()

    elif node_type == "leaf":
        info["values"] = [label.text() for label in node_obj.values_label]
        info["af_value"] = node_obj.af_value.text()
        info["af_level"] = node_obj.af_level.toPlainText()

    # Handle children recursively
    children_list = node_dict.get("childrens", [])
    if children_list:
        info["childrens"] = []
        for child in children_list:
            info["childrens"].append(extract_node_info(child, tree_type)) 

    return info
