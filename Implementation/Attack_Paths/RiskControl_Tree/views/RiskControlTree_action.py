
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy,
                             QMessageBox, QTabWidget, QTableWidget, QToolBar, QToolButton, 
                             QTableWidgetItem
                            )   
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
import models.Parameters as P
import models.helper as helper
from PyQt5.QtWidgets import QApplication

import sqlite3 
import Attack_Paths.RiskControl_Tree.views.RiskControlTree_Control_action as RCTCA
from Attack_Paths.RiskControl_Tree.views.riskcontrol_table_toolbar_panel import create_toolbar
from Attack_Paths.RiskControl_Tree.views.riskcontrol_tree_toolbar_panel import create_tree_toolbar
from Attack_Paths.views.attackpaths_table_panel import create_table_panel
from Attack_Paths.RiskControl_Tree.views.riskcontroltree_column_setup import Setup_Tabel_ColumnHeading
from controllers.schema_manager import get_instances,get_first_instance,create_instance
from controllers.tablemodel import RiskControlTreeHome, Assumptions
import models.TableStyle as TS
import models.ToolbarStyle as TBS
import controllers.DatabaseCreator as DB
import components.table.tree_row_indicator as TRI2
import components.table.multioption_selector as MOS
import controllers.TableValueHighlight as TVH
import controllers.CreateTabAction as CTA

import components.action_panel as action_panel
import styles.tree_panel_style as tree_panel_style
import styles.action_panel_style as action_panel_style
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
from components.table.table_panel import TablePanelWrapper
from Attack_Paths.RiskControl_Tree.controllers.risk_control_tree_manager import load_all_RCT, RCT_CACHE, persist_tree_changes, update_tree
from components.table.multiselect_combo import MultiSelectComboSelector
import logging

logger = logging.getLogger(__name__)
class RiskControl_Tree(QWidget):
    def __init__(self):
        super().__init__()
        logger.info("Risk Control Tree View Initialized")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.layout.setSpacing(0)  # Remove spacing between widgets
        self.data_loaded = False
        self.table_wrapper = None  # ✅ Ensure defined before use
        self.row_uuid_map = {}  # ✅ maps row index → UUID
        self.tree_datas_after = {}
        self.Init_UI()
    
    def Init_UI(self):
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
        self.table_wrapper.set_headers("riskcontroltree")  # Set column headers for scope

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
        self.update_button_states()

        # Create the child panel which will hold the inner QTabWidget
        self.child_panel = QWidget()
        self.child_panel_layout = QVBoxLayout()
        self.child_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.child_panel_layout.setSpacing(0)
        self.child_panel.setLayout(self.child_panel_layout)

        self.active_control_ct_class = None
        self.tab_control_instances = {}
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

    # Load Risk Control Tree table data from the database
    def load_data(self):
        logger.info("Risk Control Tree Table Data Loading Started")
        if self.data_loaded:
            self.table_data_changed = False
            self.tab_container.setCurrentIndex(0)
            return  # 🚫 Prevent reloading if already loaded
        
        interfaces.previous_tree = None
        self.tab_container.setCurrentIndex(0)
        self.loader = RoundLoader(self, label_text="Loading...")
        self.loader.show()
        QApplication.processEvents()

        self.table.setRowCount(0)
        loaded_trees = load_all_RCT()
        self.table_data_changed = False
        interfaces.unsaved_changes = False

        # ✅ 1. Load dropdown options
        self.assumptions_option_list = [
            f"{item.assumption_id}::{item.assumptions}"
            for item in get_instances(Assumptions)
        ]
        self.tree_datas_before = {}

        for tree in loaded_trees:
            row_index = self.table.rowCount()
            self.table_wrapper.insert_row([
                tree.id,
                tree.name,
                tree.mitigates if tree.mitigates else '',
                '',
                tree.comment if tree.comment else ''
            ])
            self.row_uuid_map[row_index] = tree.id
            self.add_multiselect_to_table_cell(row_index, 4, self.assumptions_option_list, tree.assumption_id)
            self.tree_datas_before[tree.id] = tree.comment

        # Sync open tabs with tree_ids
        available_ids = set(self.tree_datas_before.keys())
        for i in reversed(range(self.inner_tab_widget.count())):
            tab_text = self.inner_tab_widget.tabText(i)
            if tab_text not in available_ids:
                self.inner_tab_widget.removeTab(i)

        self.loader.close()
        self.data_loaded = True  # ✅ Mark as loaded

    def update_cache_data(self):
        row = self.table.currentRow()
        changed_tree_ids = []

        id_item = self.table.item(row, 1)
        name_item = self.table.item(row, 2)
        if not id_item or not name_item:
            return
        tree_id = id_item.text()
        name = name_item.text()
        mitigates = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        comments = self.table.item(row, 5).text() if self.table.item(row, 5) else ""

        if tree_id in RCT_CACHE:
            record = RCT_CACHE[tree_id]['record']
            old_comments = record.comment
            changed = update_tree(tree_id, {
                'name': name,
                'mitigates': mitigates,
                'comment': comments
            })
            if changed and old_comments != comments:
                changed_tree_ids.append(tree_id)

        self.tree_datas_after[tree_id] = comments

        logger.info(f"Tree comments before: {self.tree_datas_before}")
        logger.info(f"Tree comments after: {self.tree_datas_after}")

    # Highlight selected row in table
    def on_row_selection_changed(self):
        # temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed2(self.table, self)
        # interfaces.unsaved_changes = temp

    def get_index(self, index):
        self.index = index
        print("index: ", index)

    # Open Risk Control Tree in new tab
    def open_tree(self, index):
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

        # Extract item_id and item_name
        item_id = self.table.item(row, 1).text()
        item_name = self.table.item(row, 2).text()
        logger.info(f"Risk Control Tree Editor Opened for {item_id} {item_name}")

        # **DISABLE USER INTERACTIONS DURING LOADING**
        self.setEnabled(False)  # Disables all clicks, buttons, and interactions

        tab_index = self.is_tab_available(item_id)
        if tab_index != -1:
            # If tab exists, switch to it and load data
            self.inner_tab_widget.setCurrentIndex(tab_index)
            self.active_control_ct_class = self.tab_control_instances[f'{self.inner_tab_widget.tabText(tab_index)}']
            self.active_control_ct_class.Load_RiskControlTree()
        else:
            # Create a new tab if it doesn't exist
            tab_header = CTA.TabHeader(title=item_id, close_callback=lambda: self.Close_Tab(self.inner_tab_widget.indexOf(tab_header)))

            control_ct_class = RCTCA.ControlCTClass(self)
            if item_id not in self.tab_control_instances:
                self.tab_control_instances[item_id] = control_ct_class

            control_ct_class.Create_RiskControlTree_Tab(item_id, item_name)
            self.active_control_ct_class = self.tab_control_instances[item_id]
            self.tree_toolbar_label.setText(item_name)

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

    # save Risk Control Tree table data into the database
    def Submit_Changes(self):
        """
        Handle the submit action, ensuring pending edits are saved.
        """
        self.table.setFocus()  # Forces focus away from the current editor to trigger commit
        logger.info("Risk Control Tree Table Data Saving Started")
        self.update_button_states() 
        persist_tree_changes()
        self.tree_datas_before = self.tree_datas_after.copy()
        logger.info("Risk Control Tree Table Data Saved Successfully")
        self.table_data_changed = False
        interfaces.unsaved_changes = False
    
    def update_toolbar_tree_label(self, index):
        logger.info("Risk Control Tree Toolbar Label Update Started")
        # Get the selected tab ID
        tab_id = self.inner_tab_widget.tabText(index)
        # **Prevent unnecessary updates when selecting the same tab**
        if self.inner_tab_widget.currentIndex() == index and self.active_control_ct_class == self.tab_control_instances.get(tab_id):
            logger.info("Same tab selected, skipping update.")
            return  # ✅ Exit early to prevent unnecessary autosave prompt

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
        
        rows = get_first_instance(RiskControlTreeHome, {'id':f'{self.inner_tab_widget.tabText(index)}'})
        if rows:
            self.tree_toolbar_label.setText(rows.id) 
            self.active_control_ct_class = self.tab_control_instances[f'{self.inner_tab_widget.tabText(index)}']

            # **Update previous tree reference** 
            interfaces.previous_tree = self.active_control_ct_class

            if not interfaces.tool_reset_enable:
                self.active_control_ct_class.Load_RiskControlTree()

            interfaces.tree_tab_panel['RiskControlTree'] = (self.inner_tab_widget, self.tab_control_instances)

    # Common Save Button Handler
    def on_save_button_click(self):
        logger.info("Risk Control Tree Save Button Clicked")

        # Show the existing loader before starting the save process
        self.round_loader = RoundLoader(self, label_text='Saving...')
        self.round_loader.show()
        QApplication.processEvents()  # Ensures UI updates after showing loader

        try:
            if self.active_control_ct_class:
                self.active_control_ct_class.Save_Tree()  # Call save function

                # Hide loader **before** any message appears
                self.round_loader.accept()

                # REMOVE DUPLICATE MESSAGE BOX
                logger.info("Risk Control Tree saved successfully!")  # Just log the success message

        except Exception as e:
            # Hide loader if an error occurs
            self.round_loader.accept()
            QMessageBox.critical(None, "Error", f"Error saving Risk Control Tree: {str(e)}")

    # Close selected Tab
    def Close_Tab(self, index):  
        logger.info(f"Risk Control Tree {self.inner_tab_widget.tabText(index)} Tab Closed")      
        # Remove the threat instance from the dictionary if found
        if self.inner_tab_widget.tabText(index):
            self.tab_control_instances.pop(f'{self.inner_tab_widget.tabText(index)}', None)
            interfaces.tree_tab_panel['RiskControlTree'] = (self.inner_tab_widget, self.tab_control_instances)
        
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
    
    def on_row_selection_changed(self):
        TVH.on_row_selection_changed2(self.table, self)

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
                update_tree(tree_id, {'assumption_id': value})  # ✅ Function change
                interfaces.unsaved_changes = True

        combo.model().dataChanged.connect(on_selection_change)
        self.table.setCellWidget(row_index, column_index, combo)
