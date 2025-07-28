"""
Module Name   : RiskTreatment_action.py \n
Layer         : Presentation / Risk Treatment \n
Module ID     : CY_SM_019 \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Updated By    : Vishnu Viswanath \n
Updated On    : 2025-06-03 \n

Purpose:
--------
Manages the UI layer for the Risk Treatment module. Handles property panel rendering,
data synchronization between table and inputs, and signal-driven workflows like saving
and updating records.

Description:
------------
Combines the Risk Treatment configuration (`PROPERTY_CONFIG`) with shared UI component
factories to dynamically generate input forms. Handles all interaction logic from user
inputs, table selections, and control actions like Save or Submit. Integrates with
external data sources for claims, goals, and TOE configurations.

Responsibilities:
-----------------
- Render dynamic property panels using configuration schema
- Load related data: TOE Configurations, Security Goals, and Security Claims
- Emit Save signals with structured payloads
- Manage table-to-input and input-to-table synchronization
- Handle changes to multiselect fields
- Trigger loading and submission of Risk Treatment records

Signals:
--------
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+
| Trigger                | Signal Name            | Description                                 | Payload Format                                             |
+========================+========================+=============================================+============================================================+
| Save button clicked    | property_save_clicked  | Emits form data for saving                  | {"sender": "Property panel", "event": "save", "data": dict}|
| Table row selected     | row_selected           | Emits full data of selected row             | {"sender": "Table", "event": "row_selected", "data": dict} |
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+

Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore)
- Risk_Assessment.Risk_Treatment.config.risk_treatment_config
- Risk_Assessment.controllers.riskassessment_TableValueLoad
- Risk_Assessment.controllers.riskassessment_TableSaveRecord
- Risk_Assessment.controllers.riskassessment_PropertyValueDisplay
- components.propertypanel.property_input_components
- components.propertypanel.property_panel_layout
- components.action_panel
- components.table.table_panel
- styles.property_panel_style
- controllers.DatabaseCreator
- controllers.TableValueHighlight
- utils.interface_utils
- components.loading_dialog.RoundLoader
- Analysis.models.analysis_synchronization

Limitations:
------------
- Multiselect input population is dependent on fixed queries
- No embedded field-level validation or error highlighting
- Data format coupling between config and table layout

Improvements:
-------------
- Add schema-based validation with real-time feedback
- Modularize data loading routines for reusability
- Decouple item list loading logic from database queries

Change History:
---------------
+----------------+----------------------+-------------------------------------------------------------+----------------------+
| Version        | Date                 | Change                                                      | Author               |
+================+======================+=============================================================+======================+
| V 3.0          | 2025-06-03           |  Added dynamic property panel and signal logic              | Vishnu Viswanath     |
+----------------+----------------------+-------------------------------------------------------------+----------------------+
|                |                      |                                                             |                      |
+----------------+----------------------+-------------------------------------------------------------+----------------------+
|                |                      |                                                             |                      |
+----------------+----------------------+-------------------------------------------------------------+----------------------+
"""


from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication

import Risk_Assessment.controllers.riskassessment_TableValueLoad as TVL
import Risk_Assessment.controllers.riskassessment_TableSaveRecord as TSR
import Risk_Assessment.controllers.riskassessment_PropertyValueDisplay as PVD
from Risk_Assessment.Risk_Treatment.views.risktreatment_toolbar_panel import create_toolbar
from Risk_Assessment.Risk_Treatment.config.risk_treatment_config import PROPERTY_CONFIG, SAVE_BUTTON
from components.propertypanel.property_input_components import PropertyInputFactory
from styles.property_panel_style import property_save_button_style
from PyQt5.QtCore import pyqtSignal
import controllers.TableValueHighlight as TVH
import controllers.DatabaseCreator as DB
import components.action_panel as action_panel
import components.table.table_panel as table_panel
import components.propertypanel.property_panel_layout as property_panel_layout
import Analysis.models.analysis_synchronization as AS
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
from controllers.schema_manager import get_instances
from controllers.tablemodel import SecurityGoals, SecurityClaims, TOEConfiguration




class RiskTreatement_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    create_property_layout_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
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
        
        self.rt_property_controls = []

        self.create_property_panel_signal.connect(self.build_property_panel)
        self.create_property_panel_signal.emit()
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        create_toolbar(self)
        main_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)
        table_panel.TablePanelWrapper.create_table_panel(self)

        # Step 5: Add everything to the layout
        self.action_panel_layout.addLayout(self.table_layout)
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
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()
        self.previous_text = None

    def set_unsaved_changes(self):
        interfaces.previous_module = self
        interfaces.unsaved_changes = True 


    def on_row_selection_changed(self, selected, deselected):
        """
        Handles logic when a new row is selected in the Risk Treatment table.

        Extracts data from the currently selected row and emits a payload containing
        all mapped fields for use in populating the property panel.

        Parameters:
        -----------
        selected : QItemSelection
            The newly selected row(s).
        deselected : QItemSelection
            The previously selected row(s).

        Emits:
        -------
        row_selected : pyqtSignal
            Emitted with a structured dictionary payload:
            {
                "sender": "Table",
                "event": "row_selected",
                "data": {
                    "ID": "...",
                    "Damage": "...",
                    ...
                }
            }

        See Also:
        ---------
        - display_row_data_in_panel (signal receiver)
        """
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed(self.table)

        if self.table.currentRow() >= 0:
            row = self.table.currentRow()
            data = {
                "ID": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "Damage": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                "Impact": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                "Threat": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                "Initial AFR": self.table.item(row, 5).text() if self.table.item(row, 5) else "",
                "Initial Risk": self.table.item(row, 6).text() if self.table.item(row, 6) else "",
                "Resid AFR": self.table.item(row, 7).text() if self.table.item(row, 7) else "",
                "Resid Risk": self.table.item(row, 8).text() if self.table.item(row, 8) else "",
                "TOE Configuration": self.table.item(row, 9).text() if self.table.item(row, 9) else "",
                "Risk Treatment": self.table.item(row, 10).text() if self.table.item(row, 10) else "",
                "Security Claims": self.table.item(row, 11).text() if self.table.item(row, 11) else "",
                "Security Goals": self.table.item(row, 12).text() if self.table.item(row, 12) else "",
                "Mitigated By": self.table.item(row, 13).text() if self.table.item(row, 13) else ""
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
        # Show the round loader before loading risk treatment data
        self.loader = RoundLoader(self, label_text="Loading Risk Treatment Data...")
        self.loader.show()
        QApplication.processEvents()  # Ensure UI updates before loading starts

        try:
            # ✅ Load Security Goals and Claims via ORM
            security_goals = get_instances(SecurityGoals, {'is_deleted': False})
            security_claims = get_instances(SecurityClaims, {'is_deleted': False})

            self.SG_list = [f"{sg.id}::{sg.name}" for sg in security_goals if sg.id and sg.name]
            self.SC_list = [f"{sc.id}::{sc.name}" for sc in security_claims if sc.id and sc.name]

            self.rt_security_claims_input.additem(self.SC_list)
            self.rt_security_goals_input.additem(self.SG_list)

            # ✅ Load TOE Configuration via ORM
            toe_rows = get_instances(TOEConfiguration, {'is_deleted': False})
            self.formatted_toe_configuration = [
                f"{t.toe_configuration_id}::{t.toe_configuration_name}"
                for t in toe_rows if t.toe_configuration_id and t.toe_configuration_name
            ]
            self.rt_toe_configuration_input.additem(self.formatted_toe_configuration)
            self.rt_toe_configuration_input.items = self.formatted_toe_configuration
            self.rt_toe_configuration_input.update_items()

            # ✅ Load Risk Treatment Table
            TVL.load_risktreatement(self, self.table, self.property_panel_manager.property_panel, self.toggle_button)

            interfaces.unsaved_changes = False

        finally:
            # ✅ Always hide loader
            self.loader.close()


    def submit_changes(self):
         self.table.setFocus()
         TSR.risktreatment_submit_changes(self.table)
         AS.remove_claims_from_risk_data()
         AS.remove_toe_configurations_from_risk_data()
         self.update_button_states()
         interfaces.unsaved_changes = False
    def on_rt_property_toe_configuration_property_changed(self): PVD.on_property_multiselect_changed(self.table, 9, self.rt_toe_configuration_input)     
    def on_rt_property_rt_changed(self): PVD.on_property_multiselect_changed(self.table, 10, self.rt_risk_treatment_input)
    def on_rt_property_sc_changed(self): PVD.on_property_multiselect_changed(self.table, 11, self.rt_security_claims_input)
    def on_rt_property_sg_changed(self): PVD.on_property_multiselect_changed(self.table, 12, self.rt_security_goals_input)
    def display_selected_row(self): 
        temp = interfaces.unsaved_changes
        PVD.RiskTreatment_display_selected_row(self.table, self.rt_property_controls, self.SC_list, self.SG_list,self.property_panel,self.toggle_button)
        interfaces.unsaved_changes = temp

    def closeEvent(self, event):
        event.accept()

    def build_property_panel(self):
        """
        Dynamically builds the property input panel for Risk Treatment.

        This method reads the field definitions from `PROPERTY_CONFIG`, generates
        the corresponding UI widgets, and binds signal handlers if specified. It also
        applies read-only settings and stores references to input widgets for later use.

        If enabled via `SAVE_BUTTON`, a Save button is also created and connected
        to the `property_save_clicked` signal.

        Effects:
        --------
        - Initializes `self.rt_property_controls` with label-widget pairs.
        - Creates instance variables like `rt_toe_configuration_input`, `rt_risk_treatment_input`, etc.
        - Adds a Save button to the layout and disables it by default.

        Signals:
        --------
        - property_save_clicked: Emitted with form data payload on Save button click.

        See Also:
        ---------
        - PropertyInputFactory.create_common_property_input
        - PropertyInputFactory.create_save_button
        - risk_treatment_config.PROPERTY_CONFIG
        """

        self.property_factory = PropertyInputFactory()
        self.rt_property_controls = []

        for field in PROPERTY_CONFIG:
            input_widget = self.property_factory.create_common_property_input(
                field["label"],
                field["type"],
                self.property_layout,
                self.rt_property_controls,
                getattr(self, field.get("signal")) if field.get("signal") else None,
                field.get("items")
            )

            if field.get("readonly"):
                input_widget.setReadOnly(True)

            setattr(self, f'rt_{field["label"].lower().replace(" ", "_")}_input', input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.rt_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)
        
    def handle_property_save_signal(self, payload):
        print(f"[TARA] 💾 Risk Treatment Save Signal Received → {payload}")

    def display_row_data_in_panel(self, data):
        """
        Populates the property input panel with values from the selected table row.

        Uses a utility function to load all fields from the currently selected table row
        into the corresponding property input widgets. Handles multiselect fields using
        preloaded lists of Security Claims and Security Goals.

        Parameters:
        -----------
        data : dict
            Row selection payload in the format:
            {
                "sender": "Table",
                "event": "row_selected",
                "data": {
                    "ID": "...",
                    "Damage": "...",
                    ...
                }
            }

        Effects:
        --------
        - Clears and repopulates all property fields with current row values.
        - Handles field-specific rendering logic like multiselect population.

        See Also:
        ---------
        - PVD.RiskTreatment_display_selected_row
        """
        PVD.RiskTreatment_display_selected_row(
            self.table,
            self.rt_property_controls,
            self.SC_list,
            self.SG_list,
            self.property_panel_manager.property_panel,
            self.property_panel_manager.toggle_button
        )
    
    

