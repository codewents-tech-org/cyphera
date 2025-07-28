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
    threats = get_instances(Threats, {'is_deleted': False})
    for threat in threats:
        THREAT_CACHE[threat.uuid] = {
            'record': threat,
            'changed': False,
            'deleted': False
        }
        print("threat data",threat.uuid)
    return [entry['record'] for entry in THREAT_CACHE.values()]

def update_threat(uuid, updates: dict):
    """
    Update fields in cache and mark as changed (no DB call yet).
    Returns True if something changed, else False.
    """

    print("🛠️ update_threat() called...")

    if uuid not in THREAT_CACHE:
        print(f"❌ UUID {uuid} not found in THREAT_CACHE.")
        return False

    obj = THREAT_CACHE[uuid]['record']
    changed = False

    # 🧠 Map UI/alias field names to DB model attributes
    field_mapping = {
        'damage_scenarios': 'ds_id',
        'toe_configuration': 'toe_configuration_id',
        'misuse_cases': 'misuse_cases_id',
        'InitialAFR': 'initia_afr',
        'ResidAFR': 'resid_afr',
        'asset': 'asset_id',
    }

    for key, value in updates.items():
        actual_field = field_mapping.get(key, key)  # map or fallback to original
        if not hasattr(obj, actual_field):
            print(f"⚠️ Field '{actual_field}' not found on object 'Threats'")
            continue

        existing_value = getattr(obj, actual_field)
        if existing_value != value:
            print(f"🔄 Updating '{actual_field}': '{existing_value}' → '{value}'")
            setattr(obj, actual_field, value)
            changed = True
        else:
            print(f"🟡 No change for '{actual_field}': remains '{existing_value}'")

    if changed:
        THREAT_CACHE[uuid]['changed'] = True
        print(f"✅ Marked UUID {uuid} as changed.")
    else:
        print(f"🟡 No changes detected for UUID {uuid}.")

    return changed



def persist_threat_changes():
    """
    Saves all changed (and not deleted) threat records in cache to DB (bulk update).
    After save, resets changed flag.
    """
    print("check persist changes-------")
    updates = []
    for uuid, entry in THREAT_CACHE.items():
        print("uuid from the perists chang------",uuid)
        print(f"→ entry['changed']: {entry['changed']} | entry['deleted']: {entry['deleted']}")
        if entry['changed'] and not entry['deleted']:
            obj = entry['record']
            updates.append({
                    'uuid': uuid,
                    'threat_id': obj.threat_id,
                    'name': obj.name,
                    'ds_id': obj.ds_id,
                    'toe_configuration_id': obj.toe_configuration_id,
                    'misuse_cases_id': obj.misuse_cases_id,
                    'initia_afr': obj.initia_afr,
                    'resid_afr': obj.resid_afr,
                    'asset_id': obj.asset_id,
                    'security_properties': obj.security_properties,
                    'reasoning': obj.reasoning,
                    'comments': obj.comments,
                    'is_deleted': False
                })

            print("uuid===========",uuid)
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

