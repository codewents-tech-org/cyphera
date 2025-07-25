from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from typing import Callable, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class GUIProgressReporter:
    def __init__(self, emit_fn):
        self.emit = emit_fn

    def update(self, percent: int, message: str):
        self.emit(percent, message)

class ProgressWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, task_fn: Callable, args: Tuple, kwargs: dict):
        super().__init__()
        self.task_fn = task_fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            reporter = GUIProgressReporter(self.progress.emit)
            self.kwargs["reporter"] = reporter  # Inject into AFR function
            result = self.task_fn(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            logger.exception("Progress task failed.")
            self.error.emit(str(e))


class ProgressDialog(QDialog):
    def __init__(
        self,
        title: str,
        message: str,
        task_fn: Callable,
        task_args: Tuple = (),
        task_kwargs: dict = None,
        on_success: Callable[[Any], None] = None,
        on_failure: Callable[[str], None] = None,
        parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 140)

        self.label = QLabel(title)
        self.label.setFont(QFont('Roboto', 10, QFont.Normal))
        self.label.setAlignment(Qt.AlignCenter)

        self.comment = QLabel(message)
        self.comment.setFont(QFont('Roboto', 8, QFont.Normal))
        self.comment.setAlignment(Qt.AlignCenter)
        self.comment.setStyleSheet("color: gray;")

        self.progress = QProgressBar(self)
        self.progress.setFont(QFont('Roboto', 10, QFont.Normal))
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setFormat("%p%")  # This shows percentage text
        self.progress.setTextVisible(True)  # Ensure it's visible
        self.progress.setStyleSheet("""QProgressBar {text-align: center; font-weight: bold; font-size: 14px;}""")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.comment)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.task_fn = task_fn
        self.task_args = task_args or ()
        self.task_kwargs = task_kwargs or {}
        self.on_success = on_success
        self.on_failure = on_failure

        self.worker = ProgressWorker(self.task_fn, self.task_args, self.task_kwargs)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_done)
        self.worker.error.connect(self.on_error)
        QTimer.singleShot(0, self._start_task)
        
    def _start_task(self):
        """Start worker after dialog is fully shown."""
        self.worker.start()

    def update_progress(self, percent: int, comment: str):
        self.progress.setValue(percent)
        self.comment.setText(comment)

    def on_done(self, result: Any):
        self.accept()
        if self.on_success:
            self.on_success(result)

    def on_error(self, error: str):
        self.reject()
        if self.on_failure:
            self.on_failure(error)
        else:
            QMessageBox.critical(self, "Error", error)
