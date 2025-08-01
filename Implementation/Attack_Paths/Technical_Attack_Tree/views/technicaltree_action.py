
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, 
                             QMessageBox, QTabWidget, QTableWidget, QToolBar, QToolButton, 
                             QTableWidgetItem, QLineEdit, QComboBox, QAbstractItemView
                            )   
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
import models.Parameters as P
import models.helper as helper
import sqlite3
import Attack_Paths.Technical_Attack_Tree.views.technicaltree_tree_action as TATCA
from Attack_Paths.Technical_Attack_Tree.views.technicaltree_table_toolbar_panel import create_toolbar
from Attack_Paths.Attack_Tree.views.attacktree_tree_toolbar_panel import create_tree_toolbar
# from Attack_Paths.views.attackpaths_table_panel import create_table_panel
from Attack_Paths.Attack_Tree.views.attacktree_column_setup import Setup_Tabel_ColumnHeading
from controllers.schema_manager import delete_all_instance,create_instance,get_instances
from controllers.tablemodel import TOEConfiguration,Threats,AttackTreeHome
import models.TableStyle as TS
import models.ToolbarStyle as TBS
import controllers.DatabaseCreator as DB
import components.table.table_row_indicator as TRI
import controllers.TableValueHighlight as TVH
import controllers.CreateTabAction as CTA
import components.action_panel as action_panel
import styles.tree_panel_style as tree_panel_style
import styles.action_panel_style as action_panel_style
import utils.interface_utils as interfaces
from PyQt5.QtWidgets import QApplication
from components.loading_dialog import RoundLoader
from controllers.tablemodel import TechnicalTreeHome, TOEConfiguration, Assumptions
from Attack_Paths.Technical_Attack_Tree.controllers.technicaltree_manager import (
    load_all_technical_trees,
    create_technical_tree_and_insert_row,
    persist_technical_tree_changes,
    delete_technical_tree,
    update_technical_tree,
    TECHNICAL_TREE_CACHE
)
from Attack_Paths.RiskControl_Tree.controllers.risk_control_tree_manager import load_all_RCT, RCT_CACHE, persist_tree_changes, update_tree
from controllers.schema_manager import get_instances, get_first_instance
from components.table.multiselect_combo import MultiSelectComboSelector

import logging
from components.table.table_panel import TablePanelWrapper
logger = logging.getLogger(__name__)


class TechnicalTreeModule(QWidget):
    def __init__(self):
        super().__init__()
        logger.info("Technical Tree View Initiated")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.layout.setSpacing(0)  # Remove spacing between widgets
        self.data_loaded = False
        self.table_wrapper = None  # ✅ Ensure defined before use
        self.row_uuid_map = {}  # ✅ maps row index → UUID
        self.tree_names_after = {}
        self.init_ui()
     
    def init_ui(self):
        # Create a QTabWidget that will hold both the Home panel and the Child panel
        self.tab_container = QTabWidget()
        self.tab_container.setContentsMargins(0,0,0,0)
        self.tab_container.setTabsClosable(False)  # No need for closable tabs here
        self.tab_container.tabBar().setVisible(False)  # Hide the tab bar to make it look like a panel
        self.layout.addWidget(self.tab_container)

        # Create the parent "Home" panel
        self.home_panel = QWidget()
        self.home_panel_layout = QVBoxLayout()
        self.home_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.home_panel_layout.setSpacing(0)
        self.home_panel.setLayout(self.home_panel_layout)
        
        create_toolbar(self)
        self.home_panel_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)

        # ✅ Table wrapper setup
        self.table_wrapper = TablePanelWrapper(use_row_indicator=True, use_tree_indicator=True, parent=self)
        self.table_wrapper.create_table_panel()
        self.table_wrapper.set_headers("technicaltree")

        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout

        self.index = None
        self.table.clicked.connect(self.get_index)

        # Table goes inside the action panel
        self.action_panel_layout.addWidget(self.table_wrapper.table)
        self.home_panel_layout.addWidget(self.action_panel)
        
        # Enable/disable buttons
        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)
        
        # Connect buttons to functions
        self.add_button.clicked.connect(self.Add_Record)
        self.delete_button.clicked.connect(self.Remove_Record)
        self.submit_button.clicked.connect(self.submit_changes)


        # Connect table signals to state updater
        self.table_data_changed = False
        self.table.itemChanged.connect(self.table_data_changed_set_flag)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.itemChanged.connect(self.update_cache_data)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.update_button_states()

        # Create the child panel which will hold the inner QTabWidget
        self.child_panel = QWidget()
        self.child_panel_layout = QVBoxLayout()
        self.child_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.child_panel_layout.setSpacing(0)
        self.child_panel.setLayout(self.child_panel_layout)

        self.active_technical_at_class = None
        self.tab_technical_instances = {}
        create_tree_toolbar(self)
        self.child_panel_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)
        self.tree_submit_button.clicked.connect(self.on_save_button_click)
        
        self.action_tabwidget_panel = QWidget()
        self.action_tabwidget_panel_layout = QHBoxLayout()
        self.action_tabwidget_panel.setLayout(self.action_tabwidget_panel_layout)
        # self.action_tabwidget_panel.setContentsMargins(0,0,0,0)
        self.action_tabwidget_panel_layout.setContentsMargins(0,0,0,0)
        self.action_tabwidget_panel_layout.setSpacing(0)
        self.action_tabwidget_panel.setStyleSheet(tree_panel_style.action_panel_style)

        # Create the inner QTabWidget and add it to the child panel layout
        self.inner_tab_widget = QTabWidget() 
        self.inner_tab_widget.setTabsClosable(True)
        # self.inner_tab_widget.setContentsMargins(10,10,10,10)
        self.inner_tab_widget.setStyleSheet(action_panel_style.action_panel_style)
        self.inner_tab_widget.tabCloseRequested.connect(self.Close_Tab)
        self.inner_tab_widget.currentChanged.connect(self.update_toolbar_tree_label)
        self.action_tabwidget_panel_layout.addWidget(self.inner_tab_widget)
        self.action_panel_layout.addWidget(self.action_tabwidget_panel)
        self.action_panel_layout.setContentsMargins(10,10,10,10)
        # self.action_panel_layout.setSpacing(10)
        # self.action_panel.setStyleSheet(tree_panel_style.action_panel_style)
        self.child_panel_layout.addWidget(self.action_panel)

        # Add the "Home" panel and the child panel to the QTabWidget
        self.tab_container.addTab(self.home_panel, "Home")  # Home panel as the first tab
        self.tab_container.addTab(self.child_panel, "Child Panel")
        self.previous_text = None
        self.load_data()

    # Load Attack Tree table data from the database
    def load_data(self):
        if self.data_loaded:
            self.table_data_changed = False
            self.tab_container.setCurrentIndex(0)
            return  # 🚫 Prevent reloading if already loaded
        
        interfaces.previous_tree = None
        self.tab_container.setCurrentIndex(0)
        self.loader = RoundLoader(self, label_text="Loading...")
        self.loader.show()
        QApplication.processEvents()

        try:
            self.table.setRowCount(0)
            self.row_uuid_map.clear()
            interfaces.unsaved_changes = False

            loaded = load_all_technical_trees()
            self.technical_tree_names_before = {}

            # ✅ 1. Load dropdown options
            self.toe_configuration_option_list = [
                f"{item.toe_configuration_id}::{item.toe_configuration_name}"
                for item in get_instances(TOEConfiguration)
            ]
            self.assumptions_option_list = [
                f"{item.assumption_id}::{item.assumptions}"
                for item in get_instances(Assumptions)
            ]

            for tree in loaded:
                row_index = self.table.rowCount()
                self.table_wrapper.insert_row([
                    tree.id,
                    tree.name,
                    tree.used_in_threat if tree.used_in_threat else '',
                    tree.used_in_riskcontrol if tree.used_in_riskcontrol else '',
                    '',
                    '',
                    tree.comment if tree.comment else ''
                ])
                self.row_uuid_map[row_index] = tree.uuid
                self.add_multiselect_to_table_cell(row_index, 5, self.toe_configuration_option_list, tree.toe_configuartion_id, 'toe_configuartion_id')
                self.add_multiselect_to_table_cell(row_index, 6, self.assumptions_option_list, tree.assumption_id, 'assumption_id')
                self.technical_tree_names_before[tree.id] = tree.name

            self.data_loaded = True

        except Exception as e:
            logger.exception("❌ Error loading Technical Trees")
            QMessageBox.critical(self, "Error", f"Failed to load Technical Trees:\n{e}")

        finally:
            self.loader.close()

    def get_index(self, index):
        self.index = index
        print("index: ", index)

    # Highlight selected row in table
    def on_row_selection_changed(self):
        # temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed2(self.table, self)
        # interfaces.unsaved_changes = temp

    def Add_Record(self):
        self.table.setFocus()
        row_before = self.table.rowCount()

        create_technical_tree_and_insert_row(self)
        self.submit_changes()
        self.update_button_states()
        interfaces.unsaved_changes = False

    def update_cache_data(self):
        row = self.table.currentRow()
        changed_tree_ids = []

        id_item = self.table.item(row, 1)
        name_item = self.table.item(row, 2)
        uuid = self.row_uuid_map.get(row)
        if not uuid or not id_item or not name_item:
            return
        tree_id = id_item.text()
        name = name_item.text()
        used_in_threat = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        used_in_riskcontrol = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
        comments = self.table.item(row, 6).text() if self.table.item(row, 6) else ""

        if uuid in TECHNICAL_TREE_CACHE:
            record = TECHNICAL_TREE_CACHE[uuid]['record']
            old_name = record.name
            changed = update_technical_tree(uuid, {
                'name': name_item,
                'used_in_threat': used_in_threat,
                'used_in_riskcontrol': used_in_riskcontrol,
                'comment': comments
            })
            if changed and old_name != name_item:
                changed_tree_ids.append(tree_id)

        self.tree_names_after[tree_id] = name_item

        #logger.info(f"Tree names before: {self.tree_names_before}")
        logger.info(f"Tree names after: {self.tree_names_after}")

    def submit_changes(self):
        self.table.setFocus()
        logger.info('Technical Attack Tree Table Data Submission started')
        persist_technical_tree_changes()
        interfaces.unsaved_changes = False
        self.update_button_states()
        logger.info('✅ Technical Attack Tree Table Data Submitted successfully')
	
    def Remove_Record(self):
        selected_rows = sorted(self.table.selectionModel().selectedRows(), key=lambda x: x.row(), reverse=True)
        if not selected_rows:
            return

        for index in selected_rows:
            row = index.row()
            uuid = self.row_uuid_map.get(row)

            if not uuid:
                continue

            delete_technical_tree(uuid)
            self.table.removeRow(row)

        new_map = {}
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            if id_item:
                id_val = id_item.text().strip()
                for uuid, entry in TECHNICAL_TREE_CACHE.items():
                    if entry['record'].id == id_val:
                        new_map[row] = uuid
                        break

        self.row_uuid_map = new_map
        interfaces.unsaved_changes = True
        self.update_button_states()

    # Open Risk Control Tree in new tab
    def open_tree(self, index):
        # sender = self.sender()
        print("open tree page..... ", index)
        if not index or not index.isValid():
            QMessageBox.warning(None, "Selection Error", "Unable to determine the selected row.")
            return
        
        # Ensure no existing loader before creating a new one
        if not hasattr(self, "round_loader") or self.round_loader is None:
            self.round_loader = RoundLoader(self, label_text='Loading...')
            self.round_loader.show()
            QApplication.processEvents()  # Ensure UI updates while loader is shown

        if index is None or not index.isValid():
            QMessageBox.warning(None, "Selection Error", "Unable to determine the selected row.")
            if self.round_loader:
                self.round_loader.accept()  # Close loader in case of error
                self.round_loader = None
            self.setEnabled(True)  # Re-enable interactions
            return

        row = index.row()
        open_tree_enable = True
        # Handle unsaved changes before switching to the edit page
        if self.table_data_changed:
            if not interfaces.autosave_enabled:
                message_reply = QMessageBox.warning(None, "Warning", "Please save the changes before switching to the edit page.", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if message_reply == QMessageBox.Ok:
                    self.submit_changes()
            else:
                self.submit_changes()

        # Extract item_id and item_name from the clicked row
        print(f"self.index : {self.index}")
        # row = self.index.row()
        item_id = self.table.item(row, 1).text()
        item_name = self.table.item(row, 2).text()
        logger.info(f"Technical Tree Editor Opened for {item_id} {item_name}")

        self.setEnabled(False)
        
        # Check if the tab is already available
        tab_index = self.is_tab_available(item_id)
        if tab_index != -1:
            # Tab exists, switch to it
            self.inner_tab_widget.setCurrentIndex(tab_index)
            self.active_technical_at_class = self.tab_technical_instances[f'{self.inner_tab_widget.tabText(tab_index)}']
            self.active_technical_at_class.Load_TechnicalTree()  # Call loadtree() on the active class
        else:
            # If the tab doesn't exist, create the new tab content
            tab_header = CTA.TabHeader(title=item_id, close_callback=lambda: self.Close_Tab(self.inner_tab_widget.indexOf(tab_header)))

            # Create the new Technical Tree instance
            technical_at_class = TATCA.TechnicalATClass(self)
            if item_id not in self.tab_technical_instances.keys():
                self.tab_technical_instances[item_id] = technical_at_class
            technical_at_class.Create_TechnicalTree_Tab(item_id, item_name)
            self.active_technical_at_class = self.tab_technical_instances[item_id]
            self.tree_toolbar_label.setText(item_name)

        # Handle unsaved changes before switching to the edit page
        if open_tree_enable == True:
           self.tab_container.setCurrentIndex(1)
        self.setEnabled(True)
        # Close the round loader after the tree is fully loaded
        if self.round_loader:
            self.round_loader.accept()
            self.round_loader = None

    def update_button_states(self):
        """
        Updates the state of the Save and Delete buttons based on the table's state.
        """
        row_count = self.table.rowCount()
        has_selection = bool(self.table.selectionModel().selectedRows())

        # Update "Submit" button state
        self.submit_button.setEnabled(row_count > 0)

    def update_toolbar_tree_label(self, index):  
        logger.info(f"Switched to tab {self.inner_tab_widget.tabText(index)}")
        tab_id = self.inner_tab_widget.tabText(index)
        # **Prevent unnecessary updates when selecting the same tab**
        if self.inner_tab_widget.currentIndex() == index and self.active_technical_at_class == self.tab_technical_instances.get(tab_id):
            logger.info("Same tab selected, skipping update.")
            return  # ✅ Exit early to prevent autosave popup from triggering
        
        # **Autosave Condition (Same as Attack Tree)**
        interfaces.previous_module = None
        if interfaces.autosave_enabled and interfaces.previous_tree and interfaces.unsaved_changes:
            interfaces.previous_tree.Save_Tree()  # Corrected function name
        elif not interfaces.autosave_enabled and interfaces.previous_tree and interfaces.unsaved_changes:
            # Show a popup to confirm if the user wants to discard changes
            reply = QMessageBox.question(
                None, 'Unsaved Changes',
                "You have unsaved changes. Do you want to save them before switching?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            # Handle user's choice
            if reply == QMessageBox.Yes:
                interfaces.previous_tree.Save_Tree()  # Corrected function name
            elif reply == QMessageBox.No:
                interfaces.unsaved_changes = False

        rows = get_first_instance(TechnicalTreeHome, {'id':f'{self.inner_tab_widget.tabText(index)}'})
        if rows:
            self.tree_toolbar_label.setText(rows.id) 
            self.active_technical_at_class = self.tab_technical_instances[tab_id]
            interfaces.previous_tree = self.active_technical_at_class
            if not interfaces.tool_reset_enable:
                self.active_technical_at_class.Load_TechnicalTree()
            interfaces.tree_tab_panel['TechnicalTree'] = (self.inner_tab_widget, self.tab_technical_instances)

    # Common Save Button Handler
    def on_save_button_click(self):
        logger.info("Technical Tree Save Button Clicked")

        # Show the loader before starting the save process
        self.round_loader = RoundLoader(self, label_text= 'Saving...')
        self.round_loader.show()
        QApplication.processEvents()  # Ensures UI updates after showing loader

        try:
            if self.active_technical_at_class:
                self.active_technical_at_class.Save_Tree()  # Call save function

                # Hide the loader **before** any success message appears
                self.round_loader.accept()

                # REMOVE DUPLICATE SUCCESS MESSAGE BOX
                logger.info("Technical Tree saved successfully!")  # Just log the success message

        except Exception as e:
            # Hide loader if an error occurs
            self.round_loader.accept()
            QMessageBox.critical(None, "Error", f"Error saving Technical Tree: {str(e)}")

    # Close selected Tab
    def Close_Tab(self, index):  
        logger.info(f"Technical Tree {self.inner_tab_widget.tabText(index)} Tab Closed")       
        # Remove the threat instance from the dictionary if found
        if self.inner_tab_widget.tabText(index):
            self.tab_technical_instances.pop(f'{self.inner_tab_widget.tabText(index)}', None)
            interfaces.tree_tab_panel['TechnicalTree'] = (self.inner_tab_widget, self.tab_technical_instances)
        
        # Check if no tabs remain
        self.inner_tab_widget.removeTab(index)
        tab_count = self.inner_tab_widget.count()
        if tab_count == 0:
            self.tab_container.setCurrentIndex(0)
            interfaces.previous_tree = None
            if interfaces.tool_reset_enable != True:
                interfaces.previous_module = self
                self.load_data()
    
    def table_data_changed_set_flag(self):
        self.table_data_changed = True
        self.update_button_states()

    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True    
    
    def is_tab_available(self, item_id):
        for index in range(self.inner_tab_widget.count()):
            if self.inner_tab_widget.tabText(index) == f"{item_id}":
                return index
        return -1  # Tab not found


    def add_multiselect_to_table_cell(self, row_index, column_index, option_list, current_value, field_name):
        """
        Generic helper for adding MultiSelectComboSelector to Threat Scenarios table.

        Args:
            row_index (int): Table row index.
            column_index (int): Table column index.
            option_list (list[str]): List of selectable options.
            current_value (str): Pre-selected value from DB (comma-separated string).

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
            # self.table.setItem(row_index, column_index, QTableWidgetItem(value))
            uuid = self.row_uuid_map.get(row_index)
            if uuid:
                update_technical_tree(uuid, {field_name: value})  # ✅ Function change
                interfaces.unsaved_changes = True

        combo.model().dataChanged.connect(on_selection_change)
        self.table.setCellWidget(row_index, column_index, combo)
