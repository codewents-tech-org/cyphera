

from PyQt5.QtWidgets import QTableWidgetItem, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
import sqlite3
import controllers.DatabaseCreator as DB
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.table_row_indicator as TRI

from PyQt5.QtWidgets import QTableWidgetItem, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt

# Import your ORM model and schema_manager function
from controllers.schema_manager import get_instances
from controllers.database_tables.attack_paths_tables import AttackLeafNodes, TechnicalTreeHome

def AttackLeaves_Load_data(self):
    try:
        self.table.setRowCount(0)  # Clear the table
        self.existing_entries.clear()  # Ensure this is reset

        # ORM: Get all rows
        rows = get_instances(AttackLeafNodes)
        if not rows:
            return

        for row_idx, leaf in enumerate(rows):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 40)
            self.existing_entries.add(str(leaf.id))  # Assuming 'id' is the PK field

            # The following assumes column order: id, name, time, expertise, knowledge, access, equipment, afr_level, ... (adjust if different)
            leaf_row_data = [
                leaf.id,
                leaf.name,
                str(leaf.time),
                str(leaf.expertise),
                str(leaf.knowledge),
                str(leaf.access),
                str(leaf.equipment),
                getattr(leaf, "afr_level", ""),  # Add/rename if field name differs
                leaf.reasoning,
                leaf.comments
            ]

            for col_idx, col_data in enumerate(leaf_row_data):
                if col_idx == 0:  # id, non-editable
                    item = QTableWidgetItem(str(col_data))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx + 1, item)
                elif col_idx == 7:  # afr_level, color-coded QLineEdit
                    afr_item = QLineEdit(str(col_data))
                    afr_item.setReadOnly(True)
                    helper.Apply_AFR_Level_Color(afr_item, col_data)
                    self.table.setCellWidget(row_idx, col_idx + 1, afr_item)
                elif col_idx in [2, 3, 4, 5, 6]:  # ComboBox columns
                    combo_values = helper.attackpath_leaf_values_menu[col_idx - 2]
                    item = MOS.CustomComboBoxLeave(combo_values)
                    item.set_text(str(col_data))
                    item.currentTextChanged.connect(self.set_unsaved_changes)
                    self.table.setCellWidget(row_idx, col_idx + 1, item)
                    item.currentIndexChanged.connect(lambda: self.Update_AFR_Level(item))
                else:  # Regular editable columns
                    item = QTableWidgetItem(str(col_data))
                    self.table.setItem(row_idx, col_idx + 1, item)

            sidebar = TRI.SidebarWidget()
            self.table.setCellWidget(row_idx, 0, sidebar)

        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 1)
    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
