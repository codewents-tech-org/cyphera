
import os
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import sqlite3
import controllers.DatabaseCreator as DB
import components.table.tree_row_indicator as TRI2
import logging

logger = logging.getLogger(__name__)

def load_scope(self):
    logger.info("Scope table Loaded")
    try:
        self.table.setRowCount(0)
        rows = DB.execute_db("SELECT scope_id, scope_name, comments  FROM scope_home_mindmap")
        if not rows:    return
        
        for row_data in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 40)

            scope_id_item = QTableWidgetItem(row_data[0])
            scope_name_item = QTableWidgetItem(row_data[1])
            scope_comments_item = QTableWidgetItem(row_data[2])
            
            scope_id_item.setFlags(scope_id_item.flags() & ~Qt.ItemIsEditable)
            scope_name_item.setFlags(scope_name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 1, scope_id_item)
            self.table.setItem(row_idx, 2, scope_name_item)
            self.table.setItem(row_idx, 3, scope_comments_item)

            sidebar = TRI2.SidebarWidget(parent = self, index=row_idx)
            self.table.setCellWidget(row_idx, 0, sidebar)
        if self.table.rowCount() > 0: self.table.setCurrentCell(0, 1)
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

