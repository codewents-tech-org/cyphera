import uuid
import logging
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from controllers.schema_manager import (
    get_instances,
    create_instance,
    bulk_update_instances,
    get_max_numeric_suffix,
    get_first_instance
)
from controllers.tablemodel import TOEConfiguration

logger = logging.getLogger(__name__)

# In-memory cache
TOEC_CACHE = {}  # uuid → {'record': model, 'changed': bool, 'deleted': bool}
last_toec_number = None

# ========================== CRUD ==========================

def load_all_toe_configurations():
    """Fetch all non-deleted TOE configurations and populate cache."""
    global TOEC_CACHE
    print("🔄 Loading TOE Configurations from DB...")
    TOEC_CACHE.clear()

    toe_configs = get_instances(TOEConfiguration, {'is_deleted': 'False'})
    if not toe_configs or isinstance(toe_configs, bool):
        logger.warning("⚠️ No TOE records found or DB session failed.")
        return []

    for config in toe_configs:
        TOEC_CACHE[config.uuid] = {
            'record': config,
            'changed': False,
            'deleted': False
        }

    return [entry['record'] for entry in TOEC_CACHE.values()]

def create_toe_configuration(toec_id, name, description="", comments=""):
    """Create a new TOE Configuration and add to cache."""
    new_toec = TOEConfiguration(
        uuid=str(uuid.uuid4()),
        toe_configuration_id=toec_id,
        toe_configuration_name=name,
        toe_configuration_description=description,
        toe_configuration_comments=comments,
        created_by='system',
        updated_by='system',
        is_deleted='False'
    )
    result = create_instance(new_toec)
    if not result:
        logger.error(f"[TOEC] ❌ Failed to create TOE Configuration {toec_id}")
        return None

    full_record = get_first_instance(TOEConfiguration, {"uuid": new_toec.uuid})
    if full_record:
        TOEC_CACHE[new_toec.uuid] = {
            'record': full_record,
            'changed': False,
            'deleted': False
        }
    return full_record

def update_toe_configuration(uuid, updates: dict):
    """Update the TOE Configuration in cache if values changed."""
    if uuid in TOEC_CACHE:
        obj = TOEC_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            TOEC_CACHE[uuid]['changed'] = True
        return changed
    return False

def delete_toe_configuration(uuid):
    """Soft delete a TOE Configuration."""
    if uuid in TOEC_CACHE:
        TOEC_CACHE[uuid]['deleted'] = True
        TOEC_CACHE[uuid]['changed'] = True
        return True
    return False

def persist_toe_configuration_changes():
    """Write all changed TOE configs back to DB."""
    updates = []

    for uuid, entry in TOEC_CACHE.items():
        if not entry['changed']:
            continue
        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': 'True'})
        else:
            updates.append({
                'uuid': uuid,
                'toe_configuration_id': obj.toe_configuration_id,
                'toe_configuration_name': obj.toe_configuration_name,
                'toe_configuration_description': obj.toe_configuration_description,
                'toe_configuration_comments': obj.toe_configuration_comments,
                'updated_by': obj.updated_by,
                'is_deleted': 'False'
            })

        entry['changed'] = False
        
    for u in updates:
        print("📤 TOE Update Payload:", u)


    if updates:
        bulk_update_instances(TOEConfiguration, updates)

# ========================== UI Business Logic ==========================

def create_toe_and_insert_row(self):
    """Create new TOE config and insert it into the UI table."""
    toec_id = generate_new_toec_id()
    name = f"TOE Config {toec_id.split('-')[-1]}"
    record = create_toe_configuration(toec_id, name)
    if not record:
        QMessageBox.critical(None, "Error", f"Could not create TOE Configuration: {toec_id}")
        return

    row_index = self.table.rowCount()
    self.table.insertRow(row_index)
    self.table.setItem(row_index, 1, QTableWidgetItem(record.toe_configuration_id))
    self.table.setItem(row_index, 2, QTableWidgetItem(record.toe_configuration_name))
    self.table.setItem(row_index, 3, QTableWidgetItem(record.toe_configuration_description or ""))
    self.table.setItem(row_index, 4, QTableWidgetItem(record.toe_configuration_comments or ""))
    self.row_uuid_map[row_index] = record.uuid
    self.table.selectRow(row_index)
    self.delete_button.setEnabled(True)
    self.submit_button.setEnabled(True)

def generate_new_toec_id():
    """Generate a unique TOE Configuration ID."""
    global last_toec_number

    if last_toec_number is None:
        last_toec_number = get_max_numeric_suffix(TOEConfiguration, "toe_configuration_id", prefix="TOEC")
        if last_toec_number == 0:
            last_toec_number = 0

    last_toec_number += 1
    return f"TOEC-{last_toec_number}"
