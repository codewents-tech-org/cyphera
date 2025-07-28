
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QLineEdit, QApplication  
import models.helper as helper
import sqlite3

import controllers.DatabaseCreator as DB
import controllers.TableValueHighlight as TVH
import controllers.TableValueHighlight as TVH
import components.action_panel as action_panel

from Attack_Paths.Attack_Leaves.views.attackleaves_toolbar_panel import create_toolbar
from Attack_Paths.Attack_Leaves.views.attackleaves_table_panel import create_table_panel
from Attack_Paths.Attack_Leaves.views.attackleaves_column_setup import Setup_Tabel_ColumnHeading

from Attack_Paths.Attack_Leaves.controllers.attackleaves_TableValueLoad import AttackLeaves_Load_data
from Attack_Paths.Attack_Leaves.controllers.attackleaves_TableSaveRecord import AttackLeaves_Submit_Changes
from Attack_Paths.Attack_Leaves.controllers.attackleaves_TableAddRecord import attack_leaves_new_entry
from Attack_Paths.Attack_Leaves.controllers.attackleaves_TableRemoveRecord import attack_leaves_delete_entry
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
from models.unique_name_action import refrash_existing_entries, find_duplicates, store_selected_entry


class Attack_Leaves(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create the main layout for the entire widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # self.Setup_ToolbarPanel()
        create_toolbar(self)
        self.main_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)
        create_table_panel(self)
        self.action_panel_layout.addLayout(self.table_layout)
        self.main_layout.addWidget(self.action_panel)
        
          # Enable/disable buttons
        self.add_button.setEnabled(True)
        self.delete_button.setEnabled(False)
        self.submit_button.setEnabled(False)

        self.add_button.clicked.connect(self.Add_Record)
        self.submit_button.clicked.connect(self.Submit_Changes)
        self.delete_button.clicked.connect(self.Delete_Record)
        Setup_Tabel_ColumnHeading(self)

        # Connect table signals to state updater
        self.existing_entries = set()
        self.table.itemChanged.connect(self.update_button_states)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.itemDoubleClicked.connect(self.store_selected_entry)
        self.table.itemChanged.connect(self.find_duplicates)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()
        self.previous_text = None

    # Load Attack Leaves data from the database
    def load_data(self):
        # Show the round loader before loading attack leaves data
        self.loader = RoundLoader(self, label_text="Loading Attack Leaves Data...")
        self.loader.show()
        QApplication.processEvents()  # Ensure UI updates before loading starts

        self.table.itemChanged.disconnect(self.find_duplicates)
        # Load Attack Leaves Data
        AttackLeaves_Load_data(self)

        self.table.itemChanged.connect(self.find_duplicates)
        # Update button states after loading
        self.update_button_states()
        interfaces.unsaved_changes = False 
        # Hide the loader after loading completes
        self.loader.close()


    # Highlight selected row in table
    def on_row_selection_changed(self): 
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed(self.table)
        interfaces.unsaved_changes = temp

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
        
    def set_unsaved_changes(self):
        interfaces.unsaved_changes = True
        
    # save Attack Leaves data into the database
    def Submit_Changes(self):
        self.table.setFocus()
        AttackLeaves_Submit_Changes(self)
        interfaces.unsaved_changes = False
        self.update_button_states()

    def find_duplicates(self, changed_item):
        row = self.table.currentRow()
        column = self.table.currentColumn()
        if row >=0 and column>=0:
            if column!= 2: return
        find_duplicates(self, changed_item)
    def store_selected_entry(self, item): store_selected_entry(self, item)
    def refrash_existing_entries(self): refrash_existing_entries(self)
    
    def Add_Record(self): 
        self.table.setFocus()
        self.table.itemChanged.disconnect(self.find_duplicates)
        attack_leaves_new_entry(self)
        self.update_button_states()
        interfaces.unsaved_changes = True
        self.table.itemChanged.connect(self.find_duplicates)

    def Delete_Record(self): 
        attack_leaves_delete_entry(self)
        self.update_button_states()
        self.refrash_existing_entries()

    # calculate and update AFR_Level in table
    def Update_AFR_Level(self, item):
        selected_row = self.table.currentRow()
        value_list = []
        for i in range(3, 8):
            combo_box = self.table.cellWidget(selected_row, i)
            if combo_box is not None: value_list.append(int(combo_box.currentText().strip().split(' ')[0] if combo_box.currentText() != '' else '0'))
        afr_value = sum(value_list)
        # Set the AFR value to the QLineEdit in column 8 (convert to string)
        afr_widget = self.table.cellWidget(selected_row, 8)
        if isinstance(afr_widget, QLineEdit):
            afr_level = helper.Calculate_AFR_Level(afr_value)
            afr_widget.setText(afr_level)
            helper.Apply_AFR_Level_Color(afr_widget, afr_level)
               
    

