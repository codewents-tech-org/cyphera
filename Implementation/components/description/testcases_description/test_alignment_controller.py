#!/usr/bin/env python3
import os
import sys
import logging
import pytest

from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui     import QTextCursor, QTextTableFormat, QTextTable
from PyQt5.QtCore    import Qt

# Ensure project root is on PYTHONPATH
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.description.controllers.alignment import AlignmentController

class SignalStub:
    """Mimics a Qt signal with connect()."""
    def __init__(self):
        self._handlers = []
    def connect(self, handler):
        self._handlers.append(handler)

@pytest.fixture(scope="session")
def app():
    return QApplication([])

@pytest.fixture
def text_edit(app):
    return QTextEdit()

@pytest.fixture
def controller(text_edit):
    # Create a toolbar stub whose alignChanged signal can connect
    class DummyToolbar:
        def __init__(self):
            self.alignChanged = SignalStub()

    toolbar = DummyToolbar()
    return AlignmentController(text_edit, toolbar)

def select_plain_text(text_edit, text):
    """Helper to populate and select plain text."""
    text_edit.clear()
    text_edit.setPlainText(text)
    cursor = text_edit.textCursor()
    cursor.select(QTextCursor.Document)
    text_edit.setTextCursor(cursor)

def test_plain_text_single(controller, text_edit):
    select_plain_text(text_edit, "Line one")
    assert controller.change_alignment(Qt.AlignCenter)

def test_plain_text_multiple(controller, text_edit):
    select_plain_text(text_edit, "One\nTwo\nThree")
    assert controller.change_alignment(Qt.AlignRight)

def test_whole_table_alignment(controller, text_edit):
    cursor = text_edit.textCursor()
    fmt = QTextTableFormat()
    cursor.insertTable(2, 2, fmt)
    cursor = text_edit.textCursor()
    cursor.select(QTextCursor.Document)
    text_edit.setTextCursor(cursor)
    assert controller.change_alignment(Qt.AlignJustify)

def test_partial_table_cells(controller, text_edit):
    cursor = text_edit.textCursor()
    fmt = QTextTableFormat()
    table = cursor.insertTable(3, 3, fmt)
    cell_cursor = table.cellAt(1, 1).firstCursorPosition()
    text_edit.setTextCursor(cell_cursor)
    assert controller.change_alignment(Qt.AlignLeft)

def test_no_selection(controller, text_edit):
    text_edit.clear()
    text_edit.setTextCursor(text_edit.textCursor())
    assert controller.change_alignment(Qt.AlignLeft)

def test_invalid_alignment(controller, text_edit, caplog):
    caplog.set_level(logging.ERROR)
    select_plain_text(text_edit, "Text")
    assert not controller.change_alignment(9999)

def test_exception_in_processing(controller, text_edit, monkeypatch, caplog):
    select_plain_text(text_edit, "Text")
    monkeypatch.setattr(
        QTextCursor,
        "mergeBlockFormat",
        lambda self, fmt: (_ for _ in ()).throw(Exception("fail"))
    )
    caplog.set_level(logging.ERROR)
    assert not controller.change_alignment(Qt.AlignLeft)

def test_mixed_text_and_table(controller, text_edit):
    text_edit.clear()
    text_edit.setPlainText("Para1\nPara2")
    cursor = text_edit.textCursor()
    cursor.movePosition(QTextCursor.End)
    cursor.insertTable(2, 2, QTextTableFormat())
    cursor = text_edit.textCursor()
    cursor.select(QTextCursor.Document)
    text_edit.setTextCursor(cursor)
    assert controller.change_alignment(Qt.AlignCenter)

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
