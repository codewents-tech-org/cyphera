import pytest
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsObject
from Attack_Paths.controllers.highlight_afr_path import flatten_tree, create_arrow_lines, update_arrow_lines
from Attack_Paths.controllers.arrow_line_creator import ArrowRenderer

class DummyNode(QGraphicsObject):
    def __init__(self, node_id):
        super().__init__()
        self.node_id = node_id
        self.arrow_update_callback = None

    def boundingRect(self):
        return self.sceneBoundingRect()


# Dummy ArrowRenderer that mimics the real one
class DummyArrowRenderer:
    def __init__(self):
        self.path_set = None
        self.called = False

    def set_selected_path(self, path):
        self.path_set = path
        self.called = True

@pytest.fixture
def simple_tree():
    # Constructs a small 3-node tree
    leaf_node = DummyNode("node_2")
    inter_node = DummyNode("node_1")
    head_node = DummyNode("node_0")

    return {
        "node_type": "head",
        "node_id": "node_0",
        "node": head_node,
        "childrens": [
            {
                "node_type": "intermediate",
                "node_id": "node_1",
                "node": inter_node,
                "childrens": [
                    {
                        "node_type": "leaf",
                        "node_id": "node_2",
                        "node": leaf_node
                    }
                ]
            }
        ]
    }

def test_flatten_tree(simple_tree):
    flat = flatten_tree(simple_tree)
    assert len(flat) == 3
    assert "node_0" in flat
    assert flat["node_1"]["parent_id"] == "node_0"
    assert flat["node_2"]["parent_id"] == "node_1"
    assert flat["node_0"]["parent_id"] is None

def test_create_arrow_lines(simple_tree):


    scene = QGraphicsScene()
    selected_path = {"node_2"}

    renderer, flat_map = create_arrow_lines(scene, simple_tree, "node_0", selected_path)

    # Corrected: Verify arrow_update_callback assigned properly
    for node in flat_map.values():
        assert node["node"].arrow_update_callback == renderer.update_arrow_position

def test_update_arrow_lines_executes_set_path():
    dummy_renderer = DummyArrowRenderer()
    selected_path = {"node_1", "node_2"}

    update_arrow_lines(dummy_renderer, selected_path)

    assert dummy_renderer.called is True
    assert dummy_renderer.path_set == selected_path


def test_flatten_tree_invalid(simple_tree):
    simple_tree.pop("node")
    flat = flatten_tree(simple_tree)
