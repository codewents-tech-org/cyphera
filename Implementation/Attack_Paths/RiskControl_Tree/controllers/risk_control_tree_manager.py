import uuid
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from controllers.schema_manager import create_instance, get_instances, delete_all_instance , bulk_update_instances
from controllers.tablemodel import RiskControlTreeHome, RiskControlTree
from controllers.schema_manager import get_max_numeric_suffix

import logging

logger = logging.getLogger(__name__)

# 🧠 In-memory cache
RCT_CACHE = {}  # uuid -> {'record': model, 'changed': False, 'deleted': False}

# ========================== CRUD OPERATIONS ==========================
def load_all_RCT():
    """Fetch all non-deleted AT and populate cache."""
    global RCT_CACHE
    print("🔄 Loading AT from DB...")
    RCT_CACHE.clear()

    AT_rows = get_instances(RiskControlTreeHome, {'is_deleted': False})
    for tree in AT_rows:
        RCT_CACHE[tree.id] = {
            'record': tree,
            'changed': False,
            'deleted': False
        }

    return [entry['record'] for entry in RCT_CACHE.values()]

def update_tree(tree_id, updates: dict):
    """Update the scope in cache only if values changed."""
    if tree_id in RCT_CACHE:
        obj = RCT_CACHE[tree_id]['record']
        changed = False
        for k, v in updates.items():
            if getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            RCT_CACHE[tree_id]['changed'] = True
        return changed
    return False

def persist_tree_changes():
    """Efficiently persist changed and deleted scope records."""
    updates = []
    updated_tree_dict = {}

    for tree_id, entry in RCT_CACHE.items():
        if not entry['changed']:
            continue
        
        obj = entry['record']
        updates.append({
            'id': obj.id,
            'name': obj.name,
            'mitigates': obj.mitigates,
            'assumption_id': obj.assumption_id,
            'comment': obj.comment,
            'updated_by': obj.updated_by,
            'is_deleted': False
        })
        updated_tree_dict[obj.id] = obj.comment

        entry['changed'] = False  # reset flag after queuing update

    # 🔁 Use shared bulk update function
    if updates:
        print(updates)
        bulk_update_instances(RiskControlTreeHome, updates, filter_key="id")
