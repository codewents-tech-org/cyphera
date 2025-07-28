
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import controllers.DatabaseCreator as DB
import Target_Of_Evaluation.Scope.controllers.scope_synchronizations as Sync
import logging
logger = logging.getLogger(__name__)

def scope_delete_entry(table):
    logger.info("Scope deletion when delete button is clicked")
    try:
        replay = QMessageBox.warning(None, "Warning", "Delete selected row.", QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Ok)
        if replay == QMessageBox.Ok:
            selected_row = table.currentRow()
            if selected_row < 0:
                QMessageBox.warning("Warning", "Please select a row to delete.")
                return
            id_item = table.item(selected_row, 1).text()
            DB.update_db("DELETE FROM scope_home_mindmap WHERE scope_id = ?", (id_item,))
            DB.update_db("INSERT INTO scope_home_mindmap_trash (id) VALUES (?)", (id_item,))
            table.removeRow(selected_row)
            row_count = table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                table.selectRow(next_row)
            
            Sync.delete_asset_for_scope(id_item)

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")
