

from PyQt5.QtWidgets import QMessageBox
import controllers.DatabaseCreator as DB
import sqlite3
import Analysis.models.analysis_synchronization as AS
import re
import logging
logger = logging.getLogger(__name__)

def synch_scope_changes(scope_id):
    logger.info("Updating scope changes to Scope home mindmap dummy database")
    try:
        existing_data = DB.execute_db("SELECT scope_id, scope_name, comments FROM scope_home_mindmap")
        existing_scope_map = {row[0]:row[1] for row in existing_data}
        existing_ids_data = DB.execute_db("SELECT scope_id FROM scope_home_mindmap_dumy")
        existing_scope_ids = [row[0] for row in existing_ids_data]
        
        # update into the dummy table
        if scope_id in existing_scope_map:
            scope_name = existing_scope_map[scope_id]
            if scope_id in existing_scope_ids:
                DB.update_db("""UPDATE scope_home_mindmap_dumy SET scope_name=? WHERE scope_id=?""", (scope_name, scope_id))
            else:
                DB.update_db("""INSERT INTO scope_home_mindmap_dumy (scope_id, scope_name, Asset, threat)VALUES (?, ?, ?, ?)""", (scope_id, scope_name, "", ""))
        # if scope_id:
        #     synch_asset_record(scope_id)
        # AssetMindmap.add_new_attack_leaf()  # Uncomment if needed

    except Exception as e:
        print(f"Error occurred: {e}")
        QMessageBox.critical(None, "Error", f"An error occurred while saving changes: {str(e)}")

def scope_asset_generate_id(scope_id):
    logger.info(f"Adding New Asset record only for Scope ID: {scope_id}")
    try:
        existing_ids = DB.execute_db("SELECT asset_id FROM assets UNION SELECT id FROM asset_trash")
        # Extract the numeric part of the existing asset IDs
        existing_asset_ids = [row[0] for row in existing_ids]
        existing_max_id = 0
        if existing_asset_ids:
            existing_max_id = max([int(data.removeprefix('AST-')) for data in existing_asset_ids])
        new_id = f"AST-{existing_max_id + 1}"
        return new_id

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error generating ID: {e}")
        return ""

def synch_asset_record(scope_id):
    logger.info("ading New Asset record when Scope is submitted")
    try:
        existing_data = DB.execute_db("SELECT scope_id, scope_name, Asset FROM scope_home_mindmap_dumy")
        existing_scope_map = {row[0]:(row[1], row[2]) for row in existing_data}
        existing_ids_data = DB.execute_db("SELECT asset_id FROM assets")
        existing_asset_ids = [row[0] for row in existing_ids_data]
        
        for scope_id, (scope_name, asset_id) in existing_scope_map.items():
            if asset_id != '' or asset_id.startswith('AST-'):
                DB.update_db("""UPDATE assets SET name = ? WHERE asset_id = ?""", (scope_name, asset_id))
            else:
                new_asset_id = scope_asset_generate_id(scope_id)
                row_data = [new_asset_id, scope_name, "", "", ""]
                # Insert the new asset record into the `assets` table
                DB.update_db("""INSERT INTO assets (asset_id, name, security_properties, description, comments) VALUES (?, ?, ?, ?, ?)""", tuple(row_data))
                DB.update_db("""UPDATE scope_home_mindmap_dumy SET Asset = ? WHERE scope_id = ?""", (new_asset_id, scope_id))
        
        # Perform subsequent operations
        AS.sync_threats_with_assets()
        AS.update_threatscenario_from_threat()
        AS.update_risktreatement_data()
        AS.remove_orphaned_attack_tree_rows()
        AS.update_attack_tree_text()
        AS.sync_attack_tree_with_threats()
        AS.remove_nonexistent_threat_scenarios_from_Risk_data()
        update_scope_threats()

    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred: {e}")

def clean_scope_home_mindmap_node():
    logger.info("Removing mindmap related to a scope if that scope is deleted")
    try:
        DB.cursor.execute("SELECT scope_id FROM scope_home_mindmap")
        existing_scope_ids = {row[0] for row in DB.cursor.fetchall()}
 
        DB.cursor.execute("SELECT node_id FROM scope_home_mindmap_node")
        rows = DB.cursor.fetchall()
 
        for row in rows:
            node_id = row[0]
 
            # Extract the base scope_id from node_id using regex
            match = re.match(r"(SCOPE-\d+)_node_\d+", node_id)
            if match:
                base_scope_id = match.group(1)
 
                # Check if the extracted scope_id exists in scope_home_mindmap
                if base_scope_id not in existing_scope_ids:
                    DB.cursor.execute("DELETE FROM scope_home_mindmap_node WHERE node_id = ?", (node_id,))
 
        DB.conn.commit()
        print("Cleanup completed successfully.")
 
    except sqlite3.Error as e:
        print(f"Database error: {e}")
       
def update_scope_threats():
    logger.info("Updating the threat coloumn in scope home mindmap dumy database with threat id which has been created from Scope")
    """
    Updates the 'threat' column in the 'scope_home_mindmap_dumy' table based on matching assets
    in the 'Threat' table. If an asset is associated with multiple threat_ids, all threat_ids
    will be concatenated and stored in the 'threat' column.
    """
    try:
        # Fetch all relevant data from scope_home_mindmap_dumy
        scope_data = DB.execute_db("SELECT scope_id, Asset FROM scope_home_mindmap_dumy")
        
        # Fetch asset-to-threat_id mapping from the Threat table
        threat_data = DB.execute_db("SELECT asset, threat_id FROM Threat")
        
        # Create a dictionary to group threat_ids by asset
        from collections import defaultdict
        threat_map = defaultdict(list)
        for asset, threat_id in threat_data:
            threat_map[asset].append(threat_id)  # Group all threat_ids for an asset
        
        # Loop through scope data to update the threat column
        for scope_id, asset_id in scope_data:
            if asset_id and asset_id in threat_map:  # Check if asset exists in the Threat table
                # Join all threat_ids as a comma-separated string
                threat_ids = ",".join(map(str, threat_map[asset_id]))
                
                # Update the threat column in the database
                DB.update_db(
                    """UPDATE scope_home_mindmap_dumy SET threat = ? WHERE scope_id = ?""",
                    (threat_ids, scope_id)
                )
        
        print("Threat column updated successfully for matching assets.")
    
    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred while updating threats: {e}")

def update_scope_assets():
    logger.info("Updating the assets coloumn in scope home mindmap dumy database with threat id which has been created from Scope")
    try:
        # Fetch all relevant data from scope_home_mindmap_dumy
        scope_data = DB.execute_db("SELECT scope_id, Asset FROM scope_home_mindmap_dumy")
        
        asset_data = DB.execute_db("SELECT asset_id FROM Assets")
        existing_asset_ids = [row[0] for row in asset_data]
        for (scope_id, asset_id) in scope_data:
            if asset_id not in existing_asset_ids:
                # Update the threat column in the database
                DB.update_db(
                    """UPDATE scope_home_mindmap_dumy SET Asset=?, threat = ? WHERE scope_id = ?""",
                    ('', '', scope_id)
                )
    
    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred while updating threats: {e}")

def delete_asset_for_scope(scope_id):
    logger.info("Deleting the asset when Scope is deleted")
    try:        
        # Fetch all scope_ids from the scope_home_mindmap_dumy table
        dummy_scope_asset_data = DB.execute_db_query(f"SELECT Asset FROM scope_home_mindmap_dumy WHERE scope_id=?", (scope_id,))
        asset_id = ''
        if dummy_scope_asset_data and dummy_scope_asset_data[0][0] != '':
            asset_id = dummy_scope_asset_data[0][0]
            DB.update_db("DELETE FROM scope_home_mindmap_dumy WHERE scope_id = ?", (scope_id,))
            DB.update_db("DELETE FROM assets WHERE asset_id = ?", (asset_id,))
            print(asset_id)

        AS.sync_threats_with_assets()
        AS.update_threatscenario_from_threat()
        AS.update_risktreatement_data()
        AS.remove_orphaned_attack_tree_rows()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def update_scope_name_from_node_text():
    logger.info("Updates the node name")
    try:
        DB.cursor.execute("SELECT node_text FROM scope_home_mindmap_node")
        nodes = DB.cursor.fetchall()

        scope_id_pattern = re.compile(r"SCOPE-\d+")

        # Iterate through the rows of 'scope_home_mindmap_node'
        for node in nodes:
            node_text = node[0]
            
            match = scope_id_pattern.search(node_text)
            if match:
                scope_id = match.group(0)  
                new_scope_name = node_text[len(scope_id):].strip()  # Remove the "SCOPE-xxx" part
                
                DB.cursor.execute("""
                    UPDATE scope_home_mindmap
                    SET scope_name = ?
                    WHERE scope_id = ?
                """, (new_scope_name, scope_id))
        synch_scope_changes(scope_id)
        DB.conn.commit()

    except sqlite3.Error as e:
        # Handle any SQLite errors
        QMessageBox.critical(None, "Database Error", f"An error occurred: {e}")
    

def find_duplicates(previous_text, changed_text):
    print("---ds", changed_text, previous_text)
    # counter = Counter(existing_records)
    changed_text = changed_text.strip()
    existing_lower = refrash_existing_entries()
    if changed_text.lower() == '': 
        return -1
    elif changed_text.lower() not in existing_lower or changed_text.lower() == previous_text.lower().strip(): 
        return 0
    elif changed_text.lower() in existing_lower : 
        return 1
    else: 
        return 0


def refrash_existing_entries():
    available_scope_entrys = set()
    available_asset_entrys = set()
    existing_entries = set()
    scope_entries = DB.execute_db("SELECT scope_name FROM scope_home_mindmap")
    for (entry,) in scope_entries: available_scope_entrys.add(entry.strip().lower())
    asset_entries = DB.execute_db("SELECT name FROM assets")
    for (entry,) in asset_entries: available_asset_entrys.add(entry.strip().lower())
    for entry in available_scope_entrys: existing_entries.add(entry.strip())
    for entry in available_asset_entrys: existing_entries.add(entry.strip())
    existing_lower = {entry.lower() for entry in existing_entries}
    return existing_lower  