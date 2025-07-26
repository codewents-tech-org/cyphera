
from typing import List, Dict
from controllers.tablemodel import MindmapNodeType


def rename_mindmap_node_ids_flat(nodes: List[Dict]) -> List[Dict]:
    """
    Renames UUIDs to formatted node IDs like {scope_id}_node_{counter}.

    Args:
        nodes (List[Dict]): Flat list of node dicts from DB, each with `uuid`, `parent_id`, and `scope_id`.

    Returns:
        List[Dict]: Nodes with transformed `node_id` and `parent_id` fields.
    """
    uuid_to_node_id = {}
    counter_map = {}
    new_node_list = []

    # First pass: assign new node_id to each uuid
    for node in nodes:
        scope_id = node.scope_id
        counter = counter_map.get(scope_id, 0)
        readable_id = f"{scope_id}_node_{counter}"
        uuid_to_node_id[node.uuid] = readable_id
        counter_map[scope_id] = counter + 1
        new_node_list.append({
                'node_id':readable_id,
                'parent_id': node.parent_id,
                'scope_id': scope_id,
                'level': node.level,
                'node_text': node.node_text,
                'node_desc': node.node_desc,
                'node_type': node.node_type.value,
                'pos_x': node.pos_x,
                'pos_y': node.pos_y 
            })

    # Second pass: update parent_id to the new format
    for node in new_node_list:
        original_parent = node.get('parent_id')
        if original_parent in uuid_to_node_id:
            node['parent_id'] = uuid_to_node_id[original_parent]
        elif original_parent:
            node['parent_id'] = None  # or keep as is

    return new_node_list


def rename_attacktree_node_ids_flat(nodes: List[Dict]) -> List[Dict]:
    """
    Renames UUIDs to formatted node IDs like {threat_id}_node_{counter}.

    Args:
        nodes (List[Dict]): Flat list of node dicts from DB, each with `uuid`, `parent_id`, and `threat_id`.

    Returns:
        List[Dict]: Nodes with transformed `node_id` and `parent_id` fields.
    """
    uuid_to_node_id = {}
    counter_map = {}
    new_node_list = []

    # First pass: assign new node_id to each uuid
    for node in nodes:
        threat_id = node.tree_id
        counter = counter_map.get(threat_id, 0)
        readable_id = f"{threat_id}_node_{counter}"
        uuid_to_node_id[node.uuid] = readable_id
        counter_map[threat_id] = counter + 1
        new_node_list.append({
                'uuid':readable_id,
                'parent_id': node.parent_id,
                'tree_id': threat_id,
                'node_id':node.node_id,
                'node_uuid': node.node_uuid,
                'node_type': node.node_type.value,
                'gate': node.gate,
                'af_value': node.af_value,
                'af_level': node.af_level,
                'rf_value': node.rf_value,
                'rf_level': node.rf_level,
                'highlighted':node.highlighted,
                'x': node.x,
                'y': node.y 
            })

    # Second pass: update parent_id to the new format
    for node in new_node_list:
        original_parent = node.get('parent_id')
        if original_parent in uuid_to_node_id:
            node['parent_id'] = uuid_to_node_id[original_parent]
        elif original_parent:
            node['parent_id'] = None  # or keep as is

    return new_node_list

