"""
Module: Head Node AFR Update      \n 
File: root_afr_data_update.py      \n
Layer: UI / AFR Updater      \n
Component ID:          \n
Requirement IDs:       \n
Author: Vijaya karagi  \n
Created On: 2025-07-03     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Updates AFR and Residual AFR values on a given tree's head node by calling
the process_tree_data function and updating UI node components accordingly.

Description:
------------
This module defines the `head_node_afr_update()` function that:
- Processes a full tree structure using the AFR engine.
- Extracts initial and residual AFR sums.
- Updates the head node's af_value, af_level, rf_value, and rf_level fields based on those results.
- Converts infinite AFR values to 0 and sets AFR level appropriately using a level mapping function.

Responsibilities
----------------
- Compute initial and residual AFR using backend models.
- Safely handle infinite values or missing residual AFR.
- Update UI fields on head node objects (`af_value`, `af_level`, `rf_value`, `rf_level`).

Dependencies:
-------------
- process_tree_data (Attack_Paths.controllers.afr_data_process)
- calculate_afr_Level (Attack_Paths.models.afr_level_calculation)
- Python 3.12+
- PyQt5: for `.setText()` and `.setPlainText()` methods

Limitations
-----------
- Assumes the tree dict contains a `"node"` key with valid PyQt UI elements.
- No UI validation is performed before assignment.
- Fails silently if AFR outputs are unexpected or malformed.

Improvements
------------
- Add type checks or error handling if node elements are missing.
- Optionally return a status or result dict for logging.
- Refactor to support batch updates or custom update hooks.

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

from Attack_Paths.controllers.afr_data_process import process_tree_data
from Attack_Paths.models.afr_level_calculation import calculate_afr_Level


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def head_node_afr_update(tree: Dict[str, Any], tree_type: str) -> None:
    """
    Updates AFR and residual AFR values on the head node in a given tree.

    Args:
        tree (Dict[str, Any]): Dictionary containing the tree and its root 'node' object.
        tree_type (str): The classification of the tree (e.g., "attack_tree", "control_tree").

    Side Effects:
        Modifies the following fields in-place on tree['node']:
            - af_value (via setText)
            - af_level (via setPlainText)
            - rf_value (if present and tree supports residual AFR)
            - rf_level (if present and tree supports residual AFR)
    """
    output = process_tree_data({"tree": tree, "tree_type": tree_type})

    afr_value = output["init_afr"]["afr_sum"]
    afr_text = "0" if str(afr_value) == "inf" else str(afr_value)
    tree["node"].af_value.setText(afr_text)
    tree["node"].af_level.setPlainText(calculate_afr_Level(int(afr_text)))

    if tree_type == "attack_tree":
        if output["resid_afr"] is not None:
            afr_value = output["resid_afr"]["afr_sum"]
            if afr_value is not None:
                rf_text = "0" if str(afr_value) == "inf" else str(afr_value)
                tree["node"].rf_value.setText(rf_text)
                tree["node"].rf_value.setVisible(True)
                tree["node"].rf_level.setPlainText(calculate_afr_Level(int(rf_text)))
                tree["node"].rf_level.setVisible(True)
            else:
                tree["node"].rf_value.setText("")
                tree["node"].rf_value.setVisible(False)
                tree["node"].rf_level.setPlainText("")
                tree["node"].rf_level.setVisible(False)

    return output
