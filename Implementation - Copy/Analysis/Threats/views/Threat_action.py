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
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()
        self.previous_text = None



    def on_row_selection_changed(self, selected, deselected): 
        """
        Handles row selection events from the threat table.

        Extracts relevant values from the selected row, constructs a payload,
        and emits it via the `row_selected` signal for further processing
        (usually to update the property panel).

        Parameters:
        -----------
        selected : QItemSelection
            The newly selected row(s) in the table.
        deselected : QItemSelection
            The previously selected row(s).

        Emits:
        -------
        row_selected : pyqtSignal
            Emits a dictionary containing the selected row's data:
            {
                "sender": "Table",
                "event": "row_selected",
                "data": {
                    "ID": "...",
                    "Name": "...",
                    ...
                }
            }

        See Also:
        ---------
        - display_row_data_in_panel (slot connected to this signal)
        """
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed(self.table)

        if self.table.currentRow() >= 0:
            row = self.table.currentRow()
            data = {
                "ID": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "Name": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                "Damage Scenarios": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                "TOE Configuration": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                "Misuse Cases": self.table.item(row, 5).text() if self.table.item(row, 5) else "",
                "Asset": self.table.item(row, 8).text() if self.table.item(row, 8) else "",
                "Security Property": self.table.item(row, 9).text() if self.table.item(row, 9) else "",
                "Reasoning": self.table.item(row, 10).text() if self.table.item(row, 10) else "",
                "Comments": self.table.item(row, 11).text() if self.table.item(row, 11) else ""
            }

            payload = {
                "sender": "Table",
                "event": "row_selected",
                "data": data
            }
            self.row_selected.emit(payload)

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
        # Show loader
        self.loader = RoundLoader(self, label_text="Loading...")
        self.loader.show()
        QApplication.processEvents()

        # --- Populate select options (as you have) ---
        # Damage Scenarios
        damage_scenarios_options = [
            f"{ds.ds_id}::{ds.name}" for ds in get_instances(DamageScenarios)
        ]
        self.threat_damage_scenarios_input.additem(damage_scenarios_options)
        self.threat_damage_scenarios_input.set_text('')
        self.damage_scenarios_option_list = damage_scenarios_options

        # TOE Config
        toe_configuration_options = [
            f"{toec.toe_configuration_id}::{toec.toe_configuration_name}" for toec in get_instances(TOEConfiguration)
        ]
        self.threat_toe_configuration_input.additem(toe_configuration_options)
        self.threat_toe_configuration_input.set_text('')
        self.toe_configuration_option_list = toe_configuration_options

        # Misuse Cases
        misuse_cases_options = [
            f"{ms.misuse_cases_id}::{ms.misuse_cases_name}" for ms in get_instances(Misusecases)
        ]
        self.threat_misuse_cases_input.additem(misuse_cases_options)
        self.threat_misuse_cases_input.set_text('')
        self.misuse_cases_option_list = misuse_cases_options

        # ---- TABLE POPULATION ----
        self.table.setRowCount(0)
        threats = load_all_threats()  # List of Threats ORM records
        for row_idx, threat in enumerate(threats):
            self.table.insertRow(row_idx)
            # Fill your table columns and widgets as needed. Example:
            self.table.setItem(row_idx, 1, QTableWidgetItem(threat.threat_id))
            self.table.setItem(row_idx, 2, QTableWidgetItem(threat.name))
            # MultiSelect for columns 3-5, as in your logic above
            self.row_uuid_map[row_idx] = threat.uuid  # ✅ Store uuid for this row!
            # Optionally store the uuid → row mapping for later updates

        interfaces.unsaved_changes = False
        self.loader.close()


    def refresh_data(self):
        refresh_threats_cache()  # Clear and reload manager cache from DB
        self.load_data()      
    def submit_changes(self):
        self.table.setFocus()
        self.update_button_states()
        # For each table row, extract values and call update_threat
        for row in range(self.table.rowCount()):
            uuid = self.row_uuid_map.get(row)
            if not uuid:
                continue
            update_dict = {
                "name": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                # ... all other fields, including those from comboboxes
            }
            update_threat(uuid, update_dict)
        persist_threat_changes()
        interfaces.unsaved_changes = False


    def on_threat_property_name_changed(self): PVD.on_property_multiline_changed(self.table, 2, self.threat_name_input)
    def on_threat_property_DS_changed(self): PVD.on_property_multiselect_changed(self.table, 3, self.threat_damage_scenarios_input)
    def on_threat_property_toec_changed(self): PVD.on_property_multiselect_changed(self.table, 4, self.threat_toe_configuration_input)
    def on_threat_property_MS_changed(self): PVD.on_property_multiselect_changed(self.table, 5, self.threat_misuse_cases_input)
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

        Reads the `PROPERTY_CONFIG` to generate input widgets, assigns them to the
        property layout, binds signal handlers, and saves references for later access.
        Also adds a Save button if enabled in `SAVE_BUTTON` config.

        Effects:
        --------
        - Initializes `self.threat_property_controls` with label-widget pairs.
        - Dynamically assigns instance attributes like `self.threat_name_input`.
        - Creates and wires a Save button that emits `property_save_clicked`.

        Signals:
        --------
        - property_save_clicked: Emitted with a structured payload when Save is clicked.

        See Also:
        ---------
        - PropertyInputFactory.create_common_property_input
        - PropertyInputFactory.create_save_button
        - threats_config.PROPERTY_CONFIG
        """
        self.property_factory = PropertyInputFactory()
        for field in PROPERTY_CONFIG:
            input_widget = self.property_factory.create_common_property_input(
                field["label"],
                field["type"],
                self.property_layout,
                self.threat_property_controls,
                getattr(self, field.get("signal")) if field.get("signal") else None,
                field.get("items")
            )

            if field.get("readonly"):
                input_widget.setReadOnly(True)
            setattr(self, f'threat_{field["label"].lower().replace(" ", "_")}_input', input_widget)

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
        """
        Loads selected row data into the threat property panel.

        Delegates the task of setting values in the UI components to the utility function
        `threat_display_selected_row`, passing along dynamic configuration options.

        Parameters:
        -----------
        data : dict
            Dictionary emitted from row selection with a structure like:
            {
                "sender": "Table",
                "event": "row_selected",
                "data": {
                    "ID": "...",
                    "Name": "...",
                    ...
                }
            }

        Effects:
        --------
        - Fills property panel widgets with values from the selected table row.
        - Applies special handling for multiselect fields using option lists.

        See Also:
        ---------
        - PVD.threat_display_selected_row
        """
        PVD.threat_display_selected_row(
            self.table,
            self.threat_property_controls,
            self.damage_scenarios_option_list,
            self.toe_configuration_option_list,
            self.misuse_cases_option_list,
            self.property_panel_manager.property_panel,
            self.property_panel_manager.toggle_button
        )
    
    
        


