
import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QTextEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt
from components.propertypanel import property_input_components
import sys

@pytest.fixture(scope="session", autouse=True)
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def dummy_parent():
    widget = QWidget()
    layout = QVBoxLayout(widget)
    return widget, layout

def test_create_line_input(dummy_parent):
    widget, layout = dummy_parent
    controls = []
    factory = property_input_components.PropertyInputFactory()
    result = factory.create_common_property_input("Name", "line", layout, controls)

    assert isinstance(result, QLineEdit)
    assert controls[-1][1] == result

def test_create_multiline_input(dummy_parent):
    widget, layout = dummy_parent
    controls = []
    factory = property_input_components.PropertyInputFactory()
    result = factory.create_common_property_input("Desc", "multiline", layout, controls)

    assert isinstance(result, QTextEdit)
    assert controls[-1][1] == result

def test_create_multiselect_input(dummy_parent):
    widget, layout = dummy_parent
    controls = []
    factory = property_input_components.PropertyInputFactory()
    result = factory.create_common_property_input("Options", "multiselect", layout, controls, items=["A", "B"])

    assert result is not None
    assert hasattr(result, "set_text")

def test_create_multiselect1_input(dummy_parent):
    widget, layout = dummy_parent
    controls = []
    factory = property_input_components.PropertyInputFactory()
    result = factory.create_common_property_input("Options", "multiselect1", layout, controls, items=["A", "B"])

    assert result is not None
    assert hasattr(result, "set_text")

def test_connect_signal_lineedit(dummy_parent):
    widget, layout = dummy_parent
    controls = []
    mock_signal = MagicMock()
    factory = property_input_components.PropertyInputFactory()
    result = factory.create_common_property_input("Name", "line", layout, controls)


def test_unsupported_input_type(dummy_parent):
    widget, layout = dummy_parent
    controls = []
    factory = property_input_components.PropertyInputFactory()
    result = factory.create_common_property_input("Unsupported", "dropdown", layout, controls)

    assert result is None

def test_exception_handling_in_input(dummy_parent):
    widget, layout = dummy_parent
    controls = []
    with patch("components.propertypanel.property_input_components.QLabel", side_effect=Exception("Error")):
        factory = property_input_components.PropertyInputFactory()
        result = factory.create_common_property_input("Name", "line", layout, controls)

        assert result is None

def test_create_save_button_default(dummy_parent):
    widget, layout = dummy_parent
    button = property_input_components.PropertyInputFactory.create_save_button(widget, layout, "")
    assert isinstance(button, QPushButton)
    assert button.text() == "Save"

def test_create_save_button_custom_size(dummy_parent):
    widget, layout = dummy_parent
    button = property_input_components.PropertyInputFactory.create_save_button(widget, layout, "", width=300, height=60)
    assert button.width() == 300
    assert button.height() == 60

def test_create_save_button_exception():
    with patch("components.propertypanel.property_input_components.QPushButton", side_effect=[Exception("Fail"), QPushButton("Error")]):
        dummy = MagicMock()
        layout = MagicMock()
        result = property_input_components.PropertyInputFactory.create_save_button(dummy, layout, "")
        assert isinstance(result, QPushButton)
        assert result.text() == "Error"

def test_save_button_signal_emits_data(qtbot):
    from PyQt5.QtWidgets import QLabel, QLineEdit, QTextEdit, QWidget, QVBoxLayout
    from components.propertypanel import property_input_components

    class MockMultiSelect:
        def get_selected_items(self): return ["Python", "PyQt"]

    controls = [
        [QLabel("Name"), QLineEdit()],
        [QLabel("Bio"), QTextEdit()],
        [QLabel("Skills"), MockMultiSelect()]
    ]
    controls[0][1].setText("John Doe")
    controls[1][1].setPlainText("Software engineer")

    signal = MagicMock()
    widget = QWidget()
    layout = QVBoxLayout(widget)
    btn = property_input_components.PropertyInputFactory.create_save_button(widget, layout, "", controls, signal)
    
    qtbot.addWidget(widget)
    qtbot.mouseClick(btn, Qt.LeftButton)

    signal.emit.assert_called_once()
    payload = signal.emit.call_args[0][0]
    assert payload["data"] == {
        "Name": "John Doe",
        "Bio": "Software engineer",
        "Skills": ["Python", "PyQt"]
    }
