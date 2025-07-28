"""
Module: Tree Node Configuration Validator      \n 
File: tree_dict_validation.py      \n
Layer: Backend / validation    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-02     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose: 
------------
Validates required fields in tree node configuration dictionaries.

Description:
------------
Provides input validation logic to ensure node configuration dictionaries
contain all expected fields depending on the tree type (AttackTree, TechnicalTree, etc.).

Responsibilities:
-----------------
- Ensure all mandatory fields are defined before rendering tree nodes
- Dynamically exclude rf_value/rf_level fields for non-Attack trees

Dependencies:
-------------
- Python standard typing module

Functions:
----------
- validate_node_config(config, required_fields, tree_type)

Limitations:
------------
- Does not perform type validation on field values
- No JSON schema enforcement or deep field validation

Improvements:
-------------
- Add schema enforcement with `pydantic` or `jsonschema`
- Include optional validation for field formats or nested keys

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-02           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""


from typing import Dict, Set


def validate_node_config(config: Dict, required_fields: Set[str], tree_type: str):
    """
    Validates that all required fields are present in a node config dictionary.

    Args:
        config (Dict): The node configuration dictionary to validate.
        required_fields (Set[str]): The expected keys for the node.
        tree_type (str): The type of the tree ("AttackTree", "TechnicalTree", etc.)

    Raises:
        ValueError: If required keys are missing.
    """
    effective_required = set(required_fields)

    # Exclude RF fields for non-Attack trees
    if tree_type in {"TechnicalTree", "RiskControlTree"}:
        effective_required -= {"rf_value", "rf_level"}

    missing = effective_required - config.keys()
    if missing:
        raise ValueError(f"Missing required fields in node config: {sorted(missing)}")
