import logging
from collections import OrderedDict
from controllers.schema_manager import get_instances, get_first_instance, update_instance, create_instance, delete_instance, bulk_update_instances
from controllers.database_tables.analysis_tables import ThreatScenarios

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
    """Flush all changed (not deleted) threat scenario records to DB."""
    updates = []
    for ts_id, entry in THREAT_SCENARIO_CACHE.items():
        if entry['changed'] and not entry['deleted']:
            obj = entry['record']
            updates.append({
                'ts_id': obj.ts_id,
                'threat': obj.threat,
                'damage_scenarios': obj.damage_scenarios,
                'toe_configuration': obj.toe_configuration,
                'reasoning': obj.reasoning,
                'comments': obj.comments,
                'is_deleted': 'False'
            })
            entry['changed'] = False
    if updates:
        bulk_update_instances(ThreatScenario, updates)
        print(f"🔄 Updated {len(updates)} threat scenarios in DB.")

def refresh_threat_scenarios_cache():
    """Force reload the cache from DB."""
    load_all_threat_scenarios()

def delete_threat_scenario(ts_id):
    """Mark as deleted in cache and DB."""
    if ts_id in THREAT_SCENARIO_CACHE:
        THREAT_SCENARIO_CACHE[ts_id]['deleted'] = True
        update_instance(ThreatScenario, {"ts_id": ts_id}, {"is_deleted": "True"})

