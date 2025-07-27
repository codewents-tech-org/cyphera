
from controllers.tablemodel import AttackIntermediateNodes, AttackLeafNodes, RiskControlTree, TechnicalAttackTree
from controllers.schema_manager import get_instances, get_max_numeric_suffix, get_first_instance
from Attack_Paths.RiskControl_Tree.controllers.database_to_rct import build_rc_tree_json
from Attack_Paths.Technical_Attack_Tree.controllers.database_to_tat import build_ta_tree_json


def get_intermediate_node_id(self, last_id=0):
    self.last_intermediate_node_id = last_id+1
    # Return the next node label in the format 'Nd-<number>'
    return f'Nd-{self.last_intermediate_node_id}' if self.last_intermediate_node_id is not None else 'Nd-1'

def get_leaf_node_id(self, last_id=0, leaf_id=None):
    if leaf_id is not None:
        node = get_first_instance(AttackLeafNodes, {'id': leaf_id, 'is_deleted': False})
        if node:
            leaf = {"node_label":node.id, "node_Text": node.name, "af_level": node.afr_level}
            values = [node.time, node.expertise, node.knowledge, node.access, node.equipment]
            if not values:
                values = ['0', '0', '0', '0', '0']
            leaf["values"] = values
            af_value = str(sum(map(int, values))) if values else "0"
            leaf["af_value"] = af_value
            return leaf
        else:
            self.last_leaf_node_id = last_id+1
            return {"node_label": f'Lf-{self.last_leaf_node_id}', "node_Text": "Leaf Node Text", "values": ['0', '0', '0', '0', '0'], "af_value": "0", "af_level": "High"}

    else:
        self.last_leaf_node_id = last_id+1
        return {"node_label": f'Lf-{self.last_leaf_node_id}', "node_Text": "Leaf Node Text", "values": ['0', '0', '0', '0', '0'], "af_value": "0", "af_level": "High"}

def get_import_tree(tree_type: str, tree_id: str):
    print(f"get_import_tree called with tree_type: {tree_type}, tree_id: {tree_id}")
    match tree_type:
        case 'RiskControlTree':
            rc_nodes = get_instances(RiskControlTree, {'tree_id': tree_id, 'is_deleted': False})
            print(f"Risk Control Tree Nodes: {rc_nodes}")
            if rc_nodes:
                rc_json_tree = build_rc_tree_json(rc_nodes)
                return rc_json_tree
            else:
                return {}
        case 'TechnicalTree':
            ta_nodes = get_instances(TechnicalAttackTree, {'tree_id': tree_id, 'is_deleted': False})
            print(f"Technical Attack Tree Nodes: {ta_nodes}")
            if ta_nodes:
                ta_json_tree = build_ta_tree_json(ta_nodes)
                return ta_json_tree
            else:
                return {}
        case _:
            return {}
