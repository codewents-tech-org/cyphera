"""
Module: AFR data process      \n 
File: afr_data_process.py      \n
Layer: UI / AFR evaluator      \n
Component ID:          \n
Requirement IDs:       \n
Author: Vijaya karagi  \n
Created On: 2025-07-03     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Routes a node tree with metadata through the AFR calculation pipeline and
returns AFR and residual AFR results after evaluating gates and values.

Description:
------------
This controller receives input in the form of an `emitted` dictionary,
which contains a tree structure (with nodes and UI bindings) and a
tree type identifier. It recursively builds a simplified version of the tree,
extracting AFR-related inputs (like gate and leaf values) and passes the
result to the AFR backend engine.

Responsibilities
----------------
- Validate emitted data structure.
- Extract relevant data from all nodes recursively.
- Build node info required by AFR evaluator.
- Invoke AFR calculation module.
- Return AFR results in a consistent dictionary format.

Dependencies:
-------------
- Logging
- AFR calculation logic from `afr_calculation.py`

Limitations
-----------
- Assumes `node_dict` contains all required node attributes.
- Expects each node to have PyQt properties like `gate_button.text()` or `values_label.text()`.
- No schema validation or fallback for incomplete node graphs.

Improvements
------------
- Add schema/type checks on node attributes.
- Refactor node traversal using a strategy pattern.
- Include richer metadata in AFR results (e.g., per-node AFR contribution).

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-03           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

import logging
from typing import Dict, Any
from tqdm import tqdm
import threading
import time
from PyQt5.QtWidgets import QMessageBox

from Attack_Paths.models.afr_calculation import calculate_afr_values
from components.progress_dialog import ProgressDialog

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def process_tree_data(emitted: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes a tree structure from the UI and computes AFR outputs.

    Args:
        emitted (Dict[str, Any]): Must contain:
            - "tree" (dict): Root node dictionary with children
            - "tree_type" (str): Type of the tree ("attack_tree", "technical_tree", etc.)

    Returns:
        Dict[str, Any]: AFR calculation results

    Raises:
        ValueError: If 'emitted' is missing required keys.
    """
    if not isinstance(emitted, dict):
        raise ValueError("Expected 'emitted' to be a dictionary.")

    tree = emitted.get("tree")
    tree_type = emitted.get("tree_type")

    if not tree or not tree_type:
        raise ValueError("Both 'tree' and 'tree_type' must be provided in emitted data.")

    node_info = {}
    node_info[tree["node_id"]] = extract_node_info(tree)
    output_data = calculate_afr_data(node_info, tree_type)
    return output_data

def extract_node_info(node_dict) -> Dict[str, Any]:
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
        "node": node_obj,
    }

    if node_type in {"head", "intermediate", "control head", "technical head"}:
        info["gate"] = node_obj.gate_button.text()
    elif node_type == "leaf":
        info["values"] = [label.text() for label in node_obj.values_label]

    # Handle children recursively
    children_list = node_dict.get("childrens", [])
    if children_list:
        info["childrens"] = {
            child["node_id"]: extract_node_info(child)
            for child in children_list
        }

    return info

def calculate_afr_data(tree: Dict[str, Any], tree_type: str) -> Dict[str, Any]:
    """
    Delegates AFR evaluation to the backend AFR engine.

    Args:
        tree (Dict[str, Any]): Simplified dictionary of node_info
        tree_type (str): One of ["attack_tree", "technical_tree", "control_tree"]

    Returns:
        Dict[str, Any]: Dictionary with 'init_afr' and 'resid_afr' results.

    Raises:
        ValueError: If arguments are malformed
        Exception: On AFR evaluation failure
    """
    if not isinstance(tree, dict):
        raise ValueError("Expected 'tree' to be a dictionary.")

    if not isinstance(tree_type, str):
        raise ValueError("Expected 'tree_type' to be a string.")

    if not tree or not tree_type:
        raise ValueError("Both 'tree' and 'tree_type' must be provided in emitted data.")

    logger.info("Received data for AFR calculation - tree_type='%s'", tree_type)

    try:
        # afr_result = calculate_afr_values(tree, tree_type)
        # logger.info(f"AFR calculation complete for tree_type='{tree_type}'")
        # return afr_result

        afr_result = {"data": None, "error": None}
        def on_success(result: Dict[str, Any]):
            logger.info(f"AFR Analysis successfully complete")
            afr_result["data"] = result

        def on_failure(error_msg: str):
            logger.error("AFR Analysis failed: %s", error_msg)
            afr_result["error"] = error_msg

        dialog = ProgressDialog(
            title="Analyzing Attack Feassibility Rate, please wait...",
            message="Analyzing Attack Feassibility Rate, initiated",
            task_fn=calculate_afr_values,
            task_args=(tree, tree_type),
            on_success=on_success,
            on_failure=on_failure
        )
        dialog.exec_()

        result = afr_result["data"]
        if not result or "init_afr" not in result:
            raise ValueError("AFR Analysis returned incomplete data")

        return result

    except Exception as e:
        logger.exception("AFR Analysis failed.")
        raise
