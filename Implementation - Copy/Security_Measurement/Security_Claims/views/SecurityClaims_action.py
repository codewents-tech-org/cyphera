"""
Module Name   : SecurityClaims_action.py \n
Layer         : Presentation / Security Claims \n
Module ID     : CY_SM_011 \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Updated By    : Vishnu Viswanath \n
Updated On    : 2025-06-03 \n

Purpose:
--------
Provides the UI logic for managing Security Claims, including dynamic property
panel construction, row selection synchronization, and signal emission for Save
operations. Integrates assumptions and TOE configurations dynamically.

Description:
------------
Utilizes configuration-driven definitions to dynamically render input widgets
for Security Claims. Manages all interactions between the table and the property
panel, supports validation, and handles database-driven loading of assumptions and
TOE configurations.

Responsibilities:
-----------------
- Dynamically build and manage Security Claims property panel
- Emit signals when table rows are selected or saved
- Handle external data sources for assumptions and TOE configurations
- Respond to UI actions: Add, Delete, Save, Submit
- Clear and reset input fields upon selection change

Signals:
--------
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+
| Trigger                | Signal Name            | Description                                 | Payload Format                                             |
+========================+========================+=============================================+============================================================+
| Save button clicked    | property_save_clicked  | Emits updated property panel form data      | {"sender": "Property panel", "event": "save", "data": dict}|
| Table row selected     | row_selected           | Emits full row content on selection change  | {"sender": "Table", "event": "row_selected", "data": dict} |
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+

Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore)
- Security_Measurement.Security_Claims.config.security_claims_config
- Security_Measurement.Security_Claims.views.securityclaims_toolbar_panel
- Risk_Assessment.controllers.* (TableValueLoad, Save, Refresh, etc.)
- components.propertypanel.property_input_components
- components.propertypanel.property_panel_layout
- components.action_panel
- components.table.table_panel
- components.loading_dialog.RoundLoader
- models.unique_name_action
- styles.property_panel_style
- utils.interface_utils
- controllers.DatabaseCreator
- controllers.TableValueHighlight

Limitations:
------------
- Tight coupling between table column index and property fields
- No inline validation or undo functionality for widget inputs
- Manual refresh logic for assumptions and TOE configuration lists

Improvements:
-------------
- Add validation feedback to property widgets
- Decouple assumptions and TOE data load logic
- Introduce auto-saving or change-tracking mechanism

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

                             
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QTableWidgetItem, QMessageBox, QAbstractScrollArea, QHeaderView, QAbstractItemView
import Risk_Assessment.controllers.riskassessment_TableValueLoad as TVL
import Risk_Assessment.controllers.riskassessment_TableAddRecord as TAR
import Risk_Assessment.controllers.riskassessment_TableRemoveRecord as TRR
import Risk_Assessment.controllers.riskassessment_TableSaveRecord as TSR
import Risk_Assessment.controllers.riskassessment_TableRefreshRecord as TFR
import Risk_Assessment.controllers.riskassessment_PropertyValueDisplay as PVD
from Security_Measurement.Security_Claims.views.securityclaims_toolbar_panel import create_toolbar
from Security_Measurement.Security_Claims.config.security_claims_config import PROPERTY_CONFIG, SAVE_BUTTON
from components.propertypanel.property_input_components import PropertyInputFactory
from styles.property_panel_style import property_save_button_style
from PyQt5.QtCore import pyqtSignal, Qt
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
from controllers.database_tables.target_of_evaluation_tables import Assumptions
from controllers.database_tables.security_measurment_tables import SecurityClaims
from controllers.database_tables.target_of_evaluation_tables import TOEConfiguration
import logging
import Security_Measurement.Security_Claims.controllers.securityclaims_manager as SCM
import components.table.multioption_selector as MOS
import components.table.tree_row_indicator as TRI
logger = logging.getLogger(__name__)


class SecurityClaims_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.previous_text = ""

    def initUI(self):
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
        action_panel.create_action_panel(self)

        self.table_wrapper = table_panel.TablePanelWrapper(use_row_indicator=True, use_tree_indicator=False, parent=self)
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("securityclaims")

        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout

        self.action_panel_layout.addWidget(self.table_wrapper.table)
        self.action_panel_layout.addWidget(self.property_panel_manager.switch_property_panel)
        self.action_panel_layout.addWidget(self.property_panel_manager.property_panel)
        main_layout.addWidget(self.action_panel)

        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)
        self.save_button.setEnabled(True)

        self.add_button.clicked.connect(self.add_new_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.submit_button.clicked.connect(self.submit_changes)
        self.save_button.clicked.connect(self.submit_changes)

        self.row_uuid_map = {}
        self.row_sidebar_widgets = set()

        self.table.itemChanged.connect(self.update_cell_to_cache)
        self.table.itemDoubleClicked.connect(self.store_selected_entry)
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        
    def on_row_selection_changed(self, selected, deselected):
        TVH.on_row_selection_changed(self.table)
        if self.table.currentRow() >= 0:
            row = self.table.currentRow()
            data = {
                "ID": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "Name": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                "Assumptions": ", ".join(self.table.cellWidget(row, 3).selected_items()) if self.table.cellWidget(row, 3) else "",
                "Responsible": ", ".join(self.table.cellWidget(row, 4).selected_items()) if self.table.cellWidget(row, 4) else "",
                "TOE Configuration": ", ".join(self.table.cellWidget(row, 5).selected_items()) if self.table.cellWidget(row, 5) else "",
                "Description": self.table.item(row, 6).text() if self.table.item(row, 6) else "",
                "Comments": self.table.item(row, 7).text() if self.table.item(row, 7) else ""
            }
            payload = {
                "sender": "Table",
                "event": "row_selected",
                "data": data
            }
            self.row_selected.emit(payload)

    def load_data(self):
        self.loader = RoundLoader(self, label_text="Loading Security Claims...")
        self.loader.show()
        QApplication.processEvents()

        try:
            self.table.itemChanged.disconnect(self.find_duplicates)
        except Exception:
            pass

        # Load cached security claims from the manager
        claims = SCM.load_all_security_claims()

        # 🟩 Prepare Assumption options
        assumption_rows = get_instances(Assumptions, {})
        self.formatted_assumptions = [
            f"{a.assumption_id}::{a.assumptions}"
            for a in assumption_rows if a.assumption_id and a.assumptions
        ]
        self.security_claim_assumptions_input.additem(self.formatted_assumptions)

        # 🟩 Prepare Responsible options
        responsible_set = set()
        for claim in claims:
            if claim.responsible:
                responsible_set.update([val.strip() for val in claim.responsible.split(",") if val.strip()])
        responsible_options = list(responsible_set) or ["Customer", "Supplier"]
        self.security_claim_responsible_input.additem(responsible_options)

        # 🟩 Prepare TOE Configuration options
        toe_rows = get_instances(TOEConfiguration, {})
        self.formatted_toe_configuration = [
            f"{t.toe_configuration_id}::{t.toe_configuration_name}"
            for t in toe_rows if t.toe_configuration_id and t.toe_configuration_name
        ]
        self.security_claim_toe_configuration_input.additem(self.formatted_toe_configuration)

        # Configure table headers and clear
        self.table.setRowCount(0)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "", "ID", "Name", "Assumptions", "Responsible", "TOE Configuration", "Description", "Comments"
        ])
        self.table.setAlternatingRowColors(True)

        for idx, claim in enumerate(claims):
            self.table.insertRow(idx)
            self.table.setCellWidget(idx, 0, TRI.SidebarWidget())
            self.table.setItem(idx, 1, QTableWidgetItem(claim.sc_id or ""))
            self.table.setItem(idx, 2, QTableWidgetItem(claim.name or ""))

            # 🟨 Assumption Combo
            assum_combo = MOS.TSMultiSelectComboBox(self.formatted_assumptions, parent=self.table)
            selected_assumptions = [
                opt for opt in self.formatted_assumptions
                if opt.startswith(claim.assumption_id or "")
            ]
            assum_combo.set_text(selected_assumptions)
            assum_combo.model().dataChanged.connect(lambda: self.update_cell_to_cache(None))
            self.table.setCellWidget(idx, 3, assum_combo)

            # 🟨 Responsible Combo
            resp_combo = MOS.TSMultiSelectComboBox(responsible_options, parent=self.table)
            selected_resp = [r.strip() for r in (claim.responsible or "").split(",") if r.strip()]
            resp_combo.set_text(selected_resp)
            resp_combo.model().dataChanged.connect(lambda: self.update_cell_to_cache(None))
            self.table.setCellWidget(idx, 4, resp_combo)

            # 🟨 TOE Configuration Combo
            toe_combo = MOS.TSMultiSelectComboBox(self.formatted_toe_configuration, parent=self.table)
            selected_toe = [
                opt for opt in self.formatted_toe_configuration
                if opt.startswith(claim.toe_configuration_id or "")
            ]
            toe_combo.set_text(selected_toe)
            toe_combo.model().dataChanged.connect(lambda: self.update_cell_to_cache(None))
            self.table.setCellWidget(idx, 5, toe_combo)

            self.table.setItem(idx, 6, QTableWidgetItem(claim.description or ""))
            self.table.setItem(idx, 7, QTableWidgetItem(claim.comments or ""))
            self.row_uuid_map[idx] = claim.uuid

        self.table.itemChanged.connect(self.find_duplicates)
        interfaces.unsaved_changes = False
        self.loader.close()

    def select_first_row(self): 
        if self.table.rowCount() > 0: self.table.setCurrentCell(0, 1)

    def ensure_row_selection(self):
            """
            Ensure at least one row is selected in the table when the panel loads.
            """
            if hasattr(self, 'table_widget') and self.table_widget:
                if self.table_widget.rowCount() > 0 and not self.table_widget.selectedItems():
                    self.table_widget.selectRow(0)    

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

            # --- Extract values from row ---
            sc_id = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            name = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
            # Multi-select combos:
            assumptions = self.table.cellWidget(row, 3).selected_items() if self.table.cellWidget(row, 3) else []
            responsible = self.table.cellWidget(row, 4).selected_items() if self.table.cellWidget(row, 4) else []
            toe_config = self.table.cellWidget(row, 5).selected_items() if self.table.cellWidget(row, 5) else []
            description = self.table.item(row, 6).text() if self.table.item(row, 6) else ""
            comments = self.table.item(row, 7).text() if self.table.item(row, 7) else ""

            updates = {
                'sc_id': sc_id,
                'name': name,
                'assumption_id': ', '.join(a.split('::')[0] for a in assumptions),    # Save just ID
                'responsible': ', '.join(responsible),
                'toe_configuration_id': ', '.join(t.split('::')[0] for t in toe_config),
                'description': description,
                'comments': comments,
                # Add any other fields here as needed
            }
            SCM.update_security_claim(uuid, updates)
            interfaces.unsaved_changes = True

    def add_new_entry(self):
        self.table.setFocus()
        try:
            self.table.itemChanged.disconnect(self.find_duplicates)
        except Exception:
            pass

        new_sc_id = SCM.generate_new_sc_id()
        sc_name = f"Security Claim {new_sc_id.split('-')[-1]}"
        created = SCM.create_security_claim(sc_id=new_sc_id, name=sc_name)
        if not created:
            QMessageBox.critical(self, "Error", f"Could not create Security Claim {new_sc_id}")
            return

        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, 40)
        self.table.setCellWidget(row_idx, 0, TRI.SidebarWidget())

        id_item = QTableWidgetItem(created.sc_id)
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row_idx, 1, id_item)

        name_item = QTableWidgetItem(created.name or sc_name)
        self.table.setItem(row_idx, 2, name_item)

        # ---- CRUCIAL: Set previous_text BEFORE find_duplicates ----
        self.previous_text = name_item.text()

        # ---- Now call find_duplicates (will pass, since name is set and non-empty) ----
        self.find_duplicates(name_item)
        self.existing_entries.add(name_item.text())

        # Multi-select input widgets
        assum_widget = MOS.TSMultiSelectComboBox(self.formatted_assumptions)
        assum_widget.set_text(created.assumption_id.split(',') if created.assumption_id else [])
        self.table.setCellWidget(row_idx, 3, assum_widget)

        resp_widget = MOS.TSMultiSelectComboBox(self.security_claim_responsible_input.items)
        resp_widget.set_text(created.responsible.split(',') if created.responsible else [])
        self.table.setCellWidget(row_idx, 4, resp_widget)

        toe_widget = MOS.TSMultiSelectComboBox(self.formatted_toe_configuration)
        toe_widget.set_text(created.toe_configuration_id.split(',') if created.toe_configuration_id else [])
        self.table.setCellWidget(row_idx, 5, toe_widget)

        self.table.setItem(row_idx, 6, QTableWidgetItem(created.description or ""))
        self.table.setItem(row_idx, 7, QTableWidgetItem(created.comments or ""))

        self.row_uuid_map[row_idx] = created.uuid

        self.update_button_states()
        interfaces.unsaved_changes = True
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.setCurrentCell(row_idx, 2)  # Focus on Name cell

    def delete_entry(self):
        selected_rows = sorted(self.table.selectionModel().selectedRows(), key=lambda x: x.row(), reverse=True)
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No row selected to delete.")
            return

        for index in selected_rows:
            row = index.row()
            uuid = self.row_uuid_map.get(row)
            if uuid:
                SCM.delete_security_claim(uuid)
                self.table.removeRow(row)
            else:
                # Fallback if uuid not found, try by SC ID
                sc_id = self.table.item(row, 1).text()
                for u, entry in SCM.SECURITY_CLAIMS_CACHE.items():
                    if entry['record'].sc_id == sc_id:
                        SCM.delete_security_claim(u)
                        self.table.removeRow(row)
                        break

        # FULL REBUILD of uuid map after deletion
        new_map = {}
        for row in range(self.table.rowCount()):
            sc_id_item = self.table.item(row, 1)
            if sc_id_item:
                sc_id = sc_id_item.text().strip()
                for uuid, entry in SCM.SECURITY_CLAIMS_CACHE.items():
                    if entry['record'].sc_id == sc_id:
                        new_map[row] = uuid
                        break
        self.row_uuid_map = new_map

        self.update_button_states()
        self.refrash_existing_entries()
        interfaces.unsaved_changes = True


    def submit_changes(self):
        self.table.setFocus()

        # Clear cache and reload from table
        SCM.load_all_security_claims()  # Optional if you want to sync cache first

        # Update cache with current table rows
        for row in range(self.table.rowCount()):
            uuid_item = self.table.item(row, 0)  # or use a map like self.row_uuid_map[row]
            sc_id = self.table.item(row, 1).text()
            name = self.table.item(row, 2).text()
            assumptions = self.table.cellWidget(row, 3).selected_items() if self.table.cellWidget(row, 3) else []
            responsible = self.table.cellWidget(row, 4).selected_items() if self.table.cellWidget(row, 4) else []
            toe_config = self.table.cellWidget(row, 5).selected_items() if self.table.cellWidget(row, 5) else []
            description = self.table.item(row, 6).text() if self.table.item(row, 6) else ''
            comments = self.table.item(row, 7).text() if self.table.item(row, 7) else ''

            updates = {
                'sc_id': sc_id,
                'name': name,
                'assumption_id': ', '.join(a.split('::')[0] for a in assumptions),
                'responsible': ', '.join(responsible),
                'toe_configuration_id': ', '.join(t.split('::')[0] for t in toe_config),
                'description': description,
                'comments': comments,
                'updated_by': 'system',
            }

            # Match and update in cache
            for uuid, entry in SCM.SECURITY_CLAIMS_CACHE.items():
                if entry['record'].sc_id == sc_id:
                    SCM.update_security_claim(uuid, updates)

        # Persist changes to DB
        SCM.persist_security_claim_changes()

        # Sync downstream
        AS.update_riskData_from_securityClaims()
        AS.remove_claims_from_risk_data()

        self.update_button_states()
        interfaces.unsaved_changes = False
        

  
    def on_sc_property_name_changed(self): PVD.on_property_multiline_changed(self.table, 2, self.security_claim_name_input)
    def on_sc_property_assumptionproperty_changed(self):  PVD.on_property_multiselect_changed(self.table, 3, self.security_claim_assumptions_input)
    def on_sc_property_securityproperty_changed(self): PVD.on_property_multiselect_changed(self.table, 4, self.security_claim_responsible_input)
    def on_sc_property_toe_configuration_property_changed(self):  PVD.on_property_multiselect_changed(self.table, 5, self.security_claim_toe_configuration_input)
    def on_sc_property_description_changed(self): PVD.on_property_multiline_changed(self.table, 6, self.security_claim_description_input)       
    def on_sc_property_comment_changed(self): PVD.on_property_multiline_changed(self.table, 7, self.security_claim_comments_input)


    def closeEvent(self, event):
        event.accept()

    def build_property_panel(self):
        self.property_factory = PropertyInputFactory()
        self.security_claim_property_controls = []

        for field in PROPERTY_CONFIG:
            input_widget = self.property_factory.create_common_property_input(
                field["label"],
                field["type"],
                self.property_layout,
                self.security_claim_property_controls,
                getattr(self, field.get("signal")) if field.get("signal") else None,
                field.get("items")
            )
            if field.get("readonly"):
                input_widget.setReadOnly(True)
            setattr(self, f'security_claim_{field["label"].lower().replace(" ", "_")}_input', input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.security_claim_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)

    def handle_property_save_signal(self, payload):
        print(f"[TARA] 🔔 Security Claim Save Signal Received → {payload}")

    def display_row_data_in_panel(self, data):
        row = self.table.currentRow()
        for i, (label, widget) in enumerate(self.security_claim_property_controls):
            table_item = self.table.item(row, i + 1)  # +1 if first column is sidebar or row indicator
            if hasattr(widget, "set_text"):
                widget.set_text(table_item.text() if table_item and table_item.text() else "")
        PVD.SecurityClaims_display_selected_row(
            self.table,
            self.security_claim_property_controls,
            self.formatted_assumptions,
            self.formatted_toe_configuration,
            self.property_panel_manager.property_panel,
            self.property_panel_manager.toggle_button
        )

    def update_button_states(self):
        selected_rows = self.table.selectionModel().selectedRows()
        enable = bool(selected_rows)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(enable)
        if hasattr(self, 'submit_button'):
            self.submit_button.setEnabled(True)
        if hasattr(self, 'add_button'):
            self.add_button.setEnabled(True)
        if hasattr(self, 'save_button'):
            self.save_button.setEnabled(self.table.rowCount() > 0)


    

    # --- Helper bindings: keep these exactly as in Security Controls ---

    def find_duplicates(self, item): find_duplicates(self, item)
    def store_selected_entry(self, item): store_selected_entry(self, item)
    def refrash_existing_entries(self): refrash_existing_entries(self)
    def set_unsaved_changes(self): interfaces.unsaved_changes = True
