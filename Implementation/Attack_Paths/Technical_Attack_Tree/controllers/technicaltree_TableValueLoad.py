

from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import sqlite3
import controllers.DatabaseCreator as DB
import components.table.multioption_selector as MOS
import components.table.tree_row_indicator as TRI2
from controllers.schema_manager import get_instances, get_first_instance, create_instance, update_instance, delete_instances_like
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome 
from controllers.database_tables.target_of_evaluation_tables import TOEConfiguration
import logging
logger = logging.getLogger(__name__)


# Load Technical Tree data from the database
def TechnicalTree_Load_data(self):
    logger.info("[TechnicalTree_Load_data] Loading technical tree data")
    try:
        self.table.setRowCount(0)  # Clear the table
        logger.debug("[TechnicalTree_Load_data] Table cleared.")

        # 1. Load technical_tree_home entries via ORM
        rows = get_instances(TechnicalTreeHome)
        logger.debug(f"[TechnicalTree_Load_data] Loaded {len(rows) if rows else 0} TechnicalTreeHome rows from DB.")
        if not rows:
            logger.debug("[TechnicalTree_Load_data] No rows found. Exiting.")
            return

        # 2. Load TOE configuration options via ORM
        toe_config_objs = get_instances(TOEConfiguration)
        logger.debug(f"[TechnicalTree_Load_data] Loaded {len(toe_config_objs)} TOEConfiguration entries.")
        toe_configuration_options = [
            f"{row.toe_configuration_id}::{row.toe_configuration_name}"
            for row in toe_config_objs
        ]
        logger.debug(f"[TechnicalTree_Load_data] TOE configuration options: {toe_configuration_options}")

        # 3. Load assumptions options via ORM (disabled by default)
        # assumptions_objs = get_instances(Assumptions)
        # logger.debug(f"[TechnicalTree_Load_data] Loaded {len(assumptions_objs)} Assumptions entries.")
        # assumptions_list = [
        #     f"{row.assumption_id}::{row.assumptions}"
        #     for row in assumptions_objs
        # ]
        # logger.debug(f"[TechnicalTree_Load_data] Assumptions options: {assumptions_list}")

        # 4. Fill table row by row
        for row_idx, row_obj in enumerate(rows):
            logger.debug(f"[TechnicalTree_Load_data] Inserting row {row_idx} for: {row_obj}")
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row_obj.name)
            logger.debug(f"[TechnicalTree_Load_data] Added '{row_obj.name}' to existing_entries.")

            # Map ORM object to list in column order
            col_names = [c.name for c in TechnicalTreeHome.__table__.columns]
            logger.debug(f"[TechnicalTree_Load_data] Table columns: {col_names}")
            row_data = [getattr(row_obj, col) for col in col_names]
            logger.debug(f"[TechnicalTree_Load_data] Row data: {row_data}")

            for col_idx, col_data in enumerate(row_data):
                table_col = col_idx + 1  # first column (0) is for sidebar
                logger.debug(f"[TechnicalTree_Load_data] Row {row_idx}, Col {table_col}: Value '{col_data}'")
                if col_idx == 4:
                    widget = MOS.TSMultiSelectComboBox(toe_configuration_options)
                    widget.set_text(col_data)
                    self.table.setCellWidget(row_idx, table_col, widget)
                    widget.currentTextChanged.connect(self.set_unsaved_changes)
                    logger.debug(f"[TechnicalTree_Load_data] Set TOE combo box at ({row_idx},{table_col}).")
                # elif col_idx == 5:
                #     widget = MOS.TSMultiSelectComboBox(assumptions_list)
                #     widget.set_text(col_data)
                #     self.table.setCellWidget(row_idx, table_col, widget)
                #     widget.currentTextChanged.connect(self.set_unsaved_changes)
                #     logger.debug(f"[TechnicalTree_Load_data] Set Assumptions combo box at ({row_idx},{table_col}).")
                else:
                    item = QTableWidgetItem(str(col_data))
                    if col_idx in [0, 2, 3]:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        logger.debug(f"[TechnicalTree_Load_data] Made cell ({row_idx},{table_col}) non-editable.")
                    self.table.setItem(row_idx, table_col, item)

            # Add sidebar widget in column 0
            sidebar = TRI2.SidebarWidget(parent=self, index=row_idx)
            self.table.setCellWidget(row_idx, 0, sidebar)
            logger.debug(f"[TechnicalTree_Load_data] Added SidebarWidget at ({row_idx}, 0).")

        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 1)
            logger.debug("[TechnicalTree_Load_data] Set current cell to (0, 1).")

        logger.info("[TechnicalTree_Load_data] Finished loading technical tree data.")

    except Exception as e:
        logger.error(f"[TechnicalTree_Load_data][ERROR]: {e}")
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
