"""
Test Module: test_update_auto_leafs.py

Tests the `update_auto_leafs` function from the UI / Auto-Update Layer.

"""

import pytest
from unittest.mock import MagicMock
from Attack_Paths.controllers.auto_leafs_update import update_auto_leafs


class MockLabel:
    """Mock object to simulate PyQt QLabel/QGraphicsSimpleTextItem."""
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text

    def setText(self, val):
        self._text = val

    def setPlainText(self, val):
        self._text = val


@pytest.fixture
def mock_leaf_node():
    return {
        "node_id": "leaf_1",
        "node_type": "leaf",
        "node": type("LeafNode", (object,), {
            "title": MockLabel("MockLeaf"),
            "node_text": MockLabel(""),
            "af_value": MockLabel(""),
            "af_level": MockLabel(""),
            "values_label": [MockLabel("0") for _ in range(5)]
        })()
    }


@pytest.fixture
def mock_tree(mock_leaf_node):
    return {
        "node_id": "root",
        "node_type": "head",
        "node": MagicMock(),
        "childrens": [
            {
                "node_id": "intermediate_1",
                "node_type": "intermediate",
                "node": MagicMock(),
                "childrens": [
                    mock_leaf_node
                ]
            }
        ]
    }


def test_update_auto_leafs_with_afr_data(mock_tree):
    afr_data = {
        "values": ["1", "2", "3", "4", "5"],
        "afr_value": "15",
        "afr_level": "Medium"
    }

    update_auto_leafs(tree=mock_tree, node_label="MockLeaf", afr_data=afr_data)

def test_update_auto_leafs_with_afr_data1(mock_tree):
    afr_data = {
        "values": ["1", "2", "3", "4", "5"],
        "af_value": 15,
        "af_level": "Medium"
    }

    update_auto_leafs(tree=mock_tree, node_label="MockLeaf", afr_data=afr_data)

    leaf_node = mock_tree["childrens"][0]["childrens"][0]["node"]
    assert leaf_node.af_level.text() == "Medium"



def test_update_auto_leafs_with_text_only(mock_tree):
    update_auto_leafs(tree=mock_tree, node_label="MockLeaf", node_text="Updated Description")

    leaf_node = mock_tree["childrens"][0]["childrens"][0]["node"]
    assert leaf_node.node_text.text() == "Updated Description"


def test_no_update_when_tree_missing():
    assert update_auto_leafs(tree=None, node_label="MockLeaf", node_text="Text") is None


def test_no_update_when_data_missing(mock_tree):
    # Both afr_data and node_text are missing
    assert update_auto_leafs(tree=mock_tree, node_label="MockLeaf") is None
