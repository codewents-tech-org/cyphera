#!/usr/bin/env python3
import os
import sys
import logging
import pytest
from PyQt5.QtWidgets import QApplication, QWidget

# — Ensure your project root is on PYTHONPATH —
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.description.toolbar import DescriptionToolbar

@pytest.fixture(scope="session")
def app():
    """QApplication fixture for widget tests."""
    return QApplication([])

@pytest.fixture
def toolbar(app):
    buttons = {
        "Save": ("save.png", "Save"),
        "Refresh": ("refresh.png", "Refresh"),
        "Bold": ("bold.png", "Bold"),
        "Font Color": ("color.png", "Color"),
        "Highlight": ("highlight.png", "Highlight"),
        "Italic": ("italic.png", "Italic"),
        "Insert Picture": ("pic.png", "Pic"),
        "Bullets": ("bullets.png", "Bullets"),
        "Numbering": ("num.png", "Num"),
        "Left Align": ("left.png", "Left"),
        "Center Align": ("center.png", "Center"),
        "Right Align": ("right.png", "Right"),
        "Justify": ("justify.png", "Justify"),
        "Insert Table": ("table.png", "Table"),
        "Insert Column Left": ("col_left.png", "ColLeft"),
        "Insert Column Right": ("col_right.png", "ColRight"),
        "Insert Row Above": ("row_above.png", "RowAbove"),
        "Insert Row Below": ("row_below.png", "RowBelow"),
        "Delete Row": ("del_row.png", "DelRow"),
        "Delete Column": ("del_col.png", "DelCol"),
    }
    return DescriptionToolbar("Test", buttons)

def test_toolbar_initialization(toolbar):
    # TC1_Init
    assert "bold_button" in toolbar.refs
    assert "font_size_combo" in toolbar.refs
    assert "align_button" in toolbar.refs

def test_apply_all_true(toolbar):
    # TC2_Apply_AllTrue
    toolbar.apply_text_format_states(True, True, True, True, 14, "#123456", "Right")

def test_apply_all_false(toolbar):
    # TC3_Apply_AllFalse
    toolbar.apply_text_format_states(False, False, False, False, 10, "#00FF00", "Left")

def test_apply_invalid_size(toolbar, caplog):
    # TC4_InvalidFontSize
    caplog.set_level(logging.ERROR)
    toolbar.apply_text_format_states(True, True, True, True, "abc", "#000", "Left")
    assert "apply_text_format_states failed" in caplog.text

def test_apply_invalid_alignment(toolbar):
    # TC5_InvalidAlignment
    toolbar.apply_text_format_states(False, False, False, False, 12, "#000000", "Diagonal")

def test_missing_refs(toolbar):
    # TC6_MissingRefs
    # remove one required ref and ensure no KeyError
    toolbar.refs.pop("bold_button", None)
    toolbar.apply_text_format_states(True, True, True, True, 12, "#000", "Left")

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
