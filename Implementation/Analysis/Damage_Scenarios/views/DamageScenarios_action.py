"""
Module Name   : DamageScenarios_action.py \n
Layer         : Presentation / Damage Scenarios \n
Module ID     : CY_SM_008 \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Updated By    : Vishnu Viswanath \n
Updated On    : 2025-06-03 \n

Purpose:
--------
Manages the UI logic for handling Damage Scenario records in the application.
Handles property panel rendering, row selection events, table updates, and emitting
signals for Save and interaction tracking.

Description:
------------
Integrates damage-scenario-specific UI configuration with generic factory components
to construct dynamic property panels. Handles interaction logic for table selection,
data submission, Save actions, and synchronization of data with UI state.

Responsibilities:
-----------------
- Build property panels for Damage Scenario records
- Display data from selected rows in the property panel
- Enable Save/Add/Delete/Submit workflows
- Emit signals for Save and selection tracking

Signals:
--------
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+
| Trigger                | Signal Name            | Description                                 | Payload Format                                             |
+========================+========================+=============================================+============================================================+
| Save button clicked    | property_save_clicked  | Emits updated form data                     | {"sender": str, "event": "save", "data": dict}             |
| Table row selected     | row_selected           | Emits selected row's full data              | {"sender": "Table", "event": "row_selected", "data": dict} |
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+

Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore)
- Analysis.Damage_Scenarios.config.damage_scenarios_config
- components.propertypanel.property_input_components
- Analysis.controllers.analysis_PropertyValueDisplay
- Analysis.controllers.analysis_TableValueLoad
- styles.property_panel_style
- utils.interface_utils

Limitations:
------------
- Manual mapping between table columns and property fields
- Validation must be handled externally
- Table-column index logic is tightly coupled with widget sequence

Improvements:
-------------
- Add configurable column-field mapping layer
- Integrate inline validation with visual cues
- Support dynamic field grouping and layout templating

Change History:
---------------
+----------------+----------------------+------------------------------------------------+----------------------+
| Version        | Date                 | Change                                         | Author               |
+================+======================+================================================+======================+
| V 3.0          | 2025-06-03           | Added dynamic property panel and signal logic  | Vishnu Viswanath     |
+----------------+----------------------+------------------------------------------------+----------------------+
|                |                      |                                                |                      |
+----------------+----------------------+------------------------------------------------+----------------------+
|                |                      |                                                |                      |
+----------------+----------------------+------------------------------------------------+----------------------+
"""

                             
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QTableWidgetItem

import Analysis.controllers.analysis_TableValueLoad as TVL
import Analysis.controllers.analysis_TableAddRecord as TAR
import Analysis.controllers.analysis_TableRemoveRecord as TRR
import Analysis.controllers.analysis_TableSaveRecord as TSR
import Analysis.controllers.analysis_TableRefreshRecord as TFR 
import Analysis.controllers.analysis_PropertyValueDisplay as PVD
from Analysis.Damage_Scenarios.views.damagescenarios_toolbar_panel import create_toolbar
from Analysis.Damage_Scenarios.config.damage_scenarios_config import PROPERTY_CONFIG, SAVE_BUTTON
from components.table.multiselect_combo import MultiSelectComboSelector
from components.propertypanel.property_input_components import PropertyInputFactory
from styles.property_panel_style import property_save_button_style
import components.table.table_row_indicator as TRI
from PyQt5.QtCore import pyqtSignal
import controllers.TableValueHighlight as TVH
import components.action_panel as action_panel
import components.table.table_panel as table_panel
import components.propertypanel.property_panel_layout as property_panel_layout
from components.table.multiselect_combo import MultiSelectComboSelector
import Analysis.models.analysis_synchronization as AS
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
from models.unique_name_action import refrash_existing_entries, find_duplicates, store_selected_entry
import Analysis.Damage_Scenarios.controllers.damage_scenario_manager as DSM
from PyQt5.QtWidgets import QComboBox

class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()
class DS_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    create_property_layout_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # --- KEY: Connect selection change to property panel signal ---
        

        self.HEIGHT_MAP = {}
        self.STYLE_MAP = {}

        self.property_panel_manager = property_panel_layout.PropertyPanelManager(self)
        self.property_panel_manager.create_property_panel()

        self.toggle_button = self.property_panel_manager.toggle_button
        self.property_panel = self.property_panel_manager.property_panel
        self.property_layout = self.property_panel_manager.property_layout  # ✅ emit it

        self.DS_property_controls = []

        self.create_property_panel_signal.connect(self.build_property_panel)
        self.create_property_panel_signal.emit()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Toolbar
        create_toolbar(self)
        main_layout.addWidget(self.toolbar)

        # Action panel
        action_panel.create_action_panel(self)

        # Table wrapper setup
        self.table_wrapper = table_panel.TablePanelWrapper(
            use_row_indicator=True, use_tree_indicator=False, parent=self
        )
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("damage_scenarios")  # Table key for your headers

        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
        self.row_selected.connect(self.display_row_data_in_panel)
        # Compose layout
        self.action_panel_layout.addWidget(self.table_wrapper.table)
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
        self.table.itemChanged.connect(self.on_table_item_changed)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)  # <--- THIS IS CRITICAL
        self.update_button_states()
        self.previous_text = None
    def on_row_selection_changed(self, selected, deselected):
        """
        Handles row selection:
        - Emits structured row data
        - Highlights only the selected row's sidebar indicator (dot)
        - Updates property panel and button states
        """
        print("Table selection changed!")  # DEBUG
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed(self.table)

        current_row = self.table.currentRow()
        total_rows = self.table.rowCount()

        # ✅ Highlight selected dot
        for row in range(total_rows):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, TRI.SidebarWidget):
                widget.set_selected(row == current_row)

        # ✅ Display data in property panel
        if current_row >= 0:
            self.display_row_data_in_panel(None)

            # ✅ Emit signal
            data = {
                "ID": self.table.item(current_row, 1).text() if self.table.item(current_row, 1) else "",
                "Name": self.table.item(current_row, 2).text() if self.table.item(current_row, 2) else "",
                "Impact": self.table.item(current_row, 3).text() if self.table.item(current_row, 3) else "",
                "Impact Category": self.table.item(current_row, 4).text() if self.table.item(current_row, 4) else "",
                "Reasoning": self.table.item(current_row, 5).text() if self.table.item(current_row, 5) else "",
                "Comments": self.table.item(current_row, 6).text() if self.table.item(current_row, 6) else ""
            }
            payload = {
                "sender": "Table",
                "event": "row_selected",
                "data": data
            }
            self.row_selected.emit(payload)
            print("Signal emitted!", payload)  # DEBUG

        # ✅ Button enable/disable
        self.update_button_states()
        interfaces.unsaved_changes = temp

    
    def on_table_item_changed(self, item):
        # Defensive: skip if table is empty or no uuid map
        row = item.row()
        if not hasattr(self, 'row_uuid_map') or row not in self.row_uuid_map:
            return
        uuid = self.row_uuid_map.get(row)
        if uuid:
            ds_updates = {
                "ds_id": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "name": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                "impact": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                "impact_category": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                "description": self.table.item(row, 5).text() if self.table.item(row, 5) else "",
                "comments": self.table.item(row, 6).text() if self.table.item(row, 6) else "",
            }
            DSM.update_damage_scenario(uuid, ds_updates)
            interfaces.unsaved_changes = True

    def select_first_row(self): 
        if self.table.rowCount() > 0: self.table.setCurrentCell(0, 1)

    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True

    def update_button_states(self):
        """
        Updates the state of the Save and Delete buttons based on the table's state.
        """
        row_count = self.table.rowCount()
        has_selection = bool(self.table.selectionModel().selectedRows())

        # ✅ Safely check before accessing
        if hasattr(self, 'save_button') and self.save_button:
            self.save_button.setEnabled(row_count > 0)

        self.delete_button.setEnabled(row_count > 0 and has_selection)
        self.submit_button.setEnabled(row_count > 0)

    def load_data(self):
        print("check111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111")
        QApplication.processEvents()
        try:
            self.table.itemChanged.disconnect(self.find_duplicates)
        except (TypeError, RuntimeError):
            pass

        self.table.setRowCount(0)
        scenarios = DSM.load_all_damage_scenarios()
        self.row_uuid_map = {}

        for row_idx, ds in enumerate(scenarios):
            try:
                self.table.insertRow(row_idx)
                is_selected = (row_idx == self.table.currentRow())
                self.table.setCellWidget(row_idx, 0, TRI.SidebarWidget(row_idx=row_idx, selected=is_selected))
                self.table.setItem(row_idx, 1, QTableWidgetItem(ds.ds_id))
                self.table.setItem(row_idx, 2, QTableWidgetItem(ds.name))
                self.add_combo_to_impact_cell(row_idx, ds.impact)
                self.add_multiselect_to_impact_category_cell(row_idx, ds.impact_category)
                self.table.setItem(row_idx, 5, QTableWidgetItem(ds.description))
                self.table.setItem(row_idx, 6, QTableWidgetItem(ds.comments))
                self.row_uuid_map[row_idx] = ds.uuid
            except Exception as e:
                print(f"Row {row_idx} error: {e}")

        interfaces.unsaved_changes = False
        self.table.itemChanged.connect(self.find_duplicates)

    def find_duplicates(self, changed_item):
        row = self.table.currentRow()
        column = self.table.currentColumn()
        if row >=0 and column>=0:
            if column!= 2: return
        find_duplicates(self, changed_item)
    
    def store_selected_entry(self, item): store_selected_entry(self, item)
    
    def refrash_existing_entries(self): refrash_existing_entries(self)
    
    def refresh_data(self): TFR.DS_refresh_data(self.table)
    
    def add_new_entry(self):
        self.table.setFocus()
        try:
            self.table.itemChanged.disconnect(self.find_duplicates)
        except (TypeError, RuntimeError):
            pass

        row_idx = self.table.rowCount()
        DSM.create_damage_scenario_and_insert_row(self)
        self.add_combo_to_impact_cell(row_idx, "")
        self.add_multiselect_to_impact_category_cell(row_idx, "")
        self.update_button_states()
        interfaces.unsaved_changes = True
        self.table.itemChanged.connect(self.find_duplicates)

    def delete_entry(self): 
        # Get selected rows (may be multiple!)
        selected_rows = sorted(self.table.selectionModel().selectedRows(), key=lambda x: x.row(), reverse=True)
        for index in selected_rows:
            row = index.row()
            uuid = self.row_uuid_map.get(row)
            if uuid:
                DSM.delete_damage_scenario(uuid)  # <-- ORM manager
                self.table.removeRow(row)
                # After removal, rebuild row_uuid_map:
                self.row_uuid_map = {i: self.row_uuid_map[k] for i, k in enumerate([k for k in sorted(self.row_uuid_map) if k != row])}
        self.update_button_states()
        self.refrash_existing_entries()

    def submit_changes(self): 
        self.table.setFocus()
        DSM.persist_damage_scenario_changes()  # <-- ORM manager
        self.update_button_states()
        interfaces.unsaved_changes = False

    def on_DS_property_name_changed(self): PVD.on_property_multiline_changed(self.table, 2, self.DS_name_input)
    def on_DS_property_impact_changed(self):
        new_value = self.DS_impact_input.currentText()
        print("Impact change fired:", new_value)
        PVD.on_property_singleselect_changed(self.table, 3, self.DS_impact_input)

        row = self.table.currentRow()
        if hasattr(self, 'row_uuid_map') and row in self.row_uuid_map:
            uuid = self.row_uuid_map[row]
            DSM.update_damage_scenario(uuid, {"impact": new_value})
            interfaces.unsaved_changes = True

    def on_DS_property_impactcategory_changed(self):
        PVD.on_property_multiselect_changed(self.table, 4, self.DS_impact_category_input)

        row = self.table.currentRow()
        if row >= 0 and hasattr(self, 'row_uuid_map') and row in self.row_uuid_map:
            uuid = self.row_uuid_map[row]
            selected = self.DS_impact_category_input.selected_items()
            value = ", ".join(selected)
            DSM.update_damage_scenario(uuid, {"impact_category": value})
            interfaces.unsaved_changes = True

    def on_DS_property_description_changed(self): PVD.on_property_multiline_changed(self.table, 5, self.DS_reasoning_input)
    def on_DS_property_comment_changed(self): PVD.on_property_multiline_changed(self.table, 6, self.DS_comments_input)
    def display_selected_row(self):  
        temp = interfaces.unsaved_changes
        # PVD.ds_display_selected_row(self.table, self.DS_property_controls,self.property_panel,self.toggle_button)
        interfaces.unsaved_changes = temp

    def closeEvent(self, event):
        event.accept()

    def build_property_panel(self):
        """
        Dynamically builds the property input panel for Damage Scenarios using PROPERTY_CONFIG.
        """
        self.property_factory = PropertyInputFactory()
        for field in PROPERTY_CONFIG:
            label = field["label"]
            input_type = field["type"]
            signal_handler = getattr(self, field.get("signal")) if field.get("signal") else None
            items = field.get("items", None)
            readonly = field.get("readonly", False)

            input_widget = self.property_factory.create_common_property_input(
                label_text=label,
                input_type=input_type,
                layout=self.property_layout,
                controls_list=self.DS_property_controls,
                signal=signal_handler,
                items=items,
                setReadOnly=readonly
            )

            attr_name = f'DS_{label.lower().replace(" ", "_")}_input'
            setattr(self, attr_name, input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.DS_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)

    def handle_property_save_signal(self, payload):
        print(f"[TARA] 🔔 Signal Received → {payload}")

    def display_row_data_in_panel(self, data):
        """
        Loads and displays the selected table row's data into the property panel.

        Uses table values to set each field in the DS_property_controls panel
        by mapping column index to widget values.
        """
        print("[DEBUG] display_row_data_in_panel called with:", data)
        row = self.table.currentRow()
        if row < 0:
            return

        for i, (label, widget) in enumerate(self.DS_property_controls):
            col = i + 1  # Skip sidebar (column 0)
            table_item = self.table.item(row, col)
            cell_widget = self.table.cellWidget(row, col)

            # 🔁 For multi-select / combo box
            if hasattr(widget, "set_selected_items"):
                text = table_item.text() if table_item else ""
                selected_items = [x.strip() for x in text.split(",")] if text else []
                widget.set_selected_items(selected_items)

            # 🔁 For combo box (single-select)
            elif hasattr(widget, "setCurrentText"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.setCurrentText(value)

            # 🔁 For plain text or multi-line fields
            elif hasattr(widget, "setText"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.setText(value)

            elif hasattr(widget, "setPlainText"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.setPlainText(value)

            elif hasattr(widget, "set_text"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.set_text(value)

        # Optional: open the panel if it’s collapsed
        if self.property_panel_manager.toggle_button and not self.property_panel_manager.toggle_button.isChecked():
            self.property_panel_manager.toggle_button.click()

    def add_combo_to_impact_cell(self, row_index, current_value=None):
        from models.helper import DS_impact_menu
        combo = NoScrollComboBox()
        combo.addItems(["Select"] + DS_impact_menu)
        if current_value and current_value in DS_impact_menu:
            combo.setCurrentText(current_value)
        else:
            combo.setCurrentIndex(0)  # "Select"

        # Update table item on selection change
        def on_impact_changed(idx):
            value = combo.currentText()
            self.table.setItem(row_index, 3, QTableWidgetItem(value if value != "Select" else ""))
            # Optionally: update backend here too
            if hasattr(self, 'row_uuid_map') and row_index in self.row_uuid_map:
                uuid = self.row_uuid_map[row_index]
                DSM.update_damage_scenario(uuid, {"impact": value if value != "Select" else ""})
                interfaces.unsaved_changes = True

        combo.currentIndexChanged.connect(on_impact_changed)
        self.table.setCellWidget(row_index, 3, combo)

    def add_multiselect_to_impact_category_cell(self, row_index, current_value=None):
        from models.helper import DS_impactcatagory_menu
     
        combo = MultiSelectComboSelector(DS_impactcatagory_menu, placeholder="Select")
        if current_value:
            if isinstance(current_value, str):
                selected_items = [x.strip() for x in current_value.split(",") if x.strip()]
            else:
                selected_items = current_value
            print(f"[DEBUG] Setting selected items for row {row_index}: {selected_items}")
            combo.set_selected_items(selected_items)

        def on_selection_change():
            value = ", ".join(combo.selected_items())
            print(f"[DEBUG] on_selection_change for row {row_index}: value to set in table: {value}")
            self.table.setItem(row_index, 4, QTableWidgetItem(value))
            if hasattr(self, 'row_uuid_map') and row_index in self.row_uuid_map:
                uuid = self.row_uuid_map[row_index]
                print(f"[DEBUG] Updating backend for row {row_index}, uuid {uuid}, value: {value}")
                DSM.update_damage_scenario(uuid, {"impact_category": value})
                interfaces.unsaved_changes = True

        combo.model().dataChanged.connect(on_selection_change)
        self.table.setCellWidget(row_index, 4, combo)
