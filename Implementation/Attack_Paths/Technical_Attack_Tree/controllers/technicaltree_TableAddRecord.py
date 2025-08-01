
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
import sqlite3
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.tree_row_indicator as TRI2
import controllers.DatabaseCreator as DB

import logging
logger = logging.getLogger(__name__)

def technical_new_entry(self):
    logger.info("Adding new entry to the Technical Attack Tree")
    try:
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, 40)
        sidebar = TRI2.SidebarWidget(parent = self, index=row_idx)
        self.table.setCellWidget(row_idx, 0, sidebar)
        
        toe_configuration_options = []
        toe_configuration = DB.execute_db("SELECT toe_configuration_id, toe_configuration_name FROM toe_configuration")    
        for toec_id, toec_name in toe_configuration:
            toe_configuration_options.append(f"{toec_id}::{toec_name}")
        
        assumptions_rows = DB.execute_db("SELECT assumption_id, assumptions FROM assumptions")
        assumptions_list = [f"{assumption_id}::{assumption}" for assumption_id, assumption in assumptions_rows]
        
        # Generate an auto-generated ID
        tat_id = helper.technicalattack_generate_id(self.table)
        id_item = QTableWidgetItem(tat_id)
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row_idx, 1, id_item)

        # Extract only the last part after the last '-'
        tat_name = f"Technical Tree {tat_id.split('-')[-1]}"  # Pre-filled editable name

        # Name column (Editable)
        name_item = QTableWidgetItem(tat_name)  # Set placeholder text
        self.table.setItem(row_idx, 2, name_item)  # Editable by default
        self.table.setCurrentCell(row_idx, 2)
        self.find_duplicates(name_item)
        self.previous_text = name_item.text()
        self.existing_entries.add(name_item.text())

        # used_in_threat (Non-editable)
        used_in_threat_item = QTableWidgetItem("")
        used_in_threat_item.setFlags(used_in_threat_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row_idx, 3, used_in_threat_item)

        # used_in_riskcontrol_tree (Non-editable)
        used_in_riskcontrol_tree_item = QTableWidgetItem("")
        used_in_riskcontrol_tree_item.setFlags(used_in_riskcontrol_tree_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row_idx, 4, used_in_riskcontrol_tree_item)

        # TOE Configuration 
        toe_config_item = MOS.TSMultiSelectComboBox(toe_configuration_options)
        toe_config_item.set_text("")
        self.table.setCellWidget(row_idx, 5, toe_config_item)

        # Assumptions
        assumption_item = MOS.TSMultiSelectComboBox(assumptions_list)
        assumption_item.set_text("")
        self.table.setCellWidget(row_idx, 6, assumption_item)

        comments_item = QTableWidgetItem("")
        self.table.setItem(row_idx, 7, comments_item)

        self.table.setCurrentCell(row_idx, 1)
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
    except IndexError as e:
        print(f"IndexError: Failed to set table headers. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")