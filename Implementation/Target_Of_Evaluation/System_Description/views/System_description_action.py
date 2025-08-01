# File: System_description_action.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore    import pyqtSignal

from components.description.editor import DescriptionEditor
from components.description.model  import DescriptionModel  # ORM handler class
from controllers.database_tables.target_of_evaluation_tables import SystemDescription

class SystemDescriptionWidget(QWidget):
    """
    UI widget for 'System Description', backed by SQLAlchemy ORM + schema_manager.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # ORM-based Model using existing SQLAlchemy table
        self.description_model = DescriptionModel(
            model_class=SystemDescription,
            id_column="toe_id",           # <-- Your PK column
            content_column="content"      # <-- Your HTML/content column
        )

        # Editor
        self.description_editor = DescriptionEditor("System Description", parent=self)

        # Save binding
        self.description_editor.content_changed.connect(
            lambda html: self.description_model.save(html, record_id=1)
        )

        # Refresh binding
        if hasattr(self.description_editor.toolbar, "refreshClicked"):
            self.description_editor.toolbar.refreshClicked.connect(self.load_data)

        layout.addWidget(self.description_editor)

    def load_data(self, record_id: int = 1):
        html = self.description_model.load(record_id=record_id)
        print("\n[DEBUG] Loaded HTML content:\n", html)
        self.description_editor.load_content(html)
