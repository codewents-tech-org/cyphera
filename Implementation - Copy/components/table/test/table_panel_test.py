import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QWidget, QLineEdit, QTableWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QRect
from components.table.table_panel import SingleLineDelegate, TablePanelWrapper 
import sys
import pytest
from PyQt5.QtWidgets import QApplication

@pytest.fixture(scope="session", autouse=True)
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def delegate():
    return SingleLineDelegate()

@pytest.fixture
def mock_index():
    index = MagicMock()
    model = MagicMock()
    index.model.return_value = model
    return index

@pytest.fixture
def editor(qtbot):
    line_edit = QLineEdit()
    qtbot.addWidget(line_edit)
    return line_edit


# CY_TP_001
def test_create_editor_returns_line_edit(delegate):
    print("✅ test_create_editor_returns_line_edit started")
    parent = QWidget()
    editor = delegate.create_editor(parent, None, None)
    assert isinstance(editor, QLineEdit)

# CY_TP_002
def test_set_editor_data_string(delegate, editor, mock_index):
    mock_index.model().data.return_value = "Hello"
    delegate.set_editor_data(editor, mock_index)
    assert editor.text() == "Hello"

# CY_TP_003
def test_set_model_data_sets_text(delegate, mock_index):
    editor = MagicMock()
    editor.text.return_value = "Updated"
    model = mock_index.model()
    delegate.set_model_data(editor, model, mock_index)
    model.setData.assert_called_with(mock_index, "Updated", Qt.EditRole)

# CY_TP_004
def test_update_editor_geometry_applies_rect(delegate):
    editor = MagicMock()
    option = MagicMock()
    option.rect = QRect(10, 10, 100, 30)
    delegate.update_editor_geometry(editor, option, None)
    editor.setGeometry.assert_called_with(option.rect)

# CY_TP_005
def test_create_table_panel_sets_layout(qtbot):
    class Dummy(QWidget):
        def on_row_selection_changed(self): pass
        def display_selected_row(self): pass
    panel = Dummy()
    qtbot.addWidget(panel)
    TablePanelWrapper.create_table_panel(panel)
    assert isinstance(panel.table, QTableWidget)
    assert isinstance(panel.table_layout, QVBoxLayout)

# CY_TP_006
def test_create_editor_type(delegate):
    parent = QWidget()
    editor = delegate.create_editor(parent, None, None)
    assert isinstance(editor, QLineEdit)

# CY_TP_007
def test_create_table_panel_scroll_policy(qtbot):
    class Dummy(QWidget):
        def on_row_selection_changed(self): pass
        def display_selected_row(self): pass
    panel = Dummy()
    qtbot.addWidget(panel)
    TablePanelWrapper.create_table_panel(panel)
    assert panel.table.horizontalScrollBarPolicy() is not None

# CY_TP_008
def test_create_table_panel_delegate(qtbot):
    class Dummy(QWidget):
        def on_row_selection_changed(self): pass
        def display_selected_row(self): pass
    panel = Dummy()
    qtbot.addWidget(panel)
    TablePanelWrapper.create_table_panel(panel)
    assert isinstance(panel.table.itemDelegate(), SingleLineDelegate)

# CY_TP_009
def test_set_editor_data_none(delegate, editor, mock_index):
    mock_index.model().data.return_value = None
    delegate.set_editor_data(editor, mock_index)
    assert editor.text() == ""

# CY_TP_010
def test_set_model_data_empty(delegate, mock_index):
    editor = MagicMock()
    editor.text.return_value = ""
    model = mock_index.model()
    delegate.set_model_data(editor, model, mock_index)
    model.setData.assert_called_with(mock_index, "", Qt.EditRole)

# CY_TP_011
def test_update_editor_geometry_invalid(delegate):
    editor = MagicMock()
    option = MagicMock()
    option.rect = None
    delegate.update_editor_geometry(editor, option, None)

# CY_TP_012
def test_create_table_panel_set_delegate_exception(qtbot):
    class Dummy(QWidget):
        def on_row_selection_changed(self): pass
        def display_selected_row(self): pass
    panel = Dummy()
    qtbot.addWidget(panel)
    with patch("styles.table_style.table_style", new="INVALID{STYLE"):
        try:
            TablePanelWrapper.create_table_panel(panel)
        except Exception:
            pytest.fail("Unhandled exception")

# CY_TP_013
def test_set_editor_data_integer(delegate, editor, mock_index):
    mock_index.model().data.return_value = 123
    delegate.set_editor_data(editor, mock_index)
    assert editor.text() == "123"

# CY_TP_014
def test_set_model_data_spaces(delegate, mock_index):
    editor = MagicMock()
    editor.text.return_value = "  test  "
    model = mock_index.model()
    delegate.set_model_data(editor, model, mock_index)
    model.setData.assert_called_with(mock_index, "  test  ", Qt.EditRole)

# CY_TP_015
def test_create_table_panel_contains_table(qtbot):
    class Dummy(QWidget):
        def on_row_selection_changed(self): pass
        def display_selected_row(self): pass
    panel = Dummy()
    qtbot.addWidget(panel)
    TablePanelWrapper.create_table_panel(panel)
    assert isinstance(panel.table, QTableWidget)

# CY_TP_016
# CY_TP_016
def test_set_editor_data_exception(delegate, editor, caplog):
    index = MagicMock()
    index.model.side_effect = Exception("Error")
    with caplog.at_level("ERROR"):
        delegate.set_editor_data(editor, index)
        assert "Failed to set editor data" in caplog.text


# CY_TP_017
def test_set_model_data_exception(delegate, caplog):
    editor = MagicMock()
    editor.text.return_value = "Text"
    index = MagicMock()
    model = MagicMock()
    model.setData.side_effect = Exception("Set failed")
    index.model.return_value = model
    with caplog.at_level("ERROR"):
        delegate.set_model_data(editor, model, index)
        assert "Failed to set model data" in caplog.text

# CY_TP_018
def test_create_table_panel_selection_error(qtbot):
    class Dummy(QWidget):
        def on_row_selection_changed(self): raise Exception("fail")
        def display_selected_row(self): raise Exception("fail")
    panel = Dummy()
    qtbot.addWidget(panel)
    try:
        TablePanelWrapper.create_table_panel(panel)
    except Exception:
        pass

# CY_TP_019
def test_set_editor_data_replaces(delegate, editor, mock_index):
    editor.setText("old")
    mock_index.model().data.return_value = "new"
    delegate.set_editor_data(editor, mock_index)
    assert editor.text() == "new"

# CY_TP_020
def test_set_model_data_numeric(delegate, mock_index):
    editor = MagicMock()
    editor.text.return_value = "42"
    model = mock_index.model()
    delegate.set_model_data(editor, model, mock_index)
    model.setData.assert_called_with(mock_index, "42", Qt.EditRole)

# CY_TP_021
def test_update_editor_geometry_visible(delegate):
    editor = MagicMock()
    rect = QRect(5, 5, 100, 20)
    option = MagicMock()
    option.rect = rect
    delegate.update_editor_geometry(editor, option, None)
    editor.setGeometry.assert_called_with(rect)

# CY_TP_022
def test_create_editor_focus(delegate):
    parent = QWidget()
    editor = delegate.create_editor(parent, None, None)
    assert isinstance(editor, QLineEdit)

# CY_TP_023
def test_create_table_panel_margins(qtbot):
    parent = QWidget()
    wrapper = TablePanelWrapper.__new__(TablePanelWrapper)  # bypass __init__
    wrapper.parent = parent
    wrapper.DEFAULT_MARGIN = 10

    # Inject dummy methods to prevent AttributeError
    wrapper.on_row_selection_changed = lambda *args, **kwargs: None
    wrapper.display_selected_row = lambda *args, **kwargs: None

    # Manually invoke create_table_panel
    wrapper.create_table_panel()

    qtbot.addWidget(wrapper.parent)

    margins = wrapper.table_layout.contentsMargins()
    assert all([
        margins.left() == wrapper.DEFAULT_MARGIN,
        margins.top() == wrapper.DEFAULT_MARGIN,
        margins.right() == wrapper.DEFAULT_MARGIN,
        margins.bottom() == wrapper.DEFAULT_MARGIN
    ])




# CY_TP_024
def test_update_editor_geometry_clipped(delegate):
    editor = MagicMock()
    rect = QRect(-10, -10, 50, 50)
    option = MagicMock()
    option.rect = rect
    delegate.update_editor_geometry(editor, option, None)
    editor.setGeometry.assert_called_with(rect)

# CY_TP_025
def test_create_table_panel_existing_layout(qtbot):
    class Dummy(QWidget):
        def __init__(self):
            super().__init__()
            self.setLayout(QVBoxLayout())
        def on_row_selection_changed(self): pass
        def display_selected_row(self): pass
    panel = Dummy()
    qtbot.addWidget(panel)
    TablePanelWrapper.create_table_panel(panel)
    assert panel.layout() is not None

# CY_TP_026
def test_create_table_panel_stylesheet_error(qtbot):
    class Dummy(QWidget):
        def on_row_selection_changed(self): pass
        def display_selected_row(self): pass
    panel = Dummy()
    qtbot.addWidget(panel)
    with patch("styles.table_style.table_style", new="INVALID{STYLE"):
        try:
            TablePanelWrapper.create_table_panel(panel)
        except Exception:
            pytest.fail("Exception not handled")