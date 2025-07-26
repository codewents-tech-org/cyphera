
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
import sqlite3
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.tree_row_indicator as TRI2
import controllers.DatabaseCreator as DB
from controllers.schema_manager import get_instances, get_first_instance, create_instance, update_instance
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome, AttackLeafNodes
from controllers.database_tables.target_of_evaluation_tables import TOEConfiguration
import logging
logger = logging.getLogger(__name__)

def technical_new_entry(self):
    logger.info("Adding new entry to the Technical Attack Tree")
    try:
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, 40)
        sidebar = TRI2.SidebarWidget(parent=self, index=row_idx)
        self.table.setCellWidget(row_idx, 0, sidebar)

        # ORM: fetch TOE configuration options
        toe_configuration_rows = get_instances(TOEConfiguration)
        toe_configuration_options = [
            f"{row.toe_configuration_id}::{row.toe_configuration_name}"
            for row in toe_configuration_rows
        ]

        # ORM: fetch Assumptions
        # assumptions_rows = get_instances(Assumptions)
        # assumptions_list = [
        #     f"{row.assumption_id}::{row.assumptions}"
        #     for row in assumptions_rows
        # ]

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
        # assumption_item = MOS.TSMultiSelectComboBox(assumptions_list)
        # assumption_item.set_text("")
        # self.table.setCellWidget(row_idx, 6, assumption_item)

        comments_item = QTableWidgetItem("")
        self.table.setItem(row_idx, 7, comments_item)

        self.table.setCurrentCell(row_idx, 1)
    except Exception as e:
        # Handles ALL DB errors (including SQLAlchemy/ORM) and other exceptions
        QMessageBox.critical(None, "Error", f"Error loading data: {e}")
