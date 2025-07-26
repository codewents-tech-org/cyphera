import logging
from controllers.schema_manager import (
    get_instances, bulk_update_instances
)
from controllers.tablemodel import Threats
from collections import OrderedDict

logger = logging.getLogger(__name__)

# 🧠 In-memory cache: uuid → {record, changed, deleted}
THREAT_CACHE = OrderedDict()

def load_all_threats():
    """
    Loads all non-deleted threats, fills the cache, and returns a list of Threats ORM objects.
    """
    global THREAT_CACHE
    print("🔄 Loading threats from DB...")
    THREAT_CACHE.clear()
    threats = get_instances(Threats, {'is_deleted': 'False'})
    for threat in threats:
        THREAT_CACHE[threat.uuid] = {
            'record': threat,
            'changed': False,
            'deleted': False
        }
    return [entry['record'] for entry in THREAT_CACHE.values()]

def update_threat(uuid, updates: dict):
    """
    Update fields in cache and mark as changed (no DB call yet).
    Returns True if something changed, else False.
    """
    if uuid in THREAT_CACHE:
        obj = THREAT_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            THREAT_CACHE[uuid]['changed'] = True
        return changed
    return False

def persist_threat_changes():
    """
    Saves all changed (and not deleted) threat records in cache to DB (bulk update).
    After save, resets changed flag.
    """
    updates = []
    for uuid, entry in THREAT_CACHE.items():
        if entry['changed'] and not entry['deleted']:
            obj = entry['record']
            updates.append({
                'uuid': uuid,
                'name': obj.name,
                'damage_scenarios': obj.damage_scenarios,
                'toe_configuration': obj.toe_configuration,
                'misuse_cases': obj.misuse_cases,
                'InitialAFR': obj.InitialAFR,
                'ResidAFR': obj.ResidAFR,
                'asset': obj.asset,
                'security_properties': obj.security_properties,
                'reasoning': obj.reasoning,
                'comments': obj.comments,
                'is_deleted': 'False'
            })
            entry['changed'] = False
    if updates:
        bulk_update_instances(Threats, updates)
        print(f"🔄 Updated {len(updates)} threats in DB.")

def refresh_threats_cache():
    """
    Utility: Force reload the cache from DB (discarding unsaved edits).
    """
    load_all_threats()

# ======================= Example Table UI pattern =======================
# - When you fill your table, use load_all_threats()
# - When user edits: update_threat(uuid, {'field': value, ...})
# - On Save: persist_threat_changes()
# - If you want to force a full reload: refresh_threats_cache()

