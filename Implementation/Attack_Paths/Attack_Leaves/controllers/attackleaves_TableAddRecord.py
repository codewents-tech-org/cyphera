
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
import sqlite3
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.table_row_indicator as TRI


def attack_leaves_new_entry(self):
    try:
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, 40)
        sidebar = TRI.SidebarWidget()
        self.table.setCellWidget(row_idx, 0, sidebar)

        # Generate new leaf ID (no DB write here, just UI)
        leaf_id = helper.attack_leaves_generate_id(self.table)
        id_item = QTableWidgetItem(leaf_id)
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row_idx, 1, id_item)

        # Create a default name (editable)
        leaf_name = f"Leaf {leaf_id.split('-')[-1]}"
        name_item = QTableWidgetItem(leaf_name)
        self.table.setItem(row_idx, 2, name_item)
        self.table.setCurrentCell(row_idx, 2)

        # Business logic for finding duplicates, UI bookkeeping
        self.find_duplicates(name_item)
        self.previous_text = name_item.text()
        self.existing_entries.add(name_item.text())

        # Populate ComboBoxes (time, expertise, knowledge, access, equipment)
        for i, col_idx in enumerate([3, 4, 5, 6, 7]):  # columns 3-7 are ComboBoxes
            item = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[i])
            item.set_text(str(0))
            self.table.setCellWidget(row_idx, col_idx, item)
            item.currentIndexChanged.connect(lambda: self.Update_AFR_Level(item))

        # AFR Level column (readonly, color)
        level_item = QLineEdit('High')
        level_item.setReadOnly(True)
        helper.Apply_AFR_Level_Color(level_item, 'High')
        self.table.setCellWidget(row_idx, 8, level_item)

        # Description and comment columns (editable)
        desc_item = QTableWidgetItem('')
        self.table.setItem(row_idx, 9, desc_item)
        comment_item = QTableWidgetItem('')
        self.table.setItem(row_idx, 10, comment_item)

        self.table.setCurrentCell(row_idx, 1)

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error creating new leaf: {e}")