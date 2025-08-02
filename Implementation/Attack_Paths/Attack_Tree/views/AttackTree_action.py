
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
import Attack_Paths.Attack_Tree.views.AttackTree_Threat_action as ATTA
from Attack_Paths.Attack_Tree.views.attacktree_table_toolbar_panel import create_toolbar
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
import components.table.multioption_selector as MOS
import controllers.CreateTabAction as CTA
import Analysis.models.analysis_synchronization as AS

import components.action_panel as action_panel
import styles.tree_panel_style as tree_panel_style
import styles.action_panel_style as action_panel_style
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
from PyQt5.QtWidgets import QApplication
from controllers.schema_manager import get_first_instance
from Attack_Paths.Attack_Tree.controllers.attack_tree_manager import load_all_AT, AT_CACHE, persist_tree_changes, update_tree
from components.table.multiselect_combo import MultiSelectComboSelector

import logging
from components.table.table_panel import TablePanelWrapper
logger = logging.getLogger(__name__)


class Attack_Tree(QWidget):
    def __init__(self):
        super().__init__()
        logger.info(f'Attack Tree View Initialized')
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
        self.table_wrapper.set_headers("attacktree")  # Set column headers for scope

        self.table = self.table_wrapper.table
        self.table_layout = self.table_wrapper.table_layout

        self.index = None
        self.table.clicked.connect(self.get_index)

        # Table goes inside the action panel
        self.action_panel_layout.addWidget(self.table_wrapper.table)
        self.home_panel_layout.addWidget(self.action_panel)
        
          # Enable/disable buttons
        self.submit_button.setEnabled(False)
        
        # Connect buttons to functions
        self.submit_button.clicked.connect(self.Submit_Changes)

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

        self.active_threat_at_class = None
        self.tab_threat_instances = {}
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
        
        interfaces.previous_tree = None
        self.tab_container.setCurrentIndex(0)
        self.loader = RoundLoader(self, label_text="Loading...")
        self.loader.show()
        QApplication.processEvents()

        self.table.setRowCount(0)
        loaded_trees = load_all_AT()
        self.table_data_changed = False
        interfaces.unsaved_changes = False

        # ✅ 1. Load dropdown options
        self.toe_configuration_option_list = [
            f"{toe.toe_configuration_id}::{toe.toe_configuration_name}"
            for toe in get_instances(TOEConfiguration)
        ]
        self.tree_names_before = {}

        for tree in loaded_trees:
            row_index = self.table.rowCount()
            self.table_wrapper.insert_row([
                tree.id,
                tree.name,
                '',
                '',
                '',
                tree.comments if tree.comments else ''
            ])
            if tree.initial_afr:
                init_afr_item = QLineEdit(tree.initial_afr)
                init_afr_item.setReadOnly(True)
                helper.Apply_AFR_Level_Color(init_afr_item, tree.initial_afr)
                self.table.setCellWidget(row_index, 3, init_afr_item)
            if tree.resid_afr:
                resid_afr_item = QLineEdit(tree.resid_afr)
                resid_afr_item.setReadOnly(True)
                helper.Apply_AFR_Level_Color(resid_afr_item, tree.resid_afr)
                self.table.setCellWidget(row_index, 4, resid_afr_item)
            self.row_uuid_map[row_index] = tree.id
            self.add_multiselect_to_table_cell(row_index, 5, self.toe_configuration_option_list, tree.toe_configuration_id)
            self.tree_names_before[tree.id] = tree.comments

        # Sync open tabs with tree_ids
        available_ids = set(self.tree_names_before.keys())
        for i in reversed(range(self.inner_tab_widget.count())):
            tab_text = self.inner_tab_widget.tabText(i)
            if tab_text not in available_ids:
                self.inner_tab_widget.removeTab(i)

        self.loader.close()
        self.data_loaded = True  # ✅ Mark as loaded
        self.table_data_changed = False
        interfaces.unsaved_changes = False

    def update_cache_data(self):
        row = self.table.currentRow()
        changed_tree_ids = []

        id_item = self.table.item(row, 1)
        name_item = self.table.item(row, 2)
        if not id_item or not name_item:
            return
        tree_id = id_item.text()
        name = name_item.text()
        comments = self.table.item(row, 6).text() if self.table.item(row, 6) else ""

        if tree_id in AT_CACHE:
            record = AT_CACHE[tree_id]['record']
            old_comments = record.comments
            changed = update_tree(tree_id, {
                'name': name,
                'comments': comments
            })
            if changed and old_comments != comments:
                changed_tree_ids.append(tree_id)

        self.tree_names_after[tree_id] = comments

        logger.info(f"Tree names before: {self.tree_names_before}")
        logger.info(f"Tree names after: {self.tree_names_after}")

    # Highlight selected row in table
    def on_row_selection_changed(self):
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed2(self.table, self)
        interfaces.unsaved_changes = temp

    def get_index(self, index):
        self.index = index
        print("index: ", index)

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
                    self.Submit_Changes()
            else:
                self.Submit_Changes()

        # Extract item_id and item_name from the clicked row
        print(f"self.index : {self.index}")
        # row = self.index.row()
        item_id = self.table.item(row, 1).text()
        item_name = self.table.item(row, 2).text()
        logger.info(f'Attack Tree Editor Opened for {item_id} {item_name}')

        self.setEnabled(False)
        
        # Check if the tab is already available
        tab_index = self.is_tab_available(item_id)
        if tab_index != -1:
            # Tab exists, switch to it
            self.inner_tab_widget.setCurrentIndex(tab_index)
            self.active_threat_at_class = self.tab_threat_instances[f'{self.inner_tab_widget.tabText(tab_index)}']
            print(f"test load")
            self.active_threat_at_class.Load_AttackTree()
        else:
            # If the tab doesn't exist, create the new tab content
            tab_header = CTA.TabHeader(title=item_id, close_callback=lambda: self.Close_Tab(self.inner_tab_widget.indexOf(tab_header)))

            # Create the new Attack Tree instance
            threat_at_class = ATTA.ThreatATClass(self)
            if item_id not in self.tab_threat_instances.keys():
                self.tab_threat_instances[item_id] = threat_at_class
            print(f"test {item_id} : {item_name}")
            threat_at_class.Create_AttackTree_Tab(item_id, item_name)
            self.active_threat_at_class = self.tab_threat_instances[item_id]
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

    # save Attack Tree table data into the database
    def Submit_Changes(self):
        """Handle the submit action using ORM, ensuring pending edits are saved."""
        self.table.setFocus()
        logger.info('Attack Tree Table Data Submission started')
        self.update_button_states() 
        persist_tree_changes()
        logger.info('✅ Attack Tree Table Data Submitted successfully')
        self.table_data_changed = False
        interfaces.unsaved_changes = False

    def update_toolbar_tree_label(self, index):  
        logger.info('Attack Tree Toolbar Label Update started') 
        tab_id = self.inner_tab_widget.tabText(index)
        # **Prevent unnecessary updates when selecting the same tab**
        if self.inner_tab_widget.currentIndex() == index and self.active_threat_at_class == self.tab_threat_instances.get(tab_id):
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

        rows = get_first_instance(AttackTreeHome, {'id':f'{self.inner_tab_widget.tabText(index)}'})
        if rows:
            self.tree_toolbar_label.setText(rows.id) 
            self.active_threat_at_class = self.tab_threat_instances[f'{self.inner_tab_widget.tabText(index)}']
            interfaces.previous_tree = self.active_threat_at_class
            if interfaces.tool_reset_enable != True:
                self.active_threat_at_class.Load_AttackTree()  # Call loadtree() on the active class
            interfaces.tree_tab_panel['AttackTree'] = (self.inner_tab_widget, self.tab_threat_instances)

    # Common Save Button Handler
    def on_save_button_click(self):
        logger.info("Attack Tree Save Button Clicked")

        # Show the loader before starting the save process
        self.round_loader = RoundLoader(self, label_text= 'Saving...')
        self.round_loader.show()
        QApplication.processEvents()  # Ensures UI updates after showing loader

        try:
            if self.active_threat_at_class:
                self.active_threat_at_class.Save_Tree()  # Call save function

                # Hide the loader **before** any success message appears
                self.round_loader.accept()

                # REMOVE DUPLICATE SUCCESS MESSAGE BOX
                logger.info("Attack Tree saved successfully!")  # Just log the success message

        except Exception as e:
            # Hide loader if an error occurs
            self.round_loader.accept()
            QMessageBox.critical(None, "Error", f"Error saving Attack Tree: {str(e)}")

    # Close selected Tab
    def Close_Tab(self, index):  
        logger.info(f'Attack Tree {self.inner_tab_widget.tabText(index)} Tab Closed')      
        # Remove the threat instance from the dictionary if found
        if self.inner_tab_widget.tabText(index):
            self.tab_threat_instances.pop(f'{self.inner_tab_widget.tabText(index)}', None)
            interfaces.tree_tab_panel['AttackTree'] = (self.inner_tab_widget, self.tab_threat_instances)
        
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


    def add_multiselect_to_table_cell(self, row_index, column_index, option_list, current_value):
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
            tree_id = self.row_uuid_map.get(row_index)
            if tree_id:
                update_tree(tree_id, {'toe_configuration_id': value})  # ✅ Function change
                interfaces.unsaved_changes = True

        combo.model().dataChanged.connect(on_selection_change)
        self.table.setCellWidget(row_index, column_index, combo)
