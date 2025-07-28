"""
Module Name   : Assumptions_action.py \n
Layer         : Presentation / Assumptions \n
Module ID     : CY_SM_004 \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Updated By    : Vishnu Viswanath \n
Updated On    : 2025-06-03 \n
Purpose:
--------
Handles the user interface logic for managing Assumptions. This includes rendering
dynamic property input panels, managing table interactions, and orchestrating Save,
Submit, Add, and Delete workflows using a structured signal-payload approach.

Description:
------------
This module leverages configuration-driven inputs and reusable UI components to
render Assumption property fields. Connects signals for table selection changes
and button actions to relevant handlers, updates UI states, and synchronizes
records across the table and the property panel. Also manages uniqueness checks
and handles dynamic refreshes via the loader interface.

Responsibilities:
-----------------
- Build and manage the Assumptions property panel
- Connect UI signals and button handlers
- Load and update Assumption records from database
- Handle Save/Add/Delete/Submit logic
- Emit structured signals for Save and selection events

Signals:
--------
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+
| Trigger                | Signal Name            | Description                                 | Payload Format                                             |
+========================+========================+=============================================+============================================================+
| Save button clicked    | property_save_clicked  | Emits form data from property panel         | {"sender": "Property panel", "event": "save", "data": dict}|
| Table row selected     | row_selected           | Emits selected row’s full data              | {"sender": "Table", "event": "row_selected", "data": dict} |
+------------------------+------------------------+---------------------------------------------+------------------------------------------------------------+

Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore)
- Target_Of_Evaluation.Assumptions.config.assumptions_config
- Target_Of_Evaluation.Assumptions.views.assumption_toolbar_panel
- Target_Of_Evaluation.Assumptions.controllers.assumption_manager
- components.propertypanel.property_input_components
- components.propertypanel.property_panel_layout
- components.action_panel
- components.table.table_panel
- components.loading_dialog.RoundLoader
- models.unique_name_action
- styles.property_panel_style
- utils.interface_utils
- controllers.TableValueHighlight

Limitations:
------------
- Field validation is not embedded into the panel widgets
- Multiselect and advanced widget types require additional handling logic
- Save/Submit behavior depends on database schema alignment

Improvements:
-------------
- Add inline input validation with error feedback
- Decouple panel rendering from static config
- Modularize table-widget sync for reuse in other components

Change History:
---------------
+----------------+----------------------+------------------------------------------------------------------+----------------------+
| Version        | Date                 | Change                                                           | Author               |
+================+======================+==================================================================+======================+
| V 3.0          | 2025-06-03           | Integrated dynamic property panel, save signal, and data sync | Vishnu Viswanath     |
+----------------+----------------------+------------------------------------------------------------------+----------------------+
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QTableWidgetItem
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from Target_Of_Evaluation.Assumptions.views.assumption_toolbar_panel import create_toolbar
from Target_Of_Evaluation.Assumptions.config.assumptions_config import PROPERTY_CONFIG, SAVE_BUTTON
from components.propertypanel.property_input_components import PropertyInputFactory
from styles.property_panel_style import property_save_button_style
from PyQt5.QtCore import pyqtSignal
import controllers.TableValueHighlight as TVH
import components.table.tree_row_indicator as TRI 
import Target_Of_Evaluation.controllers.assum_PropertyValueDisplay as PVD
import components.action_panel as action_panel
import components.table.table_panel as table_panel
import components.propertypanel.property_panel_layout as property_panel_layout
import Analysis.models.analysis_synchronization as AS
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
from models.unique_name_action import refrash_existing_entries, find_duplicates, store_selected_entry
from Target_Of_Evaluation.controllers.assumption_manager import (
    load_all_assumptions,
    create_assumption_and_insert_row,
    delete_assumption,
    persist_assumption_changes,
    ASSUMPTION_CACHE
)
import logging
import uuid
logger = logging.getLogger(__name__)

class Assumptions(QWidget):
    create_property_panel_signal = pyqtSignal()
    create_property_layout_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        logger.info("Assumption table view Initiated")
        self.initUI()

    def initUI(self):
        self.row_selected.connect(self.display_row_data_in_panel)

        self.HEIGHT_MAP = {}
        self.STYLE_MAP = {}

        self.property_panel_manager = property_panel_layout.PropertyPanelManager(self)
        self.property_panel_manager.create_property_panel()

        self.toggle_button = self.property_panel_manager.toggle_button
        self.property_panel = self.property_panel_manager.property_panel
        self.property_layout = self.property_panel_manager.property_layout

        self.Assumptions_property_controls = []

        self.create_property_panel_signal.connect(self.build_property_panel)
        self.create_property_panel_signal.emit()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        create_toolbar(self)
        main_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)
        table_panel.TablePanelWrapper.create_table_panel(self)

        self.action_panel_layout.addLayout(self.table_layout)
        self.action_panel_layout.addWidget(self.property_panel_manager.switch_property_panel)
        self.action_panel_layout.addWidget(self.property_panel_manager.property_panel)
        main_layout.addWidget(self.action_panel)

        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)
        self.save_button.setEnabled(False)

        self.add_button.clicked.connect(self.add_new_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.submit_button.clicked.connect(self.submit_changes)
        self.save_button.clicked.connect(self.submit_changes)

        self.existing_entries = set()
        self.table.itemChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.itemDoubleClicked.connect(self.store_selected_entry)
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()
        self.previous_text = None

    def on_row_selection_changed(self, selected, deselected):
        self.display_selected_row()
        TVH.on_row_selection_changed(self.table)

        if self.table.currentRow() >= 0:
            current_row = self.table.currentRow()

            # 🔁 Update icon selection
            for r, widget in self.row_sidebar_widgets.items():
                if widget:
                    widget.set_selected(r == current_row)

            row = current_row
            data = {
                "ID": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "Name": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                "Comments": self.table.item(row, 3).text() if self.table.item(row, 3) else ""
            }
            payload = {"sender": "Table", "event": "row_selected", "data": data}
            self.row_selected.emit(payload)

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
        QApplication.processEvents()

    # ✅ Set 4 columns to allow column 0 (can hide it)
        self.table.setColumnCount(4)

    # ✅ Set headers (leave column 0 blank for sidebar or hide)
        headers = ["", "ID", "Assumptions", "Comments"]
        for idx, title in enumerate(headers):
            self.table.setHorizontalHeaderItem(idx, QTableWidgetItem(title))

    # ✅ Hide column 0 if not used
        self.table.setColumnHidden(0, True)

    # ✅ Stretch layout
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        self.table.setRowCount(0)
        self.row_uuid_map = {}

        assumptions = load_all_assumptions()

        for assumption in assumptions:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setCellWidget(row, 0, TRI.SidebarWidget(selected=(row == 0)))
            self.row_sidebar_widgets[row] = self.table.cellWidget(row, 0)
            self.table.setItem(row, 1, QTableWidgetItem(assumption.assumption_id))
            self.table.setItem(row, 2, QTableWidgetItem(assumption.assumptions))
            self.table.setItem(row, 3, QTableWidgetItem(assumption.comments or ""))
            self.row_uuid_map[row] = assumption.uuid
            self.existing_entries.add(assumption.assumptions)

        self.select_first_row()
        interfaces.unsaved_changes = False

    def find_duplicates(self, changed_item):
        row = self.table.currentRow()
        column = self.table.currentColumn()
        if row >= 0 and column == 2:
            find_duplicates(self, changed_item)

    def store_selected_entry(self, item):
        store_selected_entry(self, item)

    def refrash_existing_entries(self):
        refrash_existing_entries(self)

    def add_new_entry(self):
        create_assumption_and_insert_row(self)
        self.update_button_states()
        interfaces.unsaved_changes = True

    # remove Scope Tree table data into the database
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

            delete_assumption(uuid)
            self.table.removeRow(row)

        # ✅ Rebuild the UUID map correctly
        new_map = {}
        for row in range(self.table.rowCount()):
            assumption_id_item = self.table.item(row, 1)
            if assumption_id_item:
                assumption_id = assumption_id_item.text().strip()
                for uuid, entry in ASSUMPTION_CACHE.items():
                    if entry['record'].assumption_id == assumption_id:
                        new_map[row] = uuid
                        break

        self.row_uuid_map = new_map

        self.table_data_changed = True
        interfaces.unsaved_changes = True
        self.update_button_states()


    def submit_changes(self):
        persist_assumption_changes()
        #AS.sync_assumptions_with_securityClaims()
        self.update_button_states()
        interfaces.unsaved_changes = False

    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True

    def on_assum_property_name_changed(self):
        PVD.on_property_multiline_changed(self.table, 2, self.assumption_assumptions_input)

    def on_assum_property_comment_changed(self):
        PVD.on_property_multiline_changed(self.table, 3, self.assumption_comments_input)

    def display_selected_row(self):
        PVD.display_selected_row(self.table, self.Assumptions_property_controls, self.property_panel, self.toggle_button)

    def closeEvent(self, event):
        event.accept()

    def build_property_panel(self):
        self.property_factory = PropertyInputFactory()
        self.assumption_property_controls = []

        for field in PROPERTY_CONFIG:
            input_widget = self.property_factory.create_common_property_input(
                field["label"],
                field["type"],
                self.property_layout,
                self.assumption_property_controls,
                getattr(self, field.get("signal")) if field.get("signal") else None,
                field.get("items")
            )

            if field.get("readonly"):
                input_widget.setReadOnly(True)
            setattr(self, f'assumption_{field["label"].lower().replace(" ", "_")}_input', input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.assumption_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)

    def handle_property_save_signal(self, payload):
        print(f"[TARA] 🔔 Assumption Save Signal Received → {payload}")

    def display_row_data_in_panel(self, data):
        row = self.table.currentRow()

        for i, (label, widget) in enumerate(self.assumption_property_controls):
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
            self.assumption_property_controls,
            self.property_panel_manager.property_panel,
            self.property_panel_manager.toggle_button
        )
def ensure_row_selection(self):
    if self.table.rowCount() > 0 and not self.table.selectionModel().hasSelection():
        self.table.selectRow(0)
