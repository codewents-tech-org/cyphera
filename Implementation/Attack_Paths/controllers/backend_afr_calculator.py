

from Attack_Paths.Attack_Tree.controllers.database_to_at import build_at_tree_json
from Attack_Paths.RiskControl_Tree.controllers.database_to_rct import build_rc_tree_json
from Attack_Paths.Technical_Attack_Tree.controllers.database_to_tat import build_ta_tree_json
from controllers.tablemodel import NodeType, ReferenceTrees, AttackTree, TechnicalAttackTree, RiskControlTree
from Attack_Paths.models.afr_calculation import calculate_afr_values
from controllers.schema_manager import get_instances, get_first_instance, update_instance
from Attack_Paths.models.afr_level_calculation import calculate_afr_Level
from Attack_Paths.Technical_Attack_Tree.controllers.backend_tat_table_update import update_technical_tree_table
from Attack_Paths.RiskControl_Tree.controllers.backend_rct_table_update import update_riskcontrol_tree_table
from Attack_Paths.Attack_Tree.controllers.backend_at_table_update import update_attack_tree_table

import logging
logger = logging.getLogger(__name__)


def update_afr_values(updated_leaf_list: list, tree_id: str = None, tree_type: str = None) -> bool:
    try:
        technical_tree_ids, risk_control_tree_ids, attack_tree_ids = [], [], []
        match tree_type:
            case "technical_tree":
                tat_ids, rtc_ids, at_ids = collect_trees_by_updated_leaf(updated_leaf_list, tree_id)
                if tat_ids: technical_tree_ids.extend(tat_id for tat_id in tat_ids if tat_id != tree_id)
                if rtc_ids: risk_control_tree_ids.extend(rtc_id for rtc_id in rtc_ids if rtc_id != tree_id)
                if at_ids: attack_tree_ids.extend(at_id for at_id in at_ids if at_id != tree_id)

                rtc_ids, at_ids = collect_trees_by_updated_tree(tree_id, "technical_tree")
                if rtc_ids: risk_control_tree_ids.extend(rtc_id for rtc_id in rtc_ids if rtc_id != tree_id and rtc_id not in risk_control_tree_ids)
                if at_ids: attack_tree_ids.extend(at_id for at_id in at_ids if at_id != tree_id and at_id not in attack_tree_ids)
                
                print(f"Technical Trees: {technical_tree_ids}, Risk Control Trees: {risk_control_tree_ids}, Attack Trees: {attack_tree_ids}")
                for tree in technical_tree_ids:
                    update_afr(tree, "technical_tree")
                
                if tree_id:
                    update_technical_tree_table(tree_id, "technical_tree")

                for tree in risk_control_tree_ids:
                    update_afr(tree, "risk_control_tree")
                    update_technical_tree_table(tree, "risk_control_tree")
                    update_riskcontrol_tree_table(tree)

                for tree in attack_tree_ids:
                    update_afr(tree, "attack_tree")
                    update_technical_tree_table(tree, "attack_tree")
                    update_riskcontrol_tree_table(tree)
                    update_attack_tree_table(tree)

            case "risk_control_tree":
                tat_ids, rtc_ids, at_ids = collect_trees_by_updated_leaf(updated_leaf_list, tree_id)
                if tat_ids: technical_tree_ids.extend(tat_id for tat_id in tat_ids if tat_id != tree_id)
                if rtc_ids: risk_control_tree_ids.extend(rtc_id for rtc_id in rtc_ids if rtc_id != tree_id)
                if at_ids: attack_tree_ids.extend(at_id for at_id in at_ids if at_id != tree_id)

                rtc_ids, at_ids = collect_trees_by_updated_tree(tree_id, "risk_control_tree")
                if at_ids: attack_tree_ids.extend(at_id for at_id in at_ids if at_id != tree_id and at_id not in attack_tree_ids)
                
                print(f"Technical Trees: {technical_tree_ids}, Risk Control Trees: {risk_control_tree_ids}, Attack Trees: {attack_tree_ids}")
                for tree in technical_tree_ids:
                    update_afr(tree, "technical_tree")

                for tree in risk_control_tree_ids:
                    update_afr(tree, "risk_control_tree")
                    update_technical_tree_table(tree, "risk_control_tree")
                    update_riskcontrol_tree_table(tree)
                
                if tree_id:
                    update_technical_tree_table(tree_id, "risk_control_tree")
                    update_riskcontrol_tree_table(tree_id)

                for tree in attack_tree_ids:
                    update_afr(tree, "attack_tree")
                    update_technical_tree_table(tree, "attack_tree")
                    update_riskcontrol_tree_table(tree)
                    update_attack_tree_table(tree)

            case "attack_tree":
                tat_ids, rtc_ids, at_ids = collect_trees_by_updated_leaf(updated_leaf_list, tree_id)
                if tat_ids: technical_tree_ids.extend(tat_id for tat_id in tat_ids if tat_id != tree_id)
                if rtc_ids: risk_control_tree_ids.extend(rtc_id for rtc_id in rtc_ids if rtc_id != tree_id)
                if at_ids: attack_tree_ids.extend(at_id for at_id in at_ids if at_id != tree_id)
                
                print(f"Technical Trees: {technical_tree_ids}, Risk Control Trees: {risk_control_tree_ids}, Attack Trees: {attack_tree_ids}")
                for tree in technical_tree_ids:
                    update_afr(tree, "technical_tree")

                for tree in risk_control_tree_ids:
                    update_afr(tree, "risk_control_tree")
                    update_technical_tree_table(tree, "risk_control_tree")
                    update_riskcontrol_tree_table(tree)

                for tree in attack_tree_ids:
                    update_afr(tree, "attack_tree")
                    update_technical_tree_table(tree, "attack_tree")
                    update_riskcontrol_tree_table(tree)
                    update_attack_tree_table(tree)
                
                if tree_id:
                    update_technical_tree_table(tree_id, "attack_tree")
                    update_riskcontrol_tree_table(tree_id)
                    update_attack_tree_table(tree_id)
            
            case None:
                if updated_leaf_list:
                    tat_ids, rtc_ids, at_ids = collect_trees_by_updated_leaf(updated_leaf_list, tree_id)
                    if tat_ids: technical_tree_ids.extend(tat_id for tat_id in tat_ids if tat_id != tree_id)
                    if rtc_ids: risk_control_tree_ids.extend(rtc_id for rtc_id in rtc_ids if rtc_id != tree_id)
                    if at_ids: attack_tree_ids.extend(at_id for at_id in at_ids if at_id != tree_id)
                    
                    print(f"Technical Trees: {technical_tree_ids}, Risk Control Trees: {risk_control_tree_ids}, Attack Trees: {attack_tree_ids}")
                    for tree in technical_tree_ids:
                        update_afr(tree, "technical_tree")

                    for tree in risk_control_tree_ids:
                        update_afr(tree, "risk_control_tree")
                        update_technical_tree_table(tree, "risk_control_tree")
                        update_riskcontrol_tree_table(tree)

                    for tree in attack_tree_ids:
                        update_afr(tree, "attack_tree")
                        update_technical_tree_table(tree, "attack_tree")
                        update_riskcontrol_tree_table(tree)
                        update_attack_tree_table(tree)
        return True
    except Exception as e:
        logger.error(f"Error in update_afr_values: {e}")
        return False

def collect_trees_by_updated_leaf(updated_leaf_list: list, tree_id: str = None):
    try:
        technical_tree_ids = []
        risk_control_tree_ids = []
        attack_tree_ids = []
        for leaf in updated_leaf_list:
            nodes = get_instances(TechnicalAttackTree, {'node_id': leaf, 'is_deleted': False})
            if nodes:
                for node in nodes:
                    if node.tree_id not in technical_tree_ids and node.tree_id != tree_id:
                        technical_tree_ids.append(node.tree_id)

            nodes = get_instances(RiskControlTree, {'node_id': leaf, 'is_deleted': False})
            if nodes:
                for node in nodes:
                    if node.tree_id not in risk_control_tree_ids and node.tree_id != tree_id:
                        risk_control_tree_ids.append(node.tree_id)

            nodes = get_instances(AttackTree, {'node_id': leaf, 'is_deleted': False})
            if nodes:
                for node in nodes:
                    if node.tree_id not in attack_tree_ids and node.tree_id != tree_id:
                        attack_tree_ids.append(node.tree_id)

        return technical_tree_ids, risk_control_tree_ids, attack_tree_ids
    except Exception as e:
        logger.error(f"Error in collect_trees_by_updated_leaf: {e}")
        return None, None, None

def collect_trees_by_updated_tree(tree_id: str = None, tree_type: str = None):
    try:
        risk_control_tree_ids = []
        attack_tree_ids = []
        match tree_type:
            case "technical_tree":
                nodes = get_instances(RiskControlTree, {'node_id': tree_id, 'is_deleted': False})
                if nodes:
                    for node in nodes:
                        if node.tree_id not in risk_control_tree_ids and node.tree_id != tree_id: risk_control_tree_ids.append(node.tree_id)

                nodes = get_instances(AttackTree, {'node_id': tree_id, 'is_deleted': False})
                if nodes:
                    for node in nodes:
                        if node.tree_id not in attack_tree_ids and node.tree_id != tree_id: attack_tree_ids.append(node.tree_id)

                return risk_control_tree_ids, attack_tree_ids

            case "risk_control_tree":
                nodes = get_instances(AttackTree, {'node_id': tree_id, 'is_deleted': False})
                if nodes:
                    for node in nodes:
                        if node.tree_id not in attack_tree_ids and node.tree_id != tree_id: attack_tree_ids.append(node.tree_id)

                return None, attack_tree_ids

        return None, None
    except Exception as e:
        logger.error(f"Error in collect_trees_by_updated_tree: {e}")
        return None, None

def update_afr(tree_id: str, tree_type: str):
    match tree_type:
        case "technical_tree":
            tat_nodes = get_instances(TechnicalAttackTree, {'tree_id':tree_id, 'is_deleted':False})
            if tat_nodes:
                tat_json_tree = build_ta_tree_json(tat_nodes)
                tat_json_tree1 = convert_tree_to_flat_dict(tat_json_tree, tree_id)
                output = calculate_afr_values(tat_json_tree1, "technical_tree")
                print(f"Technical Tree AFR Output: {output}")
                node = get_first_instance(TechnicalAttackTree, {'tree_id': tree_id, 'node_type': NodeType.HEAD, 'is_deleted': False})
                if node and output and 'init_afr' in output:
                    update_instance(TechnicalAttackTree, {'tree_id': tree_id, 'node_type': NodeType.HEAD, 'is_deleted': False}, 
                                    {'af_value': str(output['init_afr']['afr_sum']), 'af_level': calculate_afr_Level(output['init_afr']['afr_sum'])})

        case "risk_control_tree":
            rct_nodes = get_instances(RiskControlTree, {'tree_id':tree_id, 'is_deleted':False})
            if rct_nodes:
                rct_json_tree = build_rc_tree_json(rct_nodes)
                rct_json_tree1 = convert_tree_to_flat_dict(rct_json_tree, tree_id)
                output = calculate_afr_values(rct_json_tree1, "risk_control_tree")
                print(f"Risk Control Tree AFR Output: {output}")
                node = get_first_instance(RiskControlTree, {'tree_id': tree_id, 'node_type': NodeType.HEAD, 'is_deleted': False})
                if node and output and 'init_afr' in output:
                    update_instance(RiskControlTree, {'tree_id': tree_id, 'node_type': NodeType.HEAD, 'is_deleted': False}, 
                                    {'af_value': str(output['init_afr']['afr_sum']), 'af_level': calculate_afr_Level(output['init_afr']['afr_sum'])})

        case "attack_tree":
            at_nodes = get_instances(AttackTree, {'tree_id':tree_id, 'is_deleted':False})
            if at_nodes:
                at_json_tree = build_at_tree_json(at_nodes)
                at_json_tree1 = convert_tree_to_flat_dict(at_json_tree, tree_id)
                output = calculate_afr_values(at_json_tree1, "attack_tree")
                print(f"Attack Tree AFR Output: {output}")
                node = get_first_instance(AttackTree, {'tree_id': tree_id, 'node_type': NodeType.HEAD, 'is_deleted': False})
                if node and output and 'init_afr' in output:
                    update_data = {
                        'af_value': str(output['init_afr']['afr_sum']),
                        'af_level': calculate_afr_Level(output['init_afr']['afr_sum']),
                        'rf_value': '',
                        'rf_level': ''
                    }
                    if output["resid_afr"] is not None:
                        afr_value = output['resid_afr']['afr_sum']
                        if afr_value is not None:
                            rf_text = "0" if str(afr_value) == "inf" else str(afr_value)
                            update_data['rf_value'] = rf_text
                            update_data['rf_level'] = calculate_afr_Level(int(rf_text))
                    
                    update_instance(AttackTree, {'tree_id': tree_id, 'node_type': NodeType.HEAD, 'is_deleted': False}, update_data)

def convert_tree_to_flat_dict(node_data: dict, root_label: str, index: int = 0, counter = None) -> dict:
    if counter is None:
        counter = [index]

    result = {}
    node_id = f"{root_label}_node_{counter[0]}"
    counter[0] += 1

    node_type = node_data.get("node_type", "unknown")

    node_entry = {
        "node_type": node_type,
        "node_id": node_id,
    }

    if "gate" in node_data:
        node_entry["gate"] = node_data["gate"]

    if "values" in node_data:
        node_entry["values"] = node_data["values"]

    if "node_label" in node_data:
        node_entry["node_label"] = node_data["node_label"]

    if "node_Text" in node_data:
        node_entry["node_text"] = node_data["node_Text"]

    children = node_data.get("childrens", [])
    if children:
        node_entry["childrens"] = {}
        for child in children:
            child_tree = convert_tree_to_flat_dict(child, root_label, index, counter)
            node_entry["childrens"].update(child_tree)

    result[node_id] = node_entry
    return result
