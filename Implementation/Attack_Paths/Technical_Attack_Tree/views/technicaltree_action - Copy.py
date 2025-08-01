import uuid
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QApplication
from PyQt5.QtCore import pyqtSignal, Qt
import logging

from Attack_Paths.Technical_Attack_Tree.views.technicaltree_table_toolbar_panel import create_toolbar
from components.table.table_panel import TablePanelWrapper
from components.loading_dialog import RoundLoader
import utils.interface_utils as interfaces
import controllers.TableValueHighlight as TVH
from controllers.tablemodel import TechnicalTreeHome, TOEConfiguration, Assumptions
from Attack_Paths.Technical_Attack_Tree.controllers.technicaltree_manager import (
    load_all_technical_trees,
    create_technical_tree_and_insert_row,
    persist_technical_tree_changes,
    delete_technical_tree,
    update_technical_tree,
    TECHNICAL_TREE_CACHE
)
from Attack_Paths.RiskControl_Tree.controllers.risk_control_tree_manager import load_all_RCT, RCT_CACHE, persist_tree_changes, update_tree
from controllers.schema_manager import get_instances
from components.table.multiselect_combo import MultiSelectComboSelector
logger = logging.getLogger(__name__)


class TechnicalTreeModule(QWidget):
    technical_tree_name_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        logger.info("Technical Tree View Initiated")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.data_loaded = False
        self.row_uuid_map = {}
        self.table_wrapper = None
        self.init_ui()

    def init_ui(self):
        create_toolbar(self)
        self.layout.addWidget(self.toolbar)

        self.table_wrapper = TablePanelWrapper(use_row_indicator=True)
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("technicaltree")
        self.table = self.table_wrapper.table
        self.layout.addWidget(self.table_wrapper)

        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)

        self.add_button.clicked.connect(self.Add_Record)
        self.delete_button.clicked.connect(self.Remove_Record)
        self.submit_button.clicked.connect(self.submit_changes)

        self.table.itemChanged.connect(self.table_data_changed_set_flag)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.clicked.connect(self.on_row_selection_changed)
        self.update_button_states()

    def load_data(self):
        if self.data_loaded:
            self.table_data_changed = False
            return

        self.loader = RoundLoader(self, label_text="Loading Technical Trees...")
        self.loader.show()
        QApplication.processEvents()

        try:
            self.table.setRowCount(0)
            self.row_uuid_map.clear()
            interfaces.unsaved_changes = False

            loaded = load_all_technical_trees()
            self.technical_tree_names_before = {}

            # ✅ 1. Load dropdown options
            self.toe_configuration_option_list = [
                f"{item.toe_configuration_id}::{item.toe_configuration_name}"
                for item in get_instances(TOEConfiguration)
            ]
            self.assumptions_option_list = [
                f"{item.assumption_id}::{item.assumptions}"
                for item in get_instances(Assumptions)
            ]

            for tree in loaded:
                row_index = self.table.rowCount()
                self.table_wrapper.insert_row([
                    tree.id,
                    tree.name,
                    tree.used_in_threat if tree.used_in_threat else '',
                    tree.used_in_riskcontrol if tree.used_in_riskcontrol else '',
                    '',
                    '',
                    tree.comment if tree.comment else ''
                ])
                self.row_uuid_map[row_index] = tree.uuid
                self.add_multiselect_to_table_cell(row_index, 5, self.toe_configuration_option_list, tree.toe_configuartion_id, 'toe_configuartion_id')
                self.add_multiselect_to_table_cell(row_index, 6, self.assumptions_option_list, tree.assumption_id, 'assumption_id')
                self.technical_tree_names_before[tree.id] = tree.name

            self.data_loaded = True

        except Exception as e:
            logger.exception("❌ Error loading Technical Trees")
            QMessageBox.critical(self, "Error", f"Failed to load Technical Trees:\n{e}")

        finally:
            self.loader.close()

    def Add_Record(self):
        self.table.setFocus()
        row_before = self.table.rowCount()

        create_technical_tree_and_insert_row(self)
        self.submit_changes()
        self.update_button_states()
        interfaces.unsaved_changes = False

    def update_cache_data(self):
        row = self.table.currentRow()
        changed_tree_ids = []

        id_item = self.table.item(row, 1)
        name_item = self.table.item(row, 2)
        uuid = self.row_uuid_map.get(row)
        if not uuid or not id_item or not name_item:
            return
        tree_id = id_item.text()
        name = name_item.text()
        used_in_threat = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        used_in_riskcontrol = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
        comments = self.table.item(row, 6).text() if self.table.item(row, 6) else ""

        if uuid in TECHNICAL_TREE_CACHE:
            record = TECHNICAL_TREE_CACHE[uuid]['record']
            old_name = record.name
            changed = update_technical_tree(uuid, {
                'name': name_item,
                'used_in_threat': used_in_threat,
                'used_in_riskcontrol': used_in_riskcontrol,
                'comment': comments
            })
            if changed and old_name != name_item:
                changed_tree_ids.append(tree_id)

        self.tree_names_after[tree_id] = name_item

        logger.info(f"Tree names before: {self.tree_names_before}")
        logger.info(f"Tree names after: {self.tree_names_after}")

    def submit_changes(self):
        self.table.setFocus()
        logger.info('Technical Attack Tree Table Data Submission started')
        persist_technical_tree_changes()
        interfaces.unsaved_changes = False
        self.update_button_states()
        logger.info('✅ Technical Attack Tree Table Data Submitted successfully')

    def Remove_Record(self):
        selected_rows = sorted(self.table.selectionModel().selectedRows(), key=lambda x: x.row(), reverse=True)
        if not selected_rows:
            return

        for index in selected_rows:
            row = index.row()
            uuid = self.row_uuid_map.get(row)

            if not uuid:
                continue

            delete_technical_tree(uuid)
            self.table.removeRow(row)

        new_map = {}
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            if id_item:
                id_val = id_item.text().strip()
                for uuid, entry in TECHNICAL_TREE_CACHE.items():
                    if entry['record'].id == id_val:
                        new_map[row] = uuid
                        break

        self.row_uuid_map = new_map
        interfaces.unsaved_changes = True
        self.update_button_states()

    def update_button_states(self):
        row_count = self.table.rowCount()
        has_selection = bool(self.table.selectionModel().selectedRows())
        self.delete_button.setEnabled(row_count > 0 and has_selection)
        self.submit_button.setEnabled(row_count > 0)

    def on_table_item_changed(self, item):
        if item.column() == 1:
            self.validate_unique_name(item)
        interfaces.unsaved_changes = True
        self.update_button_states()

    def validate_unique_name(self, item):
        new_text = item.text().strip()
        for row in range(self.table.rowCount()):
            if row == item.row():
                continue
            existing = self.table.item(row, 1)
            if existing and existing.text().strip() == new_text:
                QMessageBox.warning(self, "Duplicate", f"The name '{new_text}' already exists.")
                item.setText("")
                return

        uuid = self.row_uuid_map.get(item.row())
        if uuid:
            update_technical_tree(uuid, {'name': new_text})
            self.submit_button.setEnabled(True)

    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True

    def table_data_changed_set_flag(self):
        interfaces.unsaved_changes = True
        self.update_button_states()

    def on_row_selection_changed(self):
        TVH.on_row_selection_changed2(self.table, self)

    def add_multiselect_to_table_cell(self, row_index, column_index, option_list, current_value, field_name):
        """
        Generic helper for adding MultiSelectComboSelector to Threat Scenarios table.

        Args:
            row_index (int): Table row index.
            column_index (int): Table column index.
            option_list (list[str]): List of selectable options.
            current_value (str): Pre-selected value from DB (comma-separated string).

        """
        combo = MultiSelectComboSelector(option_list, placeholder="Select")

        # Set pre-selected items
        if current_value:
            if isinstance(current_value, str):
                selected_items = [x.strip() for x in current_value.split(",") if x.strip()]
            else:
                selected_items = current_value
            combo.set_selected_items(selected_items)

        def on_selection_change():
            value = ", ".join(combo.selected_items())
            # self.table.setItem(row_index, column_index, QTableWidgetItem(value))
            uuid = self.row_uuid_map.get(row_index)
            if uuid:
                update_technical_tree(uuid, {field_name: value})  # ✅ Function change
                interfaces.unsaved_changes = True

        combo.model().dataChanged.connect(on_selection_change)
        self.table.setCellWidget(row_index, column_index, combo)
