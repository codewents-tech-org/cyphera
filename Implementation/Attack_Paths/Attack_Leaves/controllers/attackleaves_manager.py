import uuid
from controllers.tablemodel import AttackLeafNodes
import logging
logger = logging.getLogger(__name__)
from controllers.database import get_engine_and_session
# Main cache: leaf_id -> { 'record': AttackLeafNodes instance, 'changed': False, 'deleted': False, ... }
ATTACK_LEAF_CACHE = {}

# -------------------------- CRUD/Cache Logic --------------------------



def load_all_attack_leaves():
    """Load all attack leaves from DB into the cache."""
    ATTACK_LEAF_CACHE.clear()
    
    # result = session.query(AttackLeafNodes).filter(...).first()
    engine, Session = get_engine_and_session()
    session = Session()
    all_leaves = session.query(AttackLeafNodes).filter_by(is_deleted=False).all()
    for leaf in all_leaves:
        ATTACK_LEAF_CACHE[leaf.id] = {
            'record': leaf,
            'changed': False,
            'deleted': False,
            'removed_from_trees': False,
        }
    return [entry['record'] for entry in ATTACK_LEAF_CACHE.values()]


def create_attack_leaf(leaf_id, leaf_name, values=None, af_level='High', description='', comments=''):
    """Create new attack leaf in cache and DB."""
    if values is None:
        values = ['0', '0', '0', '0', '0']
    # Prevent duplicate IDs
    if leaf_id in ATTACK_LEAF_CACHE:
        return None
    leaf = AttackLeafNodes(
        uuid=str(uuid.uuid4()),
        id=leaf_id,
        name=leaf_name,
        time=values[0],
        expertise=values[1],
        knowledge=values[2],
        access=values[3],
        equipment=values[4],
        afr_level=af_level,
        reasoning=description,
        comments=comments,
        is_deleted=False
    )
    # Add to DB
    try:
        leaf.save()  # If using Flask-SQLAlchemy model
    except Exception as e:
        print(f"[create_attack_leaf][ERROR] {e}")
        return None

    # Add to cache
    ATTACK_LEAF_CACHE[leaf_id] = {
        'record': leaf,
        'changed': False,
        'deleted': False,
        'removed_from_trees': False,
    }
    return leaf


def update_attack_leaf(leaf_id, updates: dict):
    """Update fields for a leaf, only if changed."""
    if leaf_id not in ATTACK_LEAF_CACHE:
        print(f"[update_attack_leaf] Leaf {leaf_id} not in cache")
        return False
    obj = ATTACK_LEAF_CACHE[leaf_id]['record']
    changed = False
    for k, v in updates.items():
        if hasattr(obj, k) and getattr(obj, k) != v:
            setattr(obj, k, v)
            changed = True
    if changed:
        ATTACK_LEAF_CACHE[leaf_id]['changed'] = True
    return changed


def soft_delete_attack_leaf(leaf_id):
    """Mark as deleted in cache and DB (soft delete)."""
    if leaf_id in ATTACK_LEAF_CACHE:
        ATTACK_LEAF_CACHE[leaf_id]['deleted'] = True
        ATTACK_LEAF_CACHE[leaf_id]['changed'] = True
        # Mark in DB
        try:
            obj = ATTACK_LEAF_CACHE[leaf_id]['record']
            obj.is_deleted = True
            obj.save()
        except Exception as e:
            print(f"[soft_delete_attack_leaf][ERROR] {e}")
        return True
    return False


def persist_attack_leaf_changes():
    """Persist only changed leaves to the DB, remove as needed."""
    for leaf_id, entry in ATTACK_LEAF_CACHE.items():
        obj = entry['record']
        if entry['changed']:
            try:
                obj.save()
            except Exception as e:
                print(f"[persist_attack_leaf_changes][ERROR] {e}")
            entry['changed'] = False
        if entry['deleted']:
            try:
                obj.is_deleted = True
                obj.save()
            except Exception as e:
                print(f"[persist_attack_leaf_changes][ERROR-delete] {e}")
            entry['deleted'] = False


def delete_leaf(uuid):
    """
    Soft delete a leaf node (set is_deleted in cache and mark as changed).
    Args:
        uuid (str): UUID of the leaf node to delete.
    Returns:
        bool: True if deleted, False if not found.
    """
    global LEAF_CACHE
    if uuid in LEAF_CACHE:
        LEAF_CACHE[uuid]['deleted'] = True
        LEAF_CACHE[uuid]['changed'] = True
        return True
    return False

# ------------------- Dictionary Cache Utility Functions -------------------


def get_leaf_by_id(leaf_id):
    """Get leaf from cache, or None if not found."""
    entry = ATTACK_LEAF_CACHE.get(leaf_id)
    if entry:
        return entry['record']
    # Optionally load from DB if not in cache (lazy fetch)
    engine, Session = get_engine_and_session()
    session = Session()
    leaf = session.query(AttackLeafNodes).filter_by(id=leaf_id).first()
    if leaf:
        ATTACK_LEAF_CACHE[leaf_id] = {
            'record': leaf,
            'changed': False,
            'deleted': False,
            'removed_from_trees': False,
        }
        return leaf
    return None


def mark_leaf_removed_from_trees(leaf_id):
    """Set removed_from_trees in the cache for this leaf."""
    if leaf_id in ATTACK_LEAF_CACHE:
        ATTACK_LEAF_CACHE[leaf_id]['removed_from_trees'] = True
        print(f"[mark_leaf_removed_from_trees] Marked leaf {leaf_id} as removed from trees.")


def mark_leaf_value_changed(leaf_id):
    if leaf_id in ATTACK_LEAF_CACHE:
        ATTACK_LEAF_CACHE[leaf_id]['changed'] = True
        print(f"[mark_leaf_value_changed] Leaf {leaf_id} value marked as changed.")


def mark_leaf_name_changed(leaf_id):
    if leaf_id in ATTACK_LEAF_CACHE:
        ATTACK_LEAF_CACHE[leaf_id]['changed'] = True  # Optionally add separate name_changed flag if needed
        print(f"[mark_leaf_name_changed] Leaf {leaf_id} name marked as changed.")

# ------------------- Remove/Sync Tree References -------------------


def remove_leaf_references_from_all_trees(leaf_id):
    """Remove references to this leaf from all trees."""
    from controllers.database import get_engine_and_session
    from controllers.database_tables.attack_paths_tables import TechnicalAttackTree, RiskControlTree, AttackTree

    engine, Session = get_engine_and_session()
    session = Session()
    try:
        # Remove from TechnicalAttackTree
        session.query(TechnicalAttackTree).filter(
            TechnicalAttackTree.node_id.like(f"{leaf_id} %"),
            TechnicalAttackTree.node_type == "leaf"
        ).delete(synchronize_session=False)
        # Remove from RiskControlTree
        session.query(RiskControlTree).filter(
            RiskControlTree.node_id.like(f"{leaf_id} %"),
            RiskControlTree.node_type.in_(["leaf", "technical leaf"])
        ).delete(synchronize_session=False)
        # Remove from AttackTree
        session.query(AttackTree).filter(
            AttackTree.node_id.like(f"{leaf_id} %"),
            AttackTree.node_type.in_([
                "leaf", "riskcontrol leaf", "technical leaf", "riskcontrol technical leaf"
            ])
        ).delete(synchronize_session=False)
        session.commit()
        print(f"[remove_leaf_references_from_all_trees] Removed {leaf_id} from all trees.")
    except Exception as e:
        session.rollback()
        print(f"[remove_leaf_references_from_all_trees][ERROR] {e}")
    finally:
        session.close()


def update_dependent_trees(updated_leaf_ids):
    """Call update logic for all affected trees/tables."""
    # You should have actual implementations for these:
    from Attack_Paths.controllers.Update_Connected_Modules import (
        Update_Threat_Table, Update_AttackTree_Table, Update_RiskTreatment_Table,
        # TechnicalTree_Update, RiskControlTree_Update, AttackTree_AFR_Update
    )
    print(f"[update_dependent_trees] Updating for leaves: {updated_leaf_ids}")
    # for leaf_id in updated_leaf_ids:
    #     TechnicalTree_Update(leaf_id)
    #     RiskControlTree_Update(leaf_id)
    #     AttackTree_AFR_Update(leaf_id)
    Update_Threat_Table()
    Update_AttackTree_Table()
    Update_RiskTreatment_Table()


def persist_leaf_changes():
    """
    Efficiently persist all changed and deleted leaf nodes from LEAF_CACHE to the DB.
    Performs soft delete for deleted leaves, and updates all changed fields for others.
    After DB sync, resets change flags and optionally synchronizes removed leaves from all trees.
    """
    from controllers.schema_manager import bulk_update_instances
    from Attack_Paths.Attack_Leaves.controllers.attackleaves_TableRemoveRecord import sync_removed_leaf_from_tree

    updates = []
    delete_leaf_list = []
    for uuid, entry in LEAF_CACHE.items():
        if not entry['changed']:
            continue

        obj = entry['record']
        if entry.get('deleted', False):
            updates.append({'uuid': uuid, 'is_deleted': 'True'})
            delete_leaf_list.append(obj.id)
        else:
            # Add all update fields as per your model
            updates.append({
                'uuid': uuid,
                'name': obj.name,
                'time': obj.time,
                'expertise': obj.expertise,
                'knowledge': obj.knowledge,
                'access': obj.access,
                'equipment': obj.equipment,
                'afr_level': getattr(obj, 'afr_level', getattr(obj, 'afr_level', 'High')),
                'reasoning': getattr(obj, 'reasoning', ''),
                'comments': getattr(obj, 'comments', ''),
                'is_deleted': 'False'
            })
        entry['changed'] = False  # Reset change flag after queuing for update

    # Bulk DB update for all changes and deletes
    if updates:
        bulk_update_instances(AttackLeafNodes, updates)
    # Remove deleted leaves from all tree structures (deep sync)
    if delete_leaf_list:
        for leaf_id in delete_leaf_list:
            sync_removed_leaf_from_tree(leaf_id)

    logger.info(f"[persist_leaf_changes] Persisted {len(updates)} leaf records, removed {len(delete_leaf_list)} leaves from all trees.")

