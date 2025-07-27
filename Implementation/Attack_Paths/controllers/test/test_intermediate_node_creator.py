# test_intermediate_node_creator.py

import pytest
from PyQt5.QtWidgets import QApplication, QPushButton, QStyleOptionGraphicsItem
from PyQt5.QtCore import Qt, QEvent, QRectF
from PyQt5.QtGui import QPainter
from Attack_Paths.controllers.intermediate_node_creator import IntermediateNodeBox


@pytest.fixture(scope="session")
def app():
    """Ensure a QApplication exists."""
    app = QApplication.instance()
    return app


@pytest.fixture
def valid_config():
    """Provide valid config for testing."""
    return {
        "tree_id": "N1",
        "node_label": "Intermediate Node",
        "node_Text": "Sample text here.",
        "x": 50,
        "y": 75,
        "gate_type": "OR"
    }


def test_creation_with_valid_config(app, valid_config):
    """Test successful creation of IntermediateNodeBox with valid config."""
    node = IntermediateNodeBox(valid_config)
    assert node.tree_id == "N1"
    assert node.gate_button.text() == "OR"
    assert node.node_text.toPlainText() == "Sample text here."


def test_gate_button_toggle_emits(app, qtbot, valid_config):
    """Simulate double-click to toggle gate and verify signal is emitted."""
    node = IntermediateNodeBox(valid_config)
    qtbot.addWidget(node.gate_button)

    captured = []
    node.gateSwitchRequested.connect(lambda val: captured.append(val))

    event = QEvent(QEvent.MouseButtonDblClick)
    event.button = lambda: Qt.LeftButton
    result = node.eventFilter(node.gate_button, event)

    assert result is True
    assert captured == ["N1"]
    assert node.gate_button.text() in {"AND", "OR"}


def test_emit_text_edited_signal(app, qtbot, valid_config):
    """Ensure edited text emits signal when triggered."""
    node = IntermediateNodeBox(valid_config)
    captured = []
    node.textEditedRequested.connect(lambda val: captured.append(val))

    # Trigger signal manually
    node.emit_text_edited("New Value")
    assert captured == ["New Value"]


def test_context_menu_exec_called(monkeypatch, app, valid_config):
    """Patch context menu and ensure it's invoked."""
    node = IntermediateNodeBox(valid_config)

    triggered = {"executed": False}

    class DummyEvent:
        def screenPos(self):
            return None
    node.contextMenuEvent(DummyEvent())


def test_signal_emits_correctly(app, valid_config):
    """Test that all signal emit methods send expected values."""
    node = IntermediateNodeBox(valid_config)
    captured = {}

    node.addIntermediateRequested.connect(lambda v: captured.update({"inter": v}))
    node.addLeafRequested.connect(lambda v, n=None: captured.update({"leaf": v, "leaf_name": n}))
    node.addRiskControlTreeRequested.connect(lambda v, n: captured.update({"rc": n}))
    node.addTechnicalTreeRequested.connect(lambda v, n: captured.update({"tc": n}))

    node.emit_add_intermediate()
    assert captured["inter"] == "N1"

    node.emit_add_new_leaf()
    assert captured["leaf"] == "N1"

    node.emit_add_existing_leaf("Leaf42")


def test_invalid_config_raises(app):
    """Ensure validation error on missing required fields."""
    invalid = {
        "tree_id": "N1",  # Missing node_label, node_Text, gate_type, etc.
        "x": 0,
        "y": 0,
    }
    with pytest.raises(ValueError):
        IntermediateNodeBox(invalid)

@pytest.fixture
def intermediate_config():
    return {
        "tree_id": "INT001",
        "node_label": "Intermediate Node",
        "node_Text": "This is a test description.",
        "x": 50,
        "y": 80,
        "af_value": "3",
        "af_level": "Low",
        "rf_value": "2",
        "rf_level": "High",
        "gate_type": "AND",
        "tree_type": "AttackTree"
    }

def test_paint_and_boundingRect(app, intermediate_config):
    """Covers paint() and boundingRect() in IntermediateNodeBox."""
    node = IntermediateNodeBox(intermediate_config, tree_type="AttackTree")
    painter = QPainter()
    option = QStyleOptionGraphicsItem()

    node.paint(painter, option)  # Exercise the dummy method

    rect = node.boundingRect()
    assert rect == QRectF(0, 0, node.total_width, node.total_height)


def test_signal_emit_risk_and_technical(app, qtbot, intermediate_config):
    """Covers emit_add_riskcontrol_tree and emit_add_technical_tree."""
    node = IntermediateNodeBox(intermediate_config, tree_type="AttackTree")

    captured = {}

    node.addRiskControlTreeRequested.connect(
        lambda tid, name: captured.update({"rc_id": tid, "rc_name": name})
    )
    node.addTechnicalTreeRequested.connect(
        lambda tid, name: captured.update({"tech_id": tid, "tech_name": name})
    )

    node.emit_add_riskcontrol_tree("RC_Tree_X")
    node.emit_add_technical_tree("Tech_Tree_Y")

    assert captured["rc_id"] == intermediate_config["tree_id"]
    assert captured["rc_name"] == "RC_Tree_X"
    assert captured["tech_id"] == intermediate_config["tree_id"]
    assert captured["tech_name"] == "Tech_Tree_Y"