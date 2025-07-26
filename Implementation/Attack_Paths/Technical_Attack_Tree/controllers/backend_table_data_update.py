
from Attack_Paths.Technical_Attack_Tree.controllers.database_to_tat import build_ta_tree_json
from controllers.tablemodel import NodeType, TechnicalTreeHome, AttackTree, TechnicalAttackTree, RiskControlTree
from Attack_Paths.models.afr_calculation import calculate_afr_values
from controllers.schema_manager import get_instances, get_first_instance, update_instance
from Attack_Paths.models.afr_level_calculation import calculate_afr_Level

import logging
logger = logging.getLogger(__name__)


def update_technical_tree_table(tree_id: str=None, tree_type: str=None):
    logger.debug(f"[START] update_technical_tree_table(tree_id={tree_id}, tree_type={tree_type})")
    try:
        risk_control_tree_map = {}
        attack_tree_map = {}
        logger.debug(f"[INIT] Empty risk_control_tree_map and attack_tree_map initialized.")

        match tree_type:
            case "risk_control_tree":
                technical_tree_ids = []
                logger.debug(f"[BRANCH] Processing for tree_type='risk_control_tree' with tree_id={tree_id}")
                
                nodes = get_instances(RiskControlTree, {'tree_id': tree_id, 'node_type': NodeType.TAT_HEAD, 'is_deleted': False})
                logger.debug(f"[QUERY] Fetched {len(nodes)} RiskControlTree nodes as TAT_HEAD with tree_id={tree_id}")
                for node in nodes:
                    logger.debug(f"  [NODE] RiskControlTree.node_id={node.node_id}")
                    if node.node_id not in technical_tree_ids:
                        technical_tree_ids.append(node.node_id)

                logger.debug(f"[IDS] Collected technical_tree_ids: {technical_tree_ids}")

                for tat_id in technical_tree_ids:
                    risk_control_tree_ids = []
                    logger.debug(f"[LOOP] Gathering risk_control_tree_ids for tat_id={tat_id}")
                    nodes = get_instances(RiskControlTree, {'node_id': tat_id, 'is_deleted': False})
                    logger.debug(f"    [QUERY] Found {len(nodes) if nodes else 0} nodes with node_id={tat_id}")
                    if nodes:
                        for node in nodes:
                            logger.debug(f"      [CHECK] node.id={getattr(node, 'id', None)}")
                            if getattr(node, 'id', None) not in risk_control_tree_ids:
                                risk_control_tree_ids.append(node.id)
                    logger.debug(f"    [RESULT] risk_control_tree_ids={risk_control_tree_ids}")
                    risk_control_tree_map[tat_id] = risk_control_tree_ids

                logger.debug(f"[MAPPING] risk_control_tree_map: {risk_control_tree_map}")

                for tat_id, rct_ids in risk_control_tree_map.items():
                    logger.debug(f"[UPDATE] Updating TechnicalTreeHome for tat_id={tat_id} with rct_ids={rct_ids}")
                    if rct_ids:
                        result = ', '.join(rct_ids)
                        update_instance(TechnicalTreeHome, {'id':tat_id, 'is_deleted':False}, {'used_in_riskcontrol': result})
                        logger.debug(f"  [UPDATE_INSTANCE] Set used_in_riskcontrol='{result}' for id={tat_id}")

            case "attack_tree":
                technical_tree_ids = []
                risk_control_tree_ids = []
                logger.debug(f"[BRANCH] Processing for tree_type='attack_tree' with tree_id={tree_id}")

                nodes = get_instances(AttackTree, {'tree_id': tree_id, 'node_type': NodeType.TAT_HEAD, 'is_deleted': False})
                logger.debug(f"[QUERY] Fetched {len(nodes)} AttackTree TAT_HEAD nodes with tree_id={tree_id}")
                for node in nodes:
                    logger.debug(f"  [NODE] AttackTree.node_id={node.node_id}")
                    if node.node_id not in technical_tree_ids:
                        technical_tree_ids.append(node.node_id)
                logger.debug(f"[IDS] Collected technical_tree_ids: {technical_tree_ids}")

                nodes = get_instances(AttackTree, {'tree_id': tree_id, 'node_type': NodeType.RCT_HEAD, 'is_deleted': False})
                logger.debug(f"[QUERY] Fetched {len(nodes)} AttackTree RCT_HEAD nodes with tree_id={tree_id}")
                for node in nodes:
                    logger.debug(f"  [NODE] RCT_HEAD node_id={node.node_id}")
                    if node.node_id not in risk_control_tree_ids:
                        risk_control_tree_ids.append(node.node_id)
                logger.debug(f"[IDS] Collected risk_control_tree_ids: {risk_control_tree_ids}")

                for rct_id in risk_control_tree_ids:
                    logger.debug(f"[LOOP] Gathering TAT_HEAD under RiskControlTree with tree_id={rct_id}")
                    nodes = get_instances(RiskControlTree, {'tree_id': rct_id, 'node_type': NodeType.TAT_HEAD, 'is_deleted': False})
                    logger.debug(f"    [QUERY] Found {len(nodes) if nodes else 0} nodes with tree_id={rct_id} node_type=TAT_HEAD")
                    if nodes:
                        for node in nodes:
                            logger.debug(f"      [CHECK] node.node_id={node.node_id}")
                            if node.node_id not in technical_tree_ids:
                                technical_tree_ids.append(node.node_id)
                logger.debug(f"[IDS] technical_tree_ids after appending from RCT: {technical_tree_ids}")

                for tat_id in technical_tree_ids:
                    attack_tree_ids = []
                    logger.debug(f"[LOOP] Gathering attack_tree_ids for tat_id={tat_id}")
                    nodes = get_instances(AttackTree, {'node_id': tat_id, 'is_deleted': False})
                    logger.debug(f"    [QUERY] Found {len(nodes) if nodes else 0} AttackTree with node_id={tat_id}")
                    if nodes:
                        for node in nodes:
                            logger.debug(f"      [CHECK] node.id={getattr(node, 'id', None)}")
                            if getattr(node, 'id', None) not in risk_control_tree_ids:
                                risk_control_tree_ids.append(node.id)
                    logger.debug(f"    [RESULT] attack_tree_ids={attack_tree_ids}")
                    risk_control_tree_map[tat_id] = risk_control_tree_ids

                logger.debug(f"[MAPPING] risk_control_tree_map: {risk_control_tree_map}")

                for tat_id, rct_ids in risk_control_tree_map.items():
                    logger.debug(f"[UPDATE] Updating TechnicalTreeHome for tat_id={tat_id} with rct_ids={rct_ids}")
                    if rct_ids:
                        result = ', '.join(rct_ids)
                        update_instance(TechnicalTreeHome, {'id':tat_id, 'is_deleted':False}, {'used_in_riskcontrol': result})
                        logger.debug(f"  [UPDATE_INSTANCE] Set used_in_riskcontrol='{result}' for id={tat_id}")

        logger.debug(f"[RETURN] technical_tree_ids={locals().get('technical_tree_ids', None)}, risk_control_tree_map={risk_control_tree_map}, attack_tree_map={attack_tree_map}")
        return technical_tree_ids, risk_control_tree_map, attack_tree_map
    except Exception as e:
        logger.error(f"[ERROR] Error in collect_trees_by_updated_leaf: {e}", exc_info=True)
        return None, None, None
