
from datetime import datetime
from sqlalchemy.orm import Session
from controllers.database_tables.attack_paths_tables import NodeType, AttackIntermediateNodes, AttackLeafNodes
from controllers.schema_manager import get_first_instance, create_instance, update_instance


def create_or_update_node(node_id: str, node_type: NodeType, node_data: dict) -> str:
    """Create or update leaf/intermediate node and return uuid."""
    name = node_data.get("node_Text", f"{node_type.value} node")

    if node_type == NodeType.LEAF:
        return update_leaf_node(node_id=node_id, name=name, node_data=node_data)

    if node_type == NodeType.INTERMEDIATE:
        return update_intermediate_node(node_id=node_id, name=name, node_data=node_data)

    return None

def update_intermediate_node(node_id: str, name: str, node_data: dict) -> str:
    node = get_first_instance(AttackIntermediateNodes, {"id": node_id})
    if not node:
        node = AttackIntermediateNodes(
            id=node_id,
            name=name,
            created_by=""
        )
        create_instance(node)
    else:
        update_instance(AttackIntermediateNodes, {'id': node_id}, {'name': name, 'updated_by': "", 'updated_on': datetime.utcnow()})
    
    return node.uuid

def update_leaf_node(node_id: str, name: str, node_data: dict) -> str:
    values = node_data.get("values", ["0", "0", "0", "0", "0"])
    if len(values) < 5:
        values += ["0"] * (5 - len(values))
    afr_level = node_data.get("af_level", "High")

    leaf = get_first_instance(AttackLeafNodes, {"id": node_id})
    if not leaf:
        leaf = AttackLeafNodes(
            id=node_id,
            name=name,
            time=values[0], expertise=values[1], knowledge=values[2],
            access=values[3], equipment=values[4],
            afr_level=afr_level,
            reasoning="", comments="", created_by=""
        )
        create_instance(leaf)
    else:
        update_instance(AttackLeafNodes, {'id': node_id}, {
            'name': name,
            'time': values[0],
            'expertise': values[1],
            'knowledge': values[2],
            'access': values[3],
            'equipment': values[4],
            'afr_level': afr_level,
            'updated_by': "",
            'updated_on': datetime.utcnow()
        })

    return leaf.uuid
