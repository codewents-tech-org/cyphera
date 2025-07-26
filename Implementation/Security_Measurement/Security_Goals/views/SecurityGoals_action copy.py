"""
Module Name   : SecurityGoals_action.py \n
Layer         : Presentation / Security Goals \n
Module ID     : CY_SM_013 \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Updated By    : Vishnu Viswanath \n
Updated On    : 2025-06-03 \n

Purpose:
--------
Handles the UI logic for Security Goals, including dynamic property panel creation,
table interaction management, and emitting structured signals to propagate changes
such as Save and row selection events.

Description:
------------
Utilizes a configuration-based design to build Security Goal property panels using
shared UI components. Connects property inputs to handler methods, manages the table’s
state, and ensures data synchronization across UI elements. Also loads external TOE
Configuration data dynamically and integrates user interactions like Add, Delete, and Submit.

Responsibilities:
-----------------
- Dynamically generate property panels from config
- Handle Save, Add, Delete, and Submit actions
- Load and sync TOE Configuration options
- Manage table state and propagate selection data
- Emit Save signals with structured payloads

Signals:
--------
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+
| Trigger                | Signal Name            | Description                                 | Payload Format                                             |
+========================+========================+=============================================+============================================================+
| Save button clicked    | property_save_clicked  | Emits updated property panel data           | {"sender": "Property panel", "event": "save", "data": dict}|
| Table row selected     | row_selected           | Emits selected row data                     | {"sender": "Table", "event": "row_selected", "data": dict} |
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+

Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore)
- Security_Measurement.Security_Goals.config.security_goals_config
- Security_Measurement.Security_Goals.views.securitygoals_toolbar_panel
- Risk_Assessment.controllers.* (TableValueLoad, Save, Refresh, etc.)
- Analysis.models.analysis_synchronization
- components.propertypanel.property_input_components
- components.propertypanel.property_panel_layout
- components.action_panel
- components.table.table_panel
- components.loading_dialog.RoundLoader
- styles.property_panel_style
- utils.interface_utils
- controllers.TableValueHighlight
- controllers.DatabaseCreator
- models.unique_name_action

Limitations:
------------
- Static dependency on table column indices
- Manual refresh logic for dropdown options
- Field-level validation is external to UI panel logic

Improvements:
-------------
- Add input validation hooks with real-time feedback
- Refactor field mapping using column headers instead of indices
- Introduce auto-loaders for supporting data lists (e.g. TOE)

Change History:
---------------
+----------------+----------------------+-------------------------------------------------------------+----------------------+
| Version        | Date                 | Change                                                      | Author               |
+================+======================+=============================================================+======================+
| V 3.0          | 2025-06-03           |Integrated dynamic property panel, save signal, and data sync| Vishnu Viswanath     |
+----------------+----------------------+-------------------------------------------------------------+----------------------+
| V 3.0          | 2025-06-04           | Updated Responsible combobox to get items from database     | Vishnu Viswanath     |
+----------------+----------------------+-------------------------------------------------------------+----------------------+
|                |                      |                                                             |                      |
+----------------+----------------------+-------------------------------------------------------------+----------------------+
"""

                             
from tkinter import messagebox
from Risk_Assessment.controllers.securityclaims_manager import SECURITY_CLAIMS_CACHE, create_security_claim, delete_security_claim, generate_new_sc_id, load_all_security_claims, persist_security_claim_changes
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QComboBox, QMessageBox, QTableWidgetItem, QTabWidget, QHBoxLayout
import Risk_Assessment.controllers.riskassessment_TableValueLoad as TVL
import Risk_Assessment.controllers.riskassessment_TableAddRecord as TAR
import Risk_Assessment.controllers.riskassessment_TableRemoveRecord as TRR
import Risk_Assessment.controllers.riskassessment_TableSaveRecord as TSR
import Risk_Assessment.controllers.riskassessment_PropertyValueDisplay as PVD
from Security_Measurement.Security_Goals.views.securitygoals_toolbar_panel import create_toolbar
from Security_Measurement.Security_Goals.config.security_goals_config import PROPERTY_CONFIG, SAVE_BUTTON
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
from models.unique_name_action import refrash_existing_entries, find_duplicates, store_selected_entry
from controllers.schema_manager import get_instances
from controllers.tablemodel import TOEConfiguration, SecurityClaims
import Implementation.Security_Measurement.Security_Goals.controllers.security_goals_manager as SGM
from Implementation.Security_Measurement.Security_Goals.controllers.security_goals_manager import SECURITY_GOALS_CACHE
import components.table.multioption_selector as MOS





class SecurityGoals_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    create_property_layout_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # Container for switching between Home and Tree Mindmap
        self.tab_container = QTabWidget()
        self.tab_container.setContentsMargins(0, 0, 0, 0)
        self.tab_container.setTabsClosable(False)
        self.tab_container.tabBar().setVisible(False)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.tab_container)

        # ------------------- HOME PANEL -------------------
        self.home_panel = QWidget()
        self.home_panel_layout = QVBoxLayout()
        self.home_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.home_panel_layout.setSpacing(0)
        self.home_panel.setLayout(self.home_panel_layout)

        create_toolbar(self)
        self.home_panel_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)

        self.table_wrapper = table_panel.TablePanelWrapper(use_row_indicator=True, use_tree_indicator=True, parent=self)
        self.table_wrapper.create_table_panel()
        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout
        self.table_wrapper.set_headers("security_goals")
        self.index = None
        self.table.clicked.connect(self.get_index)

        self.action_panel_layout.addLayout(self.table_layout)

        # Property panel setup
        self.property_panel_manager = property_panel_layout.PropertyPanelManager(self)
        self.property_panel_manager.create_property_panel()
        self.toggle_button = self.property_panel_manager.toggle_button
        self.property_panel = self.property_panel_manager.property_panel
        self.property_layout = self.property_panel_manager.property_layout
        self.sg_property_controls = []

        self.create_property_panel_signal.connect(self.build_property_panel)
        self.create_property_panel_signal.emit()

        self.action_panel_layout = QHBoxLayout()  # instead of QVBoxLayout
        self.action_panel.setLayout(self.action_panel_layout)

        self.action_panel_layout.addWidget(self.table_wrapper)
        self.action_panel_layout.addWidget(self.property_panel_manager.switch_property_panel)
        self.action_panel_layout.addWidget(self.property_panel_manager.property_panel)
        self.home_panel_layout.addWidget(self.table_wrapper)
        self.home_panel_layout.addWidget(self.action_panel)

        # Buttons
        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)
        self.save_button.setEnabled(False)

        self.add_button.clicked.connect(self.add_new_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.submit_button.clicked.connect(self.submit_changes)
        self.save_button.clicked.connect(self.submit_changes)

        # Signals
        self.row_selected.connect(self.display_row_data_in_panel)
        self.table.itemChanged.connect(self.update_button_states)
        self.table.itemDoubleClicked.connect(self.store_selected_entry)
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.update_button_states()

        # ------------------- CHILD PANEL (Optional if needed later) -------------------
        self.child_panel = QWidget()
        self.child_panel_layout = QVBoxLayout()
        self.child_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.child_panel_layout.setSpacing(0)
        self.child_panel.setLayout(self.child_panel_layout)

        # Tab container
        self.tab_container.addTab(self.home_panel, "Home")
        self.tab_container.addTab(self.child_panel, "Child Panel")

        self.previous_text = None

    def get_index(self, index):
        self.index = index    

    def ensure_row_selection(self):
        """
        Ensure at least one row is selected in the table when the panel loads.
        """
        if hasattr(self, 'table_widget') and self.table_widget:
            if self.table_widget.rowCount() > 0 and not self.table_widget.selectedItems():
                self.table_widget.selectRow(0) 

    def on_row_selection_changed(self, selected, deselected):
        """
        Emits a structured payload when a new row is selected in the table.

        Extracts the row index and values from relevant columns, builds a dictionary,
        and emits it through the `row_selected` signal to update the property panel.

        Parameters:
        -----------
        selected : QItemSelection
            The newly selected row(s).
        deselected : QItemSelection
            The previously selected row(s).

        Emits:
        -------
        row_selected : pyqtSignal
            Signal with data:
            {
                "sender": "Table",
                "event": "row_selected",
                "data": {
                    "ID": "...",
                    "Name": "...",
                    "Responsible": "...",
                    "TOE Configuration": "...",
                    "Description": "...",
                    "Comments": "..."
                }
            }

        See Also:
        ---------
        - display_row_data_in_panel (connected slot)
        """
        temp = interfaces.unsaved_changes
        
        TVH.on_row_selection_changed(self.table)

        if self.table.currentRow() >= 0:
            row = self.table.currentRow()
            data = {
                "ID": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "Name": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                "Responsible": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                "TOE Configuration": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                "Description": self.table.item(row, 5).text() if self.table.item(row, 5) else "",
                "Comments": self.table.item(row, 6).text() if self.table.item(row, 6) else ""
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

    def load_data(self):

        self.loader = RoundLoader(self, label_text="Loading Security Goals Data...")
        QApplication.processEvents()

        try:
            try:
                self.table.itemChanged.disconnect(self.find_duplicates)
            except TypeError:
                pass

            # 🔁 Load cached SecurityGoals
            goals = SGM.load_all_security_goals()

            # ✅ Load TOE Configuration
            toe_rows = get_instances(TOEConfiguration, {})
            toe_options = [
                f"{t.toe_configuration_id}::{t.toe_configuration_name}"
                for t in toe_rows if t.toe_configuration_id and t.toe_configuration_name
            ]
            self.security_goals_toe_configuration_input.additem(toe_options)
            self.security_goals_toe_configuration_input.set_text('')
            self.formatted_toe_configuration = toe_options

            # ✅ Responsible values
            responsible_set = set()
            for g in goals:
                if g.responsible:
                    responsible_set.update(v.strip() for v in g.responsible.split(',') if v.strip())
            responsible_options = list(responsible_set) or ["DefaultORG", "Customer", "Supplier"]
            self.security_goals_responsible_input.additem(responsible_options)
            self.security_goals_responsible_input.set_text('')

            # ✅ Table setup
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "ID", "Name", "Responsible", "TOE Configuration", "Description", "Comments", "UUID"
            ])
            self.table.setAlternatingRowColors(True)
            self.table.clearContents()
            self.table.setRowCount(0)

            # ✅ Populate each row
            for g in goals:
                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)

                self.table.setItem(row_idx, 0, QTableWidgetItem(g.sg_id))
                self.table.setItem(row_idx, 1, QTableWidgetItem(g.name or ""))

                # Responsible (multiselect)
                resp_widget = MOS.TSMultiSelectComboBox(responsible_options)
                resp_values = [v.strip() for v in (g.responsible or "").split(',') if v.strip()]
                resp_widget.set_text(resp_values)
                self.table.setCellWidget(row_idx, 2, resp_widget)

                # TOE Configuration
                toe_widget = MOS.TSMultiSelectComboBox(toe_options)
                matched_toe = [opt for opt in toe_options if opt.startswith(g.toe_configuration_id or "")]
                toe_widget.set_text(matched_toe)
                self.table.setCellWidget(row_idx, 3, toe_widget)

                self.table.setItem(row_idx, 4, QTableWidgetItem(g.description or ""))
                self.table.setItem(row_idx, 5, QTableWidgetItem(g.comments or ""))
                self.table.setItem(row_idx, 6, QTableWidgetItem(g.uuid))  # hidden ID

                self.table.setRowHeight(row_idx, 40)

            self.table.setColumnHidden(6, True)
            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setStretchLastSection(True)

            # ✅ Finish
            interfaces.unsaved_changes = False
            self.table.itemChanged.connect(self.find_duplicates)

        finally:
            self.loader.close()


    def update_button_states(self):
        """
        Updates the state of the Save and Delete buttons based on the table's state.
        """
        row_count = self.table.rowCount()
        has_selection = bool(self.table.selectionModel().selectedRows())

        # ✅ Safely check before accessing
        if hasattr(self, 'save_button') and self.save_button:
            self.save_button.setEnabled(row_count > 0)

        # Update "Delete" button state
        self.delete_button.setEnabled(row_count > 0 and has_selection)

        # Update "Submit" button state
        self.submit_button.setEnabled(row_count > 0)

    def find_duplicates(self, changed_item):
        row = self.table.currentRow()
        column = self.table.currentColumn()
        if row >=0 and column>=0:
            if column!= 2: return
        find_duplicates(self, changed_item)
    def store_selected_entry(self, item): store_selected_entry(self, item)
    def refrash_existing_entries(self): refrash_existing_entries(self)
    
    def add_new_entry(self):
    from controllers.security_goals_manager import generate_new_sg_id, create_security_goal

    self.table.setFocus()
    self.table.itemChanged.disconnect(self.find_duplicates)

    # 1. Generate new ID
    new_sg_id = generate_new_sg_id()

    # 2. Create new Security Goal (in-memory only)
    new_goal = create_security_goal(
        sg_id=new_sg_id,
        name="",
        responsible="",
        toe_configuration_id="",
        description="",
        comments=""
    )

    if not new_goal:
        QMessageBox.critical(self, "Error", f"Failed to create Security Goal {new_sg_id}")
        return

    # 3. Add to table
    TAR.SecurityGoals_add_new_entry(self.table, new_goal)

    # 4. Mark UI dirty
    self.update_button_states()
    interfaces.unsaved_changes = True
    self.table.itemChanged.connect(self.find_duplicates)


    def delete_entry(self):

        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a row to delete.")
            return

        # Assuming first column contains the unique sg_id
        selected_row = selected_items[0].row()
        sg_id_item = self.table.item(selected_row, 0)
        if not sg_id_item:
            QMessageBox.warning(self, "Error", "Unable to determine Security Goal ID.")
            return

        sg_id = sg_id_item.text().strip()

        # Find and soft-delete from cache
        for uuid, entry in SECURITY_GOALS_CACHE.items():
            if entry['record'].sg_id == sg_id:
                SGM.delete_security_goal(uuid)
                break
        else:
            QMessageBox.warning(self, "Error", f"Security Goal with ID {sg_id} not found in memory.")
            return

        # Run optional analysis syncs
        AS.remove_securityGoal_from_riskData()
        AS.sync_securityGoals_from_securityControl()

        # Update UI
        self.update_button_states()
        self.refrash_existing_entries()


    def submit_changes(self):


        self.table.setFocus()

        # 1. Persist in-memory SecurityGoal changes to DB
        SGM.persist_security_goal_changes()

        # 2. Run analysis sync functions (if needed)
        AS.remove_securityGoal_from_riskData()
        AS.sync_securityGoals_from_securityControl()

        # 3. Update UI state
        self.update_button_states()
        interfaces.unsaved_changes = False

    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True      
    def on_sg_property_name_changed(self): PVD.on_property_multiline_changed(self.table, 2, self.security_goals_name_input)
    def on_sg_property_securityproperty_changed(self): PVD.on_property_multiselect_changed(self.table, 3, self.security_goals_responsible_input)
    def on_sg_property_toe_configuration_property_changed(self):  PVD.on_property_multiselect_changed(self.table, 4, self.security_goals_toe_configuration_input)
    def on_sg_property_description_changed(self): PVD.on_property_multiline_changed(self.table, 5, self.security_goals_description_input)       
    def on_sg_property_comment_changed(self): PVD.on_property_multiline_changed(self.table, 6, self.security_goals_comments_input)
    def display_selected_row(self): PVD.SecurityGoals_display_selected_row(self.table, self.sg_property_controls, self.formatted_toe_configuration,self.property_panel,self.toggle_button)

    def closeEvent(self, event):
        event.accept()

    def build_property_panel(self):
        """
        Dynamically builds the property input panel for Security Goals.

        Iterates over `PROPERTY_CONFIG` to create labeled input widgets, binds signals 
        to corresponding handler methods, sets read-only fields, and stores references 
        for later access. If enabled, a Save button is added to the panel and connected 
        to emit form data through a signal.

        Effects:
        --------
        - Initializes self.security_goals_property_controls with label-widget pairs.
        - Sets instance variables for each input widget based on its label.
        - Adds and connects a Save button if enabled in SAVE_BUTTON config.

        Signals:
        --------
        - property_save_clicked: Emitted with structured form data when Save is clicked.

        See Also:
        ---------
        - PropertyInputFactory.create_common_property_input
        - PropertyInputFactory.create_save_button
        - security_goals_config.PROPERTY_CONFIG
        """
        self.property_factory = PropertyInputFactory()
        self.security_goals_property_controls = []

        for field in PROPERTY_CONFIG:
            input_widget = self.property_factory.create_common_property_input(
                field["label"],
                field["type"],
                self.property_layout,
                self.security_goals_property_controls,
                getattr(self, field.get("signal")) if field.get("signal") else None,
                field.get("items")
            )

            if field.get("readonly"):
                input_widget.setReadOnly(True)
            setattr(self, f'security_goals_{field["label"].lower().replace(" ", "_")}_input', input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.security_goals_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)

    def handle_property_save_signal(self, payload):
        print(f"[TARA] 🔔 Security Goals Save Signal Received → {payload}")

   
    def display_row_data_in_panel(self, data):
        """
        Populates the Security Goals property panel with data from the selected table row.

        For each property control, checks if the table has data in the corresponding cell.
        Clears the widget if the cell is empty. Then delegates the field population
        to the `SecurityGoals_display_selected_row` utility.

        Parameters:
        -----------
        data : dict
            Payload emitted from the table selection containing:
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
        - Clears input fields if the corresponding table cell is empty.
        - Loads new row values into the widgets in the property panel.

        See Also:
        ---------
        - PVD.SecurityGoals_display_selected_row
        """

        row = self.table.currentRow()

        for i, (label, widget) in enumerate(self.security_goals_property_controls):
            # Decide: Is this column using a cellWidget or item?
            table_item = self.table.item(row, i + 1)
            cell_widget = self.table.cellWidget(row, i + 1)

            should_clear = False

            # Case 1: Multiselect or custom combo box (uses cellWidget)
            if hasattr(widget, "selected_items") or hasattr(widget, "get_selected_items"):
                if not (hasattr(cell_widget, "selected_items") and cell_widget.selected_items()):
                    should_clear = True
                if should_clear and hasattr(widget, "set_text"):
                    widget.set_text([])  # empty list for multiselect
                continue  # skip the rest, already handled

            # Case 2: Regular QLineEdit / QTextEdit / NoWheelComboBox
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

        # Now repopulate all fields from table (this will work correctly)
        PVD.SecurityGoals_display_selected_row(
            self.table,
            self.security_goals_property_controls,
            self.formatted_toe_configuration,
            self.property_panel_manager.property_panel,
            self.property_panel_manager.toggle_button
        )
    def ensure_row_selection(self):
        """Ensure at least one row is selected in the table."""
        if hasattr(self, 'table_widget') and self.table_widget:
            if self.table_widget.rowCount() > 0 and not self.table_widget.selectedItems():
                self.table_widget.selectRow(0)





