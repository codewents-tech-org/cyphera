
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import controllers.DatabaseCreator as DB

# from Attack_Paths.RiskControl_Tree.controllers.RiskControl_TechnicanTree_Update import riskcontrol_TechnicalTree_Update
# from Attack_Paths.Attack_Tree.controllers.Attack_TechnicanTree_Update import Attack_TechnicalTree_Update
from Attack_Paths.controllers.Update_Connected_Modules import Update_Threat_Table, Update_AttackTree_Table, Update_RiskTreatment_Table

import logging
logger = logging.getLogger(__name__)
def technical_delete_entry(self):
    logger.info("Delete selected row.")
    try:
        replay = QMessageBox.warning(None, "Warning", "Delete selected row.", QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Ok)
        if replay == QMessageBox.Ok:
            selected_row = self.table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(None, "Warning", "Please select a row to delete.")
                return
            id_item = self.table.item(selected_row, 1).text()
            DB.update_db("DELETE FROM technical_tree_home WHERE id = ?", (id_item,))
            DB.update_db("INSERT INTO tat_trash (id) VALUES (?)", (id_item,))
            self.table.removeRow(selected_row)
            row_count = self.table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                self.table.selectRow(next_row)
            
            logger.info("Row deleted.")
            sync_removed_technicaltree_from_tree(id_item)
            
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error deleting row: {e}")


def sync_removed_technicaltree_from_tree(tree_id):
    logger.info("Sync removed technical tree from riskcontrol and attack tree.")
    DB.update_db('DELETE FROM technical_tree WHERE Node_ID LIKE ?', (f'{tree_id}_node%',))
    
    logger.info("Technical tree removed from Risk Control Tree.")
    cir_tech_rows = DB.execute_db(f"SELECT Node_ID, Text FROM riskcontrol_tree WHERE Node_Type='technical head' AND Text LIKE '{tree_id} %'")
    for (tree_node, tree_text) in cir_tech_rows:
        DB.update_db('DELETE FROM riskcontrol_tree WHERE Node_ID LIKE ?', (tree_node,))
        cir_tree = tree_node.split('_')[0]
        riskcontrol_TechnicalTree_Update(cir_tree)
    
    logger.info("Technical tree removed from attack tree.")
    attack_trees = set()
    att_tech_rows = DB.execute_db(f"SELECT Node_ID, Text FROM attack_tree WHERE Node_Type in ('technical head', 'riskcontrol technical head') AND Text LIKE '{tree_id} %'")
    for (tree_node, tree_text) in att_tech_rows:
            DB.update_db('DELETE FROM attack_tree WHERE Node_ID LIKE ?', (tree_node,))
            att_tree = tree_node.split('_')[0]
            attack_trees.add(att_tree)
            Attack_TechnicalTree_Update(att_tree)
    
    logger.info("Update threat, attack tree table and risk treatment.")
    Update_Threat_Table()
    Update_AttackTree_Table()
    Update_RiskTreatment_Table()

