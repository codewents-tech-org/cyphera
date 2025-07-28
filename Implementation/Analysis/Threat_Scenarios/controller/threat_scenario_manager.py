import logging
from collections import OrderedDict
from controllers.schema_manager import bulk_insert_instances, get_instances, get_first_instance, update_instance, create_instance, delete_instance, bulk_update_instances
from controllers.database_tables.analysis_tables import ThreatScenarios
import Target_Of_Evaluation.Scope.controllers.scope_synchronizations as TSS
import Analysis.models.analysis_synchronization as AS
logger = logging.getLogger("threat_scenario_manager")

# In-memory cache for ThreatScenario
THREAT_SCENARIO_CACHE = OrderedDict()  # ts_id → {record, changed, deleted}

def load_all_threat_scenarios():
    """Loads all non-deleted threat scenarios, fills the cache, returns list of ORM objects."""
    global THREAT_SCENARIO_CACHE
    THREAT_SCENARIO_CACHE.clear()
    scenarios = get_instances(ThreatScenarios, {'is_deleted': 'False'})
    for obj in scenarios:
        THREAT_SCENARIO_CACHE[obj.ts_id] = {'record': obj, 'changed': False, 'deleted': False}
    return [entry['record'] for entry in THREAT_SCENARIO_CACHE.values()]

def update_threat_scenario(ts_id, updates: dict):
    """Update fields in cache and mark as changed."""
    if ts_id in THREAT_SCENARIO_CACHE:
        obj = THREAT_SCENARIO_CACHE[ts_id]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            THREAT_SCENARIO_CACHE[ts_id]['changed'] = True
        return changed
    return False


def persist_threat_scenario_changes():
    """Flush all changes (insert, update, delete) for threat scenarios to DB."""

    print("🔄 Syncing Threat Scenario changes from cache...")

    updates = []
    inserts = []
    deleted_ids = []

    all_cache_ids = set(THREAT_SCENARIO_CACHE.keys())

    for ts_id, entry in THREAT_SCENARIO_CACHE.items():
        obj = entry['record']
        row = {
            'ts_id': obj.ts_id,
            'threat_id': obj.threat_id,  # ✅ FIXED
            'ds_id': obj.ds_id,          # ✅ FIXED
            'toe_configuration_id': obj.toe_configuration_id,  # ✅ FIXED
            'reasoning': obj.reasoning,
            'comments': obj.comments,
            'is_deleted': 'False',
        }


        if entry.get('deleted'):
            deleted_ids.append(obj.ts_id)
        elif entry.get('is_new'):
            inserts.append(ThreatScenarios(**row))
            entry['is_new'] = False
        elif entry.get('changed'):
            row['uuid'] = obj.uuid
            updates.append(row)
            entry['changed'] = False

    # ✅ Insert new threat scenarios
    if inserts:
        bulk_insert_instances(inserts)
        print(f"✅ Inserted {len(inserts)} threat scenarios.")

    # ✅ Update changed threat scenarios
    if updates:
        bulk_update_instances(ThreatScenarios, updates)
        print(f"🛠️  Updated {len(updates)} threat scenarios.")

    # ✅ Delete removed threat scenarios
    existing_db_ids = {t.ts_id for t in get_instances(ThreatScenarios)}
    to_delete = existing_db_ids - all_cache_ids
    for ts_id in to_delete:
        delete_instance(ThreatScenarios, {'ts_id': ts_id})
    if to_delete:
        print(f"🗑️  Deleted {len(to_delete)} threat scenarios.")

    # ✅ Trash table insert
   
    print("✅ ThreatScenario persistence complete.")


def refresh_threat_scenarios_cache():
    """Force reload the cache from DB."""
    load_all_threat_scenarios()

def delete_threat_scenario(ts_id):
    """Mark as deleted in cache and DB."""
    if ts_id in THREAT_SCENARIO_CACHE:
        THREAT_SCENARIO_CACHE[ts_id]['deleted'] = True
        update_instance(ThreatScenarios, {"ts_id": ts_id}, {"is_deleted": "True"})

