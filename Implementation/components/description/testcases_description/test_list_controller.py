# test_list_controller.py
import pytest
from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui     import QTextCursor
from PyQt5.QtCore    import Qt
#!/usr/bin/env python3
import os
import sys
import pytest

from PyQt5.QtWidgets import (
    QApplication, QTextEdit, QFileDialog, QDialog, QWidget
)
from PyQt5.QtCore    import Qt

# Ensure project root on PYTHONPATH
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.description.controllers.lists import ListController

class SignalStub:
    def __init__(self):
        self._handlers = []
    def connect(self, h):
        self._handlers.append(h)
    def emit(self):
        for h in self._handlers:
            h()

class ToolbarStub:
    def __init__(self):
        self.bulletsClicked   = SignalStub()
        self.numberingClicked = SignalStub()

@pytest.fixture(scope="session")
def app():
    return QApplication([])

@pytest.fixture
def editor(app):
    return QTextEdit()

@pytest.fixture
def controller(editor):
    tb = ToolbarStub()
    ctrl = ListController(editor, tb)
    return editor, tb, ctrl

def set_text(editor, text):
    editor.clear()
    editor.setPlainText(text)
    cursor = editor.textCursor()
    cursor.select(QTextCursor.Document)
    editor.setTextCursor(cursor)

def unwrap(editor):
    # Return the plain text with list‐markers stripped if any
    # PyQt keeps the unicode bullet and numbering in the text stream.
    return editor.toPlainText().replace("• ", "").replace("1. ", "")

# TC1
def test_tc1_single_plain_bullets(controller):
    editor, tb, _ = controller
    set_text(editor, "Line one")
    tb.bulletsClicked.emit()
    assert editor.toPlainText().startswith("• Line one")

# TC2
def test_tc2_single_bulleted_unwrap(controller):
    editor, tb, _ = controller
    set_text(editor, "Line one")
    tb.bulletsClicked.emit()   # now bulleted
    tb.bulletsClicked.emit()   # toggle off
    assert editor.toPlainText() == "Line one"

# TC3
def test_tc3_single_plain_numbering(controller):
    editor, tb, _ = controller
    set_text(editor, "Line one")
    tb.numberingClicked.emit()
    assert editor.toPlainText().startswith("1. Line one")

# TC4
def test_tc4_single_numbered_unwrap(controller):
    editor, tb, _ = controller
    set_text(editor, "Line one")
    tb.numberingClicked.emit()
    tb.numberingClicked.emit()
    assert editor.toPlainText() == "Line one"

# TC5
def test_tc5_multi_plain_bullets(controller):
    editor, tb, _ = controller
    set_text(editor, "A\nB\nC")
    tb.bulletsClicked.emit()
    lines = editor.toPlainText().splitlines()
    assert all(line.startswith("• ") for line in lines)

# TC6
def test_tc6_multi_bullets_unwrap(controller):
    editor, tb, _ = controller
    set_text(editor, "A\nB\nC")
    tb.bulletsClicked.emit()
    tb.bulletsClicked.emit()
    assert unwrap(editor) == "A\nB\nC"

# TC7
def test_tc7_multi_plain_numbering(controller):
    editor, tb, _ = controller
    set_text(editor, "A\nB\nC")
    tb.numberingClicked.emit()
    lines = editor.toPlainText().splitlines()
    assert lines[0].startswith("1. ") and lines[1].startswith("2. ") and lines[2].startswith("3. ")

# TC8
def test_tc8_multi_numbering_unwrap(controller):
    editor, tb, _ = controller
    set_text(editor, "A\nB\nC")
    tb.numberingClicked.emit()
    tb.numberingClicked.emit()
    assert unwrap(editor) == "A\nB\nC"

# TC9
def test_tc9_mixed_plain_bullets(controller):
    editor, tb, _ = controller
    # simulate mixed: bullet on first line only
    editor.clear()
    cursor = editor.textCursor()
    cursor.insertText("A")
    tb.bulletsClicked.emit()
    cursor.insertBlock()
    cursor.insertText("B")
    editor.setTextCursor(cursor)
    # now toggle bullets over both lines
    cursor.select(QTextCursor.Document)
    editor.setTextCursor(cursor)
    tb.bulletsClicked.emit()
    lines = editor.toPlainText().splitlines()
    assert all(l.startswith("• ") for l in lines)

# TC10
def test_tc10_mixed_plain_numbering(controller):
    editor, tb, _ = controller
    editor.clear()
    cursor = editor.textCursor()
    cursor.insertText("A")
    tb.numberingClicked.emit()
    cursor.insertBlock()
    cursor.insertText("B")
    # apply numbering to both
    cursor = editor.textCursor()
    cursor.select(QTextCursor.Document)
    editor.setTextCursor(cursor)
    tb.numberingClicked.emit()
    lines = editor.toPlainText().splitlines()
    assert lines[0].startswith("1. ") and lines[1].startswith("2. ")

# TC11
def test_tc11_caret_in_block(controller):
    editor, tb, _ = controller
    set_text(editor, "Para1\nPara2")
    # place caret in second line only
    cursor = editor.textCursor()
    cursor.clearSelection()
    cursor.movePosition(QTextCursor.NextBlock)
    editor.setTextCursor(cursor)
    tb.bulletsClicked.emit()
    blocks = editor.toPlainText().splitlines()
    assert blocks[1].startswith("• ") and not blocks[0].startswith("• ")

# TC12
def test_tc12_partial_selection(controller):
    editor, tb, _ = controller
    set_text(editor, "Para1\nPara2\nPara3")
    # select Para2–Para3
    cursor = editor.textCursor()
    cursor.setPosition(editor.document().findBlockByLineNumber(1).position())
    cursor.setPosition(editor.document().findBlockByLineNumber(3).position(), QTextCursor.KeepAnchor)
    editor.setTextCursor(cursor)
    tb.numberingClicked.emit()
    lines = editor.toPlainText().splitlines()
    assert lines[1].startswith("1. ") and lines[2].startswith("2. ") and not lines[0].startswith("1. ")

# TC13
def test_tc13_empty_document(controller):
    editor, tb, _ = controller
    editor.clear()
    tb.bulletsClicked.emit()  # should not raise
    assert editor.toPlainText() == ""

# TC14
def test_tc14_invalid_style(monkeypatch, controller):
    # Force _toggle_list to receive bad style and just no-op
    editor, tb, ctrl = controller
    monkeypatch.setattr(ctrl, "_toggle_list", lambda style: (_ for _ in ()).throw(ValueError("bad")))
    editor.setPlainText("X")
    # should catch internally and not propagate
    tb.bulletsClicked.emit()
    assert editor.toPlainText() == "X"

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))

