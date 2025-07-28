
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
from Attack_Paths.views.attackpaths_table_panel import create_table_panel
from Attack_Paths.Attack_Tree.views.attacktree_column_setup import Setup_Tabel_ColumnHeading
import models.TableStyle as TS
import models.ToolbarStyle as TBS
import controllers.DatabaseCreator as DB
import components.table.tree_row_indicator as TRI2
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
import utils.interface_utils as interfaces
from controllers.schema_manager import get_instances, delete_all_instance, create_instance
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, AttackLeafNodes, RiskControlTreeHome, TechnicalTreeHome, AttackTreeHome
from controllers.database_tables.target_of_evaluation_tables import TOEConfiguration
import logging
from PyQt5.QtWidgets import QLineEdit
logger = logging.getLogger(__name__)


class Attack_Tree(QWidget):
    def __init__(self):
        super().__init__()
        logger.info(f'Attack Tree View Initialized')
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

    def update_toolbar_tree_label(self, index):
        """
        Update the toolbar label for the risk control tree tab, handling autosave, loader display, and instance switching.
        """
        from controllers.schema_manager import get_instance
        from models.risk_control import RiskControlTreeHome  # Adjust the import to match your project

        logger.info("Risk Control Tree Toolbar Label Update Started")

        # Get the selected tab ID
        tab_id = self.inner_tab_widget.tabText(index)

        # Prevent unnecessary updates when selecting the same tab
        if (
            self.inner_tab_widget.currentIndex() == index and
            self.active_control_ct_class == self.tab_control_instances.get(tab_id)
        ):
            logger.info("Same tab selected, skipping update.")
            return

        # Autosave condition (mirrors Attack Tree behavior)
        interfaces.previous_module = None
        if interfaces.autosave_enabled and interfaces.previous_tree and interfaces.unsaved_changes:
            interfaces.previous_tree.Save_Tree()
        elif not interfaces.autosave_enabled and interfaces.previous_tree and interfaces.unsaved_changes:
            reply = QMessageBox.question(
                None, 'Unsaved Changes',
                "You have unsaved changes. Do you want to save them before switching?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                interfaces.previous_tree.Save_Tree()
            elif reply == QMessageBox.No:
                interfaces.unsaved_changes = False

        # Show loader if needed
        if not hasattr(self, "round_loader") or self.round_loader is None:
            self.round_loader = RoundLoader(self, label_text='Loading Tab...')
            self.round_loader.show()
            QApplication.processEvents()

        try:
            # Fetch the risk control tree object via ORM
            rc_tree_home = get_instance(RiskControlTreeHome, {"rc_id": tab_id})
            if rc_tree_home:
                self.tree_toolbar_label.setText(rc_tree_home.name)
                self.active_control_ct_class = self.tab_control_instances[tab_id]
                interfaces.previous_tree = self.active_control_ct_class

                if not interfaces.tool_reset_enable:
                    self.active_control_ct_class.Load_RiskControlTree()

                interfaces.tree_tab_panel['RiskControlTree'] = (self.inner_tab_widget, self.tab_control_instances)

        except Exception as e:
            logger.error(f"Error updating toolbar tree label: {e}")
            QMessageBox.critical(None, "Database Error", f"Error loading tree label: {e}")

        finally:
            # Always close the loader after loading completes
            if hasattr(self, "round_loader") and self.round_loader:
                self.round_loader.close()
                self.round_loader = None


    def load_data(self):
        try:
            interfaces.previous_tree = None
            self.tab_container.setCurrentIndex(0)
            self.loader = RoundLoader(self, label_text="Loading Attack Tree Data...")
            self.loader.show()
            QApplication.processEvents()
            logger.info('Attack Tree Table Data Loading started')
            self.table.setRowCount(0)

            # ORM Fetch
            rows = get_instances(AttackTreeHome)
            if not rows:
                return

            toe_config_rows = get_instances(ToeConfiguration)
            toe_config_ids = [str(tc.toe_configuration_id) for tc in toe_config_rows]
            toe_config_options = [f"{tc.toe_configuration_id}::{tc.toe_configuration_name}" for tc in toe_config_rows]

            for row_idx, row in enumerate(rows):
                self.table.insertRow(row_idx)
                self.table.setRowHeight(row_idx, 40)
                sidebar = TRI2.SidebarWidget(parent=self, index=row_idx)
                self.table.setCellWidget(row_idx, 0, sidebar)

                # id, name, InitialAFR, ResidAFR, toe_configuration, comments
                id_item = QTableWidgetItem(row.id)
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 1, id_item)

                name_item = QTableWidgetItem(row.name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 2, name_item)

                IAFR_item = QLineEdit(row.InitialAFR or "")
                IAFR_item.setReadOnly(True)
                helper.Apply_AFR_Level_Color(IAFR_item, row.InitialAFR or "")
                self.table.setCellWidget(row_idx, 3, IAFR_item)

                RAFR_item = QLineEdit(row.ResidAFR or "")
                RAFR_item.setReadOnly(True)
                helper.Apply_AFR_Level_Color(RAFR_item, row.ResidAFR or "")
                self.table.setCellWidget(row_idx, 4, RAFR_item)

                # toe_configuration (multi-select)
                combo_box = MOS.ReadOnlyMultiSelectComboBox(toe_config_options)
                selected_toe_configurations = (row.toe_configuration or "").split(", ")
                new_selected = []
                for data in selected_toe_configurations:
                    for x in toe_config_options:
                        if f"{data}::" in x and data != '':
                            new_selected.append(x)
                combo_box.set_text(new_selected)
                self.table.setCellWidget(row_idx, 5, combo_box)

                comment_item = QTableWidgetItem(row.comments or "")
                self.table.setItem(row_idx, 6, comment_item)

            if self.table.rowCount() > 0:
                self.table.setCurrentCell(0, 1)
            logger.info('Attack Tree Table Data Loaded successfully')
            self.table_data_changed = False
            interfaces.unsaved_changes = False

            rows = get_instances(AttackTreeHome)
            available_ids = [row.id for row in rows] if rows else []
            for i in reversed(range(self.inner_tab_widget.count())):
                if self.inner_tab_widget.tabText(i) not in available_ids:
                    self.inner_tab_widget.removeTab(i)
            if not rows:
                for i in reversed(range(self.inner_tab_widget.count())):
                    self.inner_tab_widget.removeTab(i)

        except Exception as e:
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

        # **DISABLE USER INTERACTIONS DURING LOADING**
        self.setEnabled(False)  # Disables all clicks, buttons, and interactions

        # Ensure no existing loader before creating a new one
        if not hasattr(self, "round_loader") or self.round_loader is None:
            self.round_loader = RoundLoader(self, label_text='Loading...')
            self.round_loader.show()
            QApplication.processEvents()  # Ensure UI updates while loader is shown

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

        # Extract item_id and item_name from the clicked row
        row = self.index.row()
        item_id = self.table.itemFromIndex(self.index.siblingAtColumn(1)).text()
        item_name = self.table.itemFromIndex(self.index.siblingAtColumn(2)).text()
        logger.info(f'Attack Tree Editor Opened for {item_id} {item_name}')

        self.setEnabled(False)
        
        # Check if the tab is already available
        tab_index = self.is_tab_available(item_id)
        if tab_index != -1:
            # Tab exists, switch to it
            self.inner_tab_widget.setCurrentIndex(tab_index)
            self.active_threat_at_class = self.tab_threat_instances[f'{self.inner_tab_widget.tabText(tab_index)}']
            self.active_threat_at_class.Load_AttackTree()
        else:
            # If the tab doesn't exist, create the new tab content
            tab_header = CTA.TabHeader(title=item_id, close_callback=lambda: self.Close_Tab(self.inner_tab_widget.indexOf(tab_header)))

            # Create the new Attack Tree instance
            threat_at_class = ATTA.ThreatATClass(self)
            if item_id not in self.tab_threat_instances.keys():
                self.tab_threat_instances[item_id] = threat_at_class
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



    def Submit_Changes(self):
        """
        Handle the submit action, ensuring pending edits are saved (ORM version).
        """
        self.table.setFocus()
        logger.info('Attack Tree Table Data Submission started')
        self.update_button_states()

        # 1. Clear the table via ORM
        delete_all_instance(AttackTreeHome, {})  # Delete all rows

        # 2. Loop through table and insert each row as ORM instance
        for row in range(self.table.rowCount()):
            # Build the ORM instance field values
            field_values = []
            for col in range(1, self.table.columnCount()):
                if col in [3, 4]:
                    line_edit = self.table.cellWidget(row, col)
                    if isinstance(line_edit, QLineEdit):
                        field_values.append(line_edit.text())
                    else:
                        field_values.append("")
                elif col == 5:
                    combo_box = self.table.cellWidget(row, col)
                    if combo_box is not None:
                        selected_items = combo_box.selected_items()  # e.g., ['ID1::Name1', 'ID2::Name2']
                        new_selected_items = [data.split('::')[0] for data in selected_items]
                        field_values.append(", ".join(new_selected_items))
                    else:
                        field_values.append("")
                else:
                    item = self.table.item(row, col)
                    field_values.append(item.text() if item else '')

            # Map the values to the correct ORM fields (adapt as needed)
            instance = AttackTreeHome(
                id=field_values[0],
                name=field_values[1],
                InitialAFR=field_values[2],
                ResidAFR=field_values[3],
                toe_configuration=field_values[4],
                comments=field_values[5],
                # If your model needs created_by etc., add defaults here
            )
            create_instance(instance)

        logger.info('Attack Tree Table Data Submitted successfully')
        self.table_data_changed = False
        interfaces.unsaved_changes = False


    def Submit_Changes(self):
        """
        Submit all table data for AttackTreeHome using ORM/schema_manager.
        """
        self.table.setFocus()
        logger.info('Attack Tree Table Data Submission started')
        self.update_button_states()

        # 1. Delete all previous records (ORM)
        delete_all_instance(AttackTreeHome, {})

        # 2. Insert current table rows as ORM objects
        for row in range(self.table.rowCount()):
            data = []
            for col in range(1, self.table.columnCount()):
                # Read-only QLineEdit columns
                if col in [3, 4]:
                    w = self.table.cellWidget(row, col)
                    data.append(w.text() if isinstance(w, QLineEdit) else "")
                # MultiSelectComboBox column (toe_configuration)
                elif col == 5:
                    cb = self.table.cellWidget(row, col)
                    if cb is not None:
                        selected = cb.selected_items()
                        items = [s.split("::")[0] for s in selected]
                        data.append(", ".join(items))
                    else:
                        data.append("")
                # Regular QTableWidgetItem columns
                else:
                    it = self.table.item(row, col)
                    data.append(it.text() if it else "")

            # Unpack data and build ORM instance
            # id, name, InitialAFR, ResidAFR, toe_configuration, comments
            instance = AttackTreeHome(
                id=data[0], name=data[1], InitialAFR=data[2], ResidAFR=data[3],
                toe_configuration=data[4], comments=data[5]
            )
            create_instance(instance)

        logger.info('Attack Tree Table Data Submitted successfully')
        self.table_data_changed = False
        interfaces.unsaved_changes = False

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

