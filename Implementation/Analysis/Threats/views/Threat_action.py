"""
Module Name   : Threat_action.py \n
Layer         : Presentation / Threats \n
Module ID     : CY_SM_009 \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Updated By    : Vishnu Viswanath \n
Updated On    : 2025-06-03 \n

Purpose:
--------
Manages the Threats UI module, including dynamic construction of property panels,
handling table interaction, and emitting standardized signals to support Save and
selection-driven workflows.

Description:
------------
Combines threat-specific configuration with reusable UI building blocks from the
shared component layer. Renders labeled input fields in a panel based on configuration,
tracks table selections, synchronizes UI state, and emits signals for downstream actions
like saving or updating property values.

Responsibilities:
-----------------
- Dynamically build the Threat property panel
- Handle Add, Save, Submit, Delete actions from the UI
- Sync selected table row data with input widgets
- Emit structured signals for Save and selection changes

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
- Analysis.Threats.config.threats_config
- Analysis.controllers.analysis_TableValueLoad
- Analysis.controllers.analysis_TableRefreshRecord
- Analysis.controllers.analysis_TableSaveRecord
- Analysis.controllers.analysis_PropertyValueDisplay
- components.propertypanel.property_input_components
- components.action_panel
- components.table.table_panel
- components.propertypanel.property_panel_layout
- styles.property_panel_style
- controllers.DatabaseCreator
- controllers.TableValueHighlight
- utils.interface_utils
- components.loading_dialog.RoundLoader

Limitations:
------------
- Static mapping between table columns and input fields
- Validation is not embedded at field level
- Option lists must be manually refreshed from database

Improvements:
-------------
- Add validation hooks per field with feedback
- Refactor config handling for table-column mapping
- Introduce async loaders for smoother UI responsiveness

Change History:
---------------
+----------------+----------------------+-------------------------------------------------------------+----------------------+
| Version        | Date                 | Change                                                      | Author               |
+================+======================+=============================================================+======================+
| V 3.0          | 2025-06-03           | Added dynamic property panel and signal logic               | Vishnu Viswanath     |
+----------------+----------------------+-------------------------------------------------------------+----------------------+
|                |                      |                                                             |                      |
+----------------+----------------------+-------------------------------------------------------------+----------------------+
|                |                      |                                                             |                      |
+----------------+----------------------+-------------------------------------------------------------+----------------------+
"""

                             
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QTableWidgetItem


from Analysis.Threats.views.threats_toolbar_panel import create_toolbar
from Analysis.Threats.config.threats_config import PROPERTY_CONFIG, SAVE_BUTTON
from Analysis.Threats.controllers.threat_manager import load_all_threats, persist_threat_changes, refresh_threats_cache, update_threat
from controllers.schema_manager import get_instances
from components.propertypanel.property_input_components import PropertyInputFactory
from styles.property_panel_style import property_save_button_style
from PyQt5.QtCore import pyqtSignal
import controllers.TableValueHighlight as TVH
import components.table.table_row_indicator as TRI
import Analysis.controllers.analysis_PropertyValueDisplay as PVD
import components.action_panel as action_panel
import components.table.table_panel as table_panel
import components.propertypanel.property_panel_layout as property_panel_layout
import Analysis.models.analysis_synchronization as AS
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
from controllers.database_tables.target_of_evaluation_tables import Misusecases  # adjust import
from controllers.database_tables.analysis_tables import DamageScenarios  # adjust import to your model
from controllers.database_tables.target_of_evaluation_tables import TOEConfiguration  # adjust import
from components.table.multiselect_combo import MultiSelectComboSelector


class Threat_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    create_property_layout_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.misuse_cases_option_list = []
        self.damage_scenarios_option_list = []
        self.toe_configuration_option_list = []
        self.row_uuid_map = {}
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

        self.threat_property_controls = []

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

        # ---- Table panel setup (CORRECT WAY, like Damage Scenario) ----
        self.table_wrapper = table_panel.TablePanelWrapper(
            use_row_indicator=True, use_tree_indicator=False, parent=self
        )
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("threats")  # Set correct table headers

        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout

        # Add the ACTUAL table widget, not layout!
        self.action_panel_layout.addWidget(self.table_wrapper.table)
        self.action_panel_layout.addWidget(self.property_panel_manager.switch_property_panel)
        self.action_panel_layout.addWidget(self.property_panel_manager.property_panel)
        main_layout.addWidget(self.action_panel)

        # Enable/disable buttons
        self.submit_button.setEnabled(False)
        self.save_button.setEnabled(False)

        # Connect buttons to functions
        self.submit_button.clicked.connect(self.submit_changes)
        self.save_button.clicked.connect(self.submit_changes)

        # Connect table signals to state updater
        self.table.itemChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()
        self.previous_text = None

    def on_row_selection_changed(self, selected, deselected):
        """
        Handles row selection:
        - Emits structured row data
        - Highlights only the selected row's sidebar indicator (dot)
        - Updates property panel and button states
        """
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed(self.table)

        current_row = self.table.currentRow()
        total_rows = self.table.rowCount()

        # ✅ Highlight selected row's dot
        for row in range(total_rows):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, TRI.SidebarWidget):
                widget.set_selected(row == current_row)

        # ✅ Display data in property panel and emit signal
        if current_row >= 0:
            

            data = {
                "ID": self.table.item(current_row, 1).text() if self.table.item(current_row, 1) else "",
                "Name": self.table.item(current_row, 2).text() if self.table.item(current_row, 2) else "",
                "Damage Scenarios": self.table.item(current_row, 3).text() if self.table.item(current_row, 3) else "",
                "TOE Configuration": self.table.item(current_row, 4).text() if self.table.item(current_row, 4) else "",
                "Misuse Cases": self.table.item(current_row, 5).text() if self.table.item(current_row, 5) else "",
                "Asset": self.table.item(current_row, 8).text() if self.table.item(current_row, 8) else "",
                "Security Properties": self.table.item(current_row, 9).text() if self.table.item(current_row, 9) else "",
                "Reasoning": self.table.item(current_row, 10).text() if self.table.item(current_row, 10) else "",
                "Comments": self.table.item(current_row, 11).text() if self.table.item(current_row, 11) else ""
            }

            payload = {
                "sender": "Table",
                "event": "row_selected",
                "data": data
            }
            self.display_row_data_in_panel(payload["data"])
            self.row_selected.emit(payload)

        self.update_button_states()
        interfaces.unsaved_changes = temp

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

        # Update "Submit" button state
        self.submit_button.setEnabled(row_count > 0)

    def load_data(self):
        # ✅ Show loading animation
        self.loader = RoundLoader(self, label_text="Loading...")
        self.loader.show()
        QApplication.processEvents()

        # ✅ 1. Populate dropdown options
        self.damage_scenarios_option_list = [
            f"{ds.ds_id}::{ds.name}" for ds in get_instances(DamageScenarios)
        ]
        self.threat_damage_scenarios_input.additem(self.damage_scenarios_option_list)
        self.threat_damage_scenarios_input.set_text('')

        self.toe_configuration_option_list = [
            f"{toec.toe_configuration_id}::{toec.toe_configuration_name}" for toec in get_instances(TOEConfiguration)
        ]
        self.threat_toe_configuration_input.additem(self.toe_configuration_option_list)
        self.threat_toe_configuration_input.set_text('')

        self.misuse_cases_option_list = [
            f"{ms.misuse_cases_id}::{ms.misuse_cases_name}" for ms in get_instances(Misusecases)
        ]
        self.threat_misuse_cases_input.additem(self.misuse_cases_option_list)
        self.threat_misuse_cases_input.set_text('')

        # ✅ 2. Define mapping from UI headers → DB fields (used in table)
        self.threat_column_field_map = {
            "ID": "threat_id",
            "Name": "name",
            "Damage Scenarios": "ds_id",
            "TOE Configuration": "toe_configuration_id",
            "Misuse cases": "misuse_cases_id",
            "Initial AFR": "initia_afr",
            "Resid AFR": "resid_afr",
            "Asset": "asset_id",
            "Security Properties": "security_properties",
            "Reasoning": "reasoning",
            "Comments": "comments"
        }

        # ✅ 3. Specify which columns are dropdowns
        self.threat_dropdown_columns = {
            "Damage Scenarios": self.damage_scenarios_option_list,
            "TOE Configuration": self.toe_configuration_option_list,
            "Misuse cases": self.misuse_cases_option_list
        }

        threat_headers = list(self.threat_column_field_map.keys())  # Ordered list of headers

        # ✅ 4. Load threats from DB
        print("🔄 Loading threat records...")
        self.table.setRowCount(0)
        threats = load_all_threats()

        for row_idx, threat in enumerate(threats):
            self.table.insertRow(row_idx)
            is_selected = (row_idx == self.table.currentRow())
            self.table.setCellWidget(row_idx, 0, TRI.SidebarWidget(row_idx=row_idx, selected=is_selected))
            

            for col_idx, header in enumerate(threat_headers, start=1):  # assuming column 0 is checkbox/icon
                field = self.threat_column_field_map[header]
                value = getattr(threat, field, "") or ""

                if header in self.threat_dropdown_columns:
                    options = self.threat_dropdown_columns[header]
                    self.add_multiselect_to_table_cell(row_idx, col_idx, options, value, field)
                else:
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))

            # Map row to UUID for later updates
            self.row_uuid_map[row_idx] = threat.uuid

        # ✅ 5. Final cleanup
        interfaces.unsaved_changes = False
        self.loader.close()
        print("✅ Threat table loaded successfully.")

    def refresh_data(self):
        refresh_threats_cache()  # Clear and reload manager cache from DB
        self.load_data()      
   
    def submit_changes(self):
        """
        Collects all table data, updates the threat cache, and persists to DB.
        Uses column mapping based on header definitions.
        """
        self.table.setFocus()
        self.update_button_states()
        print("🚨 Submit button clicked")

        # ✅ Column index → DB field mapping
        column_field_map = {
            1: "threat_id",
            2: "name",
            3: "ds_id",  # ✅ Correct field for Damage Scenarios
            4: "toe_configuration_id",  # ✅ Correct field for TOE
            5: "misuse_cases_id",  # ✅ Correct field for Misuse Cases
            6: "initia_afr",  # ✅ matches model
            7: "resid_afr",   # ✅ matches model
            8: "asset_id",    # ✅ matches model
            9: "security_properties",
            10: "reasoning",
            11: "comments"
        }

        for row in range(self.table.rowCount()):
            uuid = self.row_uuid_map.get(row)
            if not uuid:
                continue

            update_dict = {}
            for col, field in column_field_map.items():
                widget = self.table.cellWidget(row, col)
                if widget and hasattr(widget, "selected_items"):
                    value = ", ".join(widget.selected_items())
                else:
                    item = self.table.item(row, col)
                    value = item.text() if item else ""

                update_dict[field] = value

            changed = update_threat(uuid, update_dict)
            if changed:
                print(f"✅ Updated threat instance → {uuid}")
            else:
                print(f"🟡 No changes for threat → {uuid}")

        persist_threat_changes()
        print("🗃️ All changes persisted to DB")
        interfaces.unsaved_changes = False




    def on_threat_property_name_changed(self): PVD.on_property_multiline_changed(self.table, 2, self.threat_name_input)
    def on_threat_property_DS_changed(self):
        PVD.on_property_multiselect_changed(self.table, 3, self.threat_damage_scenarios_input)

        row = self.table.currentRow()
        if row >= 0 and row in self.row_uuid_map:
            uuid = self.row_uuid_map[row]
            value = ", ".join(self.threat_damage_scenarios_input.selected_items())
            update_threat(uuid, {"ds_id": value})
            interfaces.unsaved_changes = True

    def on_threat_property_toec_changed(self):
        PVD.on_property_multiselect_changed(self.table, 4, self.threat_toe_configuration_input)

        row = self.table.currentRow()
        if row >= 0 and row in self.row_uuid_map:
            uuid = self.row_uuid_map[row]
            value = ", ".join(self.threat_toe_configuration_input.selected_items())
            update_threat(uuid, {"toe_configuration_id": value})
            interfaces.unsaved_changes = True

    def on_threat_property_MS_changed(self):
        PVD.on_property_multiselect_changed(self.table, 5, self.threat_misuse_cases_input)

        row = self.table.currentRow()
        if row >= 0 and row in self.row_uuid_map:
            uuid = self.row_uuid_map[row]
            value = ", ".join(self.threat_misuse_cases_input.selected_items())
            update_threat(uuid, {"misuse_cases_id": value})
            interfaces.unsaved_changes = True

    def on_threat_property_asset_changed(self): PVD.on_property_line_changed(self.table, 8, self.threat_asset_input)
    def on_threat_property_securityproperty_changed(self): PVD.on_property_line_changed(self.table, 9, self.threat_security_input)
    def on_threat_property_reasoning_changed(self): PVD.on_property_multiline_changed(self.table, 10, self.threat_reasoning_input)
    def on_threat_property_comment_changed(self): PVD.on_property_multiline_changed(self.table, 11, self.threat_comments_input)
    def display_selected_row(self):
        temp = interfaces.unsaved_changes
        # PVD.threat_display_selected_row(self.table, self.threat_property_controls, self.damage_scenarios_option_list,self.toe_configuration_option_list, self.misuse_cases_option_list,self.property_panel,self.toggle_button)
        interfaces.unsaved_changes = temp

    def closeEvent(self, event):
        event.accept()

    def build_property_panel(self):
        """
        Dynamically constructs the property input panel for Threats.

        Uses PROPERTY_CONFIG to render input widgets and bind signal handlers.
        Applies read-only state if configured, and attaches save button logic.
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
                controls_list=self.threat_property_controls,
                signal=signal_handler,
                items=items,
                setReadOnly=readonly
            )

            attr_name = f"threat_{label.lower().replace(' ', '_')}_input"
            setattr(self, attr_name, input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.threat_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)

    def handle_property_save_signal(self, payload):
        print(f"[TARA] 🔔 Threat Save Signal Received → {payload}")

    def display_row_data_in_panel(self, data):
        print("[DEBUG] display_row_data_in_panel called with:", data)
        row = self.table.currentRow()
        if row < 0:
            return

        # Map each field to its actual column index in the table
        label_column_map = {
            "ID": 1,
            "Name": 2,
            "Damage Scenarios": 3,
            "TOE Configuration": 4,
            "Misuse Cases": 5,
            "Asset": 8,
            "Security Properties": 9,
            "Reasoning": 10,
            "Comments": 11,
        }

        for label, widget in self.threat_property_controls:
            col = label_column_map.get(label)
            if col is None:
                continue

            table_item = self.table.item(row, col)
            cell_widget = self.table.cellWidget(row, col)

            # Multi-select
            if hasattr(widget, "set_selected_items"):
                text = table_item.text() if table_item else ""
                selected_items = [x.strip() for x in text.split(",") if x.strip()]
                widget.set_selected_items(selected_items)

            # Dropdown/single line
            elif hasattr(widget, "setCurrentText"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.setCurrentText(value)

            # Plain text
            elif hasattr(widget, "setText"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.setText(value)

            elif hasattr(widget, "setPlainText"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.setPlainText(value)

            elif hasattr(widget, "set_text"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.set_text(value)

        # Expand panel if hidden
        if self.property_panel_manager.toggle_button and not self.property_panel_manager.toggle_button.isChecked():
            self.property_panel_manager.toggle_button.click()

    def add_multiselect_to_table_cell(self, row_index, column_index, option_list, current_value, update_field):
        """
        Generic helper for adding MultiSelectComboSelector to Threats table.

        Args:
            row_index (int): Table row index.
            column_index (int): Table column index.
            option_list (list[str]): List of selectable options.
            current_value (str): Pre-selected value from DB (comma-separated string).
            update_field (str): Field to update in backend via `update_threat`.

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
            self.table.setItem(row_index, column_index, QTableWidgetItem(value))
            uuid = self.row_uuid_map.get(row_index)
            if uuid:
                update_threat(uuid, {update_field: value})
                interfaces.unsaved_changes = True

        combo.model().dataChanged.connect(on_selection_change)
        self.table.setCellWidget(row_index, column_index, combo)
        


