import pytest
from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.QtGui import QFont
from Attack_Paths.components.node_context_menus import build_graphics_node_context_menu


@pytest.fixture
def mock_node(qtbot):
    """Mock a node with signals and tree type info for context menu generation."""
    class DummySignal:
        def emit(self, *args): pass

    class MockNode(QWidget):
        def __init__(self):
            super().__init__()
            self.tree_id = "T1"
            self.tree_type = "AttackTree"
            self.font = QFont("Arial", 10)
            self.available_leaf_nodes = {"L1": "Leaf 1"}
            self.available_technical_trees = {"Tech1": "Technical Tree"}
            self.available_control_trees = {"C1": "Control Tree"}

            # Signal stubs
            self.addIntermediateRequested = DummySignal()
            self.addLeafRequested = DummySignal()
            self.addRiskControlTreeRequested = DummySignal()
            self.addTechnicalTreeRequested = DummySignal()
            self.removeRequested = DummySignal()

    mock = MockNode()
    qtbot.addWidget(mock)
    return mock


def test_menu_structure_attacktree_insert_enabled(mock_node):
    """Test the full structure of context menu for AttackTree with insert enabled."""
    menu: QMenu = build_graphics_node_context_menu(mock_node, insert_enable=True)
    action_labels = [action.text() for action in menu.actions()]

    assert "Add Intermediate Node" in action_labels
    assert "Remove Node" in action_labels

    leaf_menu = next((a.menu() for a in menu.actions() if a.text().startswith("Add Leaf Node")), None)
    assert leaf_menu is not None

    rc_menu = next((a.menu() for a in menu.actions() if a.text().startswith("Add Risk Control Tree")), None)
    assert rc_menu is not None

    tech_menu = next((a.menu() for a in menu.actions() if a.text().startswith("Add Technical Tree")), None)
    assert tech_menu is not None

    # Ensure submenus have expected items
    leaf_texts = [a.text() for a in leaf_menu.actions()]
    assert any("New Leaf" in item for item in leaf_texts)
    assert any("Existing Leaf" in item for item in [sm.text() for sm in leaf_menu.actions() if sm.menu()])

    rc_texts = [a.text() for a in rc_menu.actions()]
    assert any("Control Tree" in item for item in rc_texts)

    tech_texts = [a.text() for a in tech_menu.actions()]
    assert any("Technical Tree" in item for item in tech_texts)

def test_menu_when_leaf_nodes_not_available(qtbot):
    """Test fallback when no leaf nodes are available."""
    class DummySignal:
        def emit(self, *args): pass

    class MockNode(QWidget):
        def __init__(self):
            super().__init__()
            self.tree_id = "T_empty"
            self.tree_type = "AttackTree"
            self.font = QFont("Arial", 10)
            self.available_leaf_nodes = {}  # << triggers else branch
            self.available_technical_trees = {}
            self.available_control_trees = {}

            self.addIntermediateRequested = DummySignal()
            self.addLeafRequested = DummySignal()
            self.addRiskControlTreeRequested = DummySignal()
            self.addTechnicalTreeRequested = DummySignal()
            self.removeRequested = DummySignal()

    node = MockNode()
    qtbot.addWidget(node)

    menu = build_graphics_node_context_menu(node, insert_enable=True)
    
    # Locate the "Add Leaf Node" menu
    leaf_menu = next((a.menu() for a in menu.actions() if a.text() == "Add Leaf Node"), None)
    assert leaf_menu is not None

    # Look for "Existing Leaf" submenu inside "Add Leaf Node"
    existing_leaf_menu = next((a.menu() for a in leaf_menu.actions() if a.menu()), None)
    assert existing_leaf_menu is not None

    leaf_action_texts = [a.text() for a in existing_leaf_menu.actions()]
    assert "Leaf Nodes not available" in leaf_action_texts
    disabled_action = next(a for a in existing_leaf_menu.actions() if a.text() == "Leaf Nodes not available")
    assert not disabled_action.isEnabled()

