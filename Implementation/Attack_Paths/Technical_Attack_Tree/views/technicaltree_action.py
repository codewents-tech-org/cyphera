import uuid
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QApplication
from PyQt5.QtCore import pyqtSignal, Qt
import logging

from Attack_Paths.Technical_Attack_Tree.views.technicaltree_table_toolbar_panel import create_toolbar
from components.table.table_panel import TablePanelWrapper
from components.loading_dialog import RoundLoader
import utils.interface_utils as interfaces
import controllers.TableValueHighlight as TVH

from Attack_Paths.Technical_Attack_Tree.controllers.technicaltree_manager import (
    load_all_technical_trees,
    create_technical_tree_and_insert_row,
    persist_technical_tree_changes,
    delete_technical_tree,
    update_technical_tree,
    TECHNICAL_TREE_CACHE
)

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

            for tree in loaded:
                row_index = self.table.rowCount()
                self.table_wrapper.insert_row([
                    tree.technical_tree_id,
                    tree.name,
                    tree.comment or ""
                ])
                self.row_uuid_map[row_index] = tree.uuid
                self.technical_tree_names_before[tree.technical_tree_id] = tree.name

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

    def submit_changes(self):
        self.table.setFocus()
        names_after = {}
        changed_ids = []

        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            comment_item = self.table.item(row, 2)

            if not id_item or not name_item:
                continue

            id_val = id_item.text()
            name_val = name_item.text()
            comment_val = comment_item.text() if comment_item else ""

            uuid = self.row_uuid_map.get(row)
            if not uuid:
                continue

            if uuid in TECHNICAL_TREE_CACHE:
                record = TECHNICAL_TREE_CACHE[uuid]['record']
                old_name = record.name
                changed = update_technical_tree(uuid, {
                    'name': name_val,
                    'comment': comment_val
                })
                if changed and old_name != name_val:
                    changed_ids.append(id_val)

            names_after[id_val] = name_val

        persist_technical_tree_changes()

        self.technical_tree_names_before = names_after.copy()
        interfaces.unsaved_changes = False
        self.update_button_states()

        for tid in changed_ids:
            self.technical_tree_name_changed.emit(tid)
            logger.info(f"📡 Signal emitted: technical_tree_name_changed({tid})")

        QMessageBox.information(self, "Saved", "All changes have been saved.")

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
                    if entry['record'].technical_tree_id == id_val:
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
        TVH.on_row_selection_changed2(self.table)