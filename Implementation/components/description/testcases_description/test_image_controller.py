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

import models.Parameters as P
from components.description.controllers.image import ImageController

class DummyDialog:
    def __init__(self, result, resized):
        self._result = result
        self._resized = resized

    def exec_(self):
        return self._result

    def get_resized_image(self):
        return self._resized

@pytest.fixture(scope="session")
def app():
    return QApplication([])

@pytest.fixture
def text_edit(app):
    return QTextEdit()

@pytest.fixture
def controller(text_edit):
    class ToolbarStub:
        def insertPictureClicked(self, handler):
            pass

    tb = ToolbarStub()
    return ImageController(text_edit, tb)

def test_no_project_path(controller):
    P.project_path = ""
    assert not controller.insert_picture()

def test_user_cancels_file_dialog(controller, monkeypatch, tmp_path):
    P.project_path = str(tmp_path)
    monkeypatch.setattr(QFileDialog, "getOpenFileName",
                        lambda *a, **k: ("", ""))
    assert not controller.insert_picture()

def test_user_cancels_resize_dialog(controller, monkeypatch, tmp_path):
    P.project_path = str(tmp_path)
    monkeypatch.setattr(QFileDialog, "getOpenFileName",
                        lambda *a, **k: ("img.png", ""))
    monkeypatch.setattr(
        "components.description.controllers.image.ResizableImageDialog",
        lambda *a, **k: DummyDialog(QDialog.Rejected, None)
    )
    assert not controller.insert_picture()

def test_invalid_get_resized_image(controller, monkeypatch, tmp_path):
    P.project_path = str(tmp_path)
    monkeypatch.setattr(QFileDialog, "getOpenFileName",
                        lambda *a, **k: ("img.png", ""))
    monkeypatch.setattr(
        "components.description.controllers.image.ResizableImageDialog",
        lambda *a, **k: DummyDialog(QDialog.Accepted, "bad")
    )
    assert not controller.insert_picture()

def test_successful_insert(controller, monkeypatch, text_edit, tmp_path):
    P.project_path = str(tmp_path)

    # create a dummy image file
    image_file = tmp_path / "img.png"
    image_file.write_bytes(b"\x89PNG\r\n")

    # stub file dialog
    monkeypatch.setattr(QFileDialog, "getOpenFileName",
                        lambda *a, **k: (str(image_file), ""))

    # stub resize dialog
    monkeypatch.setattr(
        "components.description.controllers.image.ResizableImageDialog",
        lambda *a, **k: DummyDialog(QDialog.Accepted, (str(image_file), 100, 200))
    )

    # make a QWidget‐based parent so setParent() works
    class ParentWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.updated = False
        def update_toolbar_state(self):
            self.updated = True

    pw = ParentWidget()
    text_edit.setParent(pw)

    result = controller.insert_picture()
    assert result

    # verify that an <img> tag appears in the document HTML
    html = text_edit.toHtml()
    assert "<img" in html

    # toolbar‐state update on parent must have run
    assert pw.updated

def test_exception_during_insert(controller, monkeypatch, tmp_path):
    P.project_path = str(tmp_path)
    monkeypatch.setattr(
        QFileDialog, "getOpenFileName",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail"))
    )
    assert not controller.insert_picture()

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
