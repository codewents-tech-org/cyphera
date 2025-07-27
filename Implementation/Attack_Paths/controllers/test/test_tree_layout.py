import pytest
from unittest.mock import MagicMock, patch
from Attack_Paths.controllers.tree_layout import TreeLayout


class ListDictWrapper(list):
    """
    A wrapper that behaves like both a list (for iteration) and a dict (for node_id indexing).
    """
    def __init__(self, data_list):
        super().__init__(data_list)
        self._dict = {item["node_id"]: item for item in data_list}

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._dict[key]
        return super().__getitem__(key)
    
@pytest.fixture
def sample_tree():
    return {
        "root": {
            "node": MagicMock(name="root_widget", setPos=MagicMock()),
            "node_type": "head",
            "childrens": {
                "child1": {
                    "node": MagicMock(name="child1_widget", setPos=MagicMock()),
                    "node_type": "leaf",
                    "af_value": "10"
                },
                "child2": {
                    "node": MagicMock(name="child2_widget", setPos=MagicMock()),
                    "node_type": "leaf",
                    "af_value": "15"
                }
            }
        }
    }



@pytest.fixture
def patched_tree_layout(sample_tree):
    flat_nodes_list = [
        {"node_id": "root", "parent_node": None, **sample_tree["root"]},
        {"node_id": "child1", "parent_node": "root", **sample_tree["root"]["childrens"]["child1"]},
        {"node_id": "child2", "parent_node": "root", **sample_tree["root"]["childrens"]["child2"]},
    ]
    wrapped_nodes = ListDictWrapper(flat_nodes_list)

    with patch.object(TreeLayout, 'get_treenodes_list', return_value=wrapped_nodes):
        yield TreeLayout(sample_tree)

def test_flatten_tree(sample_tree):
    layout = TreeLayout.__new__(TreeLayout)
    flat = layout.get_treenodes_list(sample_tree)
    assert isinstance(flat, list)
    assert any(n["node_id"] == "child1" and n["parent_node"] == "root" for n in flat)


def test_tree_hierarchy_building(patched_tree_layout):
    layout = patched_tree_layout
    assert layout.tree_nodes["root"].is_root
    assert layout.tree_nodes["child1"].parent.name == "root"
    assert layout.tree_nodes["child2"].parent.name == "root"


def test_layout_positions_are_computed(patched_tree_layout):
    layout = patched_tree_layout
    for node in layout.tree_nodes.values():
        assert isinstance(node.pos, tuple)
        assert all(isinstance(coord, (int, float)) for coord in node.pos)


def test_setPos_called_on_graphics_nodes(patched_tree_layout, sample_tree):
    assert sample_tree["root"]["node"].setPos.called
    assert sample_tree["root"]["childrens"]["child1"]["node"].setPos.called
    assert sample_tree["root"]["childrens"]["child2"]["node"].setPos.called
