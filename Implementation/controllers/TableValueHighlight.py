

from PyQt5.QtGui import QIcon, QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QTableWidgetItem
import models.Parameters as P
import components.table.table_row_indicator as TRI

def on_row_selection_changed(table):
    try:
        selected_indexes = table.selectedIndexes()
        if selected_indexes:
            for row_idx in range(table.rowCount()):
                selected_row = selected_indexes[0].row()
                if row_idx == selected_row:
                    sidebar_widget = table.cellWidget(selected_row, 0)
                    if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.selectedraw_icon))
                else:
                    sidebar_widget = table.cellWidget(row_idx, 0)
                    if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.deselectedrow_icon))
        else:
            for row_idx in range(table.rowCount()):
                sidebar_widget = table.cellWidget(row_idx, 0)
                if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.deselectedrow_icon))
    except Exception as e:
        pass

# def on_row_selection_changed2(table):
#     try:
#         selected_indexes = table.selectedIndexes()
#         if selected_indexes:
#             for row_idx in range(table.rowCount()):
#                 selected_row = selected_indexes[0].row()
#                 if row_idx == selected_row:
#                     sidebar_widget = table.cellWidget(selected_row, 0)
#                     if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.selectedrow_icon))
#                 else:
#                     sidebar_widget = table.cellWidget(row_idx, 0)
#                     if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.subtask_icon))
#         else:
#             for row_idx in range(table.rowCount()):
#                 sidebar_widget = table.cellWidget(row_idx, 0)
#                 if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.subtask_icon))
#     except Exception as e:
#         pass
from PyQt5.QtGui import QPainter, QColor

def on_row_selection_changed2(table, module):
    try:
        selected_indexes = table.selectedIndexes()
        selected_row = selected_indexes[0].row() if selected_indexes else -1

        for row_idx in range(table.rowCount()):
            table.removeCellWidget(row_idx, 0)
            table.setItem(row_idx, 0, QTableWidgetItem(""))

        if selected_row != -1:
            sidebar = TRI.SidebarWidget(row_idx=selected_row, selected=True, tree_indicator=True)

            # ✅ Connect tree button click to open_tree() in the correct module
            sidebar.tree_button_clicked.connect(
                lambda row: module.open_tree(table.model().index(row, 0))
            )

            table.setCellWidget(selected_row, 0, sidebar)

    except Exception as e:
        print(f"[ERROR] on_row_selection_changed2 failed: {e}")
