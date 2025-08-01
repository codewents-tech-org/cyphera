"""
Module Name   : ThreatScenarios_action.py \n
Layer         : Presentation / Threat Scenarios \n
Module ID     : CY_SM_010 \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Updated By    : Vishnu Viswanath \n
Updated On    : 2025-06-03 \n

Purpose:
--------
Manages the Threat Scenarios UI module, supporting the creation of dynamic
property panels, loading and saving scenario data, and handling interactions
between the table and property input widgets.

Description:
------------
Uses reusable factory-based components and external configuration to construct
the property panel. Handles table selection and state management while ensuring
UI consistency. Supports data loading, synchronization, and signal-based interaction
for Save operations and selection updates.

Responsibilities:
-----------------
- Render the Threat Scenario property panel using dynamic configuration
- Handle table row selection and map it to property input fields
- Emit Save and selection signals with structured payloads
- Load TOE configuration data dynamically
- Coordinate with action and table panels

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
- Analysis.Threat_Scenarios.config.threat_scenarios_config
- Analysis.controllers.analysis_TableValueLoad
- Analysis.controllers.analysis_TableSaveRecord
- Analysis.controllers.analysis_TableRefreshRecord
- Analysis.controllers.analysis_PropertyValueDisplay
- components.propertypanel.property_input_components
- components.propertypanel.property_panel_layout
- components.action_panel
- components.table.table_panel
- styles.property_panel_style
- utils.interface_utils
- controllers.TableValueHighlight
- controllers.DatabaseCreator
- components.loading_dialog.RoundLoader

Limitations:
------------
- Manual mapping between column index and property field names
- Limited validation for inputs (handled externally)
- Dependent on consistent data schema from table and configuration

Improvements:
-------------
- Introduce field-level validation feedback
- Refactor item mapping to support header-based key resolution
- Modularize property panel construction for testing and reuse

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
from components.table.multiselect_combo import MultiSelectComboSelector
from PyQt5.QtCore import Qt                          
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel, QTableWidgetItem

import Analysis.controllers.analysis_TableValueLoad as TVL
import Analysis.controllers.analysis_TableAddRecord as TAR
import Analysis.controllers.analysis_TableRemoveRecord as TRR
import Analysis.controllers.analysis_TableSaveRecord as TSR
import Analysis.controllers.analysis_TableRefreshRecord as TFR 
import Analysis.controllers.analysis_PropertyValueDisplay as PVD
from Analysis.Threat_Scenarios.views.threatscenarios_toolbar_panel import create_toolbar
from Analysis.Threat_Scenarios.config.threat_scenarios_config import PROPERTY_CONFIG, SAVE_BUTTON
from Analysis.Threat_Scenarios.controller.threat_scenario_manager import load_all_threat_scenarios, persist_threat_scenario_changes, update_threat_scenario
from models.helper import TS_header
from controllers.database_tables.target_of_evaluation_tables import TOEConfiguration
from controllers.schema_manager import get_instances
from components.propertypanel.property_input_components import PropertyInputFactory
from styles.property_panel_style import property_save_button_style
from PyQt5.QtCore import pyqtSignal
import controllers.TableValueHighlight as TVH
import components.table.table_row_indicator as TRI
import controllers.DatabaseCreator as DB
import components.action_panel as action_panel
import components.table.table_panel as table_panel
import components.propertypanel.property_panel_layout as property_panel_layout
import Analysis.models.analysis_synchronization as AS
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader


class TS_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    create_property_layout_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
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
        self.property_layout = self.property_panel_manager.property_layout  # ✅ emit it

        self.ts_property_controls = []

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

        # ---- Table panel setup (Same style as Threat module) ----
        self.table_wrapper = table_panel.TablePanelWrapper(
            use_row_indicator=True, use_tree_indicator=False, parent=self
        )
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("threat_scenarios")  # ✅ Correct table header mapping

        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout

        # Add actual widgets to layout
        self.action_panel_layout.addWidget(self.table_wrapper.table)
        self.action_panel_layout.addWidget(self.property_panel_manager.switch_property_panel)
        self.action_panel_layout.addWidget(self.property_panel_manager.property_panel)
        main_layout.addWidget(self.action_panel)

        # Enable/disable buttons
        self.submit_button.setEnabled(False)
        self.save_button.setEnabled(False)

        # Connect buttons
        self.submit_button.clicked.connect(self.submit_changes)
        self.save_button.clicked.connect(self.submit_changes)

        # Connect table signals
        self.table.itemChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()
        self.previous_text = None

    def on_row_selection_changed(self, selected, deselected):
        """
        Handles row selection:
        - Highlights sidebar dot for selected row
        - Emits structured row data for property panel update
        - Updates action button states
        """
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed(self.table)

        current_row = self.table.currentRow()
        total_rows = self.table.rowCount()

        # ✅ Highlight the selected row's dot
        for row in range(total_rows):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, TRI.SidebarWidget):
                widget.set_selected(row == current_row)

        # ✅ Emit data and display in property panel
        if current_row >= 0:
            self.display_row_data_in_panel(None)

            data = {
                "ID": self.table.item(current_row, 1).text() if self.table.item(current_row, 1) else "",
                "Threat": self.table.item(current_row, 2).text() if self.table.item(current_row, 2) else "",
                "Damage Scenarios": self.table.item(current_row, 3).text() if self.table.item(current_row, 3) else "",
                "TOE Configuration": self.table.item(current_row, 4).text() if self.table.item(current_row, 4) else "",
                "Reasoning": self.table.item(current_row, 5).text() if self.table.item(current_row, 5) else "",
                "Comments": self.table.item(current_row, 6).text() if self.table.item(current_row, 6) else ""
            }

            payload = {
                "sender": "Table",
                "event": "row_selected",
                "data": data
            }
            self.row_selected.emit(payload)

        self.update_button_states()
        interfaces.unsaved_changes = temp

    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True

    def select_first_row(self): 
        if self.table.rowCount() > 0: self.table.setCurrentCell(0, 1)

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

        # ✅ 1. Load dropdown options
        self.toe_configuration_option_list = [
            f"{toe.toe_configuration_id}::{toe.toe_configuration_name}"
            for toe in get_instances(TOEConfiguration)
        ]
        self.TS_toe_configuration_input.additem(self.toe_configuration_option_list)
        self.TS_toe_configuration_input.set_text('')

        # ✅ 2. Column → DB Field Mapping
        self.ts_column_field_map = {
            "ID": "ts_id",
            "Threat": "threat_id",
            "Damage Scenarios": "ds_id",
            "TOE Configuration": "toe_configuration_id",
            "Reasoning": "reasoning",
            "Comments": "comments"
        }

        # ✅ 3. Columns that use dropdowns
        self.ts_dropdown_columns = {
            "TOE Configuration": self.toe_configuration_option_list
        }

        ts_headers = list(self.ts_column_field_map.keys())
        self.table.setRowCount(0)

        # ✅ 4. Load rows from DB
        print("🔄 Loading threat scenario records...")
        threat_scenarios = load_all_threat_scenarios()

        for row_idx, ts in enumerate(threat_scenarios):
            self.table.insertRow(row_idx)
            is_selected = (row_idx == self.table.currentRow())
            self.table.setCellWidget(row_idx, 0, TRI.SidebarWidget(row_idx=row_idx, selected=is_selected))

            for col_idx, header in enumerate(ts_headers, start=1):  # skip icon col
                field = self.ts_column_field_map[header]
                value = getattr(ts, field, "") or ""

                if header in self.ts_dropdown_columns:
                    options = self.ts_dropdown_columns[header]
                    self.add_multiselect_to_table_cell(row_idx, col_idx, options, value, field)
                else:
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))

            # ✅ Store UUID for later update tracking
            self.row_uuid_map[row_idx] = ts.uuid

        # ✅ 5. Finalize
        interfaces.unsaved_changes = False
        self.loader.close()
        print("✅ ThreatScenario table loaded successfully.")


    def refresh_data(self): TFR.TS_refresh_data(self.table)
    def submit_changes(self): 
        self.table.setFocus()
        self.update_button_states()
        persist_threat_scenario_changes()
        interfaces.unsaved_changes = False

    def on_TS_property_threat_changed(self): PVD.on_property_line_changed(self.table, 2, self.TS_threat_input)
    def on_TS_property_DS_changed(self): PVD.on_property_multiselect_changed(self.table, 3, self.TS_DS_input)
    def on_TS_property_toec_changed(self): PVD.on_property_multiselect_changed(self.table, 4, self.TS_toec_input)
    def on_TS_property_reasoning_changed(self): PVD.on_property_multiline_changed(self.table, 5, self.TS_reasoning_input)
    def on_TS_property_comment_changed(self): PVD.on_property_multiline_changed(self.table, 6, self.TS_comments_input)
    def display_selected_row(self): 
        temp = interfaces.unsaved_changes
        # PVD.ts_display_selected_row(self.table, self.TS_property_controls, self.toes,self.property_panel,self.toggle_button)
        interfaces.unsaved_changes = temp

    def closeEvent(self, event):
       event.accept()

    def build_property_panel(self):
        """
        Dynamically builds the Threat Scenario property input panel using PROPERTY_CONFIG.

        - Uses PropertyInputFactory to render fields and bind handlers.
        - Assigns widget attributes like TS_threat_input.
        - Appends each label-widget pair to self.ts_property_controls.
        - Creates a Save button if enabled in config.
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
                controls_list=self.ts_property_controls,
                signal=signal_handler,
                items=items,
                setReadOnly=readonly
            )

            # Attribute like: self.TS_threat_input
            attr_name = f"TS_{label.lower().replace(' ', '_')}_input"
            setattr(self, attr_name, input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.ts_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)


    def handle_property_save_signal(self, payload):
        print(f"[TARA] 🔔 Threat Scenario Save Signal Received → {payload}")

    def display_row_data_in_panel(self, data):
        """
        Loads selected threat scenario row data into the property panel using
        index-based mapping like Asset and Damage Scenarios modules.
        """
        print("[DEBUG] display_row_data_in_panel called with:", data)
        row = self.table.currentRow()
        if row < 0:
            return

        # ✅ Map each property field to its correct table column index
        # Skip column 0 (row indicator)
        index_to_column = {
            0: 1,   # ID
            1: 2,   # Threat
            2: 3,   # Damage Scenarios
            3: 4,   # TOE Configuration
            4: 5,   # Reasoning
            5: 6    # Comments
        }

        for i, (label, widget) in enumerate(self.ts_property_controls):
            col = index_to_column.get(i)
            if col is None:
                continue

            table_item = self.table.item(row, col)
            cell_widget = self.table.cellWidget(row, col)

            # 🔁 For multi-select fields
            if hasattr(widget, "set_selected_items"):
                text = table_item.text() if table_item else ""
                selected_items = [x.strip() for x in text.split(",") if x.strip()]
                widget.set_selected_items(selected_items)

            # 🔁 For single-select (combo box)
            elif hasattr(widget, "setCurrentText"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.setCurrentText(value)

            # 🔁 For plain or multiline text inputs
            elif hasattr(widget, "setText"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.setText(value)

            elif hasattr(widget, "setPlainText"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.setPlainText(value)

            elif hasattr(widget, "set_text"):
                value = table_item.text().strip() if table_item and table_item.text() else ""
                widget.set_text(value)

        # ✅ Ensure the panel is expanded
        if self.property_panel_manager.toggle_button and not self.property_panel_manager.toggle_button.isChecked():
            self.property_panel_manager.toggle_button.click()

    def add_multiselect_to_table_cell(self, row_index, column_index, option_list, current_value, update_field):
        """
        Generic helper for adding MultiSelectComboSelector to Threat Scenarios table.

        Args:
            row_index (int): Table row index.
            column_index (int): Table column index.
            option_list (list[str]): List of selectable options.
            current_value (str): Pre-selected value from DB (comma-separated string).
            update_field (str): Field to update in backend via `update_threat_scenario`.

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
                update_threat_scenario(uuid, {update_field: value})  # ✅ Function change
                interfaces.unsaved_changes = True

        combo.model().dataChanged.connect(on_selection_change)
        self.table.setCellWidget(row_index, column_index, combo)

        
    


