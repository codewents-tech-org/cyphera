

from PyQt5.QtGui import QIcon, QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt
import models.Parameters as P


def on_row_selection_changed(table):
    try:
        selected_indexes = table.selectedIndexes()
        if selected_indexes:
            for row_idx in range(table.rowCount()):
                selected_row = selected_indexes[0].row()
                if row_idx == selected_row:
                    sidebar_widget = table.cellWidget(selected_row, 0)
                    if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.selectedrow_icon))
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

def on_row_selection_changed2(table):
    try:
        selected_indexes = table.selectedIndexes()
        if selected_indexes:
            for row_idx in range(table.rowCount()):
                selected_row = selected_indexes[0].row()
                if row_idx == selected_row:
                    sidebar_widget = table.cellWidget(selected_row, 0)
                    if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.selectedrow_icon))
                    pixmap_subtask = QPixmap(P.subtask_icon)
                    pixmap_subtask = pixmap_subtask.scaled(
                            sidebar_widget.tree_button.size(), 
                            Qt.KeepAspectRatio, 
                            Qt.SmoothTransformation
                        )
                        
                    color_filter = QPainter()
                    color_filter.begin(pixmap_subtask)
                    color_filter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                    color_filter.fillRect(pixmap_subtask.rect(), QColor("#009D9C"))
                    color_filter.end()
                        
                    sidebar_widget.tree_button.setIcon(QIcon(pixmap_subtask))
                        
                    #     # Apply color filter to edit_icon for round_button3
                    # pixmap_edit = QPixmap(P.edit_icon)
                    # pixmap_edit = pixmap_edit.scaled(
                    #     sidebar_widget.round_button3.size(), 
                    #         Qt.KeepAspectRatio, 
                    #         Qt.SmoothTransformation
                    #     )
                        
                    # color_filter.begin(pixmap_edit)
                    # color_filter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                    # color_filter.fillRect(pixmap_edit.rect(), QColor("#009D9C"))
                    # color_filter.end()
                        
                    # sidebar_widget.round_button3.setIcon(QIcon(pixmap_edit))
                    
                else:
                    sidebar_widget = table.cellWidget(row_idx, 0)
                    if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.deselectedrow_icon))
                    sidebar_widget.tree_button.setIcon(QIcon(P.subtask_icon))
                    # sidebar_widget.round_button3.setIcon(QIcon(P.deselectedrow_icon))
        else:
            for row_idx in range(table.rowCount()):
                sidebar_widget = table.cellWidget(row_idx, 0)
                if sidebar_widget: sidebar_widget.round_button.setIcon(QIcon(P.deselectedrow_icon))
                sidebar_widget.tree_button.setIcon(QIcon(P.subtask_icon))
                # sidebar_widget.round_button3.setIcon(QIcon(P.deselectedrow_icon))
    except Exception as e:
        pass
