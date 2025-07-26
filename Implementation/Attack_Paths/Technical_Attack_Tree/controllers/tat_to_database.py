
from datetime import datetime
from sqlalchemy.orm import Session
from controllers.database_tables.attack_paths_tables import NodeType, ReferenceTrees, TechnicalAttackTree, TechnicalTreeHome
from Attack_Paths.controllers.update_node_into_db import create_or_update_node
from controllers.schema_manager import delete_instance, get_instances, get_first_instance, create_instance, update_instance, delete_all_instance

import logging
logger = logging.getLogger(__name__)


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
    logger.debug(f"[upsert_technical_node] Begin: tree_id={tree_id}, parent_uuid={parent_uuid}, node_id={node_id}, node_type={node_type}")
    active_nodes.add((parent_uuid, node_id))

    # Find node by full triple key (to support reused node_id)
    db_node = get_first_instance(TechnicalAttackTree, {"tree_id": tree_id, "parent_id": parent_uuid, "node_id": node_id})
    logger.debug(f"[upsert_technical_node] get_first_instance returned: {db_node}")

    node_uuid = None
    if node_type != NodeType.HEAD:
        node_uuid = create_or_update_node(node_id, node_type, node_data)
        logger.debug(f"[upsert_technical_node] create_or_update_node result for {node_id}: node_uuid={node_uuid}")
    elif node_type == NodeType.HEAD:
        node = get_first_instance(TechnicalTreeHome, {"id": node_id, "is_deleted": False})
        logger.debug(f"[upsert_technical_node] TechnicalTreeHome lookup for {node_id}: {node}")
        if node: node_uuid = node.uuid

    if not db_node:
        logger.debug(f"[upsert_technical_node] No existing node, creating new TechnicalAttackTree for node_id={node_id}")
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
        logger.debug(f"[upsert_technical_node] Created: {db_node}")
    else:
        logger.debug(f"[upsert_technical_node] Node exists, updating TechnicalAttackTree for uuid={db_node.uuid}")
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

    # Compute af_level and afr_value
    logger.debug(f"[upsert_technical_node] Setting af_value/af_level for uuid={db_node.uuid}")
    update_instance(TechnicalAttackTree, {"uuid": db_node.uuid}, {
        "af_value": node_data.get("af_value", '0') if node_type == NodeType.HEAD else "",
        "af_level": node_data.get("af_level", 'High') if node_type == NodeType.HEAD else ""
    })

    # Recurse on children
    children = node_data.get("childrens", [])
    logger.debug(f"[upsert_technical_node] Node uuid={db_node.uuid} has {len(children)} children")
    for i, child in enumerate(children):
        logger.debug(f"[upsert_technical_node] Recursing to child {i+1}/{len(children)} of node_id={node_id}")
        upsert_technical_node(tree_id, db_node.uuid, child, active_nodes, tree_ref_uuid)

    logger.debug(f"[upsert_technical_node] Finished node_id={node_id}, returning uuid={db_node.uuid}")
    return db_node.uuid


def update_technical_tree(tree_id: str, root_data: dict, tree_ref_uuid: str, active_nodes: set):
    logger.info(f"[update_technical_tree] Deleting all TechnicalAttackTree entries for tree_id={tree_id}")
    delete_all_instance(TechnicalAttackTree, {"tree_id": tree_id})
    logger.info(f"[update_technical_tree] Inserting/updating tree starting from root node_id={root_data.get('node_label')}")
    upsert_technical_node(tree_id, None, root_data, active_nodes, tree_ref_uuid=tree_ref_uuid)
    logger.info(f"[update_technical_tree] Upsert complete for tree_id={tree_id}")
