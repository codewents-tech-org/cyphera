

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QHeaderView,
                             QTableWidgetItem, QApplication, QPushButton, QStyledItemDelegate,
                             QMessageBox, QToolBar, QMainWindow, QLineEdit, QLabel, QComboBox,
                             QToolTip, QGridLayout, QFileDialog, QFrame, QStackedWidget, QButtonGroup, 
                             QSpacerItem, QSizePolicy, QTextEdit, QAction, QMenu, QToolButton, QStyle
                             )
from PyQt5.QtGui import QIcon, QPainter, QCursor, QFont, QColor, QBrush
from PyQt5.QtCore import QTimer, Qt, QSize, QRect, QRectF
import sqlite3
import sys
import models.Parameters as P
import controllers.DatabaseCreator as DB
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.table_row_indicator as TRI
import Analysis.controllers.analysis_TableRefreshRecord as TRR

import logging
logger = logging.getLogger(__name__)
def load_assets(self, table, property_panel, toggle_button):
    logger.info(f"Loading data for Assets")
    try:
        table.setColumnCount(6)
        table.verticalHeader().setVisible(False)
        header_item = QTableWidgetItem('')  # Add icon with text
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28,28))
        table.setHorizontalHeaderItem(0, header_item)
        table.horizontalHeader().setFirstSectionMovable(False)
        for index, header in enumerate(helper.asset_header):
            header_item = QTableWidgetItem(header) 
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28,28))
            table.setHorizontalHeaderItem(index+1, header_item)
            table.horizontalHeader().setFixedHeight(50)

        
        helper.adjust_table_column('Asset', table)
        table.horizontalHeader().setSectionResizeMode(4,QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(5,QHeaderView.Stretch)
        table.horizontalHeader().setStretchLastSection(True)
        
        table.setRowCount(0)
        assets_rows = DB.execute_db("SELECT * FROM assets")
        
        existing_data = DB.execute_db("SELECT Asset FROM scope_home_mindmap_dumy")
        existing_scope_assets = [row[0] for row in existing_data]
        if not assets_rows:
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
        for row_idx, row_data in enumerate(assets_rows):
            table.insertRow(row_idx)
            table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row_data[1])
            for col_idx, col_data in enumerate(row_data):
                item = None
                if col_idx == 2:  # Security properties column with a multi-select combo box
                    widget = MOS.MultiSelectComboBox(helper.assert_securityproperty_menu)
                    widget.set_text(col_data)
                    table.setCellWidget(row_idx, col_idx + 1, widget)
                    widget.currentTextChanged.connect(self.set_unsaved_changes)
                else:
                    item = QTableWidgetItem(col_data)
                    if col_idx == 0:  # ID column
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make the ID column read-only
                        
                    elif col_idx == 1 and row_data[0] in existing_scope_assets:  # Name column and asset_id in scope_home_mindmap_dumy
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
                    table.setItem(row_idx, col_idx + 1, item)
            
            # Add a sidebar widget
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)
        
        # Set the first cell as current if there are rows
        if table.rowCount() > 0:
            table.setCurrentCell(0, 1)

    except sqlite3.Error as e:
        logger.error(f"Error loading data: {e}")
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

def load_damage_scenarios(self, table, property_panel, toggle_button):
    logger.info(f"Loading data for Damage Scenarios")
    try:
        table.setRowCount(0)
        table.setColumnCount(7)
        table.verticalHeader().setVisible(False)
        header_item = QTableWidgetItem('')  # Add icon with text
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28,28))
        table.setHorizontalHeaderItem(0, header_item)
        for index, header in enumerate(helper.DS_header):
            header_item = QTableWidgetItem(header) 
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28,28))
            table.setHorizontalHeaderItem(index+1, header_item)
            table.horizontalHeader().setFixedHeight(50)
        
        helper.adjust_table_column('Damage Scenarios', table)
        table.horizontalHeader().setSectionResizeMode(5,QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(6,QHeaderView.Stretch)
        table.horizontalHeader().setStretchLastSection(True)
        
        table.setRowCount(0)
        rows = DB.execute_db("SELECT * FROM damage_scenarios")
        if not rows:
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
        for row_idx, row_data in enumerate(rows):
            table.insertRow(row_idx)
            table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row_data[1])
            for col_idx, col_data in enumerate(row_data):
                if col_idx == 2:
                    widget = MOS.NoWheelComboBox()
                    widget.addItems(helper.DS_impact_menu)
                    if col_data != '':
                        widget.setCurrentText(col_data)
                    else:
                        widget.setCurrentIndex(-1)
                    widget.currentTextChanged.connect(self.set_unsaved_changes)    
                    table.setCellWidget(row_idx, col_idx+1, widget)
                elif col_idx == 3:
                    # widget = QComboBox()
                    # widget.addItems(helper.DS_impactcatagory_menu)
                    # widget.setCurrentText(col_data)
                    # table.setCellWidget(row_idx, col_idx+1, widget)
                    widget = MOS.MultiSelectComboBox(helper.DS_impactcatagory_menu)
                    widget.set_text(col_data)  # Assuming set_text handles displaying selected items
                    widget.currentTextChanged.connect(self.set_unsaved_changes)
                    table.setCellWidget(row_idx, col_idx + 1, widget)
                else:
                    item = QTableWidgetItem(col_data)
                    if col_idx == 0:  # ID column
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make the ID column read-only
                    table.setItem(row_idx, col_idx+1, item)
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)
        if table.rowCount() > 0: table.setCurrentCell(0, 1)
    except sqlite3.Error as e:
        logger.error(f"Error loading data: {e}")
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

# Function to handle key press event
def handle_key_press(event, combo_box):
    if event.key() == Qt.Key_Delete:  # Check if the Delete key is pressed
        # Clear the current selection in the combo box
        # combo_box.clear()  
        combo_box.setCurrentIndex(-1)  # Ensure that no item is selected
        # QMessageBox.information(None, "Item Deleted", "The selected item has been cleared.")  # Optional feedback
    else:
        QComboBox.keyPressEvent(combo_box, event)  # Call the original keyPressEvent for other keys

def load_threat(self,table, property_panel, toggle_button):
    logger.info(f"Loading data for Threat")
    try:
        table.setColumnCount(12)
        table.verticalHeader().setVisible(False)
        header_item = QTableWidgetItem('')  # Add icon with text
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28,28))
        table.setHorizontalHeaderItem(0, header_item)
        for index, header in enumerate(helper.threat_header):
            header_item = QTableWidgetItem(header) 
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28,28))
            table.setHorizontalHeaderItem(index+1, header_item)
            table.horizontalHeader().setFixedHeight(50)
        
        helper.adjust_table_column('Threats', table)
        table.horizontalHeader().setStretchLastSection(True)
        
        table.setRowCount(0)
        damage_scenario_map = {}
        rows = DB.execute_db(f"SELECT * FROM threat")
        row_counter = len(rows)
        damage_scenarios_options = []
        toe_configuration_options = []
        misuse_cases_options = []
        damage_scenarios = DB.execute_db("SELECT ds_id, name FROM damage_scenarios")
        for ds_id, ds_name in damage_scenarios:
            damage_scenarios_options.append(f"{ds_id}::{ds_name}")
        
        toe_configuration = DB.execute_db("SELECT toe_configuration_id, toe_configuration_name FROM toe_configuration")    
        for toec_id, toec_name in toe_configuration:
            toe_configuration_options.append(f"{toec_id}::{toec_name}")
            
        misuse_cases = DB.execute_db("SELECT misuse_cases_id, misuse_cases_name FROM misuse_cases")
        for misuse_cases_id, misuse_cases_name in misuse_cases:
            misuse_cases_options.append(f"{misuse_cases_id}::{misuse_cases_name}")    
        if not rows:
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
        for row_idx, row_data in enumerate(rows):
            table.insertRow(row_idx)
            table.setRowHeight(row_idx, 40)
            for col_idx, col_data in enumerate(row_data):
                if col_idx == 2:  
                    combo_box = MOS.TSMultiSelectComboBox(damage_scenarios_options)
                    selected_damage_scenarios = col_data.split(", ")
                    new_selected_damage_scenarios = []
                    for data in selected_damage_scenarios:
                        for x in damage_scenarios_options:
                            if f"{data}::" in x and data != '':
                                new_selected_damage_scenarios.append(x)  
                    combo_box.set_text(new_selected_damage_scenarios)
                    combo_box.currentTextChanged.connect(self.set_unsaved_changes)   
                    table.setCellWidget(row_idx, col_idx+1, combo_box)
                    
                elif col_idx == 3:  
                    combo_box = MOS.TSMultiSelectComboBox(toe_configuration_options)
                    selected_toe_configuration = col_data.split(", ")
                    new_selected_toe_configuration = []
                    for data in selected_toe_configuration:
                        for x in toe_configuration_options:
                            if f"{data}::" in x and data != '':
                                new_selected_toe_configuration.append(x)  
                    combo_box.set_text(new_selected_toe_configuration)
                    combo_box.currentTextChanged.connect(self.set_unsaved_changes)   
                    table.setCellWidget(row_idx, col_idx+1, combo_box)     
                    
                    
                elif col_idx == 4:  
                    combo_box = MOS.TSMultiSelectComboBox(misuse_cases_options)
                    selected_misuse_cases = col_data.split(", ")
                    new_selected_misuse_cases = []
                    for data in selected_misuse_cases:
                        for x in misuse_cases_options:
                            if f"{data}::" in x and data != '':
                                new_selected_misuse_cases.append(x)  
                    combo_box.set_text(new_selected_misuse_cases)
                    combo_box.currentTextChanged.connect(self.set_unsaved_changes)   
                    table.setCellWidget(row_idx, col_idx+1, combo_box)

                # Assuming col_idx is defined and corresponds to the source column
                elif col_idx == 5:
                    # Create a QLineEdit for data from column 3, but display it in column 4
                    line_edit = QLineEdit(col_data)  # Set initial text from col_data (from column 3)
                    line_edit.setReadOnly(True)       # Set to read-only
                    line_edit.setAlignment(Qt.AlignCenter)  # Center the text

                    # Customize the background color based on col_data
                    if col_data == 'High':
                        line_edit.setStyleSheet("background-color: #0097b2; font-size: 14px;")
                    elif col_data == 'Medium':
                        line_edit.setStyleSheet("background-color: #0cc0df; font-size: 14px;")
                    elif col_data == 'Low':
                        line_edit.setStyleSheet("background-color: #5ce1e6; font-size: 14px;")
                    elif col_data == 'Very Low':
                        line_edit.setStyleSheet("background-color: #cefdff; font-size: 14px;")

                    # Set the QLineEdit as the cell widget in the table at column 4
                    table.setCellWidget(row_idx, 6, line_edit)

                elif col_idx == 6:
                    # Create a QLineEdit for data from column 4, but display it in column 5
                    line_edit = QLineEdit(col_data)  # Set initial text from col_data (from column 4)
                    line_edit.setReadOnly(True)       # Set to read-only
                    line_edit.setAlignment(Qt.AlignCenter)  # Center the text

                    # Customize the background color based on col_data
                    if col_data == 'High':
                        line_edit.setStyleSheet("background-color: #0097b2; font-size: 14px;")
                    elif col_data == 'Medium':
                        line_edit.setStyleSheet("background-color: #0cc0df; font-size: 14px;")
                    elif col_data == 'Low':
                        line_edit.setStyleSheet("background-color: #5ce1e6; font-size: 14px;")
                    elif col_data == 'Very Low':
                        line_edit.setStyleSheet("background-color: #cefdff; font-size: 14px;")

                    # Set the QLineEdit as the cell widget in the table at column 5
                    table.setCellWidget(row_idx, 7, line_edit)


                    
                    

                # elif col_idx in [3,4]:    
                      
                #         if col_data == 'high':
                #             item.setBackground(QColor("#0097b2"))  # High - #0097b2
                #         elif col_data == 'medium':
                #             item.setBackground(QColor("#0cc0df"))  # Medium - #0cc0df
                #         elif col_data == 'low':
                #             item.setBackground(QColor("#5ce1e6"))  # Low - #5ce1e6
                #         elif col_data == 'very low':
                #             item.setBackground(QColor("#cefdff"))  # Very Low - #cefdff
                else:
                    item = QTableWidgetItem(col_data)
                    if col_idx in [0, 1, 3, 4, 5, 6, 7]:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row_idx, col_idx+1, item)
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)
        if table.rowCount() > 0: table.setCurrentCell(0, 1)
    except sqlite3.Error as e:
        logger.error(f"Error loading data: {e}")
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

def load_threat_scenarios(table, property_panel, toggle_button):
    logger.info(f"Loading data for Threat Scenarios")
    try:
        table.setColumnCount(7)  # Adjusting the column count to 7 (for the new "toe_configuration" column)
        table.verticalHeader().setVisible(False)
        header_item = QTableWidgetItem('')  # Add icon with text
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28,28))
        table.setHorizontalHeaderItem(0, header_item)
        for index, header in enumerate(helper.TS_header):
            header_item = QTableWidgetItem(header)
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28,28))
            table.setHorizontalHeaderItem(index+1, header_item)
            table.horizontalHeader().setFixedHeight(50)
        
        helper.adjust_table_column('Threat Scenarios', table)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)  # Stretch the new column
        table.horizontalHeader().setStretchLastSection(True)

        damage_scenario_map = {}
        rows = DB.execute_db("SELECT ts_id, threat, damage_scenarios, toe_configuration, reasoning, comments FROM threat_scenarios")
        damage_scenario_rows = DB.execute_db("SELECT ds_id, name FROM damage_scenarios")
        toe_configuration_rows = DB.execute_db("SELECT toe_configuration_id, toe_configuration_name FROM toe_configuration")
        
        # Create a map for damage scenario IDs to names
        for ds_id, ds_name in damage_scenario_rows:
            damage_scenario_map[ds_id] = ds_name
        
        # Create a list for toe_configuration options
        toe_configuration_options = [f"{toec_id}::{toec_name}" for toec_id, toec_name in toe_configuration_rows]

        table.setRowCount(0)
        if not rows:
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
        for row_idx, row_data in enumerate(rows):
            ts_id, threat, damage_scenarios, toe_configuration, reasoning, comments = row_data
            table.insertRow(table.rowCount())  # Insert a new row
            table.setRowHeight(row_idx, 40)
            
            row_idx = table.rowCount() - 1  # Correct the row index
            ts_id_item = QTableWidgetItem(ts_id)
            ts_id_item.setFlags(ts_id_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 1, ts_id_item)

            threat_item = QTableWidgetItem(threat)
            threat_item.setFlags(threat_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 2, threat_item)

            DS_item = QTableWidgetItem(damage_scenarios)
            DS_item.setFlags(DS_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 3, DS_item)

            # Create a combo box for the "toe_configuration" column
            combo_box = MOS.ReadOnlyMultiSelectComboBox(toe_configuration_options)
            selected_toe_configurations = toe_configuration.split(", ")
            new_selected_toe_configurations = []
            for data in selected_toe_configurations:
                for x in toe_configuration_options:
                    if f"{data}::" in x and data != ' ':
                        new_selected_toe_configurations.append(x)
            if toe_configuration!="":
                combo_box.set_text(new_selected_toe_configurations)
            else:
                combo_box.set_text("")   
            table.setCellWidget(row_idx, 4, combo_box)

            table.setItem(row_idx, 5, QTableWidgetItem(reasoning))
            table.setItem(row_idx, 6, QTableWidgetItem(comments))
            
            # Sidebar widget for the first column
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)
        
        if table.rowCount() > 0:
            table.setCurrentCell(0, 1)  # Set initial selection

    except sqlite3.Error as e:
        logger.error(f"Error loading data: {e}")
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
         

