"""
Module: Node Info Tree Mapper      \n 
File: construct_node_info_map.py      \n
Layer: Backend / Tree Traversal    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-04     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Converts a nested node tree into a structured dictionary format that
encapsulates metadata such as node type, object reference, and child relationships.

Description:
------------
Given a tree of UI node dictionaries (each with attributes like `node_id`, `node_type`, `node`, and `childrens`),
this function recursively builds a map (dictionary) preserving the structure of the tree,
while simplifying access to nodes and their attributes.

Responsibilities
----------------
- Traverse nested tree nodes recursively.
- Create a consistent representation of each node’s:
    - ID
    - type (head, intermediate, leaf, etc.)
    - associated object reference
    - nested child nodes (if any)

Dependencies:
-------------
- Standard Library:
    - `typing` for type annotations
    - `logging` for observability and diagnostics

Classes/Functions:
-------------
- `construct_node_info_map(node_dict)`: Returns structured metadata for a single node and its children.

Limitations
-----------
- Assumes all input dictionaries contain valid `node_id`, `node_type`, and `node` keys.
- Does not validate the object types or enforce schema contracts.
- Assumes `childrens` is always a list of node dictionaries.

Improvements
------------
- Add type validation for keys (e.g., using `pydantic` or schema checks).
- Support depth-limiting or filtering based on node types.
- Optionally flatten the tree for faster lookup in some scenarios.

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


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def construct_node_info_map(node_dict) -> Dict[str, Any]:
    """
    Recursively constructs a structured dictionary representation of a tree node.

    Args:
        node_dict (Dict[str, Any]): Dictionary containing:
            - node_id: Unique ID of the node
            - node_type: Type of the node (e.g., head, intermediate, leaf)
            - node: PyQt UI object reference
            - childrens: List of child node dictionaries (optional)

    Returns:
        Dict[str, Any]: A hierarchical dictionary representing node metadata and structure.
    """
    node_id = node_dict["node_id"]
    node_type = node_dict["node_type"]
    node_obj = node_dict["node"]

    info = {
        "node_type": node_type,
        "node": node_obj,
    }

    # Handle children recursively
    children_list = node_dict.get("childrens", [])
    if children_list:
        info["childrens"] = {
            child["node_id"]: construct_node_info_map(child)
            for child in children_list
        }
        
    return info

