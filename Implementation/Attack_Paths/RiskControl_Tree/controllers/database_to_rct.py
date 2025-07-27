

from collections import defaultdict
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import json
from controllers.tablemodel import NodeType, AttackIntermediateNodes, AttackLeafNodes, ReferenceTrees, TechnicalAttackTree, RiskControlTree, AttackTree
from Attack_Paths.Technical_Attack_Tree.controllers.database_to_tat import build_ta_tree_json


def build_rc_tree_json(rc_nodes: List[RiskControlTree]) -> dict:
    """Build full JSON tree from flat RiskControlTree nodes, including TAT_HEAD subtrees using backrefs."""

    uuid_map: Dict[str, RiskControlTree] = {node.uuid: node for node in rc_nodes}
    children_map: Dict[Optional[str], List[RiskControlTree]] = defaultdict(list)
    for node in rc_nodes:
        children_map[node.parent_id].append(node)

    def format_node(node: RiskControlTree) -> dict:
        resolved = node.resolved_node

        def base_node_data(n: RiskControlTree, name: str) -> dict:
            return {
                "node_type": n.node_type.value,
                "node_label": n.node_id,
                "node_Text": name,
                "x": n.x,
                "y": n.y,
                "selected_path": n.highlighted,
            }

        node_text = getattr(resolved, "name", getattr(resolved, "id", "Unnamed"))
        node_json = base_node_data(node, node_text)

        if node.node_type == NodeType.HEAD:
            node_json["af_value"] = node.af_value
            node_json["af_level"] = node.af_level

        if node.node_type == NodeType.LEAF and isinstance(resolved, AttackLeafNodes):
            values = [resolved.time, resolved.expertise, resolved.knowledge, resolved.access, resolved.equipment]
            
            node_json["af_value"] = str(sum(int(v) if v and v.isdigit() else 0 for v in values))
            node_json["af_level"] = getattr(resolved, "afr_level", getattr(resolved, "id", "High"))
            node_json["values"] = values
        
        if node.node_type not in [NodeType.LEAF, NodeType.TAT_HEAD]:
            node_json["gate"] = node.gate
            node_json["childrens"] = []

        # Recursively add child RiskControlTree nodes
        for child in children_map.get(node.uuid, []):
            node_json["childrens"].append(format_node(child))

        # Expand TechnicalAttackTree subtree if node is TAT_HEAD
        if node.node_type == NodeType.TAT_HEAD and isinstance(resolved, ReferenceTrees):
            tat_nodes: List[TechnicalAttackTree] = resolved.technical_attack_trees
            tat_node_json = build_ta_tree_json(tat_nodes)
            tat_node_json["node_type"] = 'technical head'
            tat_node_json["x"] = node_json['x']
            tat_node_json["y"] = node_json['y']
            return tat_node_json
        
        return node_json

    roots = [node for node in rc_nodes if node.parent_id is None]
    if not roots:
        raise ValueError("❌ No root node found in RiskControlTree")

    return format_node(roots[0])
