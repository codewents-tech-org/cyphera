from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QTextEdit, QFormLayout
from PyQt5.QtCore import Qt


class PropertyPanelWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.fields = {}  # Holds label -> widget mapping
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.form = QFormLayout()
        layout.addLayout(self.form)

        for field in self.config:
            label = field.get("label", "")
            field_type = field.get("type", "line")
            readonly = field.get("readonly", False)

            if field_type == "line":
                widget = QLineEdit()
                widget.setReadOnly(readonly)
            elif field_type == "multiline":
                widget = QTextEdit()
                widget.setReadOnly(readonly)
            else:
                widget = QLabel("Unsupported type")

            self.fields[label] = widget
            self.form.addRow(label, widget)

    def populate(self, data):
        for label, value in data.items():
            widget = self.fields.get(label)
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(str(value))
