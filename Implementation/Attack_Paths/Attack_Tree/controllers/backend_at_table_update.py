
from controllers.tablemodel import NodeType, AttackTreeHome, AttackTree, Threats, RiskData
from controllers.schema_manager import get_instances, get_first_instance, update_instance
from models.helper import risk_map
from Attack_Paths.RiskControl_Tree.controllers.backend_rct_table_update import update_riskcontrol_tree_table

import logging
logger = logging.getLogger(__name__)


def update_attack_tree_table(tree_id: str=None):
    try:        
        if tree_id:         
            node = get_first_instance(AttackTree, {'tree_id': tree_id, 'node_type': NodeType.HEAD, 'is_deleted': False})
            if node and getattr(node, 'af_level', '') is not None and getattr(node, 'rf_level', '') is not None:
                update_instance(Threats, {'threat_id': tree_id, 'is_deleted': 'False'}, {'initia_afr': node.af_level, 'resid_afr':node.rf_level})
                update_instance(AttackTreeHome, {'id': tree_id, 'is_deleted': False}, {'initial_afr': node.af_level, 'resid_afr':node.rf_level})
                mitigates_ids = []
                rct_nodes = get_instances(AttackTree, {'tree_id': tree_id, 'node_type': NodeType.RCT_HEAD, 'is_deleted': False})
                if rct_nodes:
                    for rct_node in rct_nodes:
                        if rct_node and getattr(rct_node, 'node_id', '') is not None and rct_node.node_id not in mitigates_ids:
                            mitigates_ids.append(rct_node.node_id)
                mitigates = ', '.join(mitigates_ids) if mitigates_ids else ''
                print(mitigates)
                threat_node = get_first_instance(AttackTreeHome, {'id': tree_id, 'is_deleted': False})
                rd_nodes = get_instances(RiskData, {'threat_id': f"{threat_node.id} - {threat_node.name}"})
                for rd_node in rd_nodes:
                    update_instance(RiskData, {'threat_id': rd_node.threat_id}, {'init_afr_level': node.af_level, 
                                                                                        'init_afr_value': risk_map[(rd_node.impact, node.af_level)] if 'imapact' in node and node.af_level and node.af_level != '' else '', 
                                                                                        'resid_afr_level':node.rf_level, 
                                                                                        'resid_afr_value': risk_map[(rd_node.impact, node.rf_level)] if 'imapact' in node and node.rf_level and node.rf_level != '' else '', 
                                                                                        'mitigated_by':mitigates})

        return True
    except Exception as e:
        logger.error(f"Error in collect_trees_by_updated_leaf: {e}")
        return False
