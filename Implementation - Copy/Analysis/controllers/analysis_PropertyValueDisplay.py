
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
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


def on_TS_property_comment_changed(selected_indexes, selected_row, table, data):
    try:
        if selected_indexes:
            if selected_row < 0:
                QMessageBox.warning("Warning", "Please select a row to update.")
                return
            table.item(selected_row, 7).setText(data)
    except Exception as e:
        pass

def on_property_line_changed(table, col_idx, input_control):
    try:
        if table.selectedIndexes():
            if table.currentRow() < 0:
                QMessageBox.warning("Warning", "Please select a row to update.")
                return
            table.item(table.currentRow(), col_idx).setText(input_control.text())
    except Exception as e:
        pass

def on_property_multiline_changed(table, col_idx, input_control):
    try:
        if table.selectedIndexes():
            if table.currentRow() < 0:
                QMessageBox.warning("Warning", "Please select a row to update.")
                return
            if input_control.toPlainText() != None and table.item(table.currentRow(), col_idx) != None: 
                cursor = input_control.textCursor()
                current_position = cursor.position()
                table.item(table.currentRow(), col_idx).setText(input_control.toPlainText())
                cursor.setPosition(current_position)
                input_control.setTextCursor(cursor)
    except Exception as e:
        pass

def on_property_singleselect_changed(table, col_idx, input_control):
    try:
        if table.selectedIndexes():
            if table.currentRow() < 0:
                QMessageBox.warning("Warning", "Please select a row to update.")
                return
            table.cellWidget(table.currentRow(), col_idx).setCurrentText(input_control.currentText())
    except Exception as e:
        pass

def on_property_multiselect_changed(table, col_idx, input_control):
    try:
        if table.selectedIndexes():
            if table.currentRow() < 0:
                QMessageBox.warning("Warning", "Please select a row to update.")
                return
            table.cellWidget(table.currentRow(), col_idx).set_text(", ".join(input_control.selected_items()))
    except Exception as e:
        pass

def display_selected_row(selected_option, table, property_controls, damage_scenario_menu):
    try:
        if table.selectedIndexes():
            selected_row = table.currentRow()        
            if selected_row < 0:
                return
            if selected_option == 'Asset': asset_display(table, selected_row, property_controls['Asset'])
            elif selected_option == 'Damage Scenarios': DS_display(table, selected_row, property_controls['Damage Scenarios'])
            elif selected_option == 'Threats': threat_display(table, selected_row, property_controls['Threats'], damage_scenario_menu)
            elif selected_option == 'Threat Scenarios': TS_display(table, selected_row, property_controls['Threat Scenarios'], damage_scenario_menu)
        
        else:
            if selected_option == 'Asset': asset_display_reset(property_controls['Asset'])
            elif selected_option == 'Damage Scenarios': ds_display_reset(property_controls['Damage Scenarios'])
            elif selected_option == 'Threats': threat_display_reset(property_controls['Threats'])
            elif selected_option == 'Threat Scenarios': ts_display_reset(property_controls['Threat Scenarios'])
    except Exception as e:
        pass
        # QMessageBox.critical(None, "Error", f"Error loading data: {e}")
def asset_display_selected_row(table, asset_property_controls, property_panel, toggle_button):
    print("check property panel data printed-------------------------22222222222222")
    try:
        if table.selectionModel().hasSelection():  # Only then define selected_row!
            selected_row = table.selectionModel().currentIndex().row()
            print(f"[asset_display] Populating for row: {selected_row}")
            if selected_row < 0:  # No valid row selected
                property_panel.setEnabled(False)
                property_panel.setVisible(False)
                toggle_button.setEnabled(False)
                return

            # Enable the property panel and toggle button when a valid row is selected
            property_panel.setEnabled(True)
            property_panel.setVisible(True)
            toggle_button.setEnabled(True)

            # Display data in the property panel
            asset_display(table, selected_row, asset_property_controls)
        else:
            # Disable and hide the property panel when no rows are selected
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)
            # Reset the property panel values
            asset_display_reset(asset_property_controls)
    except Exception as e:
        print(f"Error in asset_display_selected_row: {e}")  # Print error for debugging

# def asset_display_selected_row(table, property_controls, property_panel, toggle_button):
#     try:
#         if table.selectionModel().hasSelection():  # Check if any rows are selected
#             selected_row = table.selectionModel().currentIndex().row()  # Get the current selected row
#             if selected_row < 0:  # No valid row selected
#                 property_panel.setEnabled(False)  # Disable the entire property panel
#                 property_panel.setVisible(False)  # Hide the property panel
#                 toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
#                 return
            
#             # Enable the property panel and toggle button when a valid row is selected
#             property_panel.setEnabled(True)
#             property_panel.setVisible(True)
#             toggle_button.setEnabled(True)  # Enable the toggle button
            
#             # Display data in the property panel
#             asset_display(table, selected_row, property_controls)
#         else:
#             # Disable and hide the property panel when no rows are selected
#             property_panel.setEnabled(False)
#             property_panel.setVisible(False)
#             toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
            
#             # Reset the property panel values
#             asset_display_reset(property_controls)
#     except Exception as e:
#         print(f"Error in asset_display_selected_row: {e}")  # Print error for debugging


def ds_display_selected_row(table, property_controls, property_panel, toggle_button):
    try:
        if table.selectedIndexes():  # Check if any row is selected
            selected_row = table.currentRow()
            if selected_row < 0:  # No valid row selected
                property_panel.setEnabled(False)
                property_panel.setVisible(False)
                toggle_button.setEnabled(False)
                return

            # Enable and show the property panel when a row is selected
            property_panel.setEnabled(True)
            property_panel.setVisible(True)
            toggle_button.setEnabled(True)

            # Pass additional parameters to DS_display
            DS_display(table, selected_row, property_controls)
        else:
            # Disable and hide property panel when no row is selected
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)

            # Reset property panel controls
            ds_display_reset(property_controls)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error loading data: {e}")  # Show error message to the user

def threat_display_selected_row(
    table, property_controls, damage_scenario_menu, misuse_cases_menu, toe_configuration_menu, property_panel, toggle_button
):
    try:
        if table.selectionModel().hasSelection():  # Check if any rows are selected
            selected_row = table.selectionModel().currentIndex().row()  # Get the current selected row
            if selected_row < 0:  # No valid row selected
                property_panel.setEnabled(False)  # Disable the entire property panel
                property_panel.setVisible(False)  # Hide the property panel
                toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
                return
            
            # Enable the property panel and toggle button when a valid row is selected
            property_panel.setEnabled(True)
            property_panel.setVisible(True)
            toggle_button.setEnabled(True)  # Enable the toggle button
            
            # Display data in the property panel
            threat_display(
                table,
                selected_row,
                property_controls,
                damage_scenario_menu,
                misuse_cases_menu,
                toe_configuration_menu,
            )
        else:
            # Disable and hide the property panel when no rows are selected
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
            
            # Reset the property panel values
            threat_display_reset(property_controls)
    except Exception as e:
        print(f"Error in threat_display_selected_row: {e}")  # Print error for debugging



def ts_display_selected_row(table, property_controls, toes_menu, property_panel, toggle_button):
    try:
        if table.selectionModel().hasSelection():  # Check if any rows are selected
            selected_row = table.selectionModel().currentIndex().row()  # Get the current selected row
            if selected_row < 0:  # No valid row selected
                property_panel.setEnabled(False)  # Disable the entire property panel
                property_panel.setVisible(False)  # Hide the property panel
                toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
                return
            
            # Enable the property panel and toggle button when a valid row is selected
            property_panel.setEnabled(True)
            property_panel.setVisible(True)
            toggle_button.setEnabled(True)  # Enable the toggle button
            
            # Display data in the property panel
            TS_display(table, selected_row, property_controls, toes_menu)
        else:
            # Disable and hide the property panel when no rows are selected
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
            
            # Reset the property panel values
            ts_display_reset(property_controls)
    except Exception as e:
        print(f"Error in ts_display_selected_row: {e}")  # Print error for debugging



def asset_display(table, selected_row, asset_property_controls):
    try:
        existing_data = DB.execute_db("SELECT Asset FROM scope_home_mindmap_dumy")
        existing_scope_assets = [row[0] for row in existing_data]
        
        asset_id = table.item(selected_row, 1).text()
        asset_property_controls[0][1].setText(asset_id)
        asset_property_controls[1][1].setReadOnly(True) if asset_id in existing_scope_assets else asset_property_controls[1][1].setReadOnly(False)
        asset_property_controls[1][1].setText(table.item(selected_row, 2).text())
        asset_property_controls[2][1].set_text(table.cellWidget(selected_row, 3).currentText())
        description_data=''
        if table.item(selected_row, 4) != None: 
            description_data = table.item(selected_row, 4).text()
        asset_property_controls[3][1].setText(description_data)
        asset_property_controls[4][1].setText(table.item(selected_row, 5).text())
    except Exception as e:
        pass

def asset_display_reset(asset_property_controls):
    try:
        asset_property_controls[0][1].setText('')
        asset_property_controls[1][1].setText('')
        asset_property_controls[2][1].set_text('')
        asset_property_controls[3][1].setText('')
        asset_property_controls[4][1].setText('')
    except Exception as e:
        pass

def DS_display(table, selected_row, ds_property_controls):
    try:
        ds_property_controls[0][1].setText(table.item(selected_row, 1).text())
        ds_property_controls[1][1].setText(table.item(selected_row, 2).text())
        if table.cellWidget(selected_row, 3).currentText() != '': ds_property_controls[2][1].setCurrentText(table.cellWidget(selected_row, 3).currentText())
        else: ds_property_controls[2][1].setCurrentIndex(-1)
        if table.cellWidget(selected_row, 4).currentText() != '': ds_property_controls[3][1].set_text(table.cellWidget(selected_row, 4).currentText())
        else: ds_property_controls[3][1].set_text('')
        description_data=''
        if table.item(selected_row, 5) != None: 
            description_data = table.item(selected_row, 5).text()
        ds_property_controls[4][1].setText(description_data)
        ds_property_controls[5][1].setText(table.item(selected_row, 6).text())
    except Exception as e:
        pass

def ds_display_reset(ds_property_controls):
    try:
        ds_property_controls[0][1].setText('')
        ds_property_controls[1][1].setText('')
        ds_property_controls[2][1].setCurrentIndex(-1)
        ds_property_controls[3][1].set_text('')
        ds_property_controls[4][1].setText('')
        ds_property_controls[5][1].setText('')
    except Exception as e:
        pass

def threat_display(table, selected_row, threat_property_controls, damage_scenario_menu, misuse_cases_menu, toe_configuration_menu):
    try:
        # Ensure all necessary columns are populated
        for i in range(1, 10):  # Adjust range to match all columns
            if table.item(selected_row, i) is None:
                table.setItem(selected_row, i, QTableWidgetItem(''))

        # Set ID, Name, and other fields
        threat_property_controls[0][1].setText(table.item(selected_row, 1).text())  # ID
        threat_property_controls[1][1].setText(table.item(selected_row, 2).text())  # Name

        # Damage Scenarios handling (multi-selection)
        DS_data_widget = table.cellWidget(selected_row, 3)
        if DS_data_widget:
            selected_DS = DS_data_widget.selected_items()  # Fetch selected items directly
            threat_property_controls[2][1].set_text(selected_DS)
            
        # toec_data_widget = table.cellWidget(selected_row, 4)
        # if toec_data_widget:
        #     selected_toec = toec_data_widget.selected_items()  # Fetch selected items directly
        #     threat_property_controls[3][1].set_text(selected_toec)
    
        DS_data_widget = table.cellWidget(selected_row, 4)
        if DS_data_widget:
            selected_DS = DS_data_widget.selected_items()  # Fetch selected items directly
            threat_property_controls[3][1].set_text(selected_DS)    

        # Misuse Cases handling (multi-selection)
        MS_data_widget = table.cellWidget(selected_row, 5)
        if MS_data_widget:
            selected_MS = MS_data_widget.selected_items()  # Fetch selected items directly
            threat_property_controls[4][1].set_text(selected_MS)

        # Asset and Security Properties
        threat_property_controls[5][1].setText(table.item(selected_row, 8).text())  # Asset
        threat_property_controls[6][1].setText(table.item(selected_row, 9).text())  # Security Properties

        # Reasoning and Comments
        threat_property_controls[7][1].setText(table.item(selected_row, 10).text())  # Reasoning
        threat_property_controls[8][1].setText(table.item(selected_row, 11).text())  # Comments

    except Exception as e:
        pass


def threat_display_reset(threat_property_controls):
    try:
        threat_property_controls[0][1].setText('')
        threat_property_controls[1][1].setText('')
        threat_property_controls[2][1].set_text([])
        threat_property_controls[3][1].set_text('')
        threat_property_controls[4][1].set_text('')
        threat_property_controls[5][1].setText('')
        threat_property_controls[6][1].setText('')
        threat_property_controls[7][1].setText('')
    except Exception as e:
        pass

def TS_display(table, selected_row, ts_property_controls, toes_menu):
    try:
        for i in range(1,6):
            if table.item(selected_row, i) == None: table.setItem(selected_row, i, QTableWidgetItem(''))
        ts_property_controls[0][1].setText(table.item(selected_row, 1).text())
        ts_property_controls[1][1].setText(table.item(selected_row, 2).text())
        ts_property_controls[2][1].setText(table.item(selected_row, 3).text()) 
        toe_data_widget = table.cellWidget(selected_row, 4)
        if toe_data_widget:
            selected_toe = toe_data_widget.selected_items()  # Fetch selected items directly
            ts_property_controls[3][1].set_text(selected_toe)
        ts_property_controls[4][1].setText(table.item(selected_row, 5).text())
        ts_property_controls[5][1].setText(table.item(selected_row, 6).text())
    except Exception as e:
        pass 

def ts_display_reset(ts_property_controls):
    try:
        ts_property_controls[0][1].setText('')
        ts_property_controls[1][1].setText('')
        ts_property_controls[2][1].setText('')
        ts_property_controls[3][1].set_Text('')
        ts_property_controls[4][1].setText('')
        ts_property_controls[5][1].setText('')
    except Exception as e:
        pass



