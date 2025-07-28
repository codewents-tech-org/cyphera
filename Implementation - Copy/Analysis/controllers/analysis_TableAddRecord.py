
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

import logging
logger = logging.getLogger(__name__)

def asset_add_new_entry(table, self):
    logger.info("New Asset added")
    row_idx = table.rowCount()
    table.insertRow(row_idx)
    table.setRowHeight(row_idx, 40)
    
    asset_id = helper.asset_generate_id(table)
    id_item = QTableWidgetItem(asset_id)
    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # Asset ID should not be editable
    table.setItem(row_idx, 1, id_item)

    sidebar = TRI.SidebarWidget()
    table.setCellWidget(row_idx, 0, sidebar)

    # Extract only the last part after the last '-'
    asset_suffix = asset_id.split('-')[-1]
    asset_name = f"Asset {asset_suffix}"  # Pre-fill as placeholder but editable

    for col_idx in range(2, table.columnCount()):
        if col_idx == 2:
            item = QTableWidgetItem(asset_name)  # Set placeholder text
            table.setItem(row_idx, col_idx, item)
            table.setCurrentCell(row_idx, 2)
            self.find_duplicates(item)
            self.previous_text = item.text()
            self.existing_entries.add(item.text())
            # **DO NOT MAKE IT NON-EDITABLE** so the user can change it
        elif col_idx == 3:
            widget = MOS.MultiSelectComboBox(helper.assert_securityproperty_menu)
            table.setCellWidget(row_idx, col_idx, widget)
            table.setItem(row_idx, col_idx, item)
            continue
        else:
            item = QTableWidgetItem("")
            table.setItem(row_idx, col_idx, item)

    table.setCurrentCell(row_idx, 1)

    return asset_id, asset_name  # Returning both values for further use

def DS_add_new_entry(table, self):
    logger.info("New Damage Scenarios added")
    row_idx = table.rowCount()
    table.insertRow(row_idx)
    table.setRowHeight(row_idx, 40)
    
    ds_id = helper.DS_generate_id(table)
    id_item = QTableWidgetItem(ds_id)
    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # ID column should remain non-editable
    table.setItem(row_idx, 1, id_item)

    sidebar = TRI.SidebarWidget()
    table.setCellWidget(row_idx, 0, sidebar)

    # Extract only the last part after the last '-'
    ds_name = f"Damage Scenario {ds_id.split('-')[-1]}"  # Pre-filled editable name

    for col_idx in range(2, table.columnCount()):
        if col_idx == 2:
            item = QTableWidgetItem(ds_name)  # Set placeholder text
            table.setItem(row_idx, col_idx, item)
            table.setCurrentCell(row_idx, 2)
            # **DO NOT MAKE IT NON-EDITABLE** so the user can change it
            self.find_duplicates(item)
            self.previous_text = item.text()
            self.existing_entries.add(item.text())
        elif col_idx == 3:
            impact_combo = MOS.NoWheelComboBox()
            impact_combo.addItems(helper.DS_impact_menu)
            impact_combo.setCurrentIndex(-1)
            table.setCellWidget(row_idx, col_idx, impact_combo)
            table.setItem(row_idx, col_idx, item)
            continue
        elif col_idx == 4:
            impact_category_combo = MOS.MultiSelectComboBox(helper.DS_impactcatagory_menu)
            table.setCellWidget(row_idx, col_idx, impact_category_combo)
            table.setItem(row_idx, col_idx, item)
            continue
        else:
            item = QTableWidgetItem("")
            table.setItem(row_idx, col_idx, item)

    table.setCurrentCell(row_idx, 1)

    return ds_id, ds_name  # Returning both values for further use


# Function to handle key press event
def handle_key_press(event, combo_box):
    if event.key() == Qt.Key_Delete:  # Check if the Delete key is pressed
        # Clear the current selection in the combo box
        # combo_box.clear()  
        combo_box.setCurrentIndex(-1)  # Ensure that no item is selected
        # QMessageBox.information(None, "Item Deleted", "The selected item has been cleared.")  # Optional feedback
    else:
        # Call the original keyPressEvent for other keys
        QComboBox.keyPressEvent(combo_box, event)

    # Ensure the combo box is activated for a new selection
    combo_box.showPopup()  # This will open the dropdown list for the user to select an item.




