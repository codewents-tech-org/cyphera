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
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QComboBox, QMessageBox, QTableWidgetItem
import Risk_Assessment.controllers.riskassessment_TableValueLoad as TVL
import Risk_Assessment.controllers.riskassessment_TableAddRecord as TAR
import Risk_Assessment.controllers.riskassessment_TableRemoveRecord as TRR
import Risk_Assessment.controllers.riskassessment_TableSaveRecord as TSR
import Risk_Assessment.controllers.riskassessment_PropertyValueDisplay as PVD
from Security_Measurement.Security_Goals.views.securitygoals_toolbar_panel import create_toolbar
from Security_Measurement.Security_Goals.config.security_goals_config import PROPERTY_CONFIG, SAVE_BUTTON
from components.propertypanel.property_input_components import PropertyInputFactory
from styles.property_panel_style import property_save_button_style
from PyQt5.QtCore import pyqtSignal, Qt
import controllers.TableValueHighlight as TVH
import components.table.table_row_indicator as TRI
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
import Security_Measurement.Security_Goals.controllers.security_goals_manager as SGM
from Security_Measurement.Security_Goals.controllers.security_goals_manager import SECURITY_GOALS_CACHE
import components.table.multioption_selector as MOS
from components.table.multioption_selector import  TSMultiSelectComboBox

class SecurityGoals_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        
        self.previous_text = "" 
        self.formatted_toe_configuration = []
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
        action_panel.create_action_panel(self)

        self.table_wrapper = table_panel.TablePanelWrapper(
            use_row_indicator=True, use_tree_indicator=False, parent=self)
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("securitygoals")

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
        self.load_data()
        self.select_first_row()


    def on_row_selection_changed(self, selected, deselected):
        current_row = self.table.currentRow()

        # ✅ Emit selection payload (your original logic)
        if current_row >= 0:
            row = current_row
            data = {
                "ID": self.table.item(row, 0).text() if self.table.item(row, 0) else "",
                "Name": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "Responsible": "",
                "TOE Configuration": "",
                "Description": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                "Comments": self.table.item(row, 5).text() if self.table.item(row, 5) else ""
            }
            payload = {
                "sender": "Table",
                "event": "row_selected",
                "data": data
            }
            self.row_selected.emit(payload)

        # ✅ Update the sidebar dot highlight
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, TRI.SidebarWidget):
                widget.set_selected(row == current_row)

        # ✅ Update button state
        self.update_button_states()

    def load_data(self):
        """
        Loads all Security Goals and related dropdown data, and populates the table and property panel.
        """

        # 🌀 Loader
        self.loader = RoundLoader(self, label_text="Loading Security Goals Data...")
        QApplication.processEvents()

        try:
            self.table.itemChanged.disconnect(self.find_duplicates)
        except Exception:
            pass

        # 🔁 Load security goals
        goal_rows = SGM.load_all_security_goals()
        self.row_uuid_map = {}

        # ✅ Load Responsible values
        responsible_set = set()
        for g in goal_rows:
            if g.responsible:
                responsible_set.update(val.strip() for val in g.responsible.split(",") if val.strip())
        responsible_options = sorted(responsible_set) or ["Customer", "Supplier"]
        self.security_goals_responsible_input.additem(responsible_options)
        self.security_goals_responsible_input.set_text('')

        # ✅ Load TOE Configuration
        toe_rows = get_instances(TOEConfiguration, {})
        toe_configuration_options = [
            f"{t.toe_configuration_id}::{t.toe_configuration_name}"
            for t in toe_rows if t.toe_configuration_id and t.toe_configuration_name
        ]
        self.security_goals_toe_configuration_input.clear()
        self.security_goals_toe_configuration_input.additem(toe_configuration_options)
        self.security_goals_toe_configuration_input.set_text('')
        self.formatted_toe_configuration = toe_configuration_options

        # ✅ Setup table
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "", "ID", "Name", "Responsible", "TOE Configuration", "Description", "Comments"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.clearContents()
        self.table.setRowCount(0)

        # ✅ Populate table rows
        for g in goal_rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            is_selected = (row_idx == self.table.currentRow())
            self.table.setCellWidget(row_idx, 0, TRI.SidebarWidget(row_idx=row_idx, selected=is_selected))
            self.table.setItem(row_idx, 1, QTableWidgetItem(g.sg_id or ""))
            self.table.setItem(row_idx, 2, QTableWidgetItem(g.name or ""))

            # Responsible
            resp_widget = MOS.TSMultiSelectComboBox(responsible_options)
            selected_resp = [val.strip() for val in (g.responsible or "").split(",") if val.strip()]
            resp_widget.set_text(selected_resp)
            self.table.setCellWidget(row_idx, 3, resp_widget)

            # TOE Configuration
            toe_widget = MOS.TSMultiSelectComboBox(toe_configuration_options)
            toe_ids = [tid.strip() for tid in (g.toe_configuration_id or "").split(",") if tid.strip()]
            matched_toe = [opt for opt in toe_configuration_options if opt.split("::")[0] in toe_ids]
            toe_widget.set_text(matched_toe)
            self.table.setCellWidget(row_idx, 4, toe_widget)

            # Description & Comments
            self.table.setItem(row_idx, 5, QTableWidgetItem(g.description or ""))
            self.table.setItem(row_idx, 6, QTableWidgetItem(g.comments or ""))

            self.row_uuid_map[row_idx] = g.uuid


        # ✅ Reconnect validation & save triggers
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
        if item:
            row = item.row()
        else:
            row = self.table.currentRow()
        uuid = self.row_uuid_map.get(row)
        if not uuid:
            return

        # Match columns: [Sidebar, ID, Name, Responsible, TOE, Desc, Comments]
        sg_id = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        name = self.table.item(row, 2).text() if self.table.item(row, 2) else ""

        # Responsible
        responsible_widget = self.table.cellWidget(row, 3)
        responsible = responsible_widget.selected_items() if responsible_widget else []
        responsible_str = ', '.join(responsible)
        # TOE
        toe_widget = self.table.cellWidget(row, 4)
        toe_config = toe_widget.selected_items() if toe_widget else []
        toe_config_str = ', '.join([t.split('::')[0] for t in toe_config])

        description = self.table.item(row, 5).text() if self.table.item(row, 5) else ""
        comments = self.table.item(row, 6).text() if self.table.item(row, 6) else ""

        updates = {
            'sg_id': sg_id,
            'name': name,
            'responsible': responsible_str,
            'toe_configuration_id': toe_config_str,
            'description': description,
            'comments': comments
        }
        SGM.update_security_goal(uuid, updates)
        interfaces.unsaved_changes = True



    def add_new_entry(self):
        self.table.setFocus()

        try:
            self.table.itemChanged.disconnect(self.find_duplicates)
        except TypeError:
            pass

        # 🆕 Generate new Security Goal ID and name
        sg_id = SGM.generate_new_sg_id()
        name = f"Security Goal {sg_id.split('-')[-1]}"

        # ➕ Create and cache it
        goal = SGM.create_security_goal(sg_id, name)
        if not goal:
            QMessageBox.critical(self, "Error", f"Failed to create Security Goal {sg_id}")
            return

        # 🔢 Insert new row
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, 40)

        # 🔗 Track UUID
        if not hasattr(self, 'row_uuid_map'):
            self.row_uuid_map = {}
        self.row_uuid_map[row_idx] = goal.uuid

        # 🧱 Populate row
        id_item = QTableWidgetItem(sg_id)
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row_idx, 1, id_item)
        self.table.setItem(row_idx, 2, QTableWidgetItem(name))
        self.table.setItem(row_idx, 5, QTableWidgetItem(""))  # Description
        self.table.setItem(row_idx, 6, QTableWidgetItem(""))  # Comments

        # 🧩 Dropdowns: Responsible and TOE Configuration
        resp_widget = MOS.TSMultiSelectComboBox(self.security_goals_responsible_input.items)
        toe_widget = MOS.TSMultiSelectComboBox(self.formatted_toe_configuration)

        self.table.setCellWidget(row_idx, 3, resp_widget)
        self.table.setCellWidget(row_idx, 4, toe_widget)

        # ✅ Set default row selection and update UI state
        self.table.setCurrentCell(row_idx, 2)
        self.update_button_states()
        interfaces.unsaved_changes = True


     

        self.table.itemChanged.connect(self.find_duplicates)

    def delete_entry(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a row to delete.")
            return

        sg_id_item = self.table.item(selected_row, 0)
        if not sg_id_item:
            QMessageBox.warning(self, "Error", "Unable to determine Security Goal ID.")
            return

        sg_id = sg_id_item.text().strip()
        # Soft delete from cache
        for uuid, entry in SECURITY_GOALS_CACHE.items():
            if entry['record'].sg_id == sg_id:
                SGM.delete_security_goal(uuid)
                break
        else:
            QMessageBox.warning(self, "Error", f"Security Goal with ID {sg_id} not found in memory.")
            return

        self.table.removeRow(selected_row)
        self.update_button_states()
        interfaces.unsaved_changes = True

    def submit_changes(self):
        self.table.setFocus()
        print("-----------step1--------------")

        # Optional: Reload cache if needed
        SGM.load_all_security_goals()  

        # ✅ Sync all visible rows into cache
        for row in range(self.table.rowCount()):
            sg_id = self.table.item(row, 1).text() if self.table.item(row, 1) else ''
            name = self.table.item(row, 2).text() if self.table.item(row, 2) else ''
            responsible = self.table.cellWidget(row, 3).selected_items() if self.table.cellWidget(row, 3) else []
            toe_config = self.table.cellWidget(row, 4).selected_items() if self.table.cellWidget(row, 4) else []
            description = self.table.item(row, 5).text() if self.table.item(row, 5) else ''
            comments = self.table.item(row, 6).text() if self.table.item(row, 6) else ''

            updates = {
                'sg_id': sg_id,
                'name': name,
                'responsible': ', '.join(responsible),
                'toe_configuration_id': ', '.join(t.split('::')[0] for t in toe_config),
                'description': description,
                'comments': comments,
                'updated_by': 'system',
            }

            # Find UUID and update cache
            uuid = self.row_uuid_map.get(row)
            if uuid:
                SGM.update_security_goal(uuid, updates)

        # ✅ Persist changes to DB
        SGM.persist_security_goal_changes()
        print("-----------step2--------------")

        self.update_button_states()
        interfaces.unsaved_changes = False


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

    def find_duplicates(self, item): 
        find_duplicates(self, item)

    def store_selected_entry(self, item): 
        store_selected_entry(self, item)

    def refrash_existing_entries(self): 
        refrash_existing_entries(self)

    def set_unsaved_changes(self): 
        interfaces.unsaved_changes = True


    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True      
    
    # ---- Signal Handlers for Property Panel ----
    def on_sg_property_name_changed(self):
        PVD.on_property_multiline_changed(self.table, 2, self.security_goals_name_input)  # Use 2 not 1

    def on_sg_property_responsible_changed(self):
        PVD.on_property_multiselect_changed(self.table, 3, self.security_goals_responsible_input)

    def on_sg_property_toe_configuration_changed(self):
        PVD.on_property_multiselect_changed(self.table, 4, self.security_goals_toe_configuration_input)

    def on_sg_property_description_changed(self):
        PVD.on_property_multiline_changed(self.table, 5, self.security_goals_description_input)

    def on_sg_property_comments_changed(self):
        PVD.on_property_multiline_changed(self.table, 6, self.security_goals_comments_input)

    def on_sg_property_comments_changed(self):
        PVD.on_property_multiline_changed(self.table, 5, self.security_goals_comments_input)

    def display_row_data_in_panel(self, data):
        row = self.table.currentRow()
        if row < 0:
            return

        for i, (label, widget) in enumerate(self.security_goals_property_controls):
            if label == "Responsible":
                combo = self.table.cellWidget(row, 3)
                if combo and hasattr(widget, "set_text"):
                    widget.set_text(combo.selected_items())
            elif label == "TOE Configuration":
                combo = self.table.cellWidget(row, 4)
                if combo and hasattr(widget, "set_text"):
                    widget.set_text(combo.selected_items())
            else:
                table_item = self.table.item(row, i + 1)  # Skip sidebar
                if table_item and hasattr(widget, "set_text"):
                    widget.set_text(table_item.text())

    # Optional: Call this if you’re doing visual refresh or toggle syncing
        PVD.SecurityGoals_display_selected_row(
            self.table,
            self.security_goals_property_controls,
            self.formatted_toe_configuration,
            self.property_panel_manager.property_panel,
            self.property_panel_manager.toggle_button
        )

    def build_property_panel(self):
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




