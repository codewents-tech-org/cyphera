from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt



from PyQt5.QtCore import QObject, QEvent

class MultiSelectComboSelector(QComboBox):
    def __init__(self, items, parent=None, placeholder="Select"):
        super().__init__(parent)
        self.setModel(QStandardItemModel(self))
        for text in items:
            item = QStandardItem(text)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            self.model().appendRow(item)

        self.view().clicked.connect(self.handle_item_clicked) 
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.placeholder = placeholder
        self.lineEdit().setPlaceholderText(self.placeholder)
        self.lineEdit().setText("")
        self.model().dataChanged.connect(self.update_text)

        # Install event filter to catch line edit click/focus
        self.lineEdit().installEventFilter(self)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        event.ignore()  # Prevent any change on wheel/scroll
    def eventFilter(self, obj, event):
        if obj == self.lineEdit():
            if event.type() == QEvent.MouseButtonPress:
                self.showPopup()
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        self.showPopup()  # Always open the dropdown on mouse click
        super().mousePressEvent(event)

    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.update_text()

    def update_text(self, *args):
        self.selected = []
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState() == Qt.Checked:
                self.selected.append(item.text())
        if self.selected:
            self.lineEdit().setText(", ".join(self.selected))
        else:
            self.lineEdit().setText("")

    def selected_items(self):
        return getattr(self, "selected", [])

    def set_selected_items(self, items):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(Qt.Checked if item.text() in items else Qt.Unchecked)
        self.update_text()

    def handle_item_clicked(self, index):
        item = self.model().itemFromIndex(index)
        # Toggle check state only on click (not drag, not hover)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.update_text()
