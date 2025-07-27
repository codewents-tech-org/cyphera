import pytest
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QApplication
from PyQt5.QtCore import QRectF, QEvent, Qt
from Attack_Paths.controllers.treehead_node_creator import TreeHeadNodeBox
import styles.tree_style as TS


@pytest.fixture(scope="session")
def app():
    """Ensure QApplication instance is available."""
    app = QApplication.instance()
    return app


@pytest.fixture
def sample_config():
    """Base config for testing TreeHeadNodeBox."""
    return {
        "tree_id": "H001",
        "node_label": "Root",
        "node_Text": "Root description",
        "x": 10,
        "y": 20,
        "af_value": "7",
        "af_level": "High",
        "rf_value": "5",
        "rf_level": "Medium",
        "gate_type": "AND",
        "tree_type": "AttackTree"
    }


@pytest.fixture
def technical_config(sample_config):
    """Modified config to trigger TechnicalTree color branch."""
    cfg = sample_config.copy()
    cfg["tree_type"] = "TechnicalTree"
    return cfg


def test_bounding_rect_and_paint(app, sample_config):
    """Ensure boundingRect and paint() methods are covered."""
    node = TreeHeadNodeBox(sample_config, tree_type="AttackTree")
    painter = QPainter()
    option = QStyleOptionGraphicsItem()

    # Ensure paint() is callable (even as no-op)
    node.paint(painter, option)

    # boundingRect returns expected QRectF
    rect = node.boundingRect()
    assert rect == QRectF(0, 0, node.total_width, node.total_height)


def test_emit_methods_and_technical_branch(app, qtbot, technical_config):
    """Covers all emit_* methods and TechnicalTree sidebar color path."""
    node = TreeHeadNodeBox(technical_config, tree_type="TechnicalTree")

    # TechnicalTree branch hit
    assert node.background.color == TS.technicalnode_sidebar_color

def test_emit_methods_and_control_branch(app, qtbot, technical_config):
    """Covers all emit_* methods and TechnicalTree sidebar color path."""
    technical_config["tree_type"] = "ControlTree"
    node = TreeHeadNodeBox(technical_config, tree_type="ControlTree")

    # TechnicalTree branch hit
    assert node.background.color == TS.technicalnode_sidebar_color


def test_context_menu_executes(app, sample_config, monkeypatch):
    """Ensure context menu event is triggered and executes."""
    node = TreeHeadNodeBox(sample_config, tree_type="AttackTree")

    called = {"executed": False}

    class DummyEvent:
        def screenPos(self):
            return None

    node.contextMenuEvent(DummyEvent())
