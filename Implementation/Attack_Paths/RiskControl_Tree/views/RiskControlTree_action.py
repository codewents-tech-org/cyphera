
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
import utils.interface_utils as interfaces
import logging

logger = logging.getLogger(__name__)
class RiskControl_Tree(QWidget):
    def __init__(self):
        super().__init__()
        logger.info("Risk Control Tree View Initialized")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.layout.setSpacing(0)  # Remove spacing between widgets
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
        create_table_panel(self)
        self.index = None
        self.table.clicked.connect(self.get_index)
        self.action_panel_layout.addLayout(self.table_layout)
        self.home_panel_layout.addWidget(self.action_panel)
        Setup_Tabel_ColumnHeading(self)

          # Enable/disable buttons
        self.submit_button.setEnabled(False)
        
        # Connect buttons to functions
        self.submit_button.clicked.connect(self.Submit_Changes)

        # Connect table signals to state updater
        self.table_data_changed = False
        self.table.itemChanged.connect(self.table_data_changed_set_flag)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
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

    # Load Risk Control Tree table data from the database
    def load_data(self):
        logger.info("Risk Control Tree Table Data Loading Started")
        self.tab_container.setCurrentIndex(0)
        # Show the round loader before loading data
        self.loader = RoundLoader(self, label_text="Loading Risk Control Data...")
        self.loader.show()
        QApplication.processEvents() 
        self.tab_container.setCurrentIndex(0)
        try:
            self.table.setRowCount(0)
            # rows = DB.execute_db("SELECT id, name, mitigates, assumptions, comment FROM riskcontrol_tree_home")
            # if not rows:    return
            # assumptions_rows = DB.execute_db("SELECT assumption_id, assumptions FROM assumptions")
            # formatted_assumptions = [f"{assumption_id}::{assumption}" for assumption_id, assumption in assumptions_rows]
            rows = [('Ctrl-1', 'control 1', '', '', 'This is a comment'),]
            for row_idx, (control_id, name, mitigates, assumptions, comment) in enumerate(rows):
                self.table.insertRow(row_idx)
                self.table.setRowHeight(row_idx, 40)
                sidebar = TRI2.SidebarWidget(parent = self, index=row_idx, tree_indicator=True)
                sidebar.tree_button.clicked.connect(self.open_tree)
                self.table.setCellWidget(row_idx, 0, sidebar)
                id_item = QTableWidgetItem(control_id)
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 1, id_item)
                name_item = QTableWidgetItem(name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 2, name_item)
                mitigates_item = QTableWidgetItem(mitigates)
                mitigates_item.setFlags(mitigates_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 3, mitigates_item)
                formatted_assumptions = []
                assumptions_combo = MOS.TSMultiSelectComboBox(formatted_assumptions)
                selected_assumptions = assumptions.strip().split(", ")
                # new_selected_assumptions = []
                # for data in selected_assumptions:
                #     for option in formatted_assumptions:
                #         if f"{data}::" in option and data != '':
                #             new_selected_assumptions.append(option)  
                # assumptions_combo.set_text(new_selected_assumptions)
                # assumptions_combo.currentTextChanged.connect(self.set_unsaved_changes)

                self.table.setCellWidget(row_idx, 4, assumptions_combo)
                comments_item = QTableWidgetItem(comment)
                mitigates_item.setFlags(mitigates_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 5, comments_item)

            if self.table.rowCount() > 0: self.table.setCurrentCell(0, 1)
            self.table_data_changed = False
            interfaces.unsaved_changes = False   
            logger.info("Risk Control Tree Table Data Loaded successfully")

            # rows = DB.execute_db("SELECT id FROM riskcontrol_tree_home")
            # if rows:
            #     available_ids = [row[0] for row in rows]
            #     for i in reversed(range(self.inner_tab_widget.count())):
            #         if self.inner_tab_widget.tabText(i) not in available_ids:
            #             self.inner_tab_widget.removeTab(i)
            # else:
            #     for i in reversed(range(self.inner_tab_widget.count())):
            #         self.inner_tab_widget.removeTab(i)
            
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
        finally:
            self.loader.close()    

    # Highlight selected row in table
    def on_row_selection_changed(self):
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed2(self.table)
        interfaces.unsaved_changes = temp

    def get_index(self, index):
        self.index = index
        print("index: ", index)

    # Open Risk Control Tree in new tab
    def open_tree(self):
        sender = self.sender()
        if sender:
            sidebar_widget = sender.parent()
            for row in range(self.table.rowCount()):
                if self.table.cellWidget(row, 0) == sidebar_widget:
                    self.table.selectRow(row)
                    self.index = self.table.model().index(row, 0)
                    TVH.on_row_selection_changed2(self.table)
                    break

        if self.index is None or not self.index.isValid():
            QMessageBox.warning(None, "Selection Error", "Unable to determine the selected row.")
            if self.round_loader:
                self.round_loader.accept()  # Close loader in case of error
                self.round_loader = None
            self.setEnabled(True)  # Re-enable interactions
            return
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
        row = self.index.row()
        item_id = self.table.itemFromIndex(self.index.siblingAtColumn(1)).text()
        item_name = self.table.itemFromIndex(self.index.siblingAtColumn(2)).text()
        logger.info(f"Risk Control Tree Editor Opened for {item_id} {item_name}")

        # **DISABLE USER INTERACTIONS DURING LOADING**
        self.setEnabled(False)  # Disables all clicks, buttons, and interactions

        # Ensure no existing loader before creating a new one
        if not hasattr(self, "round_loader") or self.round_loader is None:
            self.round_loader = RoundLoader(self, label_text='Loading...')
            self.round_loader.show()
            QApplication.processEvents()  # Ensure UI updates after showing loader

        try:
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

        except Exception as e:
            logger.error(f"Error opening Risk Control Tree: {e}")
            QMessageBox.critical(None, "Error", f"An error occurred: {e}")

        finally:
            # **ENABLE USER INTERACTIONS AFTER LOADING COMPLETES**
            self.setEnabled(True)  # Re-enables clicks and interactions

            # Close round loader after loading completes
            if self.round_loader:
                self.round_loader.accept()
                self.round_loader = None  # Ensure loader reference is reset



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
        # Process the table data
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()

        data = []
        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data) 
        logger.info("Risk Control Tree Table Data Saving Started")
        self.update_button_states() 
        DB.execute_db("DELETE FROM riskcontrol_tree_home")
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(1, self.table.columnCount()):
                if col == 4:  # Assumptions column (multi-select combo box)
                    combo_box = self.table.cellWidget(row, col)
                    if combo_box is not None:
                        selected_items = combo_box.selected_items()
                        assumption_ids = [item.split("::")[0] for item in selected_items]
                        row_data.append(", ".join(assumption_ids))
                    else:
                        row_data.append("")
                else:
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item is not None else "")
            DB.update_db("INSERT INTO riskcontrol_tree_home VALUES (?, ?, ?, ?, ?)", tuple(row_data))
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
        
        # **Skip creating a new loader if open_tree() is running**
        if not hasattr(self, "round_loader") or self.round_loader is None:
            self.round_loader = RoundLoader(self, label_text='Loading Tab...')
            self.round_loader.show()
            QApplication.processEvents()  # Ensure UI updates

        try:
            # rows = DB.execute_db_query("SELECT name FROM riskcontrol_tree_home WHERE id = ?", (tab_id,))
            if True:
                self.tree_toolbar_label.setText('Ctrl-1')
                self.active_control_ct_class = self.tab_control_instances[tab_id]

                # **Update previous tree reference** 
                interfaces.previous_tree = self.active_control_ct_class

                if not interfaces.tool_reset_enable:
                    self.active_control_ct_class.Load_RiskControlTree()

                interfaces.tree_tab_panel['RiskControlTree'] = (self.inner_tab_widget, self.tab_control_instances)

        except Exception as e:
            logger.error(f"Error loading Risk Control Tree tab: {e}")

        finally:
            # **Close the loader only if it's not already handled**
            if self.round_loader:
                self.round_loader.accept()
                self.round_loader = None  # Ensure loader reference is reset



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

    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True        

    def is_tab_available(self, item_id):
        for index in range(self.inner_tab_widget.count()):
            if self.inner_tab_widget.tabText(index) == f"{item_id}":
                return index
        return -1  # Tab not found
