
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
import components.table.table_row_indicator as TRI
import models.TableStyle as TS
import Analysis.controllers.analysis_TableValueLoad as TVL

def asset_refresh_data(table):
    try:
        table.setRowCount(0)
        rows = DB.execute_db("SELECT * FROM assets")
        for row_idx, row_data in enumerate(rows):
            table.insertRow(row_idx)
            for col_idx, col_data in enumerate(row_data):
                if col_idx == 2:
                    widget = MOS.MultiSelectComboBox(helper.assert_securityproperty_menu)
                    widget.set_text(col_data)
                    table.setCellWidget(row_idx, col_idx+1, widget)
                else:
                    item = QTableWidgetItem(col_data)
                    if col_idx == 0:  # ID column
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make the ID column read-only
                    table.setItem(row_idx, col_idx+1, item)
            sidebar = TRI.SidebarWidget()
            table.setCellWidget(row_idx, 0, sidebar)
        if table.rowCount() > 0: table.setCurrentCell(0, 1)
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

def DS_refresh_data(table):
    try:
        table.setRowCount(0)
        rows = DB.execute_db("SELECT * FROM damage_scenarios")
        for row_idx, row_data in enumerate(rows):
            table.insertRow(row_idx)
            for col_idx, col_data in enumerate(row_data):
                if col_idx == 2:
                    widget = MOS.NoWheelComboBox()
                    widget.addItems(helper.DS_impact_menu)
                    widget.setCurrentText(col_data)
                    table.setCellWidget(row_idx, col_idx+1, widget)
                elif col_idx == 3:
                    # widget = QComboBox()
                    # widget.addItems(helper.DS_impactcatagory_menu)
                    # widget.setCurrentText(col_data)
                    # table.setCellWidget(row_idx, col_idx+1, widget)
                    widget = MOS.MultiSelectComboBox(helper.DS_impactcatagory_menu)
                    widget.set_text(col_data)  # Assuming set_text handles displaying selected items
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
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

def handle_key_press(event, combo_box):
    if event.key() == Qt.Key_Delete:  # Check if the Delete key is pressed
        # Clear the current selection in the combo box
        # combo_box.clear()  
        combo_box.setCurrentIndex(-1)  # Ensure that no item is selected
        # QMessageBox.information(None, "Item Deleted", "The selected item has been cleared.")  # Optional feedback
    else:
        QComboBox.keyPressEvent(combo_box, event)  # Call the original keyPressEvent for other keys

def generate_name(asset_id, property):
    try:
        DB.cursor.execute("SELECT name FROM assets WHERE asset_id = ?", (asset_id,))
        asset_name_row = DB.cursor.fetchone()
        
        if asset_name_row:
            asset_name = asset_name_row[0]
        else:
            return f"Unknown asset for ID {asset_id}"

        if property == "Availability":
            return f"Blocking {asset_name}"
        elif property == "Confidentiality":
            return f"Extraction of {asset_name}"
        elif property == "Integrity":
            return f"Manipulation of {asset_name}"
        elif property == "Authenticity":
            return f"Forgery of {asset_name}"
        elif property == "Correctness":
            return f"Invalidation of {asset_name}"
        elif property == "Freshness":
            return f"Replay of {asset_name}"
        elif property == "Authorization":
            return f"Unauthorized access to {asset_name}"
        elif property == "Non-repudiation":
            return f"Repudiation of {asset_name}"
        else:
            return f"Unknown impact on {asset_name}"
    except sqlite3.Error as e:
        return f"Database error: {e}"

def threat_refresh_data(table, damage_scenarios_options):
    try:
        for row in range(table.rowCount()):
            table.removeRow(0)
        TVL.load_threat(table, damage_scenarios_options)
        existing_rows = DB.execute_db("SELECT * FROM threat ORDER BY CAST(SUBSTRING(threat_id, 4) AS UNSIGNED) ASC")
        existing_scenarios_set = set((row[5], row[6]) for row in existing_rows)  
        assets = DB.execute_db("SELECT asset_id FROM assets ORDER BY asset_id ASC")
        existing_assets_set = set(id for (id,) in assets)
        assets = DB.execute_db("SELECT asset_id, security_properties FROM assets ORDER BY asset_id ASC")
        existing_asset_ds = {}
        for (id,security) in assets:
            existing_asset_ds.update({id:security})
        rows_to_remove = []
        for row in range(table.rowCount()):
            asset_id_item = table.item(row, 6)
            asset_sp_item = table.item(row, 7)
            if asset_id_item:
                asset_id = asset_id_item.text()
                if asset_id not in existing_assets_set:
                    rows_to_remove.append(row)
                else:
                    if asset_sp_item:
                        if asset_sp_item.text() not in existing_asset_ds[asset_id]:
                            rows_to_remove.append(row)
                        else:      
                            name = generate_name(asset_id_item.text(), asset_sp_item.text())
                            table.item(row, 2).setText(name)
        for row in reversed(rows_to_remove):
            asset_id = table.item(row, 6).text()
            table.removeRow(row)
            DB.update_db("DELETE FROM threat WHERE asset = ?", (asset_id,))

        for asset_id, security_properties in assets:
            security_properties_list = security_properties.split(", ") if security_properties else []
            for property in security_properties_list:
                property = property.strip()
                data = (asset_id, property)
                if data in existing_scenarios_set:
                    continue
                else:
                    threat_id = helper.threat_generate_id(table)
                    name = generate_name(asset_id, property)

                    new_row = table.rowCount()
                    row_idx = new_row
                    table.insertRow(row_idx)
                    item = QTableWidgetItem(threat_id)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row_idx, 1, item)
                    item = QTableWidgetItem(name)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row_idx, 2, item)
                    # Setting empty items in column 4 and 5 with background color
                    item_4 = QTableWidgetItem("")
                    item_4.setFlags(item_4.flags() & ~Qt.ItemIsEditable)

                    # Set background color for column 4
                    if property == 'High':
                        item_4.setBackground(QColor("#0097b2"))  # High
                    elif property == 'Medium':
                        item_4.setBackground(QColor("#0cc0df"))  # Medium
                    elif property == 'Low':
                        item_4.setBackground(QColor("#5ce1e6"))  # Low
                    elif property == 'Very Low':
                        item_4.setBackground(QColor("#cefdff"))  # Very Low

                    table.setItem(row_idx, 4, item_4)

                    item_5 = QTableWidgetItem("")
                    item_5.setFlags(item_5.flags() & ~Qt.ItemIsEditable)

                    # Set background color for column 5 (same logic as column 4)
                    if property == 'High':
                        item_5.setBackground(QColor("#0097b2"))  # High
                    elif property == 'Medium':
                        item_5.setBackground(QColor("#0cc0df"))  # Medium
                    elif property == 'Low':
                        item_5.setBackground(QColor("#5ce1e6"))  # Low
                    elif property == 'Very Low':
                        item_5.setBackground(QColor("#cefdff"))  # Very Low

                    table.setItem(row_idx, 5, item_5)
                    item = QTableWidgetItem(asset_id)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row_idx, 6, item)
                    item = QTableWidgetItem(property)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row_idx, 7, item)

                    combo_box = MOS.TSMultiSelectComboBox(damage_scenarios_options)
                    table.setCellWidget(row_idx, 3, combo_box)
                    sidebar = TRI.SidebarWidget()
                    table.setCellWidget(row_idx, 0, sidebar)
                    if table.rowCount() > 0: table.setCurrentCell(row_idx, 1)
        if table.rowCount() > 0: table.setCurrentCell(0, 1)
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error refreshing data: {e}")
    except AttributeError as e:
        QMessageBox.critical(None, "Application Error", f"An error occurred: {e}")

def TS_refresh_data(table):
    try:
        threat_rows = DB.execute_db(f"SELECT threat_id, name, damage_scenarios FROM threat")
        ds_rows = DB.execute_db("SELECT ds_id, name FROM damage_scenarios")
        ds_available_id = {id:f"{id}::{name}" for id, name in ds_rows}
        ts_available_data = {f"{threat_id} - {name}":damage_scenarios for threat_id, name, damage_scenarios in threat_rows}
        ts_available_id = [f"{threat_id} - {name}" for threat_id, name, damage_scenarios in threat_rows]
        
        damage_scenario_map = {}
        for ds_id, ds_name in ds_rows:
            damage_scenario_map[ds_id] = ds_name
        
        existing_ts_data = {}
        existing_ts_id = [] 
        for row in range(table.rowCount()):
            item = table.item(row, 2)
            if item:
                if item.text() not in  existing_ts_id: existing_ts_id.append(item.text())
            item = table.item(row, 3)
            if item:
                ds = item.text().split('::')[0]
                if ds in damage_scenario_map.keys():
                    table.item(row, 3).setText(f"{ds}::{damage_scenario_map[ds]}")

        for threat in existing_ts_id:
            ds_ids = []
            for row in range(table.rowCount()):
                item = table.item(row, 2).text()
                if item == threat:
                    if table.item(row, 3).text() not in  ds_ids: ds_ids.append(table.item(row, 3).text())
            existing_ts_data.update({threat:ds_ids})

        remove_rows = []
        for threat in existing_ts_id:
            for row in range(table.rowCount()):
                item = table.item(row, 2)
                if item:
                    if threat not in ts_available_id:
                        remove_rows.append(row)
                    else:
                        if item.text() == threat:
                            item_ds = table.item(row, 3)
                            if item_ds:
                                if item_ds.text().split('::')[0] not in ts_available_data[threat]:
                                    remove_rows.append(row)
        
        for row in reversed(remove_rows):
            threat_item_id = table.item(row, 1).text()
            table.removeRow(row)
            DB.update_db("DELETE FROM threat_scenarios WHERE ts_id = ?", (threat_item_id,))

        for row_data in threat_rows:
            threat_id, name, damage_scenarios = row_data 
            threat_name = f"{threat_id} - {name}"
            if not damage_scenarios.strip(): continue  
            damage_scenarios_data = damage_scenarios.split(', ') 
            if threat_name not in existing_ts_id:
                for ds_id in damage_scenarios_data:
                    ds_id = ds_id.strip()  
                    damage_scenario_name = damage_scenario_map.get(ds_id, '')
                    damage_scenario_text = f"{ds_id}::{damage_scenario_name}"
                    unique_id = helper.TS_generate_id(table)
                    table.insertRow(table.rowCount()) 
                    row_idx = table.rowCount()  
                    id_item = QTableWidgetItem(unique_id)
                    threat_item = QTableWidgetItem(threat_name)
                    DS_item = QTableWidgetItem(damage_scenario_text)
                    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                    threat_item.setFlags(threat_item.flags() & ~Qt.ItemIsEditable)
                    DS_item.setFlags(DS_item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row_idx - 1, 1, id_item)
                    table.setItem(row_idx - 1, 2, threat_item)
                    table.setItem(row_idx - 1, 3, DS_item)
                
                    sidebar = TRI.SidebarWidget()
                    table.setCellWidget(row_idx-1, 0, sidebar)
            else:
                for ds_id in damage_scenarios_data:
                    ds_id = ds_id.strip()  
                    damage_scenario_name = damage_scenario_map.get(ds_id, '')
                    damage_scenario_text = f"{ds_id}::{damage_scenario_name}"
                    if damage_scenario_text not in existing_ts_data[threat_name]:
                        unique_id = helper.TS_generate_id(table)
                        table.insertRow(table.rowCount()) 
                        row_idx = table.rowCount()  
                        id_item = QTableWidgetItem(unique_id)
                        threat_item = QTableWidgetItem(threat_name)
                        DS_item = QTableWidgetItem(damage_scenario_text)
                        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                        threat_item.setFlags(threat_item.flags() & ~Qt.ItemIsEditable)
                        DS_item.setFlags(DS_item.flags() & ~Qt.ItemIsEditable)
                        table.setItem(row_idx - 1, 1, id_item)
                        table.setItem(row_idx - 1, 2, threat_item)
                        table.setItem(row_idx - 1, 3, DS_item)
                    
                        sidebar = TRI.SidebarWidget()
                        table.setCellWidget(row_idx-1, 0, sidebar)
    
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
    except AttributeError as e:
        QMessageBox.critical(None, "Application Error", f"An error occurred: {e}")
    



