"""
Test Script: test_update_auto_intermediates.py

Purpose:
--------
Validates that `update_auto_intermediates()` correctly updates text fields on
intermediate nodes based on label match.

"""

import pytest
from unittest.mock import MagicMock
from Attack_Paths.controllers.auto_intermediates_update import update_auto_intermediates


class MockLabel:
    """Simulates a PyQt-style label-like object."""
    def __init__(self, text=""):
        self._text = text

    def text(self):
        return self._text

    def setText(self, new_val):
        self._text = new_val


@pytest.fixture
def mock_intermediate_node():
    """Creates a mock intermediate node with .title and .node_text."""
    return {
        "node_id": "int_1",
        "node_type": "intermediate",
        "node": type("IntermediateNode", (object,), {
            "title": MockLabel("Node-A"),
            "node_text": MockLabel("Original Text")
        })()
    }


@pytest.fixture
def mock_tree(mock_intermediate_node):
    """Builds a basic tree with head → intermediate."""
    return {
        "node_id": "root",
        "node_type": "head",
        "node": MagicMock(),
        "childrens": [
            mock_intermediate_node
        ]
    }


def test_update_auto_intermediate_success(mock_tree):
    update_auto_intermediates(
        tree=mock_tree,
        node_label="Node-A",
        node_text="Updated Text"
    )

    intermediate = mock_tree["childrens"][0]["node"]
    assert intermediate.node_text.text() == "Updated Text"


def test_no_update_if_label_mismatch(mock_tree):
    update_auto_intermediates(
        tree=mock_tree,
        node_label="DoesNotExist",
        node_text="Updated Text"
    )

    intermediate = mock_tree["childrens"][0]["node"]
    assert intermediate.node_text.text() == "Original Text"


def test_missing_tree_warns_and_skips(caplog):
    caplog.set_level("WARNING")
    update_auto_intermediates(tree=None, node_label="Node-A", node_text="New Text")
    assert "No tree provided" in caplog.text


def test_missing_text_warns_and_skips(caplog, mock_tree):
    caplog.set_level("WARNING")
    update_auto_intermediates(tree=mock_tree, node_label="Node-A", node_text=None)
    assert "No node text provided" in caplog.text
