
from Attack_Paths.Attack_Tree.controllers.database_to_at import build_at_tree_json
from Attack_Paths.RiskControl_Tree.controllers.database_to_rct import build_rc_tree_json
from Attack_Paths.Technical_Attack_Tree.controllers.database_to_tat import build_ta_tree_json
from controllers.tablemodel import NodeType, TechnicalTreeHome, AttackTree, TechnicalAttackTree, RiskControlTree
from Attack_Paths.models.afr_calculation import calculate_afr_values
from controllers.schema_manager import get_instances, get_first_instance, update_instance
from Attack_Paths.models.afr_level_calculation import calculate_afr_Level

import logging
logger = logging.getLogger(__name__)


def update_technical_tree_table(tree_id: str=None, tree_type: str=None):
    try:
        risk_control_tree_map = {}
        attack_tree_map = {}
        
        match tree_type:
            case "risk_control_tree":
                technical_tree_ids = []
                nodes = get_instances(RiskControlTree, {'tree_id': tree_id, 'node_type': NodeType.TAT_HEAD, 'is_deleted': False})
                for node in nodes:
                    if node.node_id not in technical_tree_ids:
                        technical_tree_ids.append(node.node_id)

                for tat_id in technical_tree_ids:
                    risk_control_tree_ids = []
                    nodes = get_instances(RiskControlTree, {'node_id': tat_id, 'is_deleted': False})
                    if nodes:
                        for node in nodes:
                            if node.id not in risk_control_tree_ids:
                                risk_control_tree_ids.append(node.id)
                    risk_control_tree_map[tat_id] = risk_control_tree_ids

                for tat_id, rct_ids in risk_control_tree_map.items():
                    if rct_ids:
                        result = ', '.join(rct_ids)
                        update_instance(TechnicalTreeHome, {'id':tat_id, 'is_deleted':False}, {'used_in_riskcontrol': result})
            case "attack_tree":
                technical_tree_ids = []
                risk_control_tree_ids = []
                nodes = get_instances(AttackTree, {'tree_id': tree_id, 'node_type': NodeType.TAT_HEAD, 'is_deleted': False})
                for node in nodes:
                    if node.node_id not in technical_tree_ids:
                        technical_tree_ids.append(node.node_id)
                nodes = get_instances(AttackTree, {'tree_id': tree_id, 'node_type': NodeType.RCT_HEAD, 'is_deleted': False})
                for node in nodes:
                    if node.node_id not in risk_control_tree_ids:
                        risk_control_tree_ids.append(node.node_id)
                for rct_id in risk_control_tree_ids:
                    nodes = get_instances(RiskControlTree, {'tree_id': rct_id, 'node_type': NodeType.TAT_HEAD, 'is_deleted': False})
                    if nodes:
                        for node in nodes:
                            if node.node_id not in technical_tree_ids:
                                technical_tree_ids.append(node.node_id)
                
                for tat_id in technical_tree_ids:
                    attack_tree_ids = []
                    nodes = get_instances(AttackTree, {'node_id': tat_id, 'is_deleted': False})
                    if nodes:
                        for node in nodes:
                            if node.id not in risk_control_tree_ids:
                                risk_control_tree_ids.append(node.id)
                    risk_control_tree_map[tat_id] = risk_control_tree_ids

                for tat_id, rct_ids in risk_control_tree_map.items():
                    if rct_ids:
                        result = ', '.join(rct_ids)
                        update_instance(TechnicalTreeHome, {'id':tat_id, 'is_deleted':False}, {'used_in_riskcontrol': result})

        return technical_tree_ids, risk_control_tree_map, attack_tree_map
    except Exception as e:
        logger.error(f"Error in collect_trees_by_updated_leaf: {e}")
        return None, None, None
