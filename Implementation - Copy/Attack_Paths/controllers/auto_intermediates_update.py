"""
Module: Auto Intermediate Node Updater      \n 
File: auto_intermediates_update.py      \n
Layer: UI / Auto-Update Layer    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-04     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Updates intermediate nodes' descriptive text dynamically when a leaf node value changes,
propagating risk reasoning or propagation signals automatically into the tree.

Description:
------------
This utility searches the hierarchical tree for intermediate nodes whose `title.text()`
matches the given `node_label`, and updates their `node_text` field using the supplied `node_text`

Responsibilities
----------------
- Traverse tree structure (using `construct_node_info_map`)
- Match intermediate nodes based on label
- Update `.node_text.setText()` for matched nodes
- Perform input checks and log warnings on invalid usage

Dependencies:
-------------
- PyQt5-compatible node UI structure
- construct_node_info_map (for tree normalization)

Classes/Functions:
-------------
- `update_auto_intermediates(tree, node_label, node_text)`: Main function that performs label-based update traversal.


Limitations
-----------
- Assumes the tree dictionary contains valid PyQt widgets and method bindings.
- Only updates intermediate nodes with exact text match (case-sensitive).
- No signal feedback or return values for success/failure or updated nodes.
- Silent skip on invalid node structure (not logged in detail).
- Not tested against deeply nested or malformed trees.

Improvements
------------
- Add case-insensitive matching option.
- Emit signals or collect a list of updated node IDs.
- Add unit tests for all control paths.
- Handle non-UI trees (e.g. JSON-only).
- Add metrics/logging for nodes skipped or errors.

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

import logging
from typing import Dict, Any, Optional
from Attack_Paths.models.build_node_info_tree import construct_node_info_map


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def update_auto_intermediates(
    tree: Optional[Dict[str, Any]] = None,
    node_label: Optional[str] = None,
    node_text: Optional[str] = None,
) -> None:
    """
    Updates the description text of all intermediate nodes that match a given label.

    Args:
        tree (Optional[Dict[str, Any]]): The hierarchical tree structure (UI node format).
        node_label (Optional[str]): The label used to match intermediate nodes.
        node_text (Optional[str]): The text to set on matched intermediate nodes.

    Returns:
        None
    """
    if not tree:
        logger.warning("No tree provided to update_auto_intermediates.")
        return
    
    if not node_text:
        logger.warning("No node text provided to update_auto_intermediates.")
        return
    
    logger.debug(f"[Auto-Update] Triggered by label='{node_label}' | Text={node_text}")

    def update_all_intermediates(subtree: Dict[str, Any]):
        for node_id, node in subtree.items():
            if node.get("node_type") == "intermediate":
                obj = node.get("node", None)
                if obj and hasattr(obj, "title") and callable(obj.title.text):
                    title = obj.title.text()
                    if title == node_label:
                        logger.info(f"Updating intermediate node '{node_id}'")
                        if node_text:
                            logger.debug(f"Updating intermediate node '{node_id}' text = '{node_text}")
                            if obj and hasattr(obj, "node_text") and callable(obj.node_text.setText):
                                title = obj.node_text.setText(node_text)

            if "childrens" in node:
                update_all_intermediates(node["childrens"])

    # Normalize tree structure into flat node info
    extracted_tree = {}
    extracted_tree[tree["node_id"]] = construct_node_info_map(tree)
    update_all_intermediates(extracted_tree)

