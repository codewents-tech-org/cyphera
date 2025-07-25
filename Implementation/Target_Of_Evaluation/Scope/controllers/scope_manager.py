import uuid
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from Target_Of_Evaluation.Scope.controllers.scope_synchronizations import remove_mindmaps
from controllers.schema_manager import create_instance, get_instances, delete_all_instance , bulk_update_instances
from controllers.tablemodel import ScopeHomeMindmap, ScopeMindmaps
from controllers.schema_manager import get_max_numeric_suffix

import logging

logger = logging.getLogger(__name__)

# 🧠 In-memory cache
SCOPE_CACHE = {}  # uuid -> {'record': model, 'changed': False, 'deleted': False}
last_scope_number = None

# ========================== CRUD OPERATIONS ==========================
def load_all_scopes():
    """Fetch all non-deleted scopes and populate cache."""
    global SCOPE_CACHE
    print("🔄 Loading scopes from DB...")
    SCOPE_CACHE.clear()

    scopes = get_instances(ScopeHomeMindmap, {'is_deleted': 'False'})
    for scope in scopes:
        SCOPE_CACHE[scope.uuid] = {
            'record': scope,
            'changed': False,
            'deleted': False
        }

    return [entry['record'] for entry in SCOPE_CACHE.values()]


def create_scope(scope_id, scope_name):

    scope = ScopeHomeMindmap(
        uuid=str(uuid.uuid4()),
        scope_id=scope_id,
        scope_name=scope_name,
        created_by="system",
        updated_by="system",
        version="3",
        is_latest="False",
        is_deleted="False"
    )
    scope = create_instance(scope)

    if not scope:
        print(f"[ERROR] Failed to create scope with ID: {scope_id}")
        return None

    SCOPE_CACHE[scope.uuid] = {
        "record": scope,  # ✅ ADD THISy,
        "changed": False,
        "deleted": False
    }
    return scope


def update_scope(uuid, updates: dict):
    """Update the scope in cache only if values changed."""
    if uuid in SCOPE_CACHE:
        obj = SCOPE_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            SCOPE_CACHE[uuid]['changed'] = True
        return changed
    return False


def delete_scope(uuid):
    """Soft delete scope."""
    if uuid in SCOPE_CACHE:
        SCOPE_CACHE[uuid]['deleted'] = True
        SCOPE_CACHE[uuid]['changed'] = True
        return True
    return False


def persist_scope_changes():
    """Efficiently persist changed and deleted scope records."""
    updates = []
    delete_scope_list = []
    updated_scope_dict = {}

    for uuid, entry in SCOPE_CACHE.items():
        if not entry['changed']:
            continue
        
        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': 'True'})
            delete_scope_list.append(obj.scope_id)
        else:
            updates.append({
                'uuid': uuid,
                'scope_name': obj.scope_name,
                'comments': obj.comments,
                'updated_by': obj.updated_by,
                'is_deleted': 'False'
            })
            updated_scope_dict[obj.scope_id] = obj.scope_name

        entry['changed'] = False  # reset flag after queuing update

    # 🔁 Use shared bulk update function
    if updates:
        bulk_update_instances(ScopeHomeMindmap, updates)

    if delete_scope_list:
        remove_mindmaps(delete_scope_list)
    
    # if updated_scope_dict:
    #     update_mindmaps_name(updated_scope_dict)

# ========================== BUSINESS / UI ==========================

def create_scope_and_insert_row(self):
    """Create new scope and add it to the table UI."""
    scope_id = generate_new_scope_id()
    scope_name = f"Scope {scope_id.split('-')[-1]}"
    scope = create_scope(scope_id, scope_name)

    if scope is None:
        QMessageBox.critical(None, "Error", f"Scope with ID '{scope_id}' already exists. Please try again.")
        return

    row_index = self.table.rowCount()
    self.table_wrapper.insert_row([
        scope.scope_id,
        scope.scope_name,
        scope.comments or ""
    ])
    self.row_uuid_map[row_index] = scope.uuid  # ✅ Correct usage

    self.delete_button.setEnabled(True)
    self.submit_button.setEnabled(True)

    self.table.selectRow(row_index)  # ✅ Ensure the newly added row is selected



def generate_new_scope_id():
    global last_scope_number

    if last_scope_number is None:
        # Lazy init only when first used
        last_scope_number = get_max_numeric_suffix(ScopeHomeMindmap, "scope_id", prefix="SCOPE")
        if last_scope_number == 0:
            last_scope_number = 0

    last_scope_number += 1
    return f"SCOPE-{last_scope_number}"

