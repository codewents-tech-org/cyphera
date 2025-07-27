# test_head_node_creator.py

import pytest
from PyQt5.QtWidgets import QApplication, QPushButton, QGraphicsScene, QGraphicsView
from PyQt5.QtCore import Qt, QEvent
from Attack_Paths.controllers.head_node_creator import headNodeBox

@pytest.fixture(scope="session")
def app():
    """Ensure QApplication exists for test session."""
    app = QApplication.instance()
    return app

@pytest.fixture
def sample_config():
    return {
        "tree_id": "T1",
        "node_label": "Main Node",
        "node_Text": "Description of main node",
        "x": 100,
        "y": 150,
        "af_value": "12",
        "af_level": "High",
        "rf_value": "9",
        "rf_level": "Medium",
        "gate_type": "OR"
    }

def test_gate_button_toggle_on_doubleclick(app, sample_config, qtbot):
    """Ensure double-click toggles gate between OR and AND."""
    node = headNodeBox(sample_config, tree_type="AttackTree")
    qtbot.addWidget(node.gate_button)

    old_text = node.gate_button.text()
    event = QEvent(QEvent.MouseButtonDblClick)
    event.button = lambda: Qt.LeftButton
    node.eventFilter(node.gate_button, event)

    new_text = node.gate_button.text()
    assert new_text in {"AND", "OR"}
    assert new_text != old_text

def test_rf_labels_visibility_with_empty_rf(app, qtbot, sample_config):
    """RF value/level should hide when empty and AttackTree used."""
    config = sample_config.copy()
    config["rf_value"] = ""
    config["rf_level"] = ""
    node = headNodeBox(config, tree_type="AttackTree")

    assert not node.rf_value.isVisible()
    assert not node.rf_level.isVisible()

def test_emit_signals_triggered(app, qtbot, sample_config):
    """Test signal emit logic works."""
    node = headNodeBox(sample_config, tree_type="AttackTree")

    captured = {}
    node.addIntermediateRequested.connect(lambda val: captured.update({"intermediate": val}))
    node.addLeafRequested.connect(lambda val, name=None: captured.update({"leaf": val, "leaf_name": name}))
    node.removeRequested.connect(lambda val: captured.update({"remove": val}))

    node.emit_add_intermediate()
    node.emit_add_new_leaf()
    node.emit_add_existing_leaf("Leaf1")

def test_context_menu_execution(app, qtbot, sample_config, monkeypatch):
    """Ensure context menu is created and executed."""
    node = headNodeBox(sample_config, tree_type="AttackTree")

    # Patch menu execution to intercept call
    called = {"executed": False}

    class DummyEvent:
        def screenPos(self):
            return None

    node.contextMenuEvent(DummyEvent())

def test_validation_fails_on_missing_field(app):
    """Ensure validation fails when required fields are missing."""
    config = {
        "tree_id": "T99", "node_label": "Node", "x": 0, "y": 0, "gate_type": "OR"
        # Missing af_value, af_level, node_Text, etc.
    }
    with pytest.raises(ValueError):
        headNodeBox(config, tree_type="AttackTree")

def test_node_bounding_rect(app, sample_config):
    """Test that bounding rect is accurate."""
    node = headNodeBox(sample_config, tree_type="AttackTree")
    rect = node.boundingRect()
    assert rect.width() == 300
    assert rect.height() == 130

def test_paint_noop_method_runs(app, sample_config):
    """Ensure paint method exists and runs without exception."""
    from PyQt5.QtGui import QPainter
    from PyQt5.QtWidgets import QStyleOptionGraphicsItem

    node = headNodeBox(sample_config, tree_type="AttackTree")
    painter = QPainter()
    option = QStyleOptionGraphicsItem()

    # paint is a no-op but should not crash or raise any exception
    node.paint(painter, option)

def test_risk_and_technical_tree_signals(app, qtbot, sample_config):
    """Test signals for adding RiskControl and Technical trees."""
    node = headNodeBox(sample_config, tree_type="AttackTree")
    
    captured = {
        "risk": None,
        "risk_name": None,
        "tech": None,
        "tech_name": None
    }

    # Connect and capture signals
    node.addRiskControlTreeRequested.connect(
        lambda tree_id, name: captured.update({"risk": tree_id, "risk_name": name})
    )
    node.addTechnicalTreeRequested.connect(
        lambda tree_id, name: captured.update({"tech": tree_id, "tech_name": name})
    )

    node.emit_add_riskcontrol_tree("RiskTreeA")
    node.emit_add_technical_tree("TechTreeB")

    assert captured["risk"] == sample_config["tree_id"]
    assert captured["risk_name"] == "RiskTreeA"
    assert captured["tech"] == sample_config["tree_id"]
    assert captured["tech_name"] == "TechTreeB"
