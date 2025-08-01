
from datetime import datetime
from sqlalchemy.orm import Session
from controllers.database_tables.attack_paths_tables import NodeType, ReferenceTrees, TechnicalAttackTree, TechnicalTreeHome
from Attack_Paths.controllers.update_node_into_db import create_or_update_node
from controllers.schema_manager import delete_instance, get_instances, get_first_instance, create_instance, update_instance, delete_all_instance


def upsert_technical_node(
    tree_id: str,
    parent_uuid: str | None,
    node_data: dict,
    active_nodes: set[tuple[str | None, str]],
    tree_ref_uuid: str | None
) -> str:
    """Create or update TechnicalAttackTree entry and process children recursively."""
    node_type = NodeType(node_data["node_type"])
    node_id = node_data["node_label"]
    active_nodes.add((parent_uuid, node_id))

    # Find node by full triple key (to support reused node_id)
    db_node = get_first_instance(TechnicalAttackTree, {"tree_id": tree_id, "parent_id": parent_uuid, "node_id": node_id})

    node_uuid = None
    if node_type != NodeType.HEAD:
        node_uuid = create_or_update_node(node_id, node_type, node_data)
    elif node_type == NodeType.HEAD:
        node = get_first_instance(TechnicalTreeHome, {"id": node_id, "is_deleted": False})
        if node: node_uuid = node.uuid

    if not db_node:
        db_node = TechnicalAttackTree(
            tree_id=tree_id,
            parent_id=parent_uuid,
            node_id=node_id,
            node_uuid=node_uuid,
            tree_ref_uuid=tree_ref_uuid,
            node_type=node_type,
            gate=node_data.get("gate", ""),
            highlighted=node_data.get("selected_path", False),
            x=node_data.get("x", 0),
            y=node_data.get("y", 0),
            created_by="",
            created_on=datetime.utcnow(),
            is_deleted=False,
            is_latest=True
        )
        create_instance(db_node)
    else:
        update_instance(TechnicalAttackTree, {"uuid":db_node.uuid}, {
            "parent_id": parent_uuid,
            "node_uuid": node_uuid,
            "tree_ref_uuid": tree_ref_uuid,
            "node_type": node_type,
            "gate": node_data.get("gate", ""),
            "highlighted": node_data.get("selected_path", False),
            "x": node_data.get("x", 0),
            "y": node_data.get("y", 0),
            "updated_by": "",
            "updated_on": datetime.utcnow(),
            "is_latest": True,
            "is_deleted": False
        })

    # # Compute af_level and afr_value
    update_instance(TechnicalAttackTree, {"uuid": db_node.uuid}, {
        "af_value": node_data.get("af_value", '0') if node_type == NodeType.HEAD else "",
        "af_level": node_data.get("af_level", 'High') if node_type == NodeType.HEAD else ""
    })

    # Recurse on children
    for child in node_data.get("childrens", []):
        upsert_technical_node(tree_id, db_node.uuid, child, active_nodes, tree_ref_uuid)

    return db_node.uuid

def update_technical_tree(tree_id: str, root_data: dict, tree_ref_uuid: str, active_nodes: set):
    delete_all_instance(TechnicalAttackTree, {"tree_id": tree_id})
    upsert_technical_node(tree_id, None, root_data, active_nodes, tree_ref_uuid=tree_ref_uuid)

