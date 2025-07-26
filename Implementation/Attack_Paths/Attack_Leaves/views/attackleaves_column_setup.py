
from PyQt5.QtWidgets import QTableWidgetItem   
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
import models.helper as helper

# Set the column headers
def Setup_Tabel_ColumnHeading(self):
    try:
        self.table.setColumnCount(11)  # Set the number of columns
        header_item = QTableWidgetItem('')  # Empty header for the sidebar (first column)
        header_item.setTextAlignment(Qt.AlignLeft)
        header_item.setSizeHint(QSize(28,28))
        self.table.setHorizontalHeaderItem(0, header_item)
        self.table.horizontalHeader().setFirstSectionMovable(False)
        self.table.setHorizontalHeaderItem(0, header_item)
        for index, header in enumerate(helper.attackleaves_header):
            if header.endswith('.png'):
                header_item = QTableWidgetItem(QIcon(header), '') 
            else:
                header_item = QTableWidgetItem(header)
            
            header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header_item.setSizeHint(QSize(28,28))
            self.table.setHorizontalHeaderItem(index + 1, header_item)
            self.table.horizontalHeader().setFixedHeight(50)

        helper.adjust_table_column('AttackLeaves', self.table)
        self.table.horizontalHeader().setStretchLastSection(True)
    except IndexError as e:
        print(f"IndexError: Failed to set table headers. {e}")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: One or more header icon files were not found. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



