import uuid
import logging
from controllers.schema_manager import create_instance, get_instances, bulk_update_instances, get_max_numeric_suffix
from controllers.tablemodel import SecurityGoals

logger = logging.getLogger(__name__)

# In-memory cache: uuid -> { record, changed, deleted }
SECURITY_GOALS_CACHE = {}
last_sg_number = None

# ========================== CRUD ==========================

def load_all_security_goals():
    """Fetch all non-deleted SecurityGoals and cache them."""
    global SECURITY_GOALS_CACHE
    SECURITY_GOALS_CACHE.clear()
    logger.info("🔄 Loading SecurityGoals from DB...")

    rows = get_instances(SecurityGoals, {'is_deleted': False})
    for row in rows:
        SECURITY_GOALS_CACHE[row.uuid] = {
            'record': row,
            'changed': False,
            'deleted': False
        }

    return [entry['record'] for entry in SECURITY_GOALS_CACHE.values()]


def create_security_goal(sg_id, name, responsible='', toe_configuration_id='', description='', comments=''):
    """Create and cache a new SecurityGoal."""
    goal = SecurityGoals(
        uuid=str(uuid.uuid4()),
        sg_id=sg_id,
        name=name,
        responsible=responsible,
        toe_configuration_id=toe_configuration_id,
        description=description,
        comments=comments,
        created_by="system",
        updated_by="system",
        is_deleted=False
    )

    created = create_instance(goal)
    if not created:
        logger.error(f"[❌] Failed to create SecurityGoal {sg_id}")
        return None

    SECURITY_GOALS_CACHE[created.uuid] = {
        'record': created,
        'changed': False,
        'deleted': False
    }
    return created

def update_security_goal(uuid, updates: dict):
    """Update fields of a goal in the cache."""
    if uuid in SECURITY_GOALS_CACHE:
        obj = SECURITY_GOALS_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            SECURITY_GOALS_CACHE[uuid]['changed'] = True
        return changed
    return False

def delete_security_goal(uuid):
    """Soft delete goal in memory."""
    if uuid in SECURITY_GOALS_CACHE:
        SECURITY_GOALS_CACHE[uuid]['deleted'] = True
        SECURITY_GOALS_CACHE[uuid]['changed'] = True
        return True
    return False

def persist_security_goal_changes():
    """Bulk persist changes and deletions."""
    updates = []
    for uuid, entry in SECURITY_GOALS_CACHE.items():
        if not entry['changed']:
            continue

        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': True})
        else:
            updates.append({
                'uuid': uuid,
                'sg_id': obj.sg_id,
                'name': obj.name,
                'responsible': obj.responsible,
                'toe_configuration_id': obj.toe_configuration_id,
                'description': obj.description,
                'comments': obj.comments,
                'updated_by': obj.updated_by,
                'is_deleted': False
            })
        entry['changed'] = False

    if updates:
        bulk_update_instances(SecurityGoals, updates)
        logger.info(f"[✅] Persisted {len(updates)} SecurityGoal updates.")

# ========================== ID Helper ==========================

def generate_new_sg_id():
    global last_sg_number
    if last_sg_number is None:
        last_sg_number = get_max_numeric_suffix(SecurityGoals, "sg_id", prefix="SG")
    last_sg_number += 1
    return f"SG-{last_sg_number}"
