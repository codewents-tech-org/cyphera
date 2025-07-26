import controllers.DatabaseCreator as DB
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
import sqlite3
import Analysis.models.analysis_synchronization as AS
import models.helper as helper


def assetmindmap_generate_id():
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

#
def add_new_asset_record(name="asset1", description="hello", security_properties="", comments=""):
    try:# Generate the asset ID using the function
        asset_id = assetmindmap_generate_id()

        if security_properties is None:
            security_properties = ""
        if comments is None:
            comments = ""

        
        row_data = [asset_id, name, security_properties, description, comments]

        
        DB.update_db("INSERT INTO assets (asset_id, name, security_properties, description, comments) VALUES (?, ?, ?, ?, ?)", tuple(row_data))
       
        QMessageBox.information(None, "Success", "New asset record added successfully!")
        AS.sync_threats_with_assets()
        AS.update_threatscenario_from_threat()
        AS.update_risktreatement_data()
        AS.remove_orphaned_attack_tree_rows()
        AS.update_attack_tree_text()
    except Exception as e:
       
        QMessageBox.critical(None, "Error", f"An error occurred: {e}")


def add_new_attack_leaf(name="ABc", time=0, expertise=0, knowledge=0, access=0, equipment=0, AFR_level="High"):
    try:
       
        existing_entry = DB.execute_db_query("SELECT * FROM attack_leaf_home WHERE name = ?", (name,))
        
        if existing_entry:
            
            QMessageBox.warning(None, "Warning", "An attack leaf with this name already exists!")
            return
        
        
        attack_leaf_id = helper.leaf_node_generate_id()
        # attack_leaf_id = generate_attack_leaf_id()
        
        if AFR_level is None:
            AFR_level = "High"  

        
        row_data = [attack_leaf_id, name, time, expertise, knowledge, access, equipment, AFR_level]

        
        DB.update_db("INSERT INTO attack_leaf_home (id, name, time, expertise, knowledge, access, equipment, AFR_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", tuple(row_data))
        row_data_trash = [attack_leaf_id]

        # Insert the generated ID into the `leaf_node_trash` table
        DB.update_db("INSERT INTO leaf_node_trash (id) VALUES (?)", tuple(row_data_trash))

        
        QMessageBox.information(None, "Success", "New attack leaf record added successfully!")

    except Exception as e:
       
        QMessageBox.critical(None, "Error", f"An error occurred: {e}")
