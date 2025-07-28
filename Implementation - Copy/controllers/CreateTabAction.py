
import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel


class TabHeader(QWidget):
    def __init__(self, title, close_callback):
        super().__init__()
        self.close_callback = close_callback
        self.init_ui(title)

    def init_ui(self, title):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Label for the tab title
        self.title_label = QLabel(title)
        layout.addWidget(self.title_label)

        # Close button
        self.close_button = QPushButton('x')
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.handle_close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def handle_close(self):
        if self.close_callback:
            self.close_callback()

