
import pytest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QWidget, QPushButton, QScrollArea, QLabel, QApplication, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
import sys
from components.propertypanel import property_panel_layout
import Analysis.controllers.analysis_PropertyValueDisplay as PVD
from Analysis.Asset.views.Asset_action import Asset_Module


@pytest.fixture(scope="session", autouse=True)
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def panel_manager(app):
    parent = QWidget()
    return property_panel_layout.PropertyPanelManager(parent)

def test_create_property_panel(panel_manager):
    panel_manager.create_property_panel()
    assert panel_manager.switch_property_panel is not None
    assert panel_manager.property_panel is not None
    assert panel_manager.property_scroll_area is not None

def test_create_switch_property_panel(panel_manager):
    panel_manager.create_switch_property_panel()
    assert panel_manager.switch_property_panel.layout() is not None
    assert panel_manager.toggle_button.toolTip() == "hide propert panel"

def test_create_property_scroll_panel(panel_manager):
    panel_manager.create_property_scroll_panel()
    assert panel_manager.property_scroll_area.widget() is not None

def test_setup_property_panel_layout(panel_manager):
    panel_manager.create_property_scroll_panel()
    panel_manager.setup_property_panel_layout()
    assert panel_manager.property_heading.text() == "Property"

def test_toggle_right_panel_show(panel_manager):
    panel_manager.create_property_panel()
    panel_manager.property_panel.setVisible(False)
    panel_manager.toggle_right_panel()
    assert panel_manager.property_panel.isVisible()

def test_toggle_right_panel_hide(panel_manager):
    panel_manager.create_property_panel()
    panel_manager.property_panel.setVisible(True)
    panel_manager.toggle_right_panel()
    assert not panel_manager.property_panel.isVisible()

def test_toggle_right_panel_no_property_panel():
    dummy_self = MagicMock()
    dummy_self.property_panel = None
    dummy_self.toggle_button = MagicMock()
    with patch("components.propertypanel.property_panel_layout.logger") as mock_logger:
        property_panel_layout.PropertyPanelManager.toggle_right_panel(dummy_self)
        mock_logger.error.assert_called()

def test_toggle_right_panel_no_toggle_button():
    dummy_self = MagicMock()
    dummy_self.property_panel = MagicMock()
    dummy_self.property_panel.isVisible.return_value = True
    dummy_self.toggle_button = None
    with patch("components.propertypanel.property_panel_layout.logger") as mock_logger:
        property_panel_layout.PropertyPanelManager.toggle_right_panel(dummy_self)
        mock_logger.error.assert_called()

def test_toggle_button_properties(panel_manager):
    panel_manager.create_switch_property_panel()
    assert panel_manager.toggle_button.iconSize().width() == 30
    assert panel_manager.toggle_button.iconSize().height() == 30
    assert panel_manager.toggle_button.toolTip() == 'hide propert panel'

def test_scroll_area_styling(panel_manager):
    panel_manager.create_property_scroll_panel()
    assert panel_manager.property_scroll_area.styleSheet() != ""

def test_label_alignment_and_spacing(panel_manager):
    panel_manager.create_property_scroll_panel()
    panel_manager.setup_property_panel_layout()
    assert panel_manager.property_heading.alignment() == Qt.AlignLeft

def test_switch_panel_layout_margins(panel_manager):
    panel_manager.create_switch_property_panel()
    layout = panel_manager.switch_property_panel.layout()
    assert layout.contentsMargins().left() == 0
    assert layout.spacing() == 0

def test_scrollable_content_margins(panel_manager):
    panel_manager.create_property_scroll_panel()
    margins = panel_manager.scrollable_content.contentsMargins()
    assert margins.right() == 10  # Based on code in layout

def test_full_panel_layout(panel_manager):
    panel_manager.create_property_panel()
    assert panel_manager.property_panel is not None
    assert panel_manager.property_scroll_area.widget() is not None

def test_logging_on_toggle(panel_manager):
    panel_manager.create_property_panel()
    panel_manager.property_panel.setVisible(True)
    with patch("components.propertypanel.property_panel_layout.logger") as mock_logger:
        panel_manager.toggle_right_panel()
        mock_logger.info.assert_called()

def test_create_property_signal_handlers():
    manager = property_panel_layout.PropertyPanelManager(QWidget())
    manager.create_property_layout_signal = MagicMock()

    with patch.object(manager, "create_property_panel") as mock_create_panel:
        manager.create_property_signal_handlers()
        connected_callback = manager.create_property_layout_signal.connect.call_args[0][0]
        connected_callback()
        manager.create_property_layout_signal.connect.assert_called_once()
        mock_create_panel.assert_called_once()


def test_row_selected_signal_triggers_property_display():
    asset_module = Asset_Module()
    asset_module.table.setRowCount(1)
    asset_module.table.setColumnCount(6)
    asset_module.table.setItem(0, 1, QTableWidgetItem("Asset001"))
    asset_module.table.setItem(0, 2, QTableWidgetItem("Router"))
    asset_module.table.setItem(0, 3, QTableWidgetItem("Confidentiality"))
    asset_module.table.setItem(0, 4, QTableWidgetItem("Secure Device"))
    asset_module.table.setItem(0, 5, QTableWidgetItem("Important comments"))

    with patch.object(PVD, "asset_display_selected_row") as mock_display:
        test_payload = {
            "sender": "Table",
            "event": "row_selected",
            "data": {
                "ID": "Asset001",
                "Name": "Router",
                "Security Properties": "Confidentiality",
                "Description": "Secure Device",
                "Comments": "Important comments"
            }
        }

        asset_module.row_selected.emit(test_payload)
        mock_display.assert_called_once_with(
            asset_module.table,
            asset_module.asset_property_controls,
            asset_module.panel_manager.property_panel,
            asset_module.panel_manager.toggle_button
        )
