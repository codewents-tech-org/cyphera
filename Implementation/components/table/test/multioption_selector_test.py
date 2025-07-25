

import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QEvent, QPoint,QPointF
from PyQt5.QtGui import QWheelEvent
from components.table.multioption_selector import (
    MultiSelectComboBox, TSMultiSelectComboBox, ReadOnlyMultiSelectComboBox,
    CustomComboBox, CustomComboBoxLeave, NoWheelComboBox
)
import sys

app = QApplication(sys.argv)


# UT001: get_display_text
def test_get_display_text_valid():
    combo = MultiSelectComboBox(["Item 1::desc", "Item 2"])
    combo.selected_items_list = ["Item 1::desc", "Item 2"]
    assert combo.get_display_text() == ["Item 1", "Item 2"]

# UT003: update_text
def test_update_text_sets_current_text():
    combo = MultiSelectComboBox(["A", "B"])
    combo.selected_items_list = ["A", "B"]
    combo.update_text()
    assert combo.currentText() == "A, B"

# UT004: selected_items
def test_selected_items_returns_list():
    combo = MultiSelectComboBox(["A"])
    combo.selected_items_list = ["A"]
    assert combo.selected_items() == ["A"]

# UT005: wheelEvent
def test_wheel_event_ignored():
    combo = MultiSelectComboBox(["X"])
    event = QWheelEvent(
        QPointF(0, 0), QPointF(0, 0),
        QPoint(0, 0), QPoint(0, 120),
        Qt.NoButton, Qt.NoModifier,
        Qt.ScrollUpdate, False
    )
    try:
        combo.wheelEvent(event)
        assert True
    except Exception:
        assert False

# UT006: additem
def test_additem_updates_items():
    combo = MultiSelectComboBox([])
    combo.additem(["A", "B"])
    assert combo.items == ["A", "B"]

# UT007: update_items
def test_update_items_refresh_combo():
    combo = MultiSelectComboBox(["A", "B"])
    combo.selected_items_list = ["A"]
    combo.update_items()
    assert "A" in combo.currentText()

# UT008: select_row
def test_select_row_toggle():
    combo = MultiSelectComboBox(["A", "B"])
    combo.select_row("A")
    assert "A" in combo.selected_items_list
    combo.select_row("A")
    assert "A" not in combo.selected_items_list

# UT010: toggle_item
def test_toggle_item_logic():
    combo = MultiSelectComboBox(["A", "B"])
    combo.toggle_item("A", True)
    assert "A" in combo.selected_items_list
    combo.toggle_item("A", False)
    assert "A" not in combo.selected_items_list

# UT011: set_text
def test_set_text_comma_input():
    combo = MultiSelectComboBox(["A", "B", "C"])
    combo.set_text("A, B")
    assert combo.selected_items_list == ["A", "B"]

# UT013: TSMultiSelectComboBox - set_text
def test_tsmultiselect_set_text():
    combo = TSMultiSelectComboBox(["A", "B", "C"])
    combo.set_text("B, C")
    assert combo.selected_items_list == ["B", "C"]

# UT015: ReadOnlyMultiSelectComboBox - set_text
def test_readonly_set_text():
    combo = ReadOnlyMultiSelectComboBox(["X", "Y"])
    combo.set_text("X, Y")
    assert combo.selected_items_list == ["X", "Y"]

# CustomComboBox - add_items
def test_custom_add_items():
    combo = CustomComboBox([])
    combo.add_items(["Dog", "Cat"])
    assert combo.items == ["Dog", "Cat"]

#  CustomComboBox - set_text trims
def test_custom_set_text_trims_first_word():
    combo = CustomComboBox(["Hello", "World"])
    combo.set_text("Hello World")
    assert combo.currentText() == "Hello"

# CustomComboBoxLeave - set_text auto trim
def test_custom_leave_text_trim():
    combo = CustomComboBoxLeave(["This", "Text"])
    combo.set_text("This Text")
    assert combo.currentText() == "This"

#  NoWheelComboBox - wheelEvent
def test_nowheel_combo_ignore_scroll():
    combo = NoWheelComboBox()
    event = QWheelEvent(
        QPointF(0, 0), QPointF(0, 0),
        QPoint(0, 0), QPoint(0, 120),
        Qt.NoButton, Qt.NoModifier,
        Qt.ScrollUpdate, False
    )
    try:
        combo.wheelEvent(event)
        assert True
    except Exception:
        assert False


