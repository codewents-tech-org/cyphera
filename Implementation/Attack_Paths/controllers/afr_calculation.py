"""
Module: Initial and Residual AFR Calculation module      \n 
File: afr_calculation.py      \n
Layer: Backend / Computation / afr_calculation      \n
Component ID:          \n
Requirement IDs:       \n
Author: Vijaya karagi  \n
Created On: 2025-06-26     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Provides core logic to evaluate Air-Fuel Ratio (AFR) metrics for hierarchical tree 
structures representing security attack scenarios or control systems. Supports both 
initial and residual AFR evaluations depending on the tree type and structure.

Description:
------------
This module processes hierarchical tree data structures (typically loaded from JSON),
identifying critical paths using optimization heuristics provided by evaluator classes.
It distinguishes between initial AFR (representing raw risk or impact) and residual AFR 
(representing mitigated or post-control impact), with support for tree-specific behavior.

Responsibilities
----------------
- Evaluate optimal AFR path for all tree types using AFRPathEvaluator.
- Conditionally evaluate residual AFR if the tree type is "attack_tree" and contains
  at least one control head node, using RAFRPathEvaluator.
- Log execution details to support observability and debugging.
- Provide a unified interface to consumers via the `calculate_afr_values()` function.

Dependencies:
-------------
- Python 3.12+
- Logging module for runtime diagnostics.
- Custom modules:
    - init_afr_calculation.AFRPathEvaluator
    - resid_afr_calculation.RAFRPathEvaluator

Limitations
-----------
- Assumes input trees are well-formed and use specific field conventions
  (e.g., "node_type", "childrens").
- Only "attack_tree" trees support residual AFR evaluation.
- Evaluation strategy depends on external logic defined in evaluator classes.
- No built-in input validation or JSON schema enforcement.

Improvements
------------
- Add schema validation for input tree structure.
- Extend support for additional tree types or AFR heuristics.
- Introduce parallelized evaluation for large trees.
- Make evaluators pluggable (strategy pattern or dependency injection).
- Add unit/contract tests for robustness.
- Expand logging granularity and use structured logging.
- Support configuration via environment or runtime parameters.

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-06-26           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from typing import Dict, Any, Tuple, List, Optional
from Attack_Paths.models.init_afr_calculation import AFRPathEvaluator
from Attack_Paths.models.resid_afr_calculation import RAFRPathEvaluator
from components.progress_dialog import ProgressDialog
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def contains_control_head(tree: Dict[str, Any]) -> bool:
    """
    Recursively checks if any node in the tree is a 'control head'.

    Args:
        tree (Dict[str, Any]): The tree structure.

    Returns:
        bool: True if any node has node_type 'control head'.
    """
    for node_id, node in tree.items():
        if node.get("node_type") == "control head":
            return True
        if "childrens" in node:
            if contains_control_head(node["childrens"]):
                return True
    return False


def calculate_afr_values(tree: Dict[str, Any], tree_type: str, reporter: Optional[ProgressDialog] = None) -> Dict[str, Any]:
    """
    Calculates AFR values based on the tree type.

    Args:
        tree (Dict[str, Any]): The input hierarchical tree as a JSON-like dictionary.
        tree_type (str): The type of tree ("attack_tree", "technical_tree", "control_tree").

    Returns:
        Dict[str, Any]: Dictionary with AFR results.
    """
    logger.info(f"Calculating AFR for tree_type: {tree_type}")
    result = {}

    # Step 1: Initial AFR calculation
    if reporter: reporter.update(5, "Initializing Initial AFR Analysis...")
    init_evaluator = AFRPathEvaluator(tree)
    init_path, init_vector, init_sum = init_evaluator.find_optimal_path(reporter)

    result["init_afr"] = {
        "path": init_path,
        "afr_vector": init_vector,
        "afr_sum": init_sum,
    }
    if reporter: reporter.update(100, "Initial AFR Analysis complete.")
    
    # Step 2: Residual AFR calculation for attack_tree only
    if tree_type == "attack_tree":
        if contains_control_head(tree):
            if reporter: reporter.update(5, "Evaluating residual AFR Analysis...")
            resid_evaluator = RAFRPathEvaluator(tree)
            resid_path, resid_vector, resid_sum = resid_evaluator.find_optimal_path(reporter)
            result["resid_afr"] = {
                "path": resid_path,
                "afr_vector": resid_vector,
                "afr_sum": resid_sum,
            }
            if reporter: reporter.update(100, "Residual AFR Analysis complete.")
        else:
            logger.info("No control head found. Skipping residual AFR Analysis.")
            result["resid_afr"] = {
                "path": [],
                "afr_vector": [],
                "afr_sum": None
            }
    else:
        result["resid_afr"] = None

    if reporter: reporter.update(100, "AFR Analysis complete.")
    return result
