
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
        
        leaf_id = helper.attack_leaves_generate_id(self.table)
        id_item = QTableWidgetItem(leaf_id)
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row_idx, 1, id_item)

        # Extract only the last part after the last '-'
        leaf_name = f"Leaf {leaf_id.split('-')[-1]}"  # Pre-filled editable name

        name_item = QTableWidgetItem(leaf_name)  # Set placeholder text
        self.table.setItem(row_idx, 2, name_item)  # Editable by default
        self.table.setCurrentCell(row_idx, 2)
        self.find_duplicates(name_item)
        self.previous_text = name_item.text()
        self.existing_entries.add(name_item.text())
    

        for col_idx in [2, 3, 4, 5, 6]:
            item = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[col_idx-2])
            item.set_text(str(0))
            self.table.setCellWidget(row_idx,col_idx+1, item)
            item.currentIndexChanged.connect(lambda: self.Update_AFR_Level(item))
        
        level_item = QLineEdit('High')
        level_item.setReadOnly(True)
        helper.Apply_AFR_Level_Color(level_item, 'High')
        self.table.setCellWidget(row_idx, 8, level_item)
        
        desc_item = QTableWidgetItem('')
        self.table.setItem(row_idx, 9, desc_item)
        
        comment_item = QTableWidgetItem('')
        self.table.setItem(row_idx, 10, comment_item)

        self.table.setCurrentCell(row_idx, 1)
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
    except IndexError as e:
        print(f"IndexError: Failed to set table headers. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")