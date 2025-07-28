from PyQt5.QtWidgets import QTableWidget, QSizePolicy, QVBoxLayout, QStyledItemDelegate, QLineEdit
from PyQt5.QtCore import Qt
import styles.table_style as table_style
import styles.action_background_panel_style as action_panel_style
import logging

logger = logging.getLogger(__name__)

# Custom delegate for single-line in-cell editing using QLineEdit.
class SingleLineDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        """Creates a single-line editor for table cells."""
        editor = QLineEdit(parent)
        editor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Ensures proper text alignment
        editor.setStyleSheet("""
            border: 1px solid #009D9C;
            background-color: white;
            color: black;
            padding-left: 5px;  /* Ensures proper spacing inside */
        """)
        return editor

    def setEditorData(self, editor, index):
        """Sets initial value in the editor."""
        value = index.model().data(index, Qt.EditRole)
        editor.setText(value if value else "")
        editor.selectAll()

    def setModelData(self, editor, model, index):
        """Updates the table with edited value."""
        model.setData(index, editor.text(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        """Fixes editor sizing so all text remains visible while typing."""
        editor.setGeometry(option.rect.adjusted(1, 1, -1, -1))  # Adjusts margins to prevent text cutoff
        editor.setFixedHeight(option.rect.height())  # Ensures editor height matches cell height

def create_table_panel(self):
    logger.info("Table panel creation started.")
    
    # Create the table widget
    self.table = QTableWidget()
    self.table.setSelectionBehavior(QTableWidget.SelectRows)
    self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    # Apply table styles
    self.table.setStyleSheet(table_style.table_style)
    self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 

    # Install the custom delegate for single-line editing
    self.table.setItemDelegate(SingleLineDelegate(self.table))

    # Connect table selection event
    self.table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)

    # Create table layout with margins
    self.table_layout = QVBoxLayout()
    self.table_layout.setContentsMargins(10, 10, 10, 10)  # Add 10px margin on all sides
    self.table_layout.addWidget(self.table)

    logger.info("Table panel creation completed.")
