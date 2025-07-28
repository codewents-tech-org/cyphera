"""
Module: Initial AFR Calculation module      \n 
File: init_afr_calculation.py      \n
Layer: Backend / Computation / init_afr_calculation      \n
Component ID:          \n
Requirement IDs:       \n
Author: Vijaya karagi  \n
Created On: 2025-06-25     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Evaluate the optimal Aggregated Failure Risk (AFR) path through a hierarchical
tree of nodes representing a system decomposition, based on logical relationships
(AND/OR) and AFR vectors assigned to leaf nodes.

Description:
------------
This module defines the `AFRPathEvaluator` class for computing the most optimal
path through a tree-structured system model. Nodes can be of type "internal" or "leaf",
and internal nodes use logical gates ("AND"/"OR") to control path expansion.

Each leaf node includes a vector of AFR values, and the objective is to:
- Traverse all valid root-to-leaf paths
- Calculate an aggregated AFR vector for each path (element-wise maximum)
- Select the path that results in the smallest total AFR sum

Responsibilities
----------------
- Recursively traverse hierarchical trees with support for logical AND/OR gates
- Collect AFR vectors from leaf nodes
- Aggregate AFR vectors using element-wise maximum
- Compute the total AFR score of each path
- Identify and return the optimal path with minimal AFR total
- Resolve node IDs via recursive lookup
- Handle malformed or missing node data gracefully

Dependencies:
-------------
- Python Standard Library only:
    * typing: for type annotations
    * itertools: for AND-gate cross-product logic
    * logging: for traceable diagnostic messages

Limitations
-----------
- Does not support asynchronous or parallel tree traversal
- Does not validate the structure of the input tree (assumes correctness)
- All leaf node `values` must be strings representing valid integers
- Only "leaf" nodes are considered for AFR contribution

Improvements
------------
- Add schema validation for the input tree structure
- Introduce support for dynamic gate types or additional logic (e.g., NOT, XOR)
- Allow configurable aggregation logic (e.g., sum, average, min)
- Enable runtime node exclusion via metadata or rules
- Extend to support multiple root nodes or DAGs instead of strict trees

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
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AFRPathEvaluator:
    """
    Evaluate the optimal AFR path from a hierarchical tree structure.
    """

    def __init__(self, tree: Dict[str, Any]):
        logger.info(f"Initial AFR calculation initiated.")
        self.tree = tree
        self.root_id = next(iter(tree))       # Set the root node ID (assumes single entry point)

    def find_optimal_path(self, reporter: Optional[ProgressDialog] = None) -> Tuple[List[str], List[int], int]:
        logger.info(f"Calculating Initial AFR...")
        if reporter: reporter.update(5, "Collecting Initial AFR Analysis possible paths to evaluate.")
        # Collect all complete root-to-leaf paths (including intermediate nodes)
        all_paths = self.get_full_leaf_paths(self.root_id, self.tree, [])      # Get all possible root-to-leaf paths
        logger.info(f"Collected {len(all_paths)} possible paths to evaluate.")
        if reporter: reporter.update(10, f"Collected {len(all_paths)} possible paths to evaluate.")
        allpossiblepaths = expand_paths(all_paths, self.tree)
        
        best_path = []
        best_vector = []
        best_sum = float("inf")         # Start with the worst possible (maximum) AFR

        percentage = 10
        for i, path in enumerate(allpossiblepaths):
            afr_sum, afr_vector = self.compute_combined_afr(path)       # Compute AFR for this path
            if afr_sum < best_sum:
                # If this path has a lower AFR sum, update the best-known result
                best_path = path
                best_vector = afr_vector
                best_sum = afr_sum
            progress = int(i * 90 / len(allpossiblepaths))+10
            if reporter: reporter.update(progress, f"Analyzing the Initial AFR - {progress}% completed")

        return best_path, best_vector, best_sum       # Return optimal path info

    def get_node_by_id(self, node_id: str) -> Dict[str, Any]:
        def dfs(subtree: Dict[str, Any]) -> Dict[str, Any] | None:
            for nid, node in subtree.items():
                if nid == node_id:
                    return node        # Found target node
                if "childrens" in node:
                    result = dfs(node["childrens"])        # Recurse into children
                    if result:
                        return result
            return None      # Node not found in this subtree
        
        return dfs(self.tree)      # Start DFS from root

    def compute_combined_afr(self, full_path: List[str]) -> Tuple[int, List[int]]:
        values = []
        for node_id in full_path:
            node = self.get_node_by_id(node_id)
            # Only include values from leaf nodes that have a 'values' list
            if node and node.get("node_type") == "leaf" and "values" in node:
                values.append(list(map(int, node["values"])))          # Convert all string values to integers

        if values == []:
            return float('inf'), []          # No valid AFR data; return worst case

        # Combine vectors using element-wise max to compute AFR risk
        max_vector = list(map(max, zip(*values)))
        return sum(max_vector), max_vector       # Total AFR and vector

    def get_full_leaf_paths(self, node_id: str, subtree: Dict[str, Any], prefix: List[str]) -> List[List[str]]:
        """
        Recursively return all full paths from root to each leaf node,
        respecting AND/OR gates. Each path includes intermediate nodes.
        """
        node = subtree[node_id]
        current_path = prefix       # Accumulate path history
        node_type = node.get("node_type")

        if node_type == "leaf":
            current_path = prefix + [node_id]
            return [current_path]         # Leaf reached: return the full path

        gate = node.get("gate", "OR")      # Default to OR if gate is not specified
        children = node.get("childrens", {})
        if children == {}: return [current_path]

        child_paths = []
        for cid in children:
            # Recurse into each child and collect their full paths
            sub_paths = self.get_full_leaf_paths(cid, children, current_path)
            child_paths.append(sub_paths)

        if gate == "AND":
            # For AND, combine paths from all children (cartesian product)
            return [list(dict.fromkeys(itertools.chain.from_iterable(p))) for p in itertools.product(*child_paths)]
        else:
            # For OR, any one child path is valid (flattened)
            return [p for sublist in child_paths for p in sublist]
