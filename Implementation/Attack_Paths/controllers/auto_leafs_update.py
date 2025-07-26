"""
Module: Auto Leaf Node Updater      \n 
File: update_auto_leafs.py      \n
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
Automatically updates AFR-related values in leaf nodes when a related node
(e.g., leaf or input node) emits updated AFR data or descriptive text.

Description:
------------
This module scans through the node tree to find all leaf nodes whose label matches
the triggering node's label. It then updates the matching leaf node’s:
- AFR vector (`values_label`)
- AFR value (`af_value`)
- AFR level (`af_level`)
- Optional description text (`node_text`)

Responsibilities
----------------
- Locate and update leaf nodes matching the triggering label.
- Apply AFR metadata to appropriate PyQt UI elements.
- Gracefully handle missing data with logging warnings.
- Allow both full AFR updates and text-only updates.

Dependencies:
-------------
- PyQt5-compatible node UI structure
- construct_node_info_map (for tree normalization)

Classes/Functions:
-------------
- `update_auto_leafs(tree, node_label, node_text, afr_data)`: Updates AFR and text for matching leaf nodes.


Limitations
-----------
- Assumes all leaf node objects are valid PyQt objects.
- Silent skip if `values_label` or `af_value` UI bindings are missing.
- `afr_data["values"]` must be a list of 5 strings (index-safe).
- Tree must be well-formed and include a root with `"node_id"`.

Improvements
------------
- Return list of updated node IDs for logging or audit.
- Emit UI signals post-update to notify downstream dependencies.
- Validate AFR vector length (currently assumed to be 5).
- Add type guards for PyQt interfaces to prevent runtime errors.
- Add optional fuzzy matching or partial update mode.

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

def update_auto_leafs(
    tree: Optional[Dict[str, Any]] = None,
    node_label: Optional[str] = None,
    node_text: Optional[str] = None,
    afr_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Updates auto-calculated leaf nodes when a triggering node changes.

    Args:
        tree (Dict[str, Any], optional): The node tree structure.
        node_label (str, optional): Label of the node that triggered update.
        node_text (str, optional): Description or user-entered node text.
        afr_data (Dict[str, Any], optional): AFR metadata:
            - 'node_values': List of str
            - 'afr_value': str
            - 'afr_level': str
    """
    if not tree:
        logger.warning("No tree provided to update_auto_leafs.")
        return
    
    if not node_text and not afr_data:
        logger.warning("No node text and values provided to update_auto_leafs.")
        return
    
    logger.debug(f"[Auto-Update] Triggered by label='{node_label}' | Text={node_text} | AFR Data={afr_data}")

    def update_all_leafs(subtree: Dict[str, Any]):
        for node_id, node in subtree.items():
            if node.get("node_type") == "leaf":
                obj = node.get("node", None)
                if obj and hasattr(obj, "title") and callable(obj.title.text):
                    title = obj.title.text()
                    if title == node_label:
                        logger.info(f"Updating leaf node '{node_id}'")
                        if afr_data:
                            logger.debug(f"Updating leaf node '{node_id}' afr_data = '{afr_data}")
                            if obj and hasattr(obj, "values_label"):
                                for index, value in enumerate(obj.values_label):
                                    if callable(value.setText):
                                        value.setText(afr_data["values"][index])
                                
                                if obj and hasattr(obj, "af_value") and callable(obj.af_value.setText):
                                    obj.af_value.setText(str(afr_data["af_value"]))
                                if obj and hasattr(obj, "af_level") and callable(obj.af_level.setPlainText):
                                    obj.af_level.setPlainText(afr_data["af_level"])

                        if node_text:
                            logger.debug(f"Updating leaf node '{node_id}' text = '{node_text}")
                            if obj and hasattr(obj, "node_text") and callable(obj.node_text.setText):
                                title = obj.node_text.setText(node_text)

            if "childrens" in node:
                update_all_leafs(node["childrens"])

    # Normalize tree structure into flat node info
    extracted_tree = {}
    extracted_tree[tree["node_id"]] = construct_node_info_map(tree)
    update_all_leafs(extracted_tree)

