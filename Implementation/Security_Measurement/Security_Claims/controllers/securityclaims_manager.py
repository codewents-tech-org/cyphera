import uuid
import logging
from controllers.schema_manager import create_instance, get_instances, delete_all_instance, bulk_update_instances, get_max_numeric_suffix
from controllers.tablemodel import SecurityClaims
import Analysis.models.analysis_synchronization as AS


logger = logging.getLogger(__name__)

# 🧠 In-memory cache
SECURITY_CLAIMS_CACHE = {}  # uuid -> { record, changed, deleted }
last_sc_number = None

# ========================== CRUD ==========================

def load_all_security_claims():
    """Fetch all non-deleted SecurityClaims and cache them."""
    global SECURITY_CLAIMS_CACHE
    SECURITY_CLAIMS_CACHE.clear()
    logger.info("🔄 Loading SecurityClaims from DB...")

    rows = get_instances(SecurityClaims, {'is_deleted': False})
    for row in rows:
        SECURITY_CLAIMS_CACHE[row.uuid] = {
            'record': row,
            'changed': False,
            'deleted': False
        }

    return [entry['record'] for entry in SECURITY_CLAIMS_CACHE.values()]


def create_security_claim(sc_id, name, assumption_id='', responsible='', toe_configuration_id='',
                          description='', comments=''):
    """Create and cache a new SecurityClaim."""
    claim = SecurityClaims(
        uuid=str(uuid.uuid4()),
        sc_id=sc_id,
        name=name,
        assumption_id=assumption_id,
        responsible=responsible,
        toe_configuration_id=toe_configuration_id,
        description=description,
        comments=comments,
        created_by="system",
        updated_by="system",
        is_deleted=False
    )

    created = create_instance(claim)
    if not created:
        logger.error(f"[❌] Failed to create SecurityClaim {sc_id}")
        return None

    SECURITY_CLAIMS_CACHE[created.uuid] = {
        'record': created,
        'changed': False,
        'deleted': False
    }
    return created


def update_security_claim(uuid, updates: dict):
    """Update fields of a claim in the cache."""
    if uuid in SECURITY_CLAIMS_CACHE:
        obj = SECURITY_CLAIMS_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            SECURITY_CLAIMS_CACHE[uuid]['changed'] = True
        return changed
    return False


def delete_security_claim(uuid):
    """Soft delete claim in memory."""
    if uuid in SECURITY_CLAIMS_CACHE:
        SECURITY_CLAIMS_CACHE[uuid]['deleted'] = True
        SECURITY_CLAIMS_CACHE[uuid]['changed'] = True
        return True
    return False


def persist_security_claim_changes():
    """Bulk persist changes and deletions."""
    updates = []

    for uuid, entry in SECURITY_CLAIMS_CACHE.items():
        if not entry['changed']:
            continue

        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': True})
        else:
            updates.append({
                'uuid': uuid,
                'sc_id': obj.sc_id,
                'name': obj.name,
                'assumption_id': obj.assumption_id,
                'responsible': obj.responsible,
                'toe_configuration_id': obj.toe_configuration_id,
                'description': obj.description,
                'comments': obj.comments,
                'updated_by': obj.updated_by,
                'is_deleted': False
            })
        entry['changed'] = False

    if updates:
        bulk_update_instances(SecurityClaims, updates)
        logger.info(f"[✅] Persisted {len(updates)} SecurityClaim updates.")
        
        # Sync downstream
        AS.update_riskData_from_securityClaims()
        AS.remove_claims_from_risk_data()

# ========================== ID Helper ==========================

def generate_new_sc_id():
    global last_sc_number
    if last_sc_number is None:
        last_sc_number = get_max_numeric_suffix(SecurityClaims, "sc_id", prefix="SC")
    last_sc_number += 1
    return f"SC-{last_sc_number}"
