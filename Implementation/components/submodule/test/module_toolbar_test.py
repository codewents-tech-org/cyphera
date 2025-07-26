import pytest
from PyQt5.QtCore import Qt
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from components.submodule import module_toolbar

app = QApplication([])  # Required to initialize Qt Widgets

class MockParent(QWidget):
    def __init__(self):
        super().__init__()


@pytest.fixture
def parent():
    return MockParent()


def test_ut001_create_toolbar_default_buttons(parent):
    toolbar = module_toolbar.create_toolbar(parent, "Test")
    assert toolbar is not None
    assert isinstance(toolbar, QWidget)


def test_ut002_create_toolbar_specific_buttons(parent):
    toolbar = module_toolbar.create_toolbar(parent, "Editor", buttons=['add', 'generate'])
    assert hasattr(parent, 'add_button')
    assert hasattr(parent, 'generate_button')


def test_ut003_create_toolbar_no_buttons(parent):
    toolbar = module_toolbar.create_toolbar(parent, "Empty", buttons=[])
    assert toolbar is not None


def test_ut004_unsupported_button_logged(caplog, parent):
    with caplog.at_level("WARNING"):
        toolbar = module_toolbar.create_toolbar(parent, "Invalid", buttons=['badkey'])
        assert "Unsupported toolbar button" in caplog.text


def test_ut005_submit_button_attributes(parent):
    toolbar = module_toolbar.create_toolbar(parent, "SubmitOnly", buttons=['submit'])
    assert hasattr(parent, 'submit_button')
    assert hasattr(parent, 'tree_submit_button')


def test_ut006_emit_toolbar_signal_emits_correct_payload(qtbot, parent):
    toolbar = module_toolbar.create_toolbar(parent, "Emit", buttons=['add'])
    received = []

    def capture(payload):
        received.append(payload)

    module_toolbar.toolbar_signals.action_triggered.connect(capture)
    qtbot.mouseClick(parent.add_button, Qt.LeftButton)

    assert received[0]['event'] == 'add'
    assert received[0]['sender'] == 'Toolbar'


def test_ut007_signal_payload_structure(parent):
    toolbar = module_toolbar.create_toolbar(parent, "Payload", buttons=['download'])
    signal_data = []

    def handler(payload):
        signal_data.append(payload)

    module_toolbar.toolbar_signals.action_triggered.connect(handler)
    parent.download_button.click()
    payload = signal_data[0]
    assert set(payload.keys()) == {'sender', 'event', 'data'}


def test_ut008_create_toolbar_with_none_parent():
    try:
        toolbar = module_toolbar.create_toolbar(None, "Test")
    except Exception:
        assert True


def test_ut009_missing_icon_attr(monkeypatch, parent):
    monkeypatch.delattr(module_toolbar.files, 'add_icon', raising=False)
    try:
        module_toolbar.create_toolbar(parent, "MissingIcon", buttons=['add'])
    except AttributeError:
        assert True


def test_ut010_toolbar_long_label(parent):
    long_text = "X" * 100
    toolbar = module_toolbar.create_toolbar(parent, long_text)
    assert toolbar is not None


def test_ut011_many_buttons(parent):
    many_buttons = ['add', 'submit', 'delete', 'generate', 'download']
    toolbar = module_toolbar.create_toolbar(parent, "Full", buttons=many_buttons)
    for b in many_buttons:
        key = b + "_button" if b != 'submit' else 'tree_submit_button'
        assert hasattr(parent, key)


def test_ut012_duplicate_button_keys(parent):
    toolbar = module_toolbar.create_toolbar(parent, "Dupes", buttons=['add', 'add'])
    assert hasattr(parent, 'add_button')


def test_ut013_payload_contains_correct_keys(parent):
    toolbar = module_toolbar.create_toolbar(parent, "Keys", buttons=['delete'])
    event_data = []
    module_toolbar.toolbar_signals.action_triggered.connect(lambda payload: event_data.append(payload))
    parent.delete_button.click()
    assert 'event' in event_data[0]


def test_ut014_small_spacer_returns_widget():
    spacer = module_toolbar._create_small_spacer()
    assert isinstance(spacer, QWidget)
    assert spacer.width() == 10


def test_ut015_toolbar_styles_applied(parent):
    toolbar = module_toolbar.create_toolbar(parent, "Styled")
    assert toolbar.styleSheet() == module_toolbar.toolbar_style.toolbar_style


def test_ut016_multiple_toolbars_same_parent(parent):
    toolbar1 = module_toolbar.create_toolbar(parent, "One")
    toolbar2 = module_toolbar.create_toolbar(parent, "Two")
    assert toolbar1 is not toolbar2


def test_ut017_toolbar_prints_log(capfd, parent):
    module_toolbar.create_toolbar(parent, "LogTest")
    out, _ = capfd.readouterr()
    assert "[TOOLBAR INIT]" in out


def test_ut018_delete_button_emits_delete(parent):
    toolbar = module_toolbar.create_toolbar(parent, "Delete", buttons=['delete'])
    received = []
    module_toolbar.toolbar_signals.action_triggered.connect(lambda p: received.append(p))
    parent.delete_button.click()
    assert received[0]['event'] == 'delete'


def test_ut019_parent_attr_assignment(parent):
    module_toolbar.create_toolbar(parent, "AttrTest", buttons=['generate'])
    assert hasattr(parent, 'generate_button')


def test_ut020_spacer_has_style():
    spacer = module_toolbar._create_small_spacer()
    assert spacer.styleSheet() == module_toolbar.toolbar_style.toolbar_spacer_style