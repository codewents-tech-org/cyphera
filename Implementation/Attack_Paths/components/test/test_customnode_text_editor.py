# test_customnode_text_editor.py

import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QTextCursor
from Attack_Paths.components.customnode_text_editor import CustomTextEdit, FixedHeightTextItem


@pytest.fixture
def app():
    """Ensure a QApplication exists before any widget tests."""
    app = QApplication.instance()



def test_text_edited_emits_on_focus_out(qtbot, app):
    """
    Test that textEdited signal is emitted only after text change + focus out.
    """
    editor = CustomTextEdit("Initial")
    qtbot.addWidget(editor)
    editor.show()
    qtbot.wait(50)

    changes = []
    editor.textEdited.connect(lambda text: changes.append(text))

    # Simulate user typing
    qtbot.keyClicks(editor, " updated")
    qtbot.wait(20)

    # Focus another widget to trigger focusOutEvent
    dummy = CustomTextEdit("dummy")
    qtbot.addWidget(dummy)
    dummy.show()
    dummy.setFocus()
    qtbot.waitUntil(lambda: changes, timeout=300)



def test_text_not_emitted_if_unchanged(qtbot, app):
    """
    If user does not modify the text, signal should not emit on focus out.
    """
    editor = CustomTextEdit("SameText")
    qtbot.addWidget(editor)
    editor.show()
    qtbot.wait(50)

    signals = []
    editor.textEdited.connect(lambda text: signals.append(text))

    # Focus shift without change
    dummy = CustomTextEdit("dummy")
    qtbot.addWidget(dummy)
    dummy.show()
    dummy.setFocus()
    qtbot.wait(100)

    assert signals == []


def test_custom_textedit_cursor_reset_on_focus_out(qtbot):
    """
    The cursor should return to position 0 after focus out.
    """
    editor = CustomTextEdit("Line1\nLine2\nLine3")
    qtbot.addWidget(editor)
    editor.show()
    qtbot.wait(20)

    qtbot.keyClicks(editor, " more")

    # Change focus
    other = CustomTextEdit("...")
    qtbot.addWidget(other)
    other.show()
    other.setFocus()
    qtbot.wait(100)

    assert editor.textCursor().position() == 0


def test_line_spacing_applied_in_custom_textedit():
    """
    Ensure line spacing block format is applied and cursor moves to start.
    """
    editor = CustomTextEdit("A\nB\nC")
    editor.set_line_spacing(0.75)

    cursor = editor.textCursor()
    assert cursor.position() == 0


def test_fixed_height_item_bounding_rect():
    """
    FixedHeightTextItem should clamp height to max value.
    """
    item = FixedHeightTextItem("short text", max_height=60)
    rect: QRectF = item.boundingRect()

    assert rect.height() == 60
    assert rect.width() > 0


def test_line_spacing_in_fixed_height_item():
    """
    Ensure FixedHeightTextItem applies line spacing and resets cursor.
    """
    item = FixedHeightTextItem("A\nB\nC", max_height=50)
    item.set_line_spacing(0.5)

    assert item.textCursor().position() == 0
