

from collections import defaultdict
from typing import List, Dict, Optional
import json
from controllers.tablemodel import NodeType, AttackIntermediateNodes, AttackLeafNodes, ReferenceTrees, TechnicalAttackTree, TechnicalAttackTree, AttackTree

import logging
logger = logging.getLogger(__name__)

def build_ta_tree_json(tat_nodes: List[TechnicalAttackTree]) -> dict:
    """Build full JSON tree from flat TechnicalAttackTree nodes."""
    logger.debug(f"[START] build_ta_tree_json: total_nodes={len(tat_nodes)}")

    uuid_map: Dict[str, TechnicalAttackTree] = {node.uuid: node for node in tat_nodes}
    logger.debug(f"[MAPPING] Created uuid_map with {len(uuid_map)} uuids")
    children_map: Dict[Optional[str], List[TechnicalAttackTree]] = defaultdict(list)
    for node in tat_nodes:
        children_map[node.parent_id].append(node)
    logger.debug(f"[MAPPING] Built children_map with {len(children_map)} parent_ids: {list(children_map.keys())}")

    def format_node(node: TechnicalAttackTree, depth=0) -> dict:
        resolved = node.resolved_node
        indent = "  " * depth
        logger.debug(f"{indent}[NODE] Formatting node uuid={node.uuid}, type={getattr(node.node_type, 'value', node.node_type)}, parent_id={node.parent_id}")

        def base_node_data(n: TechnicalAttackTree, name: str) -> dict:
            logger.debug(f"{indent}  [BASE] base_node_data for node {n.uuid} name={name}")
            return {
                "node_type": n.node_type.value if hasattr(n.node_type, 'value') else str(n.node_type),
                "node_label": n.node_id,
                "node_Text": name,
                "x": n.x,
                "y": n.y,
                "selected_path": n.highlighted,
            }

        node_text = getattr(resolved, "name", getattr(resolved, "id", "Unnamed"))
        logger.debug(f"{indent}  [TEXT] Node text resolved as: {node_text}")
        node_json = base_node_data(node, node_text)

        if node.node_type == NodeType.HEAD:
            logger.debug(f"{indent}  [HEAD] Adding af_value={node.af_value}, af_level={node.af_level}")
            node_json["af_value"] = node.af_value
            node_json["af_level"] = node.af_level

        if node.node_type == NodeType.LEAF and isinstance(resolved, AttackLeafNodes):
            values = [resolved.time, resolved.expertise, resolved.knowledge, resolved.access, resolved.equipment]
            logger.debug(f"{indent}  [LEAF] Values={values}")
            af_value_sum = str(sum(int(v) if v and str(v).isdigit() else 0 for v in values))
            node_json["af_value"] = af_value_sum
            node_json["af_level"] = getattr(resolved, "afr_level", getattr(resolved, "id", "High"))
            node_json["values"] = values
            logger.debug(f"{indent}  [LEAF] af_value_sum={af_value_sum}, af_level={node_json['af_level']}")

        if node.node_type not in [NodeType.LEAF, NodeType.TAT_HEAD, NodeType.RCT_HEAD]:
            logger.debug(f"{indent}  [BRANCH] Node is GATE type ({node.node_type}), setting gate and childrens")
            node_json["gate"] = node.gate
            node_json["childrens"] = []

        # Recursively add child TechnicalAttackTree nodes
        children = children_map.get(node.uuid, [])
        logger.debug(f"{indent}  [CHILDREN] Node {node.uuid} has {len(children)} children")
        for child in children:
            child_json = format_node(child, depth+1)
            if "childrens" in node_json:
                node_json["childrens"].append(child_json)

        return node_json

    roots = [node for node in tat_nodes if node.parent_id is None]
    logger.debug(f"[ROOTS] Found {len(roots)} root nodes: {[n.uuid for n in roots]}")
    if not roots:
        logger.error("❌ No root node found in TechnicalAttackTree")
        raise ValueError("❌ No root node found in TechnicalAttackTree")

    logger.debug(f"[RETURN] Returning tree starting from root uuid={roots[0].uuid}")
    return format_node(roots[0])
