#!/usr/bin/env python3
import os, sys, pytest
from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui     import QTextCursor, QTextImageFormat
from PyQt5.QtCore    import Qt

# Ensure project root is on PYTHONPATH
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.description.controllers.formatting import FormattingController

@pytest.fixture(scope="session")
def app():
    return QApplication([])

@pytest.fixture
def text_edit(app):
    return QTextEdit()

@pytest.fixture
def controller(text_edit):
    class ToolbarStub:
        def __init__(self):
            for sig in ("boldClicked","italicClicked","underlineClicked",
                        "fontSizeChanged","fontStyleChanged",
                        "fontColorClicked","highlightClicked"):
                setattr(self, sig, self.Signal())
            self.state_args = None
        class Signal:
            def __init__(self): self.handlers=[]
            def connect(self,h): self.handlers.append(h)
            def emit(self,v=None):
                for h in self.handlers:
                    if v is None: h()
                    else:        h(v)
        def apply_text_format_states(self, *args):
            self.state_args = args

    tb = ToolbarStub()
    ctrl = FormattingController(text_edit, tb)
    return ctrl, tb

def select_document(text_edit, text):
    text_edit.setPlainText(text)
    c = text_edit.textCursor(); c.select(QTextCursor.Document)
    text_edit.setTextCursor(c)

def test_toggle_bold_selection(controller, text_edit):
    ctrl, tb = controller
    select_document(text_edit, "Hello")
    tb.boldClicked.emit()
    assert tb.state_args[0] is True

def test_toggle_bold_caret(controller, text_edit):
    ctrl, tb = controller
    text_edit.setPlainText("Hello")
    # caret only (no selection)
    tb.boldClicked.emit()
    assert tb.state_args[0] is True

def test_italic_and_underline(controller, text_edit):
    ctrl, tb = controller
    select_document(text_edit, "X Y")
    tb.italicClicked.emit(); assert tb.state_args[1] is True
    tb.underlineClicked.emit(); assert tb.state_args[2] is True

def test_font_size_and_style(controller, text_edit):
    ctrl, tb = controller
    select_document(text_edit, "Size")
    tb.fontSizeChanged.emit(14); assert tb.state_args[4]==14
    tb.fontStyleChanged.emit("Heading")
    assert tb.state_args[0] is True and tb.state_args[4]==16

def test_select_font_color_cancel(controller, text_edit, monkeypatch):
    ctrl, tb = controller
    import PyQt5.QtWidgets as qw
    monkeypatch.setattr(qw.QColorDialog, "getColor", lambda *a,**k: qw.QColor())
    select_document(text_edit, "Color")
    tb.fontColorClicked.emit()
    assert tb.state_args is None

def test_select_font_color_apply(controller, text_edit, monkeypatch):
    ctrl, tb = controller
    import PyQt5.QtGui as qg
    class FakeColor(qg.QColor):
        def __init__(self): super().__init__("#ff0000")
    import PyQt5.QtWidgets as qw
    monkeypatch.setattr(qw.QColorDialog, "getColor", lambda *a,**k: FakeColor())
    select_document(text_edit, "Color")
    tb.fontColorClicked.emit()
    assert tb.state_args[5] == "#ff0000"

def test_highlight_and_skip_image(controller, text_edit):
    ctrl, tb = controller
    select_document(text_edit, "HL")
    tb.highlightClicked.emit()
    assert tb.state_args[3] is True
    # insert inline image then bold
    cursor = text_edit.textCursor()
    img = QTextImageFormat(); img.setName("x.png")
    cursor.insertImage(img)
    tb.boldClicked.emit()
    assert tb.state_args is not None

def test_error_in_apply_format(controller, text_edit, monkeypatch):
    ctrl, tb = controller
    monkeypatch.setattr(
        QTextCursor, 
        "mergeCharFormat", 
        lambda self, f: (_ for _ in ()).throw(Exception("fail"))
    )
    select_document(text_edit, "Err")
    tb.boldClicked.emit()
    # no exception should bubble
    assert True

def test_update_toolbar_state(controller, text_edit):
    ctrl, tb = controller
    select_document(text_edit, "Upd")
    ctrl.update_toolbar_state()
    assert isinstance(tb.state_args, tuple)

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
