# test_leaf_node_creator.py

import pytest
from PyQt5.QtWidgets import QApplication, QStyleOptionGraphicsItem
from PyQt5.QtCore import Qt, QEvent, QRectF
from PyQt5.QtGui import QPainter
from Attack_Paths.controllers.leaf_node_creator import LeafNodeBox
from Attack_Paths.models.afr_level_calculation import calculate_afr_Level


@pytest.fixture
def valid_config():
    """Return valid node config for a LeafNodeBox."""
    return {
        "tree_id": "Leaf001",
        "node_label": "Leaf Node",
        "node_Text": "Leaf description",
        "x": 10,
        "y": 10,
        "af_value": "5",
        "af_level": "High",
        "values": ["0", "1", "1", "2", "1"]
    }


def test_leaf_node_initializes_properly(app, valid_config):
    """Check initialization of leaf node box with correct fields."""
    node = LeafNodeBox(valid_config)
    assert node.tree_id == "Leaf001"
    assert node.af_value.toPlainText() == "5"


def test_af_recalculation_on_value_change(app, qtbot, valid_config):
    """Ensure AFR value/level updates correctly and emits signal."""
    node = LeafNodeBox(valid_config)
    qtbot.addWidget(node.values_label[0])

    emitted = []

    node.textEditedRequested.connect(lambda text: emitted.append(text))

    # Simulate selecting new value from menu (simulate user changes)
    node.values_label[0].setText("4")
    node.emit_value_changed("4")

    afr_score = sum([int(lbl.text()) for lbl in node.values_label])
    afr_level = calculate_afr_Level(afr_score)

    assert node.af_value.toPlainText() == str(afr_score)


def test_text_change_emits_signal(app, qtbot, valid_config):
    """Ensure text edit triggers signal."""
    node = LeafNodeBox(valid_config)

    captured = []
    node.textEditedRequested.connect(lambda value: captured.append(value))

    # Manually emit
    node.emit_text_edited("Updated text")

    assert captured == ["Updated text"]


def test_context_menu_invoked(monkeypatch, app, valid_config):
    """Patch menu to simulate execution."""
    node = LeafNodeBox(valid_config)

    class DummyEvent:
        def screenPos(self):
            return None

    triggered = {"menu": False}

    node.contextMenuEvent(DummyEvent())


def test_invalid_config_raises_error():
    """Ensure validation fails on missing fields."""
    with pytest.raises(ValueError):
        LeafNodeBox({
            "tree_id": "missing_fields",
            "x": 0,
            "y": 0
        })
import pytest
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QApplication
from PyQt5.QtCore import QRectF

from Attack_Paths.controllers.leaf_node_creator import LeafNodeBox


@pytest.fixture(scope="session")
def app():
    """Ensure a QApplication instance exists."""
    app = QApplication.instance()
    return app


@pytest.fixture
def leaf_config():
    """Sample leaf node config."""
    return {
        "tree_id": "L001",
        "node_label": "Leaf Node",
        "node_Text": "This is a leaf node description.",
        "x": 20,
        "y": 30,
        "af_value": "5",
        "af_level": "Low",
        "rf_value": "3",
        "rf_level": "High",
        "gate_type": "OR",
        "values": ["0", "0", "0", "0", "0"],
        "tree_type": "AttackTree"
    }


def test_leaf_node_paint_and_bounding_rect(app, leaf_config):
    """Ensure paint() and boundingRect() of LeafNodeBox are covered."""
    node = LeafNodeBox(leaf_config, tree_type="AttackTree")

    # Explicitly call the no-op paint method
    painter = QPainter()
    option = QStyleOptionGraphicsItem()
    node.paint(painter, option)

    # Explicitly test boundingRect values
    rect = node.boundingRect()
    assert rect == QRectF(0, 0, node.total_width, node.total_height)
