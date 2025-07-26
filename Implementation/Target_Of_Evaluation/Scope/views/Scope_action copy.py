
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, 
                             QMessageBox, QTabWidget, QTableWidget, QToolBar, QToolButton, 
                             QTableWidgetItem, QLineEdit, QComboBox, QAbstractItemView, QApplication
                            )   
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

import models.Parameters as P
import models.helper as helper
import sqlite3
import models.TableStyle as TS
import models.ToolbarStyle as TBS
import controllers.DatabaseCreator as DB
import components.table.table_row_indicator as TRI
import controllers.TableValueHighlight as TVH
import controllers.CreateTabAction as CTA

import Target_Of_Evaluation.Scope.controllers.scope_TableValueLoad as TVL
import Target_Of_Evaluation.Scope.controllers.scope_TableAddRecord as TAR
import Target_Of_Evaluation.Scope.controllers.scope_TableRemoveRecord as TRR
import Target_Of_Evaluation.Scope.controllers.scope_TableSaveRecord as TSR
import Target_Of_Evaluation.Scope.views.Scope_MindMap_action as SM

from Target_Of_Evaluation.Scope.views.scope_toolbar_panel import create_toolbar
from Target_Of_Evaluation.Scope.views.scope_table_panel import create_table_panel
from Target_Of_Evaluation.Scope.views.scope_column_setup import Setup_Tabel_ColumnHeading
from Target_Of_Evaluation.Scope.views.scope_mindmap_toolbar_panel import create_tree_toolbar

import components.action_panel as action_panel
import styles.tree_panel_style as tree_panel_style
import styles.action_panel_style as action_panel_style
import Target_Of_Evaluation.Scope.controllers.scope_synchronizations as SCSS
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
import logging
from Scope.controllers.scope_manager import load_all_scopes, SCOPE_CACHE,create_scope_and_insert_row,persist_scope_changes,delete_scope,mark_scope_updated



logger = logging.getLogger(__name__)


class ScopeModule(QWidget):
    def __init__(self):
        super().__init__()
        logger.info("Scope table View Initiated")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.layout.setSpacing(0)  # Remove spacing between widgets
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
        create_table_panel(self)
        self.index = None
        self.table.clicked.connect(self.get_index)
        self.action_panel_layout.addLayout(self.table_layout)
        self.home_panel_layout.addWidget(self.action_panel)
        Setup_Tabel_ColumnHeading(self)

          # Enable/disable buttons
        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)

        self.add_button.clicked.connect(self.Add_Record)
        self.submit_button.clicked.connect(self.submit_changes)
        self.delete_button.clicked.connect(self.Remove_Record) 

        # Connect table signals to state updater
        self.table_data_changed = False
        self.table.itemChanged.connect(self.table_data_changed_set_flag)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.update_button_states()

        # Create the child panel which will hold the inner QTabWidget
        self.child_panel = QWidget()
        self.child_panel_layout = QVBoxLayout()
        self.child_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.child_panel_layout.setSpacing(0)
        self.child_panel.setLayout(self.child_panel_layout)
        
        self.active_mindmap_class = None
        self.tab_mindmap_instances = {}
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
        self.inner_tab_widget.currentChanged.connect(self.update_toolbar_tree_label)
        self.inner_tab_widget.tabCloseRequested.connect(self.Close_Tab)
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

    def load_data(self):
        interfaces.previous_tree = None
        self.tab_container.setCurrentIndex(0)
        self.loader = RoundLoader(self, label_text="Loading...")
        self.loader.show()
        QApplication.processEvents()

        self.table.setRowCount(0)  # Clear table
        loaded_scopes = load_all_scopes()
        self.table_data_changed = False
        interfaces.unsaved_changes = False

        self.scope_names_before = {}

        for scope_entry in loaded_scopes:
            scope = scope_entry['record']
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(scope.uuid))
            self.table.setItem(row, 1, QTableWidgetItem(scope.scope_id))
            self.table.setItem(row, 2, QTableWidgetItem(scope.scope_name))
            self.table.setItem(row, 3, QTableWidgetItem(scope.comments or ""))
            self.scope_names_before[scope.scope_id] = scope.scope_name

        # Sync open tabs with scope_ids
        available_ids = set(self.scope_names_before.keys())
        for i in reversed(range(self.inner_tab_widget.count())):
            tab_text = self.inner_tab_widget.tabText(i)
            if tab_text not in available_ids:
                self.inner_tab_widget.removeTab(i)

        self.loader.close()  

    # Highlight selected row in table
    def on_row_selection_changed(self): TVH.on_row_selection_changed2(self.table)

    def Add_Record(self):
        self.table.setFocus()
        row_before = self.table.rowCount()

        create_scope_and_insert_row(self.table)  # Adds to table + cache + DB

        self.submit_changes()
        self.update_button_states()
        interfaces.unsaved_changes = False

        # Find and open tree for latest added row
        row_after = self.table.rowCount()
        if row_after <= row_before:
            logger.error("No new row added.")
            return

        new_scope_id = self.table.item(row_after - 1, 1).text()
        for row in range(self.table.rowCount()):
            if self.table.item(row, 1).text() == new_scope_id:
                self.index = self.table.model().index(row, 0)
                break

        if self.index and self.index.isValid():
            logger.info(f"Opening tree for new Scope ID: {new_scope_id}")
            self.open_tree()


    def submit_changes(self):
        self.table.setFocus()

        scope_names_after = {}
        for row in range(self.table.rowCount()):
            scope_id = self.table.item(row, 1).text()
            scope_name = self.table.item(row, 2).text()
            uuid = self.table.item(row, 0).text()

            if uuid in SCOPE_CACHE:
                record = SCOPE_CACHE[uuid]['record']
                if record.scope_name != scope_name:

                    mark_scope_updated(uuid, {'scope_name': scope_name})

            scope_names_after[scope_id] = scope_name

        logger.info(f"Scope names before submission: {self.scope_names_before}")
        logger.info(f"Scope names after submission: {scope_names_after}")

        persist_scope_changes()  # 🔁 Actual DB update

        for scope_id, old_name in self.scope_names_before.items():
            new_name = scope_names_after.get(scope_id, old_name)
            if old_name != new_name:
                for i in range(self.inner_tab_widget.count()):
                    if self.inner_tab_widget.tabText(i) == str(scope_id):
                        self.Close_Tab(i)
                        break

        self.load_data()
        self.update_button_states()
        self.scope_names_before = scope_names_after.copy()
        interfaces.unsaved_changes = False
        logger.info("Scope data successfully submitted and updated.")

    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True
    
    # remove Scope Tree table data into the database
    def Remove_Record(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        for index in selected_rows:
            uuid = self.table.item(index.row(), 0).text()
            delete_scope(uuid)


        persist_scope_changes()

        SCSS.clean_scope_home_mindmap_node()
        self.load_data()
        self.update_button_states()
   
    def update_button_states(self):
        """
        Updates the state of the Save and Delete buttons based on the table's state.
        """
        row_count = self.table.rowCount()
        has_selection = bool(self.table.selectionModel().selectedRows())

        # Update "Delete" button state
        self.delete_button.setEnabled(row_count > 0 and has_selection)

        # Update "Submit" button state
        self.submit_button.setEnabled(row_count > 0)

    def get_index(self, index):
        self.index = index
        print("index: ", index)

    # Open Risk Control Tree in new tab
    def open_tree(self):
    # Determine the row where the button was clicked
        sender = self.sender()
        if sender:
            # Get the parent widget (SidebarWidget) and identify the row in the table
            sidebar_widget = sender.parent()
            for row in range(self.table.rowCount()):
                if self.table.cellWidget(row, 0) == sidebar_widget:  # Assuming SidebarWidget is in column 0
                    self.table.selectRow(row)  # Select the row programmatically
                    self.index = self.table.model().index(row, 0)  # Update self.index to the correct row
                    TVH.on_row_selection_changed2(self.table)
                    break

        if self.index is None or not self.index.isValid():
            QMessageBox.warning(None, "Selection Error", "Unable to determine the selected row.")
            return
        open_tree_enable = True
        # Handle unsaved changes before switching to the edit page
        if self.table_data_changed:
            if not interfaces.autosave_enabled:
                message_reply = QMessageBox.warning(None, "Warning", "Please save the changes before switching to the edit page.", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if message_reply == QMessageBox.Ok:
                    self.submit_changes()
            else:
                self.submit_changes()

        # Retrieve item_id and item_name from the selected row
        row = self.index.row()
        item_id = self.table.item(row, 1).text()
        item_name = self.table.item(row, 2).text()

        logger.info(f"Scope Mindmap Editor Opened for {item_id} {item_name}")

        # Check if the tab for the item already exists
        tab_index = self.is_tab_available(item_id)
        if tab_index != -1:
            # Tab exists, switch to it
            self.inner_tab_widget.setCurrentIndex(tab_index)
            self.active_mindmap_class = self.tab_mindmap_instances[f'{self.inner_tab_widget.tabText(tab_index)}']
            interfaces.previous_tree = self.active_mindmap_class
            
        else:
            # Create a new tab
            tab_header = CTA.TabHeader(title=item_id, close_callback=lambda: self.Close_Tab(self.inner_tab_widget.indexOf(tab_header)))
            MindMap_Class = SM.MindMapClass(self)
            if item_id not in self.tab_mindmap_instances.keys():
                self.tab_mindmap_instances[item_id] = MindMap_Class
            MindMap_Class.Create_MindMap_Tab(item_id, item_name)
            self.active_mindmap_class = self.tab_mindmap_instances[item_id]
            self.tree_toolbar_label.setText(item_name)
            interfaces.previous_tree = self.active_mindmap_class

        # Handle unsaved changes before switching to the edit page
        if open_tree_enable == True:
           self.tab_container.setCurrentIndex(1)

    def update_toolbar_tree_label(self, index):   
        logger.info(f"Switched to tab {self.inner_tab_widget.tabText(index)}")  

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

        rows = DB.execute_db_query("SELECT scope_name FROM scope_home_mindmap WHERE scope_id = ?", (f'{self.inner_tab_widget.tabText(index)}',))
        if rows:
            self.tree_toolbar_label.setText(rows[0][0]) 
            self.active_mindmap_class = self.tab_mindmap_instances[f'{self.inner_tab_widget.tabText(index)}']
            interfaces.previous_tree = self.active_mindmap_class
            interfaces.tree_tab_panel['Mindmap'] = (self.inner_tab_widget, self.tab_mindmap_instances)
            
    # Common Save Button Handler
    def on_save_button_click(self):
        logger.info("Scope Save Button Clicked")
        if self.active_mindmap_class:
            self.active_mindmap_class.Save_Tree()   # Call savetree() on the active class

    # Close selected Tab
    def Close_Tab(self, index):  
        logger.info(f"Scope {self.inner_tab_widget.tabText(index)} Tab Closed")   
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
        # Remove the threat instance from the dictionary if found
        if self.inner_tab_widget.tabText(index):
            self.tab_mindmap_instances.pop(self.inner_tab_widget.tabText(index), None)
            interfaces.tree_tab_panel['Mindmap'] = (self.inner_tab_widget, self.tab_mindmap_instances)
        
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
        interfaces.unsaved_changes = True
        self.update_button_states()
    
    def is_tab_available(self, item_id):
        for index in range(self.inner_tab_widget.count()):
            if self.inner_tab_widget.tabText(index) == f"{item_id}":
                return index
        return -1  # Tab not found

