import uuid
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from controllers.schema_manager import create_instance, get_instances, delete_all_instance , bulk_update_instances
from controllers.tablemodel import AttackTreeHome, AttackTree
from controllers.schema_manager import get_max_numeric_suffix

import logging

logger = logging.getLogger(__name__)

# 🧠 In-memory cache
AT_CACHE = {}  # uuid -> {'record': model, 'changed': False, 'deleted': False}

# ========================== CRUD OPERATIONS ==========================
def load_all_AT():
    """Fetch all non-deleted AT and populate cache."""
    global AT_CACHE
    print("🔄 Loading AT from DB...")
    AT_CACHE.clear()

    AT_rows = get_instances(AttackTreeHome, {'is_deleted': False})
    for tree in AT_rows:
        AT_CACHE[tree.id] = {
            'record': tree,
            'changed': False,
            'deleted': False
        }

    return [entry['record'] for entry in AT_CACHE.values()]

def update_tree(tree_id, updates: dict):
    """Update the scope in cache only if values changed."""
    if tree_id in AT_CACHE:
        obj = AT_CACHE[tree_id]['record']
        changed = False
        for k, v in updates.items():
            if getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            AT_CACHE[tree_id]['changed'] = True
        return changed
    return False

def persist_tree_changes():
    """Efficiently persist changed and deleted scope records."""
    updates = []
    updated_tree_dict = {}

    for tree_id, entry in AT_CACHE.items():
        if not entry['changed']:
            continue
        
        obj = entry['record']
        updates.append({
            'id': obj.id,
            'name': obj.name,
            'initial_afr': obj.initial_afr,
            'resid_afr': obj.resid_afr,
            'toe_configuration_id': obj.toe_configuration_id,
            'comments': obj.comments,
            'updated_by': obj.updated_by,
            'is_deleted': False
        })
        updated_tree_dict[obj.id] = obj.comments

        entry['changed'] = False  # reset flag after queuing update

    # 🔁 Use shared bulk update function
    if updates:
        bulk_update_instances(AttackTreeHome, updates, filter_key="id")
