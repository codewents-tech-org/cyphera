import uuid
from controllers.schema_manager import (
    get_instances, create_instance, bulk_update_instances, get_max_numeric_suffix,get_first_instance
)
from controllers.tablemodel import Misusecases
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import logging

logger = logging.getLogger(__name__)

# In-memory cache of misuse cases
MISUSE_CASE_CACHE = {}

# Global counter for generating new IDs
last_misusecase_number = None

def generate_new_misusecase_id():
    global last_misusecase_number
    if last_misusecase_number is None:
        last_misusecase_number = get_max_numeric_suffix(Misusecases, "misuse_cases_id", prefix="MUC")
    last_misusecase_number += 1
    return f"MUC-{last_misusecase_number}"

def load_all_misusecases():
    logger.info("🔄 Loading misuse cases from DB...")
    MISUSE_CASE_CACHE.clear()

    rows = get_instances(Misusecases, {'is_deleted': 'False'})
    for r in rows:
        MISUSE_CASE_CACHE[r.uuid] = {'record': r, 'changed': False, 'deleted': False}

    return [entry['record'] for entry in MISUSE_CASE_CACHE.values()]

def create_misusecase(misusecase_id, name, comments=""):
    misusecase = Misusecases(
        uuid=str(uuid.uuid4()),
        misuse_cases_id=misusecase_id,
        misuse_cases_name=name,
        misuse_cases_comments=comments,
        created_by='system',
        updated_by='system',
        is_deleted='False'
    )
    result = create_instance(misusecase)
    if not result:
        logger.error(f"❌ Failed to create misuse case {misusecase_id}")
        return None
    
    full_record = get_first_instance(Misusecases, {"uuid": misusecase.uuid})
    if not full_record:
        logger.error(f"❌ Could not fetch newly created misuse case {misusecase_id}")
        return None


    MISUSE_CASE_CACHE[misusecase.uuid] = {'record': misusecase, 'changed': False, 'deleted': False}
    return full_record

def update_misusecase(uuid, updates: dict):
    if uuid in MISUSE_CASE_CACHE:
        obj = MISUSE_CASE_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            MISUSE_CASE_CACHE[uuid]['changed'] = True
        return changed
    return False

def delete_misusecase(uuid):
    if uuid in MISUSE_CASE_CACHE:
        MISUSE_CASE_CACHE[uuid]['deleted'] = True
        MISUSE_CASE_CACHE[uuid]['changed'] = True
        return True
    return False

def persist_misusecase_changes():
    updates = []
    for uuid, entry in MISUSE_CASE_CACHE.items():
        if not entry['changed']:
            continue
        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': 'True'})
        else:
            updates.append({
                'uuid': uuid,
                'misuse_cases_id': obj.misuse_cases_id,
                'misuse_cases_name': obj.misuse_cases_name,
                'misuse_cases_comments': obj.misuse_cases_comments,
                'updated_by': obj.updated_by,
                'is_deleted': 'False'
            })
        entry['changed'] = False

    if updates:
        bulk_update_instances(Misusecases, updates)

def create_misusecase_and_insert_row(self):
    misusecase_id = generate_new_misusecase_id()
    name = f"Misuse Case {misusecase_id.split('-')[-1]}"
    misusecase = create_misusecase(misusecase_id, name)

    if not misusecase:
        QMessageBox.critical(None, "Error", f"Misuse Case with ID '{misusecase_id}' already exists.")
        return

    row_index = self.table.rowCount()
    self.table.insertRow(row_index)
    self.table.setItem(row_index, 1, QTableWidgetItem(misusecase.misuse_cases_id))
    self.table.setItem(row_index, 2, QTableWidgetItem(misusecase.misuse_cases_name))
    self.table.setItem(row_index, 3, QTableWidgetItem(misusecase.misuse_cases_comments or ""))

    if not hasattr(self, "row_uuid_map"):
        self.row_uuid_map = {}
    self.row_uuid_map[row_index] = misusecase.uuid

    self.table.selectRow(row_index)
    self.delete_button.setEnabled(True)
    self.submit_button.setEnabled(True)
    for row in range(self.table.rowCount()):
        for col in range(1, 4):
            item = self.table.item(row, col)
            print(f"[Row {row}, Col {col}] = {item.text() if item else 'None'}")
