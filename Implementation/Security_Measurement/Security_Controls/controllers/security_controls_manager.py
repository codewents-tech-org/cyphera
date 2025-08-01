import uuid
import logging
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from controllers.schema_manager import (
    create_instance, get_instances, bulk_update_instances, get_max_numeric_suffix
)
from controllers.tablemodel import SecurityControls
import Analysis.models.analysis_synchronization as AS

logger = logging.getLogger(__name__)

# 🧠 In-memory cache
SECURITY_CONTROLS_CACHE = {}  # uuid -> {'record': model, 'changed': False, 'deleted': False}
last_scc_number = None

# ========================== CRUD FUNCTIONS ==========================

def load_all_security_controls():
    """Load all non-deleted SecurityControls into memory cache."""
    global SECURITY_CONTROLS_CACHE
    logger.info("🔄 Loading SecurityControls from DB...")
    SECURITY_CONTROLS_CACHE.clear()

    rows = get_instances(SecurityControls, {'is_deleted': False})  # Correct: Boolean False
    logger.info(f"✔️ Loaded {len(rows)} SecurityControls from DB")
    for row in rows:
        SECURITY_CONTROLS_CACHE[row.uuid] = {
            'record': row,
            'changed': False,
            'deleted': False
        }

    return [entry['record'] for entry in SECURITY_CONTROLS_CACHE.values()]


def create_security_control(scc_id, name, security_goal_id, description, comments):
    control = SecurityControls(
        uuid=str(uuid.uuid4()),
        scc_id=scc_id,
        name=name,
        security_goal_id=security_goal_id,  # <-- Include it here
        description=description,
        comments=comments,
        created_by="system",
        updated_by="system",
        is_deleted=False
    )

    created = create_instance(control)
    if created:
        SECURITY_CONTROLS_CACHE[created.uuid] = {
            'record': created,
            'changed': False,
            'deleted': False
        }
        return created
    else:
        logger.error(f"[❌] Failed to create Security Control {scc_id}")
        return None


def update_security_control(uuid, updates: dict):
    """Update a SecurityControl in the cache if values differ."""
    if uuid in SECURITY_CONTROLS_CACHE:
        obj = SECURITY_CONTROLS_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            SECURITY_CONTROLS_CACHE[uuid]['changed'] = True
        return changed
    return False


def delete_security_control(uuid):
    """Soft delete the SecurityControl by marking is_deleted=True in cache."""
    if uuid in SECURITY_CONTROLS_CACHE:
        SECURITY_CONTROLS_CACHE[uuid]['deleted'] = True
        SECURITY_CONTROLS_CACHE[uuid]['changed'] = True
        return True
    return False


def persist_security_control_changes():
    """Persist all changed/deleted SecurityControls to the DB."""
    updates = []
    print("----------------step3----------------")

    for uuid, entry in SECURITY_CONTROLS_CACHE.items():
        if not entry['changed']:
            continue

        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': 'True'})
            print("----------------step5----------------")
        else:
            updates.append({
                'uuid': uuid,
                'name': obj.name,
                'description': obj.description,
                'comments': obj.comments,
                'security_goal_id': obj.security_goal_id,
                'updated_by': obj.updated_by,
                'is_deleted': 'False'
            })
            print("----------------step6----------------")

        entry['changed'] = False  # Reset flag
        print("----------------step7----------------")

    if updates:
        logger.info(f"🔁 Persisting {len(updates)} updated/deleted SecurityControls...")
        bulk_update_instances(SecurityControls, updates)
        print("controles update completed step1")
        AS.remove_SC_from_risk_data()
        print("controles update completed step2")
        AS.sync_security_controls_with_riskcontrol()
        print("controles update completed step3")
        AS.sync_security_controls_with_attack()
        print("controles update completed step4")

# ========================== UI HOOK ==========================

def create_security_control_and_insert_row(self):
    """Create and insert new row in UI table for SecurityControl."""
    scc_id = generate_new_scc_id()
    name = f"Control {scc_id.split('-')[-1]}"
    control = create_security_control(scc_id, name)

    if control is None:
        QMessageBox.critical(None, "Error", f"Control with ID '{scc_id}' already exists.")
        return

    row_index = self.table.rowCount()
    self.table_wrapper.insert_row([
        control.scc_id,
        control.name,
        control.description or "",
        control.comments or ""
    ])
    self.row_uuid_map[row_index] = control.uuid

    self.delete_button.setEnabled(True)
    self.submit_button.setEnabled(True)
    self.table.selectRow(row_index)

# ========================== ID GENERATOR ==========================

def generate_new_scc_id():
    global last_scc_number
    if last_scc_number is None:
        last_scc_number = get_max_numeric_suffix(SecurityControls, "scc_id", prefix="Ctrl")
        if last_scc_number == 0:
            last_scc_number = 0
    last_scc_number += 1
    return f"Ctrl-{last_scc_number}"
