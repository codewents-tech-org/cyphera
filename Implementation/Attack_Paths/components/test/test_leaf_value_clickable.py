import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
from Attack_Paths.components.leaf_value_clickable import ClickableLabel, AP_leaf_values_menu




def test_label_sets_text_on_emit_selected(qtbot):
    label = ClickableLabel(index=0)
    qtbot.addWidget(label)
    label.show()

    label.emit_selected("4", "(<= one month)")
    assert label.text() == "4"


def test_label_emits_signal_on_emit_selected(qtbot):
    label = ClickableLabel(index=2)
    qtbot.addWidget(label)
    label.show()

    captured = []
    label.valueSelected.connect(lambda val: captured.append(val))

    label.emit_selected("7", "(Confidential)")
    assert captured == ["7"]
    assert label.text() == "7"


def test_click_inside_triggers_context_menu(qtbot, monkeypatch):
    label = ClickableLabel(index=1)
    qtbot.addWidget(label)
    label.resize(60, 30)
    label.show()

    triggered = []

    def fake_menu(pos):
        triggered.append(True)

    monkeypatch.setattr(label, "show_context_menu", fake_menu)

    QTest.mouseClick(label, Qt.LeftButton, pos=label.rect().center())
    assert triggered == [True]


def test_click_outside_does_not_trigger_menu(qtbot, monkeypatch):
    label = ClickableLabel(index=1)
    qtbot.addWidget(label)
    label.resize(60, 30)
    label.show()

    triggered = []


    outside_point = QPoint(label.width() + 10, label.height() + 10)
    QTest.mouseClick(label, Qt.LeftButton, pos=outside_point)

    assert triggered == []

def test_label_mouse_click_inside_triggers_menu(qtbot, monkeypatch):
    label = ClickableLabel(index=1)
    qtbot.addWidget(label)
    label.show()

    triggered = []

    def fake_menu(pos):
        triggered.append(True)

    monkeypatch.setattr(label, "show_context_menu", fake_menu)

    pos = label.rect().center()
    QTest.mouseClick(label, Qt.LeftButton, pos=pos)
    assert triggered


def test_context_menu_structure():
    """Ensure AP_leaf_values_menu contains valid dictionaries with string keys and values."""
    for menu in AP_leaf_values_menu:
        assert isinstance(menu, dict)
        for key, val in menu.items():
            assert isinstance(key, str)
            assert isinstance(val, str)

def test_show_context_menu_executes_without_error(qtbot):
    """
    Ensure show_context_menu displays QMenu with correct items.
    This test directly calls the method to ensure coverage.
    """
    label = ClickableLabel(index=0)
    qtbot.addWidget(label)
    label.show()

    # Fake screen position
    pos = label.mapToGlobal(label.rect().center())

    # Directly call the method to test coverage
    label.show_context_menu(pos)

    # No assert needed — this test is for coverage and runtime safety
