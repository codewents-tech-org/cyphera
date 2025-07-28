"""
Module: Residual AFR Calculation module      \n 
File: resid_afr_calculation.py      \n
Layer: Backend / Computation / resid_afr_calculation      \n
Component ID:          \n
Requirement IDs:       \n
Author: Vijaya karagi  \n
Created On: 2025-06-25     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Computes the optimal residual Aggregated Failure Risk (AFR) path from a hierarchical
tree structure that includes AND/OR logic and control gating. This is used to determine
minimal-risk propagation paths through complex system trees.

Description:
------------
This module implements the RAFRPathEvaluator class that evaluates optimal AFR paths
from hierarchical data structures, supporting:
- Logical gate traversal (AND, OR)
- Leaf node AFR vector aggregation
- Exclusion of 'control head' nodes and their descendant leaf nodes from
  both AFR calculations and final output paths
- Graceful error handling for malformed nodes or data

Responsibilities
----------------
- Traverse tree structures with hierarchical logic gates
- Identify and compute maximum AFR vectors per path
- Respect 'control head' semantics for exclusion logic
- Return minimal AFR-sum path with supporting vector and cleaned node path

Dependencies:
-------------
- Python Standard Library: typing, itertools, logging

Limitations
-----------
- Tree is expected to be well-formed and rooted (single-entry point)
- AFR values must be valid integers or parsable strings
- 'control head' exclusion is absolute and non-configurable at runtime

Improvements
------------
- Add tree validation utilities
- Support AFR vector aggregation policies (min, avg)
- Add async support for large-scale trees
- Optionally annotate skipped nodes in debug mode

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-06-25           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from typing import Dict, Any, List, Tuple, Optional
import itertools
from Attack_Paths.models.get_full_path import expand_paths
from components.progress_dialog import ProgressDialog
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RAFRPathEvaluator:
    """
    Evaluates the optimal Aggregated Failure Risk (AFR) path from a hierarchical
    tree structure, excluding 'control head' nodes and their leaf descendants.
    """

    def __init__(self, tree: Dict[str, Any]):
        """
        Initializes the evaluator with a hierarchical node tree.
        
        Args:
            tree (Dict[str, Any]): Dictionary-based tree with node definitions.
        """
        logger.info(f"Residual AFR calculation initiated.")
        self.tree = tree
        self.root_id = next(iter(tree))

    def find_optimal_path(self, reporter: Optional[ProgressDialog] = None) -> Tuple[List[str], List[int], int]:
        """
        Finds the path with the smallest AFR sum.

        Returns:
            Tuple: (Clean path, AFR vector, AFR sum)
        """
        logger.info(f"Calculating Residual AFR...")
        if reporter: reporter.update(5, "Collecting Initial AFR Analysis possible paths to evaluate.")
        all_paths = self.get_full_leaf_paths(self.root_id, self.tree, [])
        logger.info(f"Collected {len(all_paths)} possible paths to evaluate.")
        if reporter: reporter.update(10, f"Collected {len(all_paths)} possible paths to evaluate.")
        allpossiblepaths = expand_paths(all_paths, self.tree)

        best_path = []
        best_vector = []
        best_sum = float("inf")     # Initialize with worst possible AFR

        percentage = 10
        for i, path in enumerate(allpossiblepaths):
            afr_sum, afr_vector, clean_path = self.compute_combined_afr(path)
            if afr_sum < best_sum:
                best_path = clean_path
                best_vector = afr_vector
                best_sum = afr_sum          # Update best result if current one is better
            progress = int(i * 90 / len(allpossiblepaths))+10
            if reporter: reporter.update(progress, f"Analyzing the Residual AFR - {progress}% completed")

        return best_path, best_vector, best_sum

    def get_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Recursively searches for a node by ID using DFS.

        Args:
            node_id (str): ID of the node to find.

        Returns:
            Node dictionary or None if not found.
        """
        def dfs(subtree: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            for nid, node in subtree.items():
                if nid == node_id:
                    return node        # Found the node
                if "childrens" in node:
                    result = dfs(node["childrens"])       # Recurse into children
                    if result:
                        return result
            return None     # Node not found
        
        return dfs(self.tree)

    def compute_combined_afr(self, full_path: List[str]) -> Tuple[int, List[int], List[str]]:
        """
        Computes the AFR vector and sum from a path, excluding nodes under 'control head'.

        Args:
            full_path (List[str]): Sequence of node IDs representing a full path.

        Returns:
            Tuple: (AFR sum, AFR vector, Cleaned path)
        """
        values = []             # AFR vectors to be aggregated
        skip_subtree = False    # Flag to indicate if a control head was encountered
        clean_path = []         # Path with excluded nodes removed

        for node_id in full_path:
            node = self.get_node_by_id(node_id)
            if node is None:
                logger.warning(f"Node {node_id} not found.")
                continue      # Skip missing node

            node_type = node.get("node_type")

            if node_type == "control head":
                skip_subtree = True
                logger.info(f"Control head {node_id} encountered. Skipping subtree.")
                continue      # Skip this and following nodes

            if skip_subtree:
                if node_type == "leaf":
                    logger.debug(f"Skipping leaf {node_id} under control head.")
                    continue
                continue  # Skip any node under a control head

            if node_type == "leaf" and "values" in node:
                try:
                    values.append(list(map(int, node["values"])))          # Parse AFR values as integers
                    clean_path.append(node_id)           # Add to cleaned output path
                except ValueError:
                    logger.error(f"Invalid values in node {node_id}: {node['values']}")
                    return float("inf"), [], []             # Return worst case on parse error
            else:
                clean_path.append(node_id)        # Internal or non-leaf nodes added to path

        if not values:
            return float("inf"), [], []        # No usable AFR data

        max_vector = list(map(max, zip(*values)))         # Combine vectors by max at each position
        return sum(max_vector), max_vector, clean_path

    def get_full_leaf_paths(self, node_id: str, subtree: Dict[str, Any], prefix: List[str]) -> List[List[str]]:
        """
        Recursively builds all full paths from root to leaves.

        Args:
            node_id (str): Current node ID
            subtree (Dict[str, Any]): Subtree context
            prefix (List[str]): Accumulated node path

        Returns:
            List of all valid paths (List of node ID Lists)
        """
        node = subtree[node_id]
        current_path = prefix
        node_type = node.get("node_type")

        if node_type == "leaf":
            current_path = prefix + [node_id]
            return [current_path]      # Base case: leaf reached

        gate = node.get("gate", "OR")
        children = node.get("childrens", {})

        child_paths = []
        for cid in children:
            if children.get(cid).get("node_type") == "control head": pass
            else:
                sub_paths = self.get_full_leaf_paths(cid, children, current_path)
                child_paths.append(sub_paths)            # Collect child paths recursively

        if gate == "AND":
            # Cartesian product of all child paths
            return [
                list(dict.fromkeys(itertools.chain.from_iterable(p)))
                for p in itertools.product(*child_paths)
            ]
        else:  # OR gate
            # Flatten all OR paths into one list
            return [p for sublist in child_paths for p in sublist]
