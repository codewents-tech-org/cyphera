
from Attack_Paths.Attack_Tree.controllers.database_to_at import build_at_tree_json
from Attack_Paths.RiskControl_Tree.controllers.database_to_rct import build_rc_tree_json
from Attack_Paths.Technical_Attack_Tree.controllers.database_to_tat import build_ta_tree_json
from controllers.tablemodel import NodeType, TechnicalTreeHome, AttackTree, TechnicalAttackTree, RiskControlTree
from Attack_Paths.models.afr_calculation import calculate_afr_values
from controllers.schema_manager import get_instances, get_first_instance, delete_all_instance
from Attack_Paths.models.afr_level_calculation import calculate_afr_Level
from Attack_Paths.controllers.backend_afr_calculator import update_afr
from Attack_Paths.Technical_Attack_Tree.controllers.backend_tat_table_update import update_technical_tree_table
from Attack_Paths.RiskControl_Tree.controllers.backend_rct_table_update import update_riskcontrol_tree_table
from Attack_Paths.Attack_Tree.controllers.backend_at_table_update import update_attack_tree_table

import logging
logger = logging.getLogger(__name__)


def update_tree_data(tree_ids: list[str]=[]):
    try:
        control_ids = []
        attack_ids = []
        for tree_id in tree_ids:
            delete_all_instance(TechnicalAttackTree, {'tree_id': tree_id, 'is_deleted': False})

        for tree_id in tree_ids:
            nodes = get_instances(RiskControlTree, {'node_id': tree_id, 'is_deleted': False})
            if nodes:
                for node in nodes:
                    if node.tree_id not in control_ids: control_ids.append(node.tree_id)
    
        for tree_id in tree_ids:
            delete_all_instance(RiskControlTree, {'node_id': tree_id, 'is_deleted': False})

        for tree_id in tree_ids:
            nodes = get_instances(AttackTree, {'node_id': tree_id, 'is_deleted': False})
            if nodes:
                for node in nodes:
                    if node.tree_id not in attack_ids: attack_ids.append(node.tree_id)

            for rct_id in control_ids:
                nodes = get_instances(AttackTree, {'node_id': rct_id, 'is_deleted': False})
                if nodes:
                    for node in nodes:
                        if node.tree_id not in attack_ids: attack_ids.append(node.tree_id)

        for tree_id in tree_ids:
            delete_all_instance(AttackTree, {'node_id': tree_id, 'is_deleted': False})
        
        for tree in control_ids:
            update_afr(tree, "risk_control_tree")
            update_technical_tree_table(tree, "risk_control_tree")
            update_riskcontrol_tree_table(tree)

        for tree in attack_ids:
            update_afr(tree, "attack_tree")
            update_technical_tree_table(tree, "attack_tree")
            update_riskcontrol_tree_table(tree)
            update_attack_tree_table(tree)
        
        for tree_id in tree_ids:
            update_technical_tree_table(tree_id, "technical_tree")

    except Exception as e:
        logger.error(f"Error in update tree data: {e}")
        return None, None, None
