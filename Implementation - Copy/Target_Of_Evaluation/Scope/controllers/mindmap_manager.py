
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from controllers.tablemodel import ScopeHomeMindmap, ScopeMindmaps, MindmapNodeType
from controllers.schema_manager import create_instance, delete_all_instance, bulk_insert_instances
import logging

logger = logging.getLogger(__name__)


def update_mindmap_tree(scope_id: str, root_data: dict):
    updated_data_list = []
    print(scope_id)
    delete_all_instance(ScopeMindmaps, {'scope_id':scope_id})
    
    def upsert_mindmap_node(scope_id: str, parent_uuid: str | None, node_data: dict, updated_data: list[dict]=[]) -> str:
        """Create or update ScopeMindmaps entry and process children recursively."""

        node_uuid = str(uuid.uuid4())
        updated_data.append(
                    ScopeMindmaps(
                        uuid=node_uuid,
                        parent_id=parent_uuid,
                        scope_id=scope_id,
                        level=node_data["level"],
                        node_text=node_data['node_text'],
                        node_desc=node_data['node_desc'],
                        node_type=node_data['node_type'],
                        pos_x=node_data['pos_x'],
                        pos_y=node_data['pos_y'],
                        created_by="system",
                        created_on=datetime.utcnow(),
                        updated_by="system",
                        updated_on=datetime.utcnow(),
                        version="3"
                    )
                )

        # Recurse on children
        for child in node_data.get("children", []):
            upsert_mindmap_node(scope_id, node_uuid, child, updated_data)

    upsert_mindmap_node(scope_id, None, root_data, updated_data_list)
    bulk_insert_instances(updated_data_list)


