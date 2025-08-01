import uuid
import logging
from PyQt5.QtWidgets import QMessageBox
from controllers.schema_manager import create_instance, get_instances, bulk_update_instances, get_max_numeric_suffix
from controllers.tablemodel import TechnicalTreeHome

logger = logging.getLogger(__name__)

# In-memory cache
TECHNICAL_TREE_CACHE = {}  # uuid → {'record': model, 'changed': False, 'deleted': False}
last_tt_number = None

# ========================== CRUD ==========================

def load_all_technical_trees():
    global TECHNICAL_TREE_CACHE
    print("🔄 Loading Technical Trees from DB...")
    TECHNICAL_TREE_CACHE.clear()

    try:
        records = get_instances(TechnicalTreeHome, {'is_deleted': False}) or []
    except Exception as e:
        logger.error(f"❌ Failed to load Technical Trees (DB error): {e}")
        return []

    for rec in records:
        TECHNICAL_TREE_CACHE[rec.uuid] = {
            'record': rec,
            'changed': False,
            'deleted': False
        }

    return [entry['record'] for entry in TECHNICAL_TREE_CACHE.values()]



def create_technical_tree(tt_id, name):
    tree = TechnicalTreeHome(
        uuid=str(uuid.uuid4()),
        id=tt_id,
        name=name,
        created_by="system",
        updated_by="system",
        version="3",
        is_latest=True,
        is_deleted=False
    )
    tree = create_instance(tree)

    if not tree:
        logger.error(f"[❌] Failed to create Technical Tree with ID: {tt_id}")
        return None

    TECHNICAL_TREE_CACHE[tree.uuid] = {
        'record': tree,
        'changed': False,
        'deleted': False
    }
    return tree


def update_technical_tree(uuid, updates: dict):
    if uuid in TECHNICAL_TREE_CACHE:
        obj = TECHNICAL_TREE_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            TECHNICAL_TREE_CACHE[uuid]['changed'] = True
        return changed
    return False


def delete_technical_tree(uuid):
    if uuid in TECHNICAL_TREE_CACHE:
        TECHNICAL_TREE_CACHE[uuid]['deleted'] = True
        TECHNICAL_TREE_CACHE[uuid]['changed'] = True
        return True
    return False


def persist_technical_tree_changes():
    updates = []

    for uuid, entry in TECHNICAL_TREE_CACHE.items():
        if not entry['changed']:
            continue

        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': True})
        else:
            updates.append({
                'uuid': uuid,
                'id': obj.id,
                'name': obj.name,
                'used_in_threat': obj.used_in_threat,
                'used_in_riskcontrol': obj.used_in_riskcontrol,
                'toe_configuartion_id': obj.toe_configuartion_id,
                'assumption_id': obj.assumption_id,
                'comment': obj.comment,
                'updated_by': obj.updated_by,
                'is_deleted': False
            })

        entry['changed'] = False

    if updates:
        bulk_update_instances(TechnicalTreeHome, updates)
        logger.info(f"[✅] Persisted {len(updates)} Technical Tree records")


# ========================== UI Business Logic ==========================

def create_technical_tree_and_insert_row(self):
    tt_id = generate_new_id()
    name = f"Technical Tree {tt_id.split('-')[-1]}"
    tree = create_technical_tree(tt_id, name)

    if tree is None:
        QMessageBox.critical(None, "Error", f"Technical Tree with ID '{tt_id}' already exists.")
        return

    row_index = self.table.rowCount()
    self.table_wrapper.insert_row([
        tree.id,
        tree.name,
        tree.comment or ""
    ])
    self.row_uuid_map[row_index] = tree.uuid

    self.delete_button.setEnabled(True)
    self.submit_button.setEnabled(True)
    self.table.selectRow(row_index)


def generate_new_id():
    global last_tt_number

    if last_tt_number is None:
        last_tt_number = get_max_numeric_suffix(TechnicalTreeHome, "id", prefix="TAT")
        if last_tt_number == 0:
            last_tt_number = 0

    last_tt_number += 1
    return f"TAT-{last_tt_number}"
