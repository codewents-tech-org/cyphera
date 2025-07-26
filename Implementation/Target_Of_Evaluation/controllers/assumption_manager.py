import uuid
from controllers.schema_manager import get_instances, create_instance, update_instance, bulk_update_instances, get_max_numeric_suffix
from controllers.tablemodel import Assumptions
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import logging

logger = logging.getLogger(__name__)

# In-memory cache of assumptions
ASSUMPTION_CACHE = {}

# Global counter for generating new IDs
last_assumption_number = None

def generate_new_assumption_id():
    global last_assumption_number
    if last_assumption_number is None:
        last_assumption_number = get_max_numeric_suffix(Assumptions, "assumption_id", prefix="ASSUM")
    last_assumption_number += 1
    return f"ASSUM-{last_assumption_number}"

def load_all_assumptions():
    logger.info("🔄 Loading assumptions from DB...")
    ASSUMPTION_CACHE.clear()

    rows = get_instances(Assumptions, {'is_deleted': 'False'})
    for r in rows:
        ASSUMPTION_CACHE[r.uuid] = {'record': r, 'changed': False, 'deleted': False}

    return [entry['record'] for entry in ASSUMPTION_CACHE.values()]

def create_assumption(assumption_id, name, comments=""):
    assumption = Assumptions(
        uuid=str(uuid.uuid4()),
        assumption_id=assumption_id,
        assumptions=name,
        comments=comments,
        created_by='system',
        updated_by='system',
        is_deleted='False'
    )
    result = create_instance(assumption)
    if not result:
        logger.error(f"❌ Failed to create assumption {assumption_id}")
        return None

    ASSUMPTION_CACHE[assumption.uuid] = {'record': assumption, 'changed': False, 'deleted': False}
    return result

def update_assumption(uuid, updates: dict):
    if uuid in ASSUMPTION_CACHE:
        obj = ASSUMPTION_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            ASSUMPTION_CACHE[uuid]['changed'] = True
        return changed
    return False

def delete_assumption(uuid):
    if uuid in ASSUMPTION_CACHE:
        ASSUMPTION_CACHE[uuid]['deleted'] = True
        ASSUMPTION_CACHE[uuid]['changed'] = True
        return True
    return False

def persist_assumption_changes():
    updates = []
    for uuid, entry in ASSUMPTION_CACHE.items():
        if not entry['changed']:
            continue
        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': 'True'})
        else:
            updates.append({
                'uuid': uuid,
                'assumption_id': obj.assumption_id,
                'assumptions': obj.assumptions,
                'comments': obj.comments,
                'updated_by': obj.updated_by,
                'is_deleted': 'False'
            })
        entry['changed'] = False

    if updates:
        bulk_update_instances(Assumptions, updates)

def create_assumption_and_insert_row(self):
    assumption_id = generate_new_assumption_id()
    name = f"Assumption {assumption_id.split('-')[-1]}"
    assumption = create_assumption(assumption_id, name)

    if not assumption:
        QMessageBox.critical(None, "Error", f"Assumption with ID '{assumption_id}' already exists.")
        return

    row_index = self.table.rowCount()
    self.table.insertRow(row_index)
    self.table.setItem(row_index, 1, QTableWidgetItem(assumption.assumption_id))
    self.table.setItem(row_index, 2, QTableWidgetItem(assumption.assumptions))
    self.table.setItem(row_index, 3, QTableWidgetItem(assumption.comments or ""))

    if not hasattr(self, "row_uuid_map"):
        self.row_uuid_map = {}
    self.row_uuid_map[row_index] = assumption.uuid

    self.table.selectRow(row_index)
    self.delete_button.setEnabled(True)
    self.submit_button.setEnabled(True)
