

from PyQt5.QtWidgets import QMessageBox
import controllers.DatabaseCreator as DB
import components.table.multioption_selector as MOS
import sqlite3

import logging
logger = logging.getLogger(__name__)
# save Technical tree data into the database
def technical_Submit_Changes(self):
    logger.info("Saving technical tree data to the database") 
    try:
        self.update_button_states()
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col+1)
                if item is not None:
                    row_data.append(item.text())
                else:
                    widget = self.table.cellWidget(row, col+1)
                    if widget is not None:
                        if isinstance(widget, MOS.TSMultiSelectComboBox):
                            row_data.append(", ".join(widget.selected_items()))
                        else:
                            row_data.append(widget.selected_items())
            DB.update_db("INSERT OR REPLACE INTO technical_tree_home VALUES (?, ?, ?, ?, ?, ?, ?)", tuple(row_data))
        Sync_TechnicalTree_name()
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error saving data: {e}")
    except IndexError as e:
        print(f"IndexError: Failed to set table headers. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def Sync_TechnicalTree_name():
    technicaltree_rows = DB.execute_db("SELECT id, name FROM technical_tree_home")
    technicaltree_map = {row[0]: row[1] for row in technicaltree_rows}
    
    # Fetch all rows of technical tree head from other tree
    available_tech_tree = DB.execute_db("SELECT Node_ID, Text FROM technical_tree  WHERE Node_Type = 'head'")
    available_cir_tech_tree = DB.execute_db("SELECT Node_ID, Text FROM riskcontrol_tree  WHERE Node_Type = 'technical head'")
    available_att_tech_tree = DB.execute_db("SELECT Node_ID, Text FROM attack_tree  WHERE Node_Type = 'technical head'")
    available_att_cir_tech_tree = DB.execute_db("SELECT Node_ID, Text FROM attack_tree  WHERE Node_Type = 'riskcontrol technical head'")
    
    
    # Sync threats with attack_tree_home
    for tech_id, tech_name in technicaltree_map.items():
        for (node_id, node_text) in available_tech_tree:
            if node_text.startswith(f"{tech_id} "):
                DB.update_db("""UPDATE technical_tree SET Text= ? WHERE Node_ID = ?""", (f"{tech_id} {tech_name}", node_id))
        for (node_id, node_text) in available_cir_tech_tree:
            if node_text.startswith(f"{tech_id} "):
                DB.update_db("""UPDATE riskcontrol_tree SET Text= ? WHERE Node_ID = ?""", (f"{tech_id} {tech_name}", node_id))
        for (node_id, node_text) in available_att_tech_tree:
            if node_text.startswith(f"{tech_id} "):
                DB.update_db("""UPDATE attack_tree SET Text= ? WHERE Node_ID = ?""", (f"{tech_id} {tech_name}", node_id))
        for (node_id, node_text) in available_att_cir_tech_tree:
            if node_text.startswith(f"{tech_id} "):
                DB.update_db("""UPDATE attack_tree SET Text= ? WHERE Node_ID = ?""", (f"{tech_id} {tech_name}", node_id))
    