from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QApplication, QMessageBox, QTableWidgetItem, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal

from components.table.multiselect_combo import MultiSelectComboSelector
from Security_Measurement.Security_Controls.views.securitycontrol_toolbar_panel import create_toolbar
from Security_Measurement.Security_Controls.config.security_controls_config import PROPERTY_CONFIG, SAVE_BUTTON
from Security_Measurement.Security_Controls.controllers import security_controls_manager as SCM

from controllers.tablemodel import SecurityGoals
from controllers.schema_manager import get_instances
import Analysis.models.analysis_synchronization as AS

from styles.property_panel_style import property_save_button_style
from components.propertypanel.property_input_components import PropertyInputFactory
from components.propertypanel import property_panel_layout
from components.table.table_panel import TablePanelWrapper
from components.action_panel import create_action_panel
from components.loading_dialog import RoundLoader
from models.unique_name_action import refrash_existing_entries, find_duplicates, store_selected_entry
import utils.interface_utils as interfaces
import controllers.TableValueHighlight as TVH
import Risk_Assessment.controllers.riskassessment_PropertyValueDisplay as PVD

import logging
logger = logging.getLogger(__name__)

class SecurityControls_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.row_selected.connect(self.display_row_data_in_panel)

        self.property_panel_manager = property_panel_layout.PropertyPanelManager(self)
        self.property_panel_manager.create_property_panel()

        self.toggle_button = self.property_panel_manager.toggle_button
        self.property_panel = self.property_panel_manager.property_panel
        self.property_layout = self.property_panel_manager.property_layout

        self.create_property_panel_signal.connect(self.build_property_panel)
        self.create_property_panel_signal.emit()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        create_toolbar(self)
        main_layout.addWidget(self.toolbar)
        create_action_panel(self)

        self.table_wrapper = TablePanelWrapper(use_row_indicator=True, use_tree_indicator=False, parent=self)
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("securitycontrols")

        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout

        self.action_panel_layout.addWidget(self.table_wrapper.table)
        self.action_panel_layout.addWidget(self.property_panel_manager.switch_property_panel)
        self.action_panel_layout.addWidget(self.property_panel_manager.property_panel)
        main_layout.addWidget(self.action_panel)

        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.submit_button.setEnabled(False)
        self.save_button.setEnabled(False)

        self.add_button.clicked.connect(self.add_new_entry)
        print("[DEBUG] Connecting delete_button")
        self.delete_button.clicked.connect(self.delete_entry)
        self.submit_button.clicked.connect(self.submit_changes)
        self.save_button.clicked.connect(self.submit_changes)

        self.existing_entries = set()
        self.row_uuid_map = {}

        self.table.itemChanged.connect(self.update_cell_to_cache)
        self.table.itemDoubleClicked.connect(self.store_selected_entry)
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
        self.table.itemChanged.connect(self.set_unsaved_changes)

    def load_data(self):
        self.loader = RoundLoader(self, label_text="Loading...")
        self.loader.show()
        QApplication.processEvents()

        try:
            goal_rows = get_instances(SecurityGoals, {'is_deleted': False})
            self.security_property_list = [
                f"{g.sg_id}::{g.name}" for g in goal_rows if g.sg_id and g.name
            ]
            self.security_control_security_goals_input.additem(self.security_property_list)

            self.table.itemChanged.disconnect(self.find_duplicates)
            rows = SCM.load_all_security_controls()

            self.table.setRowCount(0)
            for idx, obj in enumerate(rows):
                self.table.insertRow(idx)
                self.table.setItem(idx,1, QTableWidgetItem(obj.scc_id or ""))
                self.table.setItem(idx, 2, QTableWidgetItem(obj.name or ""))

                # Multi-select for Security Goals
                sg_combo = MultiSelectComboSelector(self.security_property_list, parent=self.table)
                selected_sgs = [s.strip() for s in (obj.security_goal_id or "").split(",") if s.strip()]
                sg_combo.set_selected_items(selected_sgs)
                sg_combo.model().dataChanged.connect(lambda: self.update_cell_to_cache(None))
                self.table.setCellWidget(idx, 3, sg_combo)

                self.table.setItem(idx, 4, QTableWidgetItem(obj.description or ""))
                self.table.setItem(idx, 5, QTableWidgetItem(obj.comments or ""))
                self.row_uuid_map[idx] = obj.uuid


            self.table.itemChanged.connect(self.find_duplicates)
            interfaces.unsaved_changes = False
        finally:
            self.loader.close()

    def add_new_entry(self):
        self.table.setFocus()
        self.table.itemChanged.disconnect(self.find_duplicates)

        # --- 1. Add to DB/ORM/cache ---
        obj = SCM.create_security_control(
            scc_id=f"SCC-{self.table.rowCount()+1}",
            name=f"SCC-{self.table.rowCount()+1}",
            security_goal_id="",
            description="",
            comments=""
        )
        # This should save and return the new record with UUID

        # --- 2. Add to UI table ---
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setItem(row_idx, 1, QTableWidgetItem(obj.scc_id))
        self.table.setItem(row_idx, 2, QTableWidgetItem(obj.name))

        sg_combo = MultiSelectComboSelector(self.security_property_list, parent=self.table)
        sg_combo.set_selected_items([])
        sg_combo.model().dataChanged.connect(lambda: self.update_cell_to_cache(None))
        self.table.setCellWidget(row_idx, 3, sg_combo)
        self.table.setItem(row_idx, 4, QTableWidgetItem(""))
        self.table.setItem(row_idx, 5, QTableWidgetItem(""))

        self.row_uuid_map[row_idx] = obj.uuid

        self.update_button_states()
        interfaces.unsaved_changes = True
        self.table.itemChanged.connect(self.find_duplicates)


    def delete_entry(self):
        print("delete entry check.......................")
        selected_rows = sorted(self.table.selectionModel().selectedRows(), key=lambda x: x.row(), reverse=True)
        if not selected_rows:
            print("[DEBUG] No row selected for deletion.")
            return

        for index in selected_rows:
            row = index.row()
            uuid = self.row_uuid_map.get(row)
            print(f"[DEBUG] UUID for row {row}: {uuid}")
            if uuid:
                print(f"[DEBUG] Deleting security control with UUID: {uuid}")
                SCM.delete_security_control(uuid)
                self.table.removeRow(row)
            else:
                print(f"[DEBUG] No UUID found for row {row}. Skipping.")

        # FULL REBUILD of uuid map
        new_map = {}
        for row in range(self.table.rowCount()):
            scc_id_item = self.table.item(row, 1)
            if scc_id_item:
                scc_id = scc_id_item.text().strip()
                for uuid, entry in SCM.SECURITY_CONTROLS_CACHE.items():
                    if entry['record'].scc_id == scc_id:
                        new_map[row] = uuid
                        break
        self.row_uuid_map = new_map
        print(f"[DEBUG] Remapped row_uuid_map: {self.row_uuid_map}")

        self.update_button_states()
        self.refrash_existing_entries()
        interfaces.unsaved_changes = True

    def submit_changes(self):
        self.table.setFocus()
        SCM.persist_security_control_changes()
        AS.remove_SC_from_risk_data()
        AS.sync_security_controls_with_riskcontrol()
        AS.sync_security_controls_with_attack()
        self.update_button_states()
        interfaces.unsaved_changes = False

    def update_cell_to_cache(self, item=None):
        # item can be None if called from dropdown
        if item:
            row = item.row()
        else:
            # Called from dropdown, find current row in focus or selected
            row = self.table.currentRow()
        uuid = self.row_uuid_map.get(row)
        if not uuid:
            return

        # For multi-select widget in "Security Goals" (column 2)
        sg_combo = self.table.cellWidget(row, 2)
        if sg_combo:
            sg_selected = sg_combo.selected_items()
            security_goal_id = ", ".join(sg_selected)
        else:
            # fallback to text
            security_goal_id = self.table.item(row, 2).text() if self.table.item(row, 2) else ""

        updates = {
            "scc_id": self.table.item(row, 0).text() if self.table.item(row, 0) else "",
            "name": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
            "security_goal_id": security_goal_id,
            "description": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
            "comments": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
        }
        SCM.update_security_control(uuid, updates)
        interfaces.unsaved_changes = True

    
    def update_button_states(self):
        selected_rows = self.table.selectionModel().selectedRows()
        enable = bool(selected_rows)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(True)
        if hasattr(self, 'submit_button'):
            self.submit_button.setEnabled(True)
        if hasattr(self, 'add_button'):
            self.add_button.setEnabled(True)

    def find_duplicates(self, item): find_duplicates(self, item)
    def store_selected_entry(self, item): store_selected_entry(self, item)
    def refrash_existing_entries(self): refrash_existing_entries(self)
    def set_unsaved_changes(self): interfaces.unsaved_changes = True

    def build_property_panel(self):
        self.property_factory = PropertyInputFactory()
        self.security_control_property_controls = []

        for field in PROPERTY_CONFIG:
            input_widget = self.property_factory.create_common_property_input(
                field["label"], field["type"], self.property_layout,
                self.security_control_property_controls,
                getattr(self, field.get("signal")) if field.get("signal") else None,
                field.get("items")
            )

            if field.get("readonly"):
                input_widget.setReadOnly(True)
            setattr(self, f'security_control_{field["label"].lower().replace(" ", "_")}_input', input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.security_control_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)

    def handle_property_save_signal(self, payload):
        print(f"[🔁] Save clicked from property panel: {payload}")

    def display_row_data_in_panel(self, data):
        row = self.table.currentRow()
        for i, (label, widget) in enumerate(self.security_control_property_controls):
            table_item = self.table.item(row, i)
            if hasattr(widget, "set_text"):
                widget.set_text(table_item.text() if table_item and table_item.text() else "")

        PVD.SecurityControls_display_selected_row(
            self.table,
            self.security_control_property_controls,
            self.security_property_list,
            self.property_panel_manager.property_panel,
            self.property_panel_manager.toggle_button
        )

    def update_button_states(self):
        selected_rows = self.table.selectionModel().selectedRows()
        enable = bool(selected_rows)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(True)
        if hasattr(self, 'submit_button'):
            self.submit_button.setEnabled(True)
        if hasattr(self, 'add_button'):
            self.add_button.setEnabled(True)


    def on_row_selection_changed(self, selected, deselected):
        if self.table.currentRow() >= 0:
            self.display_row_data_in_panel(None)

    def on_scc_property_name_changed(self): pass
    def on_scc_property_securityproperty_changed(self): pass
    def on_scc_property_description_changed(self): pass
    def on_scc_property_comment_changed(self): pass

    def closeEvent(self, event):
        event.accept()
