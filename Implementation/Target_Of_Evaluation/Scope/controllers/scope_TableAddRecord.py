
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
import models.helper as helper
import components.table.tree_row_indicator as TRI2
import logging
logger = logging.getLogger(__name__) 


def scope_add_new_entry(table, self):
    logger.info("Scope Add new entry")
    row_idx = table.rowCount()
    table.insertRow(row_idx)
    table.setRowHeight(row_idx, 40)

    scope_id = helper.scope_generate_id(table)
    id_item = QTableWidgetItem(scope_id)
    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
    table.setItem(row_idx, 1, id_item)

    sidebar = TRI2.SidebarWidget(parent=self, index=row_idx)
    table.setCellWidget(row_idx, 0, sidebar)

    # Set empty values for other columns
    scope_name = f"Scope {scope_id.split('-')[-1]}"  
    for col_idx in range(2, table.columnCount()):
        item = QTableWidgetItem(scope_name if col_idx == 2 else "")
        if col_idx == 2:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make Scope Name read-only
        table.setItem(row_idx, col_idx, item)

    table.setCurrentCell(row_idx, 1)

    return scope_id, scope_name  # Return scope_id and scope_name for further use
