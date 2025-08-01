
from Attack_Paths.Attack_Tree.controllers.database_to_at import build_at_tree_json
from Attack_Paths.RiskControl_Tree.controllers.database_to_rct import build_rc_tree_json
from Attack_Paths.Technical_Attack_Tree.controllers.database_to_tat import build_ta_tree_json
from controllers.tablemodel import NodeType, RiskControlTreeHome, AttackTree
from Attack_Paths.models.afr_calculation import calculate_afr_values
from controllers.schema_manager import get_instances, get_first_instance, update_instance
from Attack_Paths.models.afr_level_calculation import calculate_afr_Level

import logging
logger = logging.getLogger(__name__)


def update_riskcontrol_tree_table(tree_id: str=None):
    try:        
        if tree_id:
            mitigates_ids_map = {}
            risk_control_tree_ids = []            
            nodes = get_instances(AttackTree, {'tree_id': tree_id, 'node_type': NodeType.RCT_HEAD, 'is_deleted': False})
            print(nodes)
            for node in nodes:
                if node.node_id not in risk_control_tree_ids:
                    risk_control_tree_ids.append(node.node_id)
            
            for rct_id in risk_control_tree_ids:
                mitigates_ids = []
                nodes = get_instances(AttackTree, {'node_id': rct_id, 'node_type': NodeType.RCT_HEAD, 'is_deleted': False})
                print(rct_id, " : ", nodes)
                if nodes:
                    for node in nodes:
                        if node.tree_id not in mitigates_ids:
                            mitigates_ids.append(node.tree_id)
                mitigates_ids_map[rct_id] = mitigates_ids
            print(mitigates_ids_map)
            for rct_id, mitigates_ids in mitigates_ids_map.items():
                if mitigates_ids:
                    result = ', '.join(mitigates_ids)
                    update_instance(RiskControlTreeHome, {'id': rct_id, 'is_deleted': False}, {'mitigates': result})

        return True
    except Exception as e:
        logger.error(f"Error in collect_trees_by_updated_leaf: {e}")
        return False
