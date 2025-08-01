import uuid
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from controllers.schema_manager import (
    create_instance, get_instances, get_first_instance,
    delete_all_instance, bulk_update_instances, get_max_numeric_suffix
)
from controllers.database_tables.analysis_tables import DamageScenarios  # Your ORM model
import Analysis.models.analysis_synchronization as AS
import logging

logger = logging.getLogger(__name__)

# 🧠 In-memory cache (uuid → {'record': obj, 'changed': bool, 'deleted': bool})
DAMAGE_SCENARIO_CACHE = {}
last_ds_number = None

# ==================== CRUD OPERATIONS ====================
def load_all_damage_scenarios():
    """Fetch all non-deleted damage scenarios and populate cache."""
    global DAMAGE_SCENARIO_CACHE
    DAMAGE_SCENARIO_CACHE.clear()

    scenarios = get_instances(DamageScenarios, {'is_deleted': 'False'})
    for ds in scenarios:
        DAMAGE_SCENARIO_CACHE[ds.uuid] = {
            'record': ds,
            'changed': False,
            'deleted': False
        }
    return [entry['record'] for entry in DAMAGE_SCENARIO_CACHE.values()]

def create_damage_scenario(ds_id, name, impact, impact_category, desc="", comments=""):
    ds = DamageScenarios(
        uuid=str(uuid.uuid4()),
        ds_id=ds_id,
        name=name,
        impact=impact,
        impact_category=impact_category,
        description=desc,
        comments=comments,
        created_by="system",
        updated_by="system",
        is_deleted="False"
    )
    ds = create_instance(ds)
    if not ds:
        print(f"[ERROR] Failed to create Damage Scenario with ID: {ds_id}")
        return None
    DAMAGE_SCENARIO_CACHE[ds.uuid] = {
        "record": ds,
        "changed": False,
        "deleted": False
    }
    return ds

def update_damage_scenario(uuid, updates: dict):
    """Update in cache only if values changed."""
    if uuid in DAMAGE_SCENARIO_CACHE:
        obj = DAMAGE_SCENARIO_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            DAMAGE_SCENARIO_CACHE[uuid]['changed'] = True
        return changed
    return False

def delete_damage_scenario(uuid):
    """Soft delete."""
    if uuid in DAMAGE_SCENARIO_CACHE:
        DAMAGE_SCENARIO_CACHE[uuid]['deleted'] = True
        DAMAGE_SCENARIO_CACHE[uuid]['changed'] = True
        return True
    return False

def persist_damage_scenario_changes():
    """Efficiently persist changed and deleted records."""
    updates = []
    for uuid, entry in DAMAGE_SCENARIO_CACHE.items():
        if not entry['changed']:
            continue
        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': 'True'})
        else:
            updates.append({
                'uuid': uuid,
                'ds_id': obj.ds_id,
                'name': obj.name,
                'impact': obj.impact,
                'impact_category': obj.impact_category,
                'description': obj.description,
                'comments': obj.comments,
                'updated_by': obj.updated_by,
                'is_deleted': 'False'
            })
        entry['changed'] = False  # reset
    if updates:
        bulk_update_instances(DamageScenarios, updates)

        AS.update_threat_TS_from_DS()
        AS.update_risktreatement_data()

# ==================== UI-BUSINESS LOGIC ====================

def create_damage_scenario_and_insert_row(self):
    """Create new scenario, add to table."""
    ds_id = generate_new_ds_id()
    ds_name = f"Damage Scenario {ds_id.split('-')[-1]}"
    ds = create_damage_scenario(ds_id, ds_name, impact="", impact_category="")
    if ds is None:
        QMessageBox.critical(None, "Error", f"Damage Scenario with ID '{ds_id}' already exists. Please try again.")
        return
    row_index = self.table.rowCount()
    self.table_wrapper.insert_row([
        ds.ds_id, ds.name, ds.impact, ds.impact_category, ds.description, ds.comments
    ])
    self.row_uuid_map[row_index] = ds.uuid
    self.delete_button.setEnabled(True)
    self.submit_button.setEnabled(True)
    self.table.selectRow(row_index)

def generate_new_ds_id():
    global last_ds_number
    if last_ds_number is None:
        last_ds_number = get_max_numeric_suffix(DamageScenarios, "ds_id", prefix="DS")
        if last_ds_number == 0:
            last_ds_number = 0
    last_ds_number += 1
    return f"DS-{last_ds_number}"
