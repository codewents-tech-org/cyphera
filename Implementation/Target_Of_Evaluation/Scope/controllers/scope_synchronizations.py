

from controllers.schema_manager import (
                                            delete_all_instance, 
                                            update_instance, 
                                            get_first_instance, 
                                            create_instance, 
                                            get_max_numeric_suffix,
                                            get_instances
                                        )
from controllers.tablemodel import ScopeHomeMindmap, MindmapNodeType, ScopeMindmaps, ScopesReference, Assets, Threats
import Analysis.models.analysis_synchronization as AS
from Target_Of_Evaluation.Scope.Scope_MindMap.mindmap_at_generator import mindmap_attacktree_generator

import uuid
import datetime
import logging


logger = logging.getLogger(__name__)


def remove_mindmaps(delete_scope_list):
    # 🧹 Synchronization from scope to mindmap
    for scope_id in delete_scope_list:
        try:
            delete_all_instance(ScopeMindmaps, {'scope_id': scope_id})
            logger.debug(f"🗑️ Deleted ScopeMindmaps with scope_id = {scope_id}")
        except Exception as e:
            logger.exception(f"❌ Failed to delete ScopeMindmaps for scope_id = {scope_id}: {e}")

def update_mindmaps_name(updated_scope_dict):
    # 🧹 Synchronization from scope to mindmap
    for scope_id, scope_name in updated_scope_dict.items():
        try:
            update_instance(ScopeMindmaps, {'scope_id': scope_id, 'node_type': MindmapNodeType.HEAD}, {'node_text': scope_name})
            logger.debug(f"🗑️ Deleted ScopeMindmaps with scope_id = {scope_id}")
        except Exception as e:
            logger.exception(f"❌ Failed to delete ScopeMindmaps for scope_id = {scope_id}: {e}")

from Analysis.controllers.asset_manager import (
    generate_new_asset_id,
    add_new_asset,
    refresh_assets_cache,
    update_asset,
    ASSET_CACHE,
    persist_asset_changes
)

def synch_mindmap_changes(scope_id, scope_name):
    logger.info("🔄 Updating scope name from mindmap")
    try:
        asset_id = ''
        threat_ids = []

        # Update scope name in mindmap and scope reference
        update_instance(ScopeHomeMindmap, {'scope_id': scope_id}, {'scope_name': scope_name})
        scope_instance = get_first_instance(ScopesReference, {'scope_id': scope_id})

        if scope_instance:
            update_instance(ScopesReference, {'scope_id': scope_id}, {'scope_name': scope_name})

            if scope_instance.asset_id:
                asset_id = scope_instance.asset_id
                if scope_instance.threat_id:
                    mindmap_attacktree_generator(scope_id, scope_name)
                else:
                    update_threat_data(scope_id, asset_id)
            else:
                # No asset linked → create one
                asset_id = create_asset_record(scope_name)
                AS.sync_threats_with_assets()
                update_threat_data(scope_id, asset_id)

        else:
            # No ScopesReference → create new
            instance = ScopesReference(
                uuid=str(uuid.uuid4()),
                scope_id=scope_id,
                scope_name=scope_name,
                asset_id='',
                threat_id='',
                created_by="system"
            )
            create_instance(instance)

            asset_id = create_asset_record(scope_name)
            AS.sync_threats_with_assets()
            update_threat_data(scope_id, asset_id)

    except Exception as e:
        logger.error(f"Error occurred in synch_mindmap_changes: {e}")

def create_asset_record(scope_name):
    asset_id = f"AST-{get_max_numeric_suffix(Assets, 'asset_id', 'AST')+1}"
    asset_instance = Assets(
            asset_id=asset_id,
            name=scope_name,
            security_properties= '',
            description='',
            comments='',
            created_by='system'
        )
    create_instance(asset_instance)
   
    refresh_assets_cache()
    return asset_id

def update_threat_data(scope_id, asset_id):
    threat_ids = []
    threat_instances = get_instances(Threats, {'asset_id':asset_id})
    for threat in threat_instances:
        if threat.threat_id not in threat_ids: threat_ids.append(threat.threat_id)
    print(f"{scope_id} : {asset_id} : {threat_ids}")
    update_instance(ScopesReference, {'scope_id':scope_id}, {'asset_id':asset_id, 'threat_id': ", ".join(threat_ids)})

    return asset_id

def sync_linked_modules():
    AS.update_threatscenario_from_threat()
    AS.update_risktreatement_data()
    AS.remove_orphaned_attack_tree_rows()
    AS.update_attack_tree_text()
    AS.sync_attack_tree_with_threats()
    AS.remove_nonexistent_threat_scenarios_from_Risk_data()