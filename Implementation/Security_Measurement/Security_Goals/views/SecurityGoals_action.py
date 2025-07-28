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


class SecurityGoals_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.previous_text = ""
        self.formatted_toe_configuration = []

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

    def on_row_selection_changed(self, selected, deselected):
        TVH.on_row_selection_changed(self.table)
        if self.table.currentRow() >= 0:
            row = self.table.currentRow()
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

    def load_data(self):
        self.loader = RoundLoader(self, label_text="Loading Security Goals...")
        self.loader.show()
        QApplication.processEvents()

        try:
            self.table.itemChanged.disconnect(self.find_duplicates)
        except Exception:
            pass

        try:
            # ✅ Load Security Goals
            goal_rows = SGM.load_all_security_goals()

            # ✅ Prepare Responsible options
            responsible_set = set()
            for g in goal_rows:
                if g.responsible:
                    responsible_set.update([r.strip() for r in g.responsible.split(',') if r.strip()])
            self.responsible_options = sorted(responsible_set) or ["Customer", "Supplier"]

            # ✅ Prepare TOE Config options
            toe_rows = get_instances(TOEConfiguration, {'is_deleted': False})
            self.formatted_toe_configuration = [
                f"{t.toe_configuration_id}::{t.toe_configuration_name}"
                for t in toe_rows
                if t.toe_configuration_id and t.toe_configuration_name
            ]
            print("📦 TOE Rows:", toe_rows)
            print("📋 Formatted TOE Config:", self.formatted_toe_configuration)

            # ✅ Also update property panel TOE dropdown
            if hasattr(self, "security_goals_toe_configuration_input"):
                print("✅ TOE input exists")
                self.security_goals_toe_configuration_input.additem(self.formatted_toe_configuration)
            else:
                print("❌ security_goals_toe_configuration_input not found")

            self.table.setRowCount(0)
            for idx, obj in enumerate(goal_rows):
                self.table.insertRow(idx)
                self.table.setCellWidget(idx, 0, TRI.SidebarWidget())
                self.table.setItem(idx, 1, QTableWidgetItem(obj.sg_id or ""))
                self.table.setItem(idx, 2, QTableWidgetItem(obj.name or ""))

                # Responsible dropdown
                resp_combo = MOS.TSMultiSelectComboBox(self.responsible_options, parent=self.table)
                selected_resp = [r.strip() for r in (obj.responsible or "").split(",") if r.strip()]
                resp_combo.set_text(selected_resp)
                resp_combo.model().dataChanged.connect(lambda: self.update_cell_to_cache(None))
                self.table.setCellWidget(idx, 3, resp_combo)

                # TOE Configuration dropdown
                toe_combo = MOS.TSMultiSelectComboBox(self.formatted_toe_configuration, parent=self.table)
                selected_toe = [
                    opt for opt in self.formatted_toe_configuration
                    if opt.startswith(obj.toe_configuration_id or "")
                ]
                toe_combo.set_text(selected_toe)
                toe_combo.model().dataChanged.connect(lambda: self.update_cell_to_cache(None))
                self.table.setCellWidget(idx, 4, toe_combo)
                print(f"🧪 TOE selected for row {idx}: {selected_toe}")

                self.table.setItem(idx, 5, QTableWidgetItem(obj.description or ""))
                self.table.setItem(idx, 6, QTableWidgetItem(obj.comments or ""))

                self.row_uuid_map[idx] = obj.uuid

            self.table.itemChanged.connect(self.find_duplicates)
            interfaces.unsaved_changes = False

        finally:
            self.loader.close()

        if hasattr(self, "security_goals_responsible_input"):
            self.security_goals_responsible_input.additem(self.responsible_options)

        if hasattr(self, "security_goals_toe_configuration_input"):
            print("✅ TOE input exists")
            self.security_goals_toe_configuration_input.additem(self.formatted_toe_configuration)

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
        except Exception:
            pass

        new_sg_id = SGM.generate_new_sg_id()
        sg_name = f"Security Goal {new_sg_id.split('-')[-1]}"
        created = SGM.create_security_goal(sg_id=new_sg_id, name=sg_name)
        if not created:
            QMessageBox.critical(self, "Error", f"Could not create SecurityGoal {new_sg_id}")
            return

        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, 40)
        self.table.setCellWidget(row_idx, 0, TRI.SidebarWidget())

        id_item = QTableWidgetItem(created.sg_id)
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row_idx, 1, id_item)

        name_item = QTableWidgetItem(created.name or sg_name)
        self.table.setItem(row_idx, 2, name_item)

        # Track for duplicate prevention
        self.previous_text = name_item.text()
        self.find_duplicates(name_item)
        self.existing_entries.add(name_item.text())

        # Responsible dropdown
        responsible_widget = MOS.TSMultiSelectComboBox(self.responsible_options)
        responsible_widget.set_text(created.responsible.split(',') if created.responsible else [])
        responsible_widget.model().dataChanged.connect(lambda: self.update_cell_to_cache(None))
        self.table.setCellWidget(row_idx, 3, responsible_widget)

        # TOE Configuration dropdown
        toe_widget = MOS.TSMultiSelectComboBox(self.formatted_toe_configuration)
        toe_widget.set_text(created.toe_configuration_id.split(',') if created.toe_configuration_id else [])
        toe_widget.model().dataChanged.connect(lambda: self.update_cell_to_cache(None))
        self.table.setCellWidget(row_idx, 4, toe_widget)

        self.table.setItem(row_idx, 5, QTableWidgetItem(created.description or ''))
        self.table.setItem(row_idx, 6, QTableWidgetItem(created.comments or ''))

        self.row_uuid_map[row_idx] = created.uuid

        self.update_button_states()
        interfaces.unsaved_changes = True
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.setCurrentCell(row_idx, 2)

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
        AS.remove_securityGoal_from_riskData()
        AS.sync_securityGoals_from_securityControl()
        self.update_button_states()
        interfaces.unsaved_changes = True

    def submit_changes(self):
        self.table.setFocus()
        SGM.persist_security_goal_changes()
        AS.remove_securityGoal_from_riskData()
        AS.sync_securityGoals_from_securityControl()
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


    def display_row_data_in_panel(self, data):
        row = self.table.currentRow()

        # Explicit mapping: label → column index
        label_column_map = {
            "ID": 1,
            "Name": 2,
            "Responsible": 3,
            "TOE Configuration": 4,
            "Description": 5,
            "Comments": 6
        }

        for label, widget in self.security_goals_property_controls:
            col = label_column_map.get(label)
            if col is None:
                continue

            if label in ["Responsible", "TOE Configuration"]:
                cell_widget = self.table.cellWidget(row, col)
                selected = cell_widget.selected_items() if cell_widget else []
                text = ", ".join(selected)
            else:
                item = self.table.item(row, col)
                text = item.text() if item else ""

            if hasattr(widget, "set_text"):
                widget.set_text(text)
            elif hasattr(widget, "setText"):
                widget.setText(text)

        # Update visual selection highlight
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

        # Add only one global Save button at the end
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




