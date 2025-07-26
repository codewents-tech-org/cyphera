# asset_manager.py

import logging
from collections import OrderedDict
# --- Add to asset_manager.py (top) ---
from controllers.schema_manager import get_max_numeric_suffix

from controllers.schema_manager import (
    get_instances, get_first_instance, update_instance, create_instance, delete_instance
)
from controllers.database_tables.analysis_tables import Assets

logger = logging.getLogger("asset_manager")

ASSET_CACHE = OrderedDict()

def load_all_assets():
    """
    Loads all assets from DB to cache and returns a list of Asset ORM objects.
    """
    global ASSET_CACHE
    logger.info("🔄 Loading assets from DB...")
    ASSET_CACHE.clear()
    assets = get_instances(Assets)
    for asset in assets:
        ASSET_CACHE[asset.asset_id] = {
            'record': asset,
            'changed': False,
            'deleted': False
        }
    return [entry['record'] for entry in ASSET_CACHE.values()]

def update_asset(asset_id, updates: dict):
    """
    Update fields in cache and mark as changed.
    Returns True if something changed, else False.
    """
    if asset_id in ASSET_CACHE:
        obj = ASSET_CACHE[asset_id]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            ASSET_CACHE[asset_id]['changed'] = True
        return changed
    return False

def persist_asset_changes():
    """
    Saves all changed (not deleted) asset records in cache to DB (bulk update).
    """
    updates = []
    for asset_id, entry in ASSET_CACHE.items():
        if entry['changed'] and not entry['deleted']:
            obj = entry['record']
            updates.append({
                'asset_id': obj.asset_id,
                'name': obj.name,
                'security_properties': obj.security_properties,
                'description': obj.description,
                'comments': obj.comments,
                # add other fields as needed
            })
            entry['changed'] = False
    if updates:
        update_instance(Assets, updates)
        logger.info(f"🔄 Updated {len(updates)} assets in DB.")

def refresh_assets_cache():
    """
    Force reload the cache from DB, discarding unsaved edits.
    """
    load_all_assets()

def delete_asset(asset_id):
    """
    Marks asset as deleted and removes from cache and DB.
    """
    if asset_id in ASSET_CACHE:
        delete_instance(Assets, {"asset_id": asset_id})
        ASSET_CACHE[asset_id]['deleted'] = True
        logger.info(f"🗑️ Deleted asset {asset_id} from DB and cache.")

def add_new_asset(asset_obj):
    """
    Adds a new asset both in DB and cache.
    """
    create_instance(asset_obj)
    ASSET_CACHE[asset_obj.asset_id] = {
        'record': asset_obj,
        'changed': False,
        'deleted': False
    }
    logger.info(f"➕ Added new asset {asset_obj.asset_id} to DB and cache.")

last_asset_number = None

def generate_new_asset_id():
    global last_asset_number

    if last_asset_number is None:
        # Only fetch from DB on first use after startup
        last_asset_number = get_max_numeric_suffix(Assets, "asset_id", prefix="ASSET")
        if last_asset_number == 0:
            last_asset_number = 0

    last_asset_number += 1
    return f"ASSET-{last_asset_number}"


def is_asset_name_duplicate(name, exclude_asset_id=None):
    """
    Check if an asset name already exists (case-insensitive).
    Optionally, exclude a specific asset_id (e.g., when editing).
    """
    name_lower = name.strip().lower()
    for asset_id, data in ASSET_CACHE.items():
        if exclude_asset_id and asset_id == exclude_asset_id:
            continue
        record = data['record']
        if record.name.strip().lower() == name_lower:
            return True
    return False
