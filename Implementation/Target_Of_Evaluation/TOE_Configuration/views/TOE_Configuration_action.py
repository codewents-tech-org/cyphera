from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSignal,Qt
import logging


# Toolbar, Config, Styling
from Target_Of_Evaluation.TOE_Configuration.views.toeconfiguration_toolbar_panel import create_toolbar
from Target_Of_Evaluation.TOE_Configuration.config.toe_configuration_config import PROPERTY_CONFIG, SAVE_BUTTON
from styles.property_panel_style import property_save_button_style

# UI Components
import components.action_panel as action_panel
import components.table.table_panel as table_panel
import components.propertypanel.property_panel_layout as property_panel_layout
from components.propertypanel.property_input_components import PropertyInputFactory
from components.loading_dialog import RoundLoader
from Target_Of_Evaluation.TOE_Configuration.controllers.TOE_Configuration_manager import update_toe_configuration

# Controller Logic
import Target_Of_Evaluation.TOE_Configuration.controllers.toec_PropertyValueDisplay as PVD
from Target_Of_Evaluation.TOE_Configuration.controllers.TOE_Configuration_manager import (
    load_all_toe_configurations,
    create_toe_and_insert_row,
    delete_toe_configuration,
    persist_toe_configuration_changes,
    TOEC_CACHE
)

# Utilities
import utils.interface_utils as interfaces
from models.unique_name_action import refrash_existing_entries, find_duplicates, store_selected_entry
import controllers.TableValueHighlight as TVH
import components.table.table_row_indicator as TRI

logger = logging.getLogger(__name__)

class TOEConfigurationModule(QWidget):
    create_property_panel_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        logger.info("TOE Configuration table view Initiated")
        self.initUI()

    def initUI(self):
        self.row_selected.connect(self.display_row_data_in_panel)

        self.HEIGHT_MAP = {}
        self.STYLE_MAP = {}

        self.property_panel_manager = property_panel_layout.PropertyPanelManager(self)
        self.property_panel_manager.create_property_panel()

        self.toggle_button = self.property_panel_manager.toggle_button
        self.property_panel = self.property_panel_manager.property_panel
        self.property_layout = self.property_panel_manager.property_layout      # ✅ emit it

        self.MisuseCases_property_controls = []

        self.create_property_panel_signal.connect(self.build_property_panel)
        self.create_property_panel_signal.emit()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        create_toolbar(self)
        main_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)

        # ----------- Fix: TablePanelWrapper as object -----------
        self.table_wrapper = table_panel.TablePanelWrapper(use_row_indicator=True, use_tree_indicator=False, parent=self)
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("toe_configuration")  # Replace with your table key if needed

        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout
        # --------------------------------------------------------

        # Add the table to the action panel
        self.action_panel_layout.addWidget(self.table)
        self.action_panel_layout.addWidget(self.property_panel_manager.switch_property_panel)
        self.action_panel_layout.addWidget(self.property_panel_manager.property_panel)
        main_layout.addWidget(self.action_panel)

        # Enable/disable buttons
        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)
        self.save_button.setEnabled(False)

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_new_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.submit_button.clicked.connect(self.submit_changes)
        self.save_button.clicked.connect(self.submit_changes)

        # Connect table signals to state updater
        self.existing_entries = set()
        self.table.itemChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.itemDoubleClicked.connect(self.store_selected_entry)
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
        self.update_button_states()
        self.previous_text = None


    def on_row_selection_changed(self, selected, deselected):
        temp = interfaces.unsaved_changes
        current_row = self.table.currentRow()

        # ✅ Update property panel
        if current_row >= 0:
            self.display_selected_row()
            self.display_row_data_in_panel(None)

            # ✅ Emit selected row data
            data = {
                "ID": self.table.item(current_row, 1).text() if self.table.item(current_row, 1) else "",
                "Name": self.table.item(current_row, 2).text() if self.table.item(current_row, 2) else "",
                "Description": self.table.item(current_row, 3).text() if self.table.item(current_row, 3) else "",
                "Comments": self.table.item(current_row, 4).text() if self.table.item(current_row, 4) else ""
            }
            payload = {"sender": "Table", "event": "row_selected", "data": data}
            self.row_selected.emit(payload)

        # ✅ Dot highlight update (e.g., sidebar indicator)
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, TRI.SidebarWidget):
                widget.set_selected(row == current_row)

        # ✅ Track selection for unsaved state
        TVH.on_row_selection_changed(self.table)

        # ✅ Update Add/Save/Delete button states
        self.update_button_states()
        
        interfaces.unsaved_changes = temp

    def select_first_row(self):
        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 1)

    def update_button_states(self):
        row_count = self.table.rowCount()
        has_selection = bool(self.table.selectionModel().selectedRows())

        if hasattr(self, 'save_button') and self.save_button:
            self.save_button.setEnabled(row_count > 0)

        self.delete_button.setEnabled(row_count > 0 and has_selection)
        self.submit_button.setEnabled(row_count > 0)

    def load_data(self):
        self.loader = RoundLoader(self, label_text="Loading TOE Configurations...")
        self.loader.show()
        QApplication.processEvents()

        try:
            self.table.itemChanged.disconnect(self.find_duplicates)
        except TypeError:
            pass

        self.table.setRowCount(0)
        self.row_uuid_map = {}

        records = load_all_toe_configurations()
        for row_index, record in enumerate(records):
            self.table.insertRow(row_index)
            is_selected = (row_index == self.table.currentRow())
            self.table.setCellWidget(row_index, 0, TRI.SidebarWidget(row_idx=row_index, selected=is_selected))
            self.table.setItem(row_index, 1, QTableWidgetItem(record.toe_configuration_id))
            self.table.setItem(row_index, 2, QTableWidgetItem(record.toe_configuration_name))
            self.table.setItem(row_index, 3, QTableWidgetItem(record.toe_configuration_description or ""))
            self.table.setItem(row_index, 4, QTableWidgetItem(record.toe_configuration_comments or ""))
            self.row_uuid_map[row_index] = record.uuid

        interfaces.unsaved_changes = False
        self.table.itemChanged.connect(self.find_duplicates)
        self.loader.close()


    def add_new_entry(self):
        self.table.setFocus()
        try:
            self.table.itemChanged.disconnect(self.find_duplicates)
        except TypeError:
            pass

        create_toe_and_insert_row(self)

        self.update_button_states()
        interfaces.unsaved_changes = True

        self.table.itemChanged.connect(self.find_duplicates)


    def delete_entry(self):
        selected_rows = sorted(self.table.selectionModel().selectedRows(), key=lambda x: x.row(), reverse=True)
        if not selected_rows:
            return

        for index in selected_rows:
            row = index.row()
            uuid = self.row_uuid_map.get(row)
            if not uuid:
                logger.warning(f"No UUID found for row {row}. Skipping deletion.")
                continue

            delete_toe_configuration(uuid)
            self.table.removeRow(row)

        new_map = {}
        for row in range(self.table.rowCount()):
            toe_id_item = self.table.item(row, 1)
            if toe_id_item:
                toe_id = toe_id_item.text().strip()
                for uuid, entry in TOEC_CACHE.items():
                    if entry['record'].toe_configuration_id == toe_id:
                        new_map[row] = uuid
                        break

        self.row_uuid_map = new_map
        self.table_data_changed = True
        interfaces.unsaved_changes = True
        self.update_button_states()

    def submit_changes(self):
        persist_toe_configuration_changes()
        self.update_button_states()
        interfaces.unsaved_changes = False

    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True

    def on_toec_property_name_changed(self):
        PVD.on_property_multiline_changed(self.table, 2, self.toe_name_input)

    def on_toec_property_description_changed(self):
        PVD.on_property_multiline_changed(self.table, 3, self.toe_description_input)

    def on_toec_property_comment_changed(self):
        PVD.on_property_multiline_changed(self.table, 4, self.toe_comments_input)

    def display_selected_row(self):
        PVD.display_selected_row(self.table, self.toe_property_controls, self.property_panel, self.toggle_button)

    def closeEvent(self, event):
        event.accept()

    def build_property_panel(self):
        self.property_factory = PropertyInputFactory()
        self.toe_property_controls = []

        for field in PROPERTY_CONFIG:
            input_widget = self.property_factory.create_common_property_input(
                field["label"],
                field["type"],
                self.property_layout,
                self.toe_property_controls,
                getattr(self, field.get("signal")) if field.get("signal") else None,
                field.get("items")
            )

            if field.get("readonly"):
                input_widget.setReadOnly(True)
            setattr(self, f'toe_{field["label"].lower().replace(" ", "_")}_input', input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.toe_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)

    def handle_property_save_signal(self, payload):
        print(f"[TARA] 🔔 TOE Configuration Save Signal Received → {payload}")

        if not payload or payload.get("sender") != "Property panel":
            return

        data = payload.get("data", {})
        toe_id = data.get("ID")
        name = data.get("Name")
        description = data.get("Description")
        comments = data.get("Comments")

        # Step 1: Find matching UUID
        uuid = None
        for u, entry in TOEC_CACHE.items():
            if entry['record'].toe_configuration_id == toe_id:
                uuid = u
                break

        if not uuid:
            print(f"[❌] No record found for TOE ID {toe_id}")
            return

        # Step 2: Update in-memory cache
        updated = update_toe_configuration(uuid, {
            'toe_configuration_name': name,
            'toe_configuration_description': description,
            'toe_configuration_comments': comments
        })

        if updated:
            print(f"✅ Cached TOE {toe_id} marked for update.")
            persist_toe_configuration_changes()
            print("✅ Changes persisted to DB.")
        else:
            print(f"⚠️ No changes detected for TOE {toe_id}.")

    def display_row_data_in_panel(self, data):
        row = self.table.currentRow()
        for i, (label, widget) in enumerate(self.toe_property_controls):
            table_item = self.table.item(row, i + 1)
            cell_widget = self.table.cellWidget(row, i + 1)
            should_clear = False

            if hasattr(widget, "selected_items") or hasattr(widget, "get_selected_items"):
                if not (hasattr(cell_widget, "selected_items") and cell_widget.selected_items()):
                    should_clear = True
                if should_clear and hasattr(widget, "set_text"):
                    widget.set_text([])
                continue

            if table_item is None or not table_item.text().strip():
                should_clear = True

            if should_clear:
                if hasattr(widget, "set_text"):
                    widget.set_text("")
                elif hasattr(widget, "setPlainText"):
                    widget.setPlainText("")
                elif hasattr(widget, "setText"):
                    widget.setText("")
                elif hasattr(widget, "setCurrentText"):
                    widget.setCurrentText("")
                elif hasattr(widget, "clear"):
                    widget.clear()

        PVD.display_selected_row(
            self.table,
            self.toe_property_controls,
            self.property_panel_manager.property_panel,
            self.property_panel_manager.toggle_button
        )

    def refrash_existing_entries(self):
        self.existing_entries = set()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 2)  # Column 2 is the Name field
            if item:
                self.existing_entries.add(item.text().strip())


    def find_duplicates(self, item):
        if not item:
            return
        row = item.row()
        column = item.column()

        if column == 2:  # Only check 'Name' column
            self.refrash_existing_entries()

            current_value = item.text().strip()
            duplicates = [
                r for r in range(self.table.rowCount())
                if r != row and self.table.item(r, 2) and self.table.item(r, 2).text().strip() == current_value
            ]

            if duplicates:
                item.setBackground(Qt.red)
            else:
                item.setBackground(Qt.white)
                
    def store_selected_entry(self, item):
        store_selected_entry(self, item)

    def ensure_row_selection(self):
        if self.table.rowCount() > 0 and not self.table.selectionModel().hasSelection():
            self.table.selectRow(0)
