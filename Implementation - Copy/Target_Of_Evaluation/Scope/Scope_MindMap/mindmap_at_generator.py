

from controllers.schema_manager import get_instances, update_instance, get_first_instance, create_instance, get_max_numeric_suffix, bulk_insert_instances, delete_all_instance
from controllers.tablemodel import NodeType, MindmapNodeType, ScopeMindmaps, ScopesReference, AttackIntermediateNodes, AttackLeafNodes, AttackTree, AttackTreeHome, ReferenceTrees
from Target_Of_Evaluation.Scope.Scope_MindMap.tree_id_converter import rename_mindmap_node_ids_flat, rename_attacktree_node_ids_flat
from Attack_Paths.controllers.backend_afr_calculator import update_afr

import uuid
import datetime
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def build_tree_json(nodes: List[Dict[str, Any]]):
    lookup = {node["node_id"]: {**node, "children": []} for node in nodes}
    root_nodes = []

    for node in nodes:
        node_id = node["node_id"]
        parent_id = node.get("parent_id")

        if parent_id and parent_id in lookup:
            lookup[parent_id]["children"].append(lookup[node_id])
        else:
            root_nodes.append(lookup[node_id])

    return root_nodes

def generate_new_node_id(node_type):
    sufix = ''
    last_scope_number = 0
    match node_type:
        case MindmapNodeType.INTERMEDIATE:
            sufix = 'Nd'
            last_scope_number = get_max_numeric_suffix(AttackIntermediateNodes, "id", prefix=sufix)
        case MindmapNodeType.LEAF:
            sufix = 'Lf'
            last_scope_number = get_max_numeric_suffix(AttackLeafNodes, "id", prefix=sufix)
        case _:
            pass

    last_scope_number += 1
    return f"{sufix}-{last_scope_number}"

def create_node(node_type: MindmapNodeType, name: str) -> str:
    is_created = False
    is_valid_values = False
    node_id = None
    match node_type:
        case MindmapNodeType.INTERMEDIATE:
            node = get_first_instance(AttackIntermediateNodes, {'name':name})
            if not node:
                node_id = generate_new_node_id(MindmapNodeType.INTERMEDIATE)
                node = AttackIntermediateNodes(
                    id=node_id,
                    name=name,
                    created_by="system"
                )
                create_instance(node)
                creis_createdated = True
            else:
                node_id = node.id
        case MindmapNodeType.LEAF:
            node = get_first_instance(AttackLeafNodes, {'name':name})
            if not node:
                node_id = generate_new_node_id(MindmapNodeType.LEAF)
                node = AttackLeafNodes(
                    id=node_id, name=name,
                    time='0', expertise='0', knowledge='0', access='0', equipment='0',
                    afr_level='High', reasoning="", comments="", created_by=""
                )
                create_instance(node)
                is_created = True
            else:
                values = [node.time, node.expertise, node.knowledge, node.access, node.equipment]
                afr_value = sum(map(int, values))
                if afr_value > 0: is_valid_values = True
                node_id = node.id
        case _:
            pass
    return is_created, is_valid_values, node_id

def create_mindmap_attack_tree(mind_map_nodes, scope_id='', threat_id=''):
    if mind_map_nodes:
        for instance in mind_map_nodes:
            instance['node_id'].replace(scope_id, threat_id)
            instance['parent_id'].replace(scope_id, threat_id)
    
    return mind_map_nodes

def build_attack_tree(trees_data):
    attack_tree_datas = {}
    for tree_data in trees_data:
        attack_tree_datas[tree_data['parent_id']] = tree_data
    return attack_tree_datas

def update_attacktree_datas(mind_map_nodes, new_tree=True, attack_tree_data=[], threat_id=''):
    attack_tree_nodes=[]
    if attack_tree_data: attack_tree_data = build_attack_tree(attack_tree_data)
    if mind_map_nodes:
        for instance in mind_map_nodes:
            scope_id = instance['scope_id']
            node_label = instance['node_label'] if instance['node_label'] else threat_id
            node_data ={
                "node_id": instance['node_id'].replace(scope_id, threat_id),
                "parent_id": instance['parent_id'].replace(scope_id, threat_id) if instance['parent_id'] else None,
                "tree_id": threat_id,
                "node_type": instance['node_type'].lower(),
                "node_label": node_label,
                "gate": '',
                "x": 0,
                "y": 0,
                "af_value":"",
                "af_level":"",
                "rf_value":"",
                "rf_level":"",
                "created_by": 'system',
                "selected_path": False
                }
            
            match instance['node_type']:
                case 'INTERMEDIATE':
                    node = get_first_instance(AttackIntermediateNodes, {'id':node_label})
                    if node: node_data["node_uuid"] = node.uuid
                    node_data["gate"] = "AND"
                    if not new_tree:
                        if (node_data["parent_id"] in attack_tree_data and 
                            node_data["node_id"] == attack_tree_data[node_data["parent_id"]]["uuid"] and 
                            node_data["node_label"] == attack_tree_data[node_data["parent_id"]]["node_id"]):
                            node_data["gate"] = attack_tree_data[node_data["parent_id"]]["gate"] if attack_tree_data[node_data["parent_id"]]["gate"] != '' else 'AND'
                
                case 'LEAF':
                    node = get_first_instance(AttackLeafNodes, {'id':node_label})
                    if node: node_data["node_uuid"] = node.uuid
                
                case 'HEAD':
                    node = get_first_instance(AttackTreeHome, {'id':node_label})
                    if node: node_data["node_uuid"] = node.uuid
                    node_data["gate"] = "AND"
                    node_data["af_value"] = "0"
                    node_data["af_level"] = "High"
                    node_data["rf_value"] = ""
                    node_data["rf_level"] = ""
                    if not new_tree:
                        if (node_data["parent_id"] in attack_tree_data and 
                            node_data["node_id"] == attack_tree_data[node_data["parent_id"]]["uuid"] and 
                            node_data["node_label"] == attack_tree_data[node_data["parent_id"]]["node_id"]):
                            node_data["gate"] = attack_tree_data[node_data["parent_id"]]["gate"] if attack_tree_data[node_data["parent_id"]]["gate"] != '' else 'AND'
                case _:
                    pass
            attack_tree_nodes.append(node_data)
    
    return attack_tree_nodes

def generate_attack_tree(attak_tree, tree_id):
    ref_tree = get_first_instance(ReferenceTrees, {"id": tree_id, "is_deleted": False})
    if ref_tree is None:
        ref_tree = ReferenceTrees(id=tree_id, created_by="system")
        create_instance(ref_tree)

    ref_tree = get_first_instance(ReferenceTrees, {"id": tree_id, "is_deleted": False})
    ref_uuid = ref_tree.uuid if ref_tree else None  # ✅ UNPACK THE TUPLE

    def upsert_attack_node(parent_uuid, node_data, tree_ref_uuid, updated_attack_tree):
        try:
            node_id = node_data["node_label"]
            node_type=node_data['node_type']
            match node_data['node_type']:
                case 'head': node_type = NodeType.HEAD
                case 'intermediate': node_type = NodeType.INTERMEDIATE
                case 'leaf': node_type = NodeType.LEAF
            node_uuid = str(uuid.uuid4())
            
            instance = AttackTree(
                            uuid=node_uuid,
                            parent_id=parent_uuid,
                            tree_id=node_data['tree_id'],
                            node_id=node_id,
                            node_uuid=node_data.get("node_uuid", ""),
                            tree_ref_uuid=tree_ref_uuid,
                            node_type=node_type,
                            gate=node_data['gate'],
                            af_value=node_data.get("af_value", "0"),
                            af_level=node_data.get("af_level", "High"),
                            rf_value=node_data.get("rf_value", ""),
                            rf_level=node_data.get("rf_level", ""),
                            highlighted=node_data.get("selected_path", False),
                            x=int(node_data.get("x", 0)),
                            y=int(node_data.get("y", 0)),
                            created_by="system",
                            is_deleted=False,
                            is_latest=True
                        )
            
            updated_attack_tree.append(instance)
            # Recurse on children
            for child in node_data.get("children", []):
                upsert_attack_node(node_uuid, child, tree_ref_uuid, updated_attack_tree)

            return node_uuid
    
        except Exception as e:
            print(f"Error occurred: {e}")

    delete_all_instance(AttackTree, {"tree_id": tree_id})
    updated_attack_tree = []
    root_data = {}
    if isinstance(attak_tree, list):
        root_data = attak_tree[0] 
    elif isinstance(attak_tree, dict):
        root_data = attak_tree
    
    upsert_attack_node(None, root_data, tree_ref_uuid=ref_uuid, updated_attack_tree=updated_attack_tree)
    bulk_insert_instances(updated_attack_tree)

def mindmap_attacktree_generator(scope_id, scope_name):
    logger.info("auto-generation attack tree from mindmap.")
    try:
        scope_instance = get_first_instance(ScopesReference, {'scope_id':scope_id})
        if scope_instance:
            
            if not scope_instance.threat_id:
                logger.info("No threats found to auto-generation attack tree from mindmap.")
                return
            
            threats = [t.strip() for t in scope_instance.threat_id.split(',')]

            mind_map_nodes = get_instances(ScopeMindmaps, {'scope_id':scope_id})
            mind_map_nodes = rename_mindmap_node_ids_flat(mind_map_nodes)

            if mind_map_nodes:
                is_afr_calc_enable = False
                for instance in mind_map_nodes:
                    node_id = None
                    match instance['node_type']:
                        case 'INTERMEDIATE':
                            is_created, is_valid_values, node_id = create_node(MindmapNodeType.INTERMEDIATE, instance['node_text'])
                        case 'LEAF':
                            is_created, is_valid_values, node_id = create_node(MindmapNodeType.LEAF, instance['node_text'])
                            if not is_created and is_valid_values and not is_afr_calc_enable:
                                is_afr_calc_enable = True
                        case _:
                            pass
                    instance['node_label'] = node_id
            
            for threat in threats:
                attack_tree_nodes = get_instances(AttackTree, {'tree_id':threat})
                if attack_tree_nodes:
                    attack_tree_nodes = rename_attacktree_node_ids_flat(attack_tree_nodes)
                    attack_tree_nodes = update_attacktree_datas(mind_map_nodes, False if attack_tree_nodes else True, attack_tree_nodes, threat)
                    attack_tree = build_tree_json(attack_tree_nodes)
                    generate_attack_tree(attack_tree, threat)
                else:
                    attack_tree_nodes = update_attacktree_datas(mind_map_nodes, False if attack_tree_nodes else True, [], threat)
                    attack_tree = build_tree_json(attack_tree_nodes)
                    generate_attack_tree(attack_tree, threat)
            
            if is_afr_calc_enable:
                for threat in threats:
                    update_afr(threat, "attack_tree")

    except Exception as e:
        print(f"Error occurred: {e}")



