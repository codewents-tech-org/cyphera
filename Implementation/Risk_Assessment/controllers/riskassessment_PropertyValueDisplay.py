
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
from controllers.schema_manager import get_instances
from controllers.database_tables.catalog_tables import ThreatCatalog


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
            table.cellWidget(table.currentRow(), col_idx).setCurrentIndex(input_control.currentIndex())
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


def SecurityClaims_display_selected_row(table, property_controls, formatted_assumptions, formatted_toe_configuration, property_panel, toggle_button):
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
            SecurityClaims_display(
                table, selected_row, property_controls, formatted_assumptions, formatted_toe_configuration
            )
        else:
            # Disable and hide the property panel when no rows are selected
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
            
            # Reset the property panel values
            SecurityClaims_display_reset(property_controls)
    except Exception as e:
        print(f"Error in SecurityClaims_display_selected_row: {e}")  # Print error for debugging

def SecurityGoals_display_selected_row(table, property_controls, formatted_toe_configuration, property_panel, toggle_button):
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
            SecurityGoals_display(table, selected_row, property_controls, formatted_toe_configuration)
        else:
            # Disable and hide the property panel when no rows are selected
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
            
            # Reset the property panel values
            SecurityGoals_display_reset(property_controls)
    except Exception as e:
        print(f"Error in SecurityGoals_display_selected_row: {e}")  # Print error for debugging

def SecurityControls_display_selected_row(table, property_controls, securitycontrol_menu, property_panel, toggle_button):
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
            SecurityControls_display(table, selected_row, property_controls, securitycontrol_menu)
        else:
            # Disable and hide the property panel when no rows are selected
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
            
            # Reset the property panel values
            SecurityControls_display_reset(property_controls)
    except Exception as e:
        print(f"Error in SecurityControls_display_selected_row: {e}")  # Print error for debugging



def RiskTreatment_display_selected_row(table, property_controls, SC_list, SG_list, property_panel, toggle_button):
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
            RiskTreatment_display(
                table,
                selected_row,
                property_controls,
                SC_list,
                SG_list,
            )
        else:
            # Disable and hide the property panel when no rows are selected
            property_panel.setEnabled(False)
            property_panel.setVisible(False)
            toggle_button.setEnabled(False)  # Disable the toggle button when the panel is hidden
            
            # Reset the property panel values
            RiskTreatment_display_reset(property_controls)
    except Exception as e:
        print(f"Error in RiskTreatment_display_selected_row: {e}")  # Print error for debugging

def SecurityClaims_display(table, selected_row, sc_property_controls, formatted_assumptions, formatted_toe_configuration):
    try:
        sc_property_controls[0][1].setText(table.item(selected_row, 1).text())
        sc_property_controls[1][1].setText(table.item(selected_row, 2).text())
        assum_data_widget = table.cellWidget(selected_row, 3)
        if assum_data_widget:
            selected_assum = assum_data_widget.selected_items()  # Fetch selected items directly
            sc_property_controls[2][1].set_text(selected_assum)
        sc_property_controls[3][1].set_text(table.cellWidget(selected_row, 4).currentText())
        toe_data_widget = table.cellWidget(selected_row, 5)
        if toe_data_widget:
            selected_toe = toe_data_widget.selected_items()  # Fetch selected items directly
            sc_property_controls[4][1].set_text(selected_toe)
        description_data=''
        if table.item(selected_row, 6) != None: 
            description_data = table.item(selected_row, 6).text()
        sc_property_controls[5][1].setText(description_data)
        sc_property_controls[6][1].setText(table.item(selected_row, 7).text())
        
    except Exception as e:
        pass

def SecurityClaims_display_reset(sc_property_controls):
    try:
        sc_property_controls[0][1].setText('')
        sc_property_controls[1][1].setText('')
        sc_property_controls[2][1].set_text('')
        sc_property_controls[3][1].set_text('')
        sc_property_controls[4][1].set_text('')
        sc_property_controls[5][1].setText('')
        sc_property_controls[6][1].setText('')
    except Exception as e:
        pass

def SecurityGoals_display(table, selected_row, sg_property_controls, securitycontrol_menu):
    try:
        sg_property_controls[0][1].setText(table.item(selected_row, 1).text())
        sg_property_controls[1][1].setText(table.item(selected_row, 2).text())
        sg_property_controls[2][1].set_text(table.cellWidget(selected_row, 3).currentText())
        toe_data_widget = table.cellWidget(selected_row, 4)
        if toe_data_widget:
            selected_toe = toe_data_widget.selected_items()  # Fetch selected items directly
            sg_property_controls[3][1].set_text(selected_toe)
        description_data=''
        if table.item(selected_row, 5) != None: 
            description_data = table.item(selected_row, 5).text()
        sg_property_controls[4][1].setText(description_data)
        sg_property_controls[5][1].setText(table.item(selected_row, 6).text())
    except Exception as e:
        pass

def SecurityGoals_display_reset(sg_property_controls):
    try:
        sg_property_controls[0][1].setText('')
        sg_property_controls[1][1].setText('')
        sg_property_controls[2][1].set_text('')
        sg_property_controls[3][1].set_text('')
        sg_property_controls[4][1].setText('')
        sg_property_controls[5][1].setText('')
    except Exception as e:
        pass

def SecurityControls_display(table, selected_row, tsc_property_controls, securitycontrol_menu):
    """
    Display the selected Security Control row's details using data from ThreatCatalog table only.

    :param table: QTableWidget displaying all Security Controls.
    :param selected_row: The currently selected row index in the table.
    :param tsc_property_controls: List of (label, widget) tuples for property panel.
    :param securitycontrol_menu: List of all security control options (for dropdown/multi-select).
    """
    try:
        # 1. Load all mitigation names from ThreatCatalog table (mitigation_checkbox field)
        catalog_rows = get_instances(ThreatCatalog, {})
        existing_security_control_names = {
            getattr(row, 'mitigation_checkbox').strip()
            for row in catalog_rows
            if getattr(row, 'mitigation_checkbox', None)
        }

        # 2. Set the ID field (assume column 1 is the ID)
        if table.item(selected_row, 1):
            tsc_property_controls[0][1].setText(table.item(selected_row, 1).text())
        else:
            tsc_property_controls[0][1].clear()

        # 3. Security Control name (column 2)
        security_control_name = table.item(selected_row, 2).text() if table.item(selected_row, 2) else ""
        is_readonly = security_control_name in existing_security_control_names
        tsc_property_controls[1][1].setReadOnly(is_readonly)
        tsc_property_controls[1][1].setText(security_control_name)

        # 4. Security Goal multi-selection (column 3)
        ds_widget = table.cellWidget(selected_row, 3)
        selected_DS = []
        if hasattr(ds_widget, "selected_items"):
            selected_DS = ds_widget.selected_items()
        elif hasattr(ds_widget, "currentText"):
            ds_value = ds_widget.currentText()
            if ds_value:
                selected_DS = [item for item in securitycontrol_menu if ds_value in item]
        tsc_property_controls[2][1].set_text(selected_DS)

        # 5. Description (column 4)
        description = table.item(selected_row, 4).text() if table.item(selected_row, 4) else ""
        tsc_property_controls[3][1].setText(description)

        # 6. Comments (column 5)
        comments = table.item(selected_row, 5).text() if table.item(selected_row, 5) else ""
        tsc_property_controls[4][1].setText(comments)

    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Error in SecurityControls_display: {e}")


def SecurityControls_display_reset(tsc_property_controls):
    try:
        tsc_property_controls[0][1].setText('')
        tsc_property_controls[1][1].setText('')
        tsc_property_controls[2][1].set_text('')
        tsc_property_controls[3][1].setText('')
        tsc_property_controls[4][1].setText('')
    except Exception as e:
        pass

def RiskTreatment_display(table, selected_row, rt_property_controls, SC_list, SG_list):
    try:
        rt_property_controls[0][1].setText(table.item(selected_row, 1).text())
        rt_property_controls[1][1].setText(table.item(selected_row, 2).text())
        rt_property_controls[2][1].setText(table.cellWidget(selected_row, 3).text())
        rt_property_controls[3][1].setText(table.item(selected_row, 4).text())
        rt_property_controls[4][1].setText(table.cellWidget(selected_row, 5).text())
        rt_property_controls[5][1].setText(table.cellWidget(selected_row, 6).text())
        rt_property_controls[6][1].setText(table.cellWidget(selected_row, 7).text())
        rt_property_controls[7][1].setText(table.cellWidget(selected_row, 8).text())
        toe_data_widget = table.cellWidget(selected_row, 9)
        if toe_data_widget:
            selected_toe = toe_data_widget.selected_items()  # Fetch selected items directly
            rt_property_controls[8][1].set_text(selected_toe)
        rt_data_widget = table.cellWidget(selected_row, 10)
        if rt_data_widget:
            selected_rt = rt_data_widget.selected_items()  # Fetch selected items directly
            rt_property_controls[9][1].set_text(selected_rt)
        sc_data_widget = table.cellWidget(selected_row, 11)
        if sc_data_widget:
            selected_sc = sc_data_widget.selected_items()  # Fetch selected items directly
            rt_property_controls[10][1].set_text(selected_sc)
        sg_data_widget = table.cellWidget(selected_row, 12)
        if sg_data_widget:
            selected_sg = sg_data_widget.selected_items()  # Fetch selected items directly
            rt_property_controls[11][1].set_text(selected_sg)
        rt_property_controls[12][1].setText(table.item(selected_row, 13).text())
    except Exception as e:
        pass

def RiskTreatment_display_reset(rt_property_controls):
    try:
        rt_property_controls[0][1].setText('')
        rt_property_controls[1][1].setText('')
        rt_property_controls[2][1].set_text('')
        rt_property_controls[3][1].setText('')
        rt_property_controls[4][1].set_text('')
        rt_property_controls[5][1].set_text('')
        rt_property_controls[6][1].set_text('')
        rt_property_controls[7][1].set_text('')
        rt_property_controls[8][1].set_text('')
        rt_property_controls[9][1].set_text('')
        rt_property_controls[10][1].set_text('')
        rt_property_controls[11][1].set_text('')
        rt_property_controls[12][1].setText('')
    except Exception as e:
        pass



