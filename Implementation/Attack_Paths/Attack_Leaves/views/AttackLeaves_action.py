
import sys
from Attack_Paths.Attack_Leaves.controllers.attack_leaves_manager import ATTACK_LEAF_CACHE, create_attack_leaf, delete_attack_leaf, generate_new_attack_leaf_id, load_all_attack_leaves, persist_attack_leaf_changes, update_attack_leaf
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QLineEdit, QApplication, QTableWidgetItem  
from PyQt5.QtCore import Qt
import models.helper as helper
import sqlite3
import components.table.table_row_indicator as TRI
import controllers.DatabaseCreator as DB
import controllers.TableValueHighlight as TVH
import controllers.TableValueHighlight as TVH
import components.action_panel as action_panel

from Attack_Paths.Attack_Leaves.views.attackleaves_toolbar_panel import create_toolbar
from Attack_Paths.Attack_Leaves.views.attackleaves_table_panel import create_table_panel
from Attack_Paths.Attack_Leaves.views.attackleaves_column_setup import Setup_Tabel_ColumnHeading

from Attack_Paths.Attack_Leaves.controllers.attackleaves_TableValueLoad import AttackLeaves_Load_data
from Attack_Paths.Attack_Leaves.controllers.attackleaves_TableSaveRecord import AttackLeaves_Submit_Changes
from Attack_Paths.Attack_Leaves.controllers.attackleaves_TableAddRecord import attack_leaves_new_entry
from Attack_Paths.Attack_Leaves.controllers.attackleaves_TableRemoveRecord import attack_leaves_delete_entry
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
from models.unique_name_action import refrash_existing_entries, find_duplicates, store_selected_entry
import components.table.multioption_selector as MOS

class Attack_Leaves(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create the main layout for the entire widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # self.Setup_ToolbarPanel()
        create_toolbar(self)
        self.main_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)
        create_table_panel(self)
        self.action_panel_layout.addLayout(self.table_layout)
        self.main_layout.addWidget(self.action_panel)
        
          # Enable/disable buttons
        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)

        self.add_button.clicked.connect(self.Add_Record)
        self.submit_button.clicked.connect(self.Submit_Changes)
        self.delete_button.clicked.connect(self.Delete_Record)
        Setup_Tabel_ColumnHeading(self)

        # Connect table signals to state updater
        self.existing_entries = set()
        self.table.itemChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.itemDoubleClicked.connect(self.store_selected_entry)
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()
        self.previous_text = None

    # Load Attack Leaves data from the database
    def load_data(self):
        self.loader = RoundLoader(self, label_text="Loading Attack Leaves Data...")
        self.loader.show()
        QApplication.processEvents()

        self.table.itemChanged.disconnect(self.find_duplicates)
        self.attack_leaves_load_data()
        self.table.itemChanged.connect(self.find_duplicates)
        self.update_button_states()
        interfaces.unsaved_changes = False
        self.loader.close()

    def attack_leaves_load_data(self):
        self.table.setRowCount(0)
        self.existing_entries.clear()
        rows = load_all_attack_leaves()
        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row.id)
            sidebar = TRI.SidebarWidget()
            self.table.setCellWidget(row_idx, 0, sidebar)
            id_item = QTableWidgetItem(row.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 1, id_item)
            name_item = QTableWidgetItem(row.name)
            self.table.setItem(row_idx, 2, name_item)
            for i, (val, col_idx) in enumerate(zip(
                [row.time, row.expertise, row.knowledge, row.access, row.equipment], [3,4,5,6,7])):
                combo = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[i])
                combo.set_text(str(val) if val is not None else "0")
                combo.currentTextChanged.connect(self.set_unsaved_changes)
                combo.currentIndexChanged.connect(lambda: self.Update_AFR_Level(combo))
                self.table.setCellWidget(row_idx, col_idx, combo)
            afr_item = QLineEdit(row.afr_level if row.afr_level else 'High')
            afr_item.setReadOnly(True)
            helper.Apply_AFR_Level_Color(afr_item, row.afr_level or 'High')
            self.table.setCellWidget(row_idx, 8, afr_item)
            reasoning_item = QTableWidgetItem(row.reasoning or '')
            self.table.setItem(row_idx, 9, reasoning_item)
            comment_item = QTableWidgetItem(row.comments or '')
            self.table.setItem(row_idx, 10, comment_item)
        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 1)

    def create_attack_leaf_and_insert_row(self):
        leaf_id = generate_new_attack_leaf_id(self)
        leaf_name = f"Leaf {leaf_id.split('-')[-1]}"
        leaf = create_attack_leaf(leaf_id, leaf_name)
        if leaf is None:
            QMessageBox.critical(None, "Error", f"Attack Leaf with ID '{leaf_id}' already exists. Please try again.")
            return
        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
        self.table.setRowHeight(row_index, 40)
        sidebar = TRI.SidebarWidget()
        self.table.setCellWidget(row_index, 0, sidebar)
        id_item = QTableWidgetItem(leaf.id)
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row_index, 1, id_item)
        name_item = QTableWidgetItem(leaf.name)
        self.table.setItem(row_index, 2, name_item)
        self.table.setCurrentCell(row_index, 2)
        for i, (value, col_idx) in enumerate(zip(
            [leaf.time, leaf.expertise, leaf.knowledge, leaf.access, leaf.equipment], [3, 4, 5, 6, 7]
        )):
            combo = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[i])
            combo.set_text(str(value) if value is not None else "0")
            combo.currentTextChanged.connect(self.set_unsaved_changes)
            combo.currentIndexChanged.connect(lambda: self.Update_AFR_Level(combo))
            self.table.setCellWidget(row_index, col_idx, combo)
        afr_item = QLineEdit(leaf.afr_level if leaf.afr_level else 'High')
        afr_item.setReadOnly(True)
        helper.Apply_AFR_Level_Color(afr_item, leaf.afr_level or 'High')
        self.table.setCellWidget(row_index, 8, afr_item)
        reasoning_item = QTableWidgetItem(leaf.reasoning or '')
        self.table.setItem(row_index, 9, reasoning_item)
        comment_item = QTableWidgetItem(leaf.comments or '')
        self.table.setItem(row_index, 10, comment_item)
        if hasattr(self, "row_uuid_map"):
            self.row_uuid_map[row_index] = leaf.uuid
        self.delete_button.setEnabled(True)
        self.submit_button.setEnabled(True)
        self.table.selectRow(row_index)

    def Submit_Changes(self):
        print("submit changes......")
        self.table.setFocus()
        for row_idx in range(self.table.rowCount()):
            row_id = self.table.item(row_idx, 1).text()
            uuid_in_cache = None
            for uuid, entry in ATTACK_LEAF_CACHE.items():
                if entry['record'].id == row_id:
                    uuid_in_cache = uuid
                    break
            if not uuid_in_cache:
                continue  # row not in cache, skip (should not happen)

            # Collect all cell values
            updates = {}
            cache_obj = ATTACK_LEAF_CACHE[uuid_in_cache]['record']
            updates_fields = ['name', 'time', 'expertise', 'knowledge', 'access', 'equipment', 'afr_level', 'reasoning', 'comments']
            col_map = [2, 3, 4, 5, 6, 7, 8, 9, 10]  # table column indices for each field

            for field, col in zip(updates_fields, col_map):
                if col in [3, 4, 5, 6, 7]:  # ComboBoxes
                    val = self.table.cellWidget(row_idx, col).currentText()
                elif col == 8:  # QLineEdit (AFR)
                    val = self.table.cellWidget(row_idx, col).text()
                else:
                    val = self.table.item(row_idx, col).text()
                if getattr(cache_obj, field) != val:
                    updates[field] = val

            if updates:
                update_attack_leaf(uuid_in_cache, updates)

        persist_attack_leaf_changes()
        interfaces.unsaved_changes = False
        self.update_button_states()


    def Add_Record(self): 
        self.table.setFocus()
        self.table.itemChanged.disconnect(self.find_duplicates)
        self.create_attack_leaf_and_insert_row()
        self.update_button_states()
        interfaces.unsaved_changes = True
        self.table.itemChanged.connect(self.find_duplicates)

    def Delete_Record(self): 
        # (optional: ask for confirmation in UI)
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(None, "Warning", "Please select a row to delete.")
            return
        leaf_id = self.table.item(selected_row, 1).text()
        # Mark as deleted in cache and persist
        uuid_to_delete = None
        for uuid, entry in ATTACK_LEAF_CACHE.items():
            if entry['record'].id == leaf_id:
                uuid_to_delete = uuid
                break
        if uuid_to_delete:
            delete_attack_leaf(uuid_to_delete)
            persist_attack_leaf_changes()
        self.table.removeRow(selected_row)
        self.update_button_states()
        self.refrash_existing_entries()

    def update_button_states(self):
        row_count = self.table.rowCount()
        has_selection = bool(self.table.selectionModel().selectedRows())
        self.delete_button.setEnabled(row_count > 0 and has_selection)
        self.submit_button.setEnabled(row_count > 0)
        
    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True

    def find_duplicates(self, changed_item):
        # (your implementation here)
        pass
    def store_selected_entry(self, item):
        pass
    def refrash_existing_entries(self):
        pass

    def on_row_selection_changed(self): 
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed(self.table)
        interfaces.unsaved_changes = temp

    def Update_AFR_Level(self, item):
        selected_row = self.table.currentRow()
        value_list = []
        for i in range(3, 8):
            combo_box = self.table.cellWidget(selected_row, i)
            if combo_box is not None:
                value_list.append(int(combo_box.currentText().strip().split(' ')[0] if combo_box.currentText() != '' else '0'))
        afr_value = sum(value_list)
        afr_widget = self.table.cellWidget(selected_row, 8)
        if isinstance(afr_widget, QLineEdit):
            afr_level = helper.Calculate_AFR_Level(afr_value)
            afr_widget.setText(afr_level)
            helper.Apply_AFR_Level_Color(afr_widget, afr_level)