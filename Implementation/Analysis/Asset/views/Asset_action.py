"""
Module Name   : Asset_action.py \n
Layer         : Presentation / Asset \n
Module ID     : CY_SM_007 \n
Requirement ID: N/A \n
Version       : V 3.0 \n
Updated By    : Vishnu Viswanath \n
Updated On    : 2025-06-03 \n

Purpose:
--------
Provides the UI logic for managing Asset records, including the creation and
display of property panels, handling table interactions, and emitting standardized
signals for downstream consumption.

Description:
------------
Integrates the asset-specific input configuration (`PROPERTY_CONFIG`) with reusable
UI components (`PropertyInputFactory`) to create dynamic property panels. Manages
event-driven updates between the table and property widgets. Facilitates actions like
add, delete, submit, and Save, while preserving UI consistency.

Responsibilities:
-----------------
- Render and manage asset-specific property panels
- Synchronize row data between table and input widgets
- Handle Save, Add, Delete, and Submit actions
- Emit signals for row selection and property updates

Signals:
--------
+------------------------+------------------------+---------------------------------------------+-----------------------------------------------------------+
| Trigger                | Signal Name            | Description                                 | Payload Format                                            |
+========================+========================+=============================================+===========================================================+
| Save button clicked    | property_save_clicked  | Emits updated form data                     | {"sender": str, "event": "save", "data": dict}            |
| Table row selected     | row_selected           | Emits selected row's full data              | {"sender": "Table", "event": "row_selected", "data": dict}|
+------------------------+------------------------+---------------------------------------------+-----------------------------------------------------------+

Dependencies:
-------------
- PyQt5 (QtWidgets, QtCore)
- components.propertypanel.property_input_components
- Analysis.Asset.config.asset_config
- Analysis.controllers.analysis_PropertyValueDisplay
- Analysis.controllers.analysis_TableValueLoad
- styles.property_panel_style
- utils.interface_utils

Limitations:
------------
- Validation logic is not enforced at input level
- Property config assumes consistent index mapping with table columns

Improvements:
-------------
- Add inline field validation with visual feedback
- Support tabbed or grouped property layouts
- Decouple table column index dependency via header mapping

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


from venv import logger
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidgetItem, QMessageBox

import Analysis.controllers.analysis_TableValueLoad as TVL
import Analysis.controllers.analysis_TableAddRecord as TAR
import Analysis.controllers.analysis_TableRemoveRecord as TRR
import Analysis.controllers.analysis_TableSaveRecord as TSR
import Analysis.controllers.analysis_TableRefreshRecord as TFR 
import Analysis.controllers.analysis_PropertyValueDisplay as PVD
from Analysis.Asset.views.asset_toolbar_panel import create_toolbar

from Analysis.controllers.asset_manager import ASSET_CACHE, add_new_asset, delete_asset, generate_new_asset_id, is_asset_name_duplicate, load_all_assets, persist_asset_changes, update_asset
from controllers.database_tables.analysis_tables import Assets
import controllers.TableValueHighlight as TVH
import components.action_panel as action_panel
import components.table.table_panel as table_panel
import components.propertypanel.property_panel_layout as property_panel_layout
import Analysis.models.analysis_synchronization as AS
import Target_Of_Evaluation.Scope.controllers.scope_synchronizations as TSS
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
from Analysis.Asset.models.unique_name_action import find_duplicates, store_selected_entry
from Analysis.Asset.config.asset_config import PROPERTY_CONFIG, SAVE_BUTTON
from styles.property_panel_style import property_save_button_style
from components.propertypanel.property_input_components import PropertyInputFactory 
from PyQt5.QtCore import pyqtSignal
from models.helper import asset_header  # Ensure this import is at the top



class Asset_Module(QWidget):
    create_property_panel_signal = pyqtSignal()
    create_property_layout_signal = pyqtSignal()
    property_save_clicked = pyqtSignal(dict)
    row_selected = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.table = None   # Optional, prevents attribute error
        self.initUI()
        self.data_loaded = False
        self.table_data_changed = False
        self.row_id_map = {}
        self.asset_names_before = {}

    def initUI(self):
        self.HEIGHT_MAP = {}
        self.STYLE_MAP = {}

        self.panel_manager = property_panel_layout.PropertyPanelManager(self)
        self.panel_manager.create_property_panel()

        self.toggle_button = self.panel_manager.toggle_button
        self.property_panel = self.panel_manager.property_panel
        self.property_layout = self.panel_manager.property_layout

        self.asset_property_controls = []

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

        # Table setup
        self.table_wrapper = table_panel.TablePanelWrapper(
            use_row_indicator=True, use_tree_indicator=False, parent=self
        )
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("asset")
        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout

        # Now it is SAFE to connect selection
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
        self.row_selected.connect(self.display_row_data_in_panel)

        # Compose layout
        self.action_panel_layout.addWidget(self.table_wrapper.table)
        self.action_panel_layout.addWidget(self.panel_manager.switch_property_panel)
        self.action_panel_layout.addWidget(self.panel_manager.property_panel)
        main_layout.addWidget(self.action_panel)

        # Button setup
        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)

        self.add_button.clicked.connect(self.add_new_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.submit_button.clicked.connect(self.submit_changes)
        self.save_button.clicked.connect(self.submit_changes)

        # Table signals (all on self.table!)
        self.existing_entries = set()
        self.table.itemChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        # self.table.itemDoubleClicked.connect(self.store_selected_entry)
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed) 
        self.update_button_states()
        self.table.setFocus()
        self.previous_text = None



    def load_data(self):
        if self.data_loaded:
            self.table_data_changed = False
            return
        self.table.setRowCount(0)
        loaded_assets = load_all_assets()
        self.table_data_changed = False
        self.asset_names_before = {}

        asset_attr_map = {
            'ID': 'asset_id',
            'Name': 'name',
            'Security Properties': 'security_properties',
            'Description': 'description',
            'Comments': 'comments'
        }

        for asset in loaded_assets:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for col_index, header in enumerate(asset_header):
                attr = asset_attr_map[header]
                value = getattr(asset, attr, "") or ""
                # If you want a ComboBox for 'Security Properties', add logic here:
                if header == "Security Properties":
                    # self.add_combo_to_security_property_cell(row_index, value)
                    self.table.setItem(row_index, col_index + 1, QTableWidgetItem(value))
                else:
                    self.table.setItem(row_index, col_index + 1, QTableWidgetItem(value))

            self.row_id_map[row_index] = asset.asset_id
            self.asset_names_before[asset.asset_id] = asset.name

        self.data_loaded = True


    def on_row_selection_changed(self, selected, deselected):
        """
        Emits row_selected signal with structured data when a new table row is selected.
        """
        temp = interfaces.unsaved_changes  # preserve current state if needed
        TVH.on_row_selection_changed(self.table)

        print("check on row slction changdd 1111111111111111111111111111")
        if self.table.currentRow() >= 0:
            row = self.table.currentRow()
            data = {
                "ID": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "Name": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                "Security Properties": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                "Description": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                "Comments": self.table.item(row, 5).text() if self.table.item(row, 5) else "",
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

        self.delete_button.setEnabled(row_count > 0 and has_selection)
        self.submit_button.setEnabled(row_count > 0)


    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True

    def find_duplicates(self, changed_item):
        row = self.table.currentRow()
        column = self.table.currentColumn()
        # Only check for the Name column (column 2)
        if row < 0 or column != 2:
            return

        changed_text = changed_item.text().strip()
        asset_id = self.row_id_map.get(row)  # The asset_id for this row (edit or new)

        if not changed_text:
            QMessageBox.warning(None, "Name Error", f"Name should not be empty.")
            changed_item.setText(self.previous_text or "Unnamed")
            return

        # Use cache-based duplicate check
        if is_asset_name_duplicate(changed_text, exclude_asset_id=asset_id):
            QMessageBox.warning(None, "Name Error", f"'{changed_text}' already exists. Please use a unique name.")
            count = 1
            new_text = f"{changed_text} copy"
            while is_asset_name_duplicate(new_text, exclude_asset_id=asset_id):
                new_text = f"{changed_text} copy {count}"
                count += 1
            changed_item.setText(new_text)
        # else: name is unique, nothing to do

    def store_selected_entry(self, item): store_selected_entry(self, item)
    
    def refresh_data(self): TFR.asset_refresh_data(self.table)

    def add_new_entry(self):
        self.table.setFocus()
        row_before = self.table.rowCount()
        # -- Create new asset with unique ID --
        asset_id = generate_new_asset_id()
        asset_name = f"Asset {asset_id.split('-')[-1]}"
        asset = Assets(
        asset_id=asset_id,
        name=asset_name,
        security_properties="",
        description="",
        comments="",
        created_by="system",     # <-- Add this!
        updated_by="system"      # <-- And this!
    )
        add_new_asset(asset)  # adds to DB/cache

        # Add to table
        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
        self.table.setItem(row_index, 1, QTableWidgetItem(asset.asset_id))
        self.table.setItem(row_index, 2, QTableWidgetItem(asset.name))
        self.table.setItem(row_index, 3, QTableWidgetItem(asset.security_properties))
        self.table.setItem(row_index, 4, QTableWidgetItem(asset.description))
        self.table.setItem(row_index, 5, QTableWidgetItem(asset.comments))
        self.row_id_map[row_index] = asset.asset_id
        self.asset_names_before[asset.asset_id] = asset.name
        self.submit_changes()  # Optionally auto-save after add
        self.data_loaded = False   # <-- force reload!
        self.load_data()
        self.table.viewport().update()  # Refresh UI

        
    def delete_entry(self): 
     
        selected_rows = sorted(self.table.selectionModel().selectedRows(), key=lambda x: x.row(), reverse=True)
        if not selected_rows:
            return
        for index in selected_rows:
            row = index.row()
            asset_id = self.row_id_map.get(row)
            if not asset_id:
                logger.warning(f"No asset_id for row {row}. Skipping.")
                continue
            delete_asset(asset_id)
            self.table.removeRow(row)
        # Rebuild row_id_map
        new_map = {}
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item:
                asset_id = item.text().strip()
                if asset_id in ASSET_CACHE:
                    new_map[row] = asset_id
        self.row_id_map = new_map
        self.table_data_changed = True

    def submit_changes(self):
        self.table.setFocus()
        asset_names_after = {}
        changed_asset_ids = []

        for row in range(self.table.rowCount()):
            asset_id_item = self.table.item(row, 1)
            asset_name_item = self.table.item(row, 2)
            if not asset_id_item or not asset_name_item:
                continue
            asset_id = asset_id_item.text()
            name = asset_name_item.text()
            security_properties = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
            description = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
            comments = self.table.item(row, 5).text() if self.table.item(row, 5) else ""

            if asset_id in ASSET_CACHE:
                record = ASSET_CACHE[asset_id]['record']
                old_name = record.name
                changed = update_asset(asset_id, {
                    'name': name,
                    'security_properties': security_properties,
                    'description': description,
                    'comments': comments
                })
                if changed and old_name != name:
                    changed_asset_ids.append(asset_id)

            asset_names_after[asset_id] = name

        logger.info(f"Asset names before: {self.asset_names_before}")
        logger.info(f"Asset names after: {asset_names_after}")

        persist_asset_changes()
        self.asset_names_before = asset_names_after.copy()
        self.table_data_changed = False
        logger.info("Asset data successfully submitted and updated.")
    
    def on_asset_property_name_changed(self): PVD.on_property_multiline_changed(self.table, 2, self.asset_name_input)
    def on_asset_property_securityproperty_changed(self): PVD.on_property_multiselect_changed(self.table, 3, self.asset_security_properties_input)
    def on_asset_property_description_changed(self): PVD.on_property_multiline_changed(self.table, 4, self.asset_description_input)       
    def on_asset_property_comment_changed(self): PVD.on_property_multiline_changed(self.table, 5, self.asset_comments_input)
    
    def display_selected_row(self): 
  
        temp = interfaces.unsaved_changes
        PVD.asset_display_selected_row(self.table, self.asset_property_controls,self.property_panel,self.toggle_button)
        interfaces.unsaved_changes = temp

    def closeEvent(self, event):
        event.accept()

    def build_property_panel(self):
        """
        Dynamically constructs the property input panel based on configuration.

        Reads the PROPERTY_CONFIG to generate input widgets, binds signal handlers
        to relevant fields, and appends them to the property layout.

        Also creates and configures a Save button if enabled in SAVE_BUTTON config.

        Signals:
        --------
        - Binds property change signals for each widget.
        - Connects Save button to property_save_clicked signal.

        Effects:
        --------
        - Sets instance attributes like asset_name_input, asset_description_input, etc.
        - Stores controls in self.asset_property_controls.
        - Save button is conditionally added and enabled/disabled.

        See Also:
        ---------
        - PropertyInputFactory.create_common_property_input
        - PropertyInputFactory.create_save_button
        """
        print("paroerty pannel builddddddddddddddd---------------------------")
        self.property_factory = PropertyInputFactory()
        for field in PROPERTY_CONFIG:
            input_widget = self.property_factory.create_common_property_input(
                field["label"],
                field["type"],
                self.property_layout,
                self.asset_property_controls,
                getattr(self, field.get("signal")) if field.get("signal") else None,
                field.get("items")
            )

            if field.get("readonly"):
                input_widget.setReadOnly(True)
            setattr(self, f'asset_{field["label"].lower().replace(" ", "_")}_input', input_widget)

        if SAVE_BUTTON.get("enabled"):
            self.save_button = self.property_factory.create_save_button(
                layout=self.property_layout,
                style=property_save_button_style,
                controls_list=self.asset_property_controls,
                signal=self.property_save_clicked,
                sender="Property panel"
            )
            self.save_button.setEnabled(False)

        self.property_save_clicked.connect(self.handle_property_save_signal)

    def handle_property_save_signal(self, payload):
        print(f"[TARA] 🔔 Signal Received → {payload}")

    def display_row_data_in_panel(self, data):
        """
        Displays the selected table row's data in the property panel.

        Clears or resets fields based on table state and repopulates
        the widgets with the corresponding values from the currently selected row.

        Parameters:
        -----------
        data : dict
            Dictionary containing the selection payload with structure:
            {
                "sender": "Table",
                "event": "row_selected",
                "data": {
                    "Field 1": "value",
                    ...
                }
            }

        Effects:
        --------
        - Clears widgets if table cells are empty.
        - Loads table data into property panel fields.
        - Delegates final rendering to asset_display_selected_row().

        See Also:
        ---------
        - PVD.asset_display_selected_row
        """

        row = self.table.currentRow()

        for i, (label, widget) in enumerate(self.asset_property_controls):
            table_item = self.table.item(row, i + 1)
            cell_widget = self.table.cellWidget(row, i + 1)

            should_clear = False

            # Handle multiselect or custom widget
            if hasattr(widget, "selected_items") or hasattr(widget, "get_selected_items"):
                if not (hasattr(cell_widget, "selected_items") and cell_widget.selected_items()):
                    should_clear = True
                if should_clear and hasattr(widget, "set_text"):
                    widget.set_text([])  # Clear multiselect with empty list
                continue  # Skip to next widget

            # Regular text/combo field
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

        # Finally populate data from the table
        print("check property panel data printed-------------------------11111111")
        PVD.asset_display_selected_row(
             
            self.table,
            self.asset_property_controls,
            self.panel_manager.property_panel,
            self.panel_manager.toggle_button
        )

