#!/usr/bin/env python3
import os
import sys
import pytest
from PyQt5.QtWidgets import QApplication, QTextEdit, QDialog
from PyQt5.QtGui     import QTextTableFormat
from PyQt5.QtCore    import Qt

# Ensure project root on PYTHONPATH
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.description.controllers.table import TableController, TableDialog

class ToolbarStub:
    def __init__(self, accepted):
        self.accepted = accepted
        # create a “signal” stub
        self.insertTableClicked = self.Signal()
        self.insertRowAboveClicked    = self.Signal()
        self.insertRowBelowClicked    = self.Signal()
        self.deleteRowClicked         = self.Signal()
        self.insertColumnLeftClicked  = self.Signal()
        self.insertColumnRightClicked = self.Signal()
        self.deleteColumnClicked      = self.Signal()

    class Signal:
        def __init__(self):
            self._handlers = []
        def connect(self, h):  self._handlers.append(h)
        def emit(self):
            for h in self._handlers:
                h()

@pytest.fixture(scope="session")
def app():
    return QApplication([])

@pytest.fixture(params=[False, True])
def controller(request, text_edit):
    """
    Parameterized over accepted=False (cancel) and accepted=True (OK).
    """
    tb = ToolbarStub(accepted=request.param)
    ctrl = TableController(text_edit, tb)

    # stub the TableDialog.exec_ and get_table_size
    original = TableDialog.__init__
    def fake_init(self, parent=None):
        original(self, parent)
    TableDialog.__init__ = fake_init
    TableDialog.exec_ = lambda self: QDialog.Accepted if request.param else QDialog.Rejected
    TableDialog.get_table_size = lambda self: (2, 3)

    return text_edit, tb, ctrl, request.param

@pytest.fixture
def text_edit(app):
    return QTextEdit()

def unwrap(editor):
    """Helper to extract plain text without trailing empty block."""
    txt = editor.document().toPlainText().rstrip("\u2029")
    return txt

def test_cancel_insert(controller):
    editor, tb, ctrl, accepted = controller
    # when stub returns Rejected, no table should appear
    tb.insertTableClicked.emit()

    if not accepted:
        # cancelled ⇒ document stays empty
        assert unwrap(editor) == ""
    else:
        # accepted ⇒ we inserted a 2×3 table, which is 2*3 cells + blocks
        assert editor.document().blockCount() > 1

def test_add_row_above(controller):
    editor, tb, ctrl, accepted = controller
    if not accepted:
        pytest.skip("dialog cancelled, skip table edits")
    tb.insertTableClicked.emit()
    # place cursor in the first cell
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.NextCell)
    editor.setTextCursor(cursor)

    tb.insertRowAboveClicked.emit()
    # after adding above, row count should be 3
    table = editor.document().findBlockByLineNumber(0).begin().currentTable()
    assert table.rows() == 3

def test_add_row_below(controller):
    editor, tb, ctrl, accepted = controller
    if not accepted:
        pytest.skip("dialog cancelled, skip table edits")
    tb.insertTableClicked.emit()
    # move to first cell
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.NextCell)
    editor.setTextCursor(cursor)

    tb.insertRowBelowClicked.emit()
    table = editor.document().findBlockByLineNumber(0).begin().currentTable()
    assert table.rows() == 3

def test_delete_row(controller):
    editor, tb, ctrl, accepted = controller
    if not accepted:
        pytest.skip("dialog cancelled, skip table edits")
    tb.insertTableClicked.emit()
    # move to first cell
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.NextCell)
    editor.setTextCursor(cursor)

    tb.deleteRowClicked.emit()
    table = editor.document().findBlockByLineNumber(0).begin().currentTable()
    # originally 2 rows, now 1
    assert table.rows() == 1

def test_add_column_left(controller):
    editor, tb, ctrl, accepted = controller
    if not accepted:
        pytest.skip("dialog cancelled, skip table edits")
    tb.insertTableClicked.emit()
    tb.insertColumnLeftClicked.emit()
    table = editor.document().findBlockByLineNumber(0).begin().currentTable()
    assert table.columns() == 4

def test_add_column_right(controller):
    editor, tb, ctrl, accepted = controller
    if not accepted:
        pytest.skip("dialog cancelled, skip table edits")
    tb.insertTableClicked.emit()
    tb.insertColumnRightClicked.emit()
    table = editor.document().findBlockByLineNumber(0).begin().currentTable()
    assert table.columns() == 4

def test_delete_column(controller):
    editor, tb, ctrl, accepted = controller
    if not accepted:
        pytest.skip("dialog cancelled, skip table edits")
    tb.insertTableClicked.emit()
    tb.deleteColumnClicked.emit()
    table = editor.document().findBlockByLineNumber(0).begin().currentTable()
    assert table.columns() == 2

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
