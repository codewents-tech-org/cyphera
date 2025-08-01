

from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import sqlite3
import controllers.DatabaseCreator as DB
import components.table.multioption_selector as MOS
import components.table.tree_row_indicator as TRI2

import logging
logger = logging.getLogger(__name__)
# Load Technical Tree data from the database
def TechnicalTree_Load_data(self):
    logger.info("Loading technical tree data")
    try:
        self.table.setRowCount(0)  # Clear the table
        rows = [('TAT-1', 'technical 1', '', '', '', '', 'This is a comment'),]
        # rows = DB.execute_db("SELECT * FROM technical_tree_home")
        if not rows:    return
        
        toe_configuration_options = []
        # toe_configuration = DB.execute_db("SELECT toe_configuration_id, toe_configuration_name FROM toe_configuration")    
        # for toec_id, toec_name in toe_configuration:
        #     toe_configuration_options.append(f"{toec_id}::{toec_name}")
        
        # assumptions_rows = DB.execute_db("SELECT assumption_id, assumptions FROM assumptions")
        # assumptions_list = [f"{assumption_id}::{assumption}" for assumption_id, assumption in assumptions_rows]
        assumptions_list = []
        
        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row_data[1])
            for col_idx, col_data in enumerate(row_data):
                if col_idx == 4:
                    widget = MOS.TSMultiSelectComboBox(toe_configuration_options)
                    widget.set_text(col_data)
                    self.table.setCellWidget(row_idx, col_idx + 1, widget)
                    widget.currentTextChanged.connect(self.set_unsaved_changes)
                elif col_idx == 5:
                    widget = MOS.TSMultiSelectComboBox(assumptions_list)
                    widget.set_text(col_data)
                    self.table.setCellWidget(row_idx, col_idx + 1, widget)
                    widget.currentTextChanged.connect(self.set_unsaved_changes)
                else:
                    item = QTableWidgetItem(col_data)
                    if col_idx in [0, 2, 3]: 
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx + 1, item)

            sidebar = TRI2.SidebarWidget(parent = self, index=row_idx, tree_indicator=True)
            sidebar.tree_button.clicked.connect(self.open_tree)
            self.table.setCellWidget(row_idx, 0, sidebar)

        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 1)
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
    except IndexError as e:
        print(f"IndexError: Failed to set table headers. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")