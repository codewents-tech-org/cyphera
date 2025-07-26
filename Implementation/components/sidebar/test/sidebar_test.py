import pytest
import os
import json
from unittest.mock import patch, mock_open
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
import utils.interface_utils as interfaces
import components.sidebar.views.load_modules as load_modules_view
import components.sidebar.views.load_profile as load_profile_view
import components.sidebar.views.load_settings as load_settings_view
import components.sidebar.sidebar as sidebar
import views.TARA_Tool as tara_tool


app = QApplication([])

VALID_JSON = {
    "modules": [
        {
            "name": "TestModule",
            "icon": "test_icon",
            "enabled": True,
            "licensed": True,
            "submodules": [
                {
                    "name": "Sub1",
                    "icon": "sub_icon1",
                    "file": "mock.module.path",
                    "class": "MockSubClass",
                    "enabled": True,
                    "licensed": True
                }
            ]
        }
    ]
}

class MockParent(QWidget):
    def __init__(self):
        super().__init__()
        self.module_layout = QVBoxLayout()
        self.submodule_layout = QVBoxLayout()
        self.Action_layer = QStackedWidget()

# UT001
def test_sidebar_initializes():
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert sidebar_cls is not None

# UT002
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(VALID_JSON))
@patch("os.path.exists", return_value=True)
def test_load_modules_success(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() > 0

# UT003
@patch("os.path.exists", return_value=False)
def test_load_modules_file_missing(mock_exists):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent, module_json_path="nonexistent.json")
    assert mock_parent.submodule_layout.count() == 0

# UT004
@patch("builtins.open", new_callable=mock_open, read_data="{ invalid json }")
@patch("os.path.exists", return_value=True)
def test_load_modules_invalid_json(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 0

# UT005
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({}))
@patch("os.path.exists", return_value=True)
def test_load_modules_no_modules_key(mock_exists, mock_file):  # MISSING ✅
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 1

# UT006
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{"name": "Mod", "enabled": False, "licensed": True}]
}))
@patch("os.path.exists", return_value=True)
def test_load_modules_module_disabled(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 1

# UT007
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{"name": "Mod", "enabled": True, "licensed": False}]
}))
@patch("os.path.exists", return_value=True)
def test_load_modules_module_unlicensed(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 1

# UT008
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [ {
        "name": "Mod",
        "enabled": True,
        "licensed": True,
        "submodules": [{"name": "Sub", "enabled": False, "licensed": True}]
    }]
}))
@patch("os.path.exists", return_value=True)
def test_load_modules_submodule_disabled(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() >= 1  # Only label

# UT009
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{
        "name": "Mod",
        "enabled": True,
        "licensed": True,
        "submodules": [{"name": "Sub", "enabled": True, "licensed": False}]
    }]
}))
@patch("os.path.exists", return_value=True)
def test_load_modules_submodule_unlicensed(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 2

# UT010
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{
        "name": "Mod",
        "enabled": True,
        "licensed": True,
        "submodules": [{"name": "Sub"}]
    }]
}))
@patch("os.path.exists", return_value=True)
def test_load_modules_submodule_no_icon(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() >= 2

# UT011
def test_emit_submodule_signal_payload(qtbot):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    module_name = "TestMod"
    frame = "frame"
    submodule = {"name": "TestSub", "icon": "icon.svg", "frame": "frame", "submodule": {}, "enabled": True, "licensed": True}
    captured = {}

    def receiver(payload):
        captured.update(payload)

    sidebar_cls.submodule_selected.connect(receiver)
    sidebar_cls.emit_submodule_signal("TestMod", module_name, submodule, frame)
    assert captured["data"]["name"] == "TestSub"
    assert captured["data"]["module"] == "TestMod"

# UT012
def test_submodule_signal_without_receiver():  # MISSING ✅
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    try:
        sidebar_cls.emit_submodule_signal("Dummy", "Module", {"name": "NoReceiver"}, "frame")
    except Exception:
        pytest.fail("emit_submodule_signal raised Exception unexpectedly!")

# UT013
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": []
}))
@patch("os.path.exists", return_value=True)
def test_load_modules_empty_modules(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 1

# UT014
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{
        "name": "Mod", "enabled": True, "licensed": True,
        "submodules": [{"icon": "some_icon", "enabled": True, "licensed": True}]
    }]
}))
@patch("os.path.exists", return_value=True)
def test_submodule_missing_name(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 2

# UT015
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{"name": f"Mod{i}", "enabled": True, "licensed": True,
                 "submodules": [{"name": f"Sub{i}{j}", "enabled": True, "licensed": True,
                                 "file": "mock.path", "class": "MockClass"}
                                for j in range(5)]} for i in range(5)]
}))
@patch("os.path.exists", return_value=True)
@patch("importlib.import_module")
def test_large_module_list(mock_import, mock_exists, mock_file):
    class MockClass:
        def __init__(self): pass
        def load_data(self): pass
    mock_import.return_value = type("MockModule", (), {"MockClass": MockClass})

    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    # 5 module labels + 5 * 5 = 25 submodule buttons
    assert mock_parent.submodule_layout.count() >= 30

# UT016
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{"name": "Mod", "enabled": True, "licensed": True,
                 "submodules": [{"name": "Sub", "enabled": True, "licensed": True},
                                {"name": "Sub", "enabled": True, "licensed": True}]}]
}))
@patch("os.path.exists", return_value=True)
def test_duplicate_submodule_names(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 4

# UT017
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{"name": "Mod", "enabled": True, "licensed": True}]
}))
@patch("os.path.exists", return_value=True)
def test_module_without_submodules(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 2

# UT018
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{"name": "Mod", "enabled": True, "licensed": True,
                 "submodules": [{"name": "   ", "enabled": True, "licensed": True}]}]
}))
@patch("os.path.exists", return_value=True)
def test_submodule_whitespace_name(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 2

# UT019
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
    "modules": [{"name": "Mod", "enabled": True, "licensed": True,
                 "submodules": [{"name": "Sub", "icon": "non_existent_icon", "enabled": True, "licensed": True}]}]
}))
@patch("os.path.exists", return_value=True)
def test_invalid_icon_attribute(mock_exists, mock_file):
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent)
    assert mock_parent.submodule_layout.count() == 3

# UT020
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(VALID_JSON))
@patch("os.path.exists", return_value=True)
def test_sidebar_with_custom_json_path(mock_exists, mock_file):  # MISSING ✅
    mock_parent = MockParent()
    sidebar_cls = sidebar.Sidebar(parent=mock_parent, json_path="custom_modules.json")
    assert mock_parent.submodule_layout.count() > 0
