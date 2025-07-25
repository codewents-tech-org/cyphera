"""
Test Module: test_construct_node_info_map.py

Tests the construct_node_info_map function from the Backend / Tree Traversal layer.

"""

import pytest
from typing import Dict, Any
from Attack_Paths.models.build_node_info_tree import construct_node_info_map


class DummyNode:
    """
    Dummy PyQt-like node object for test simulation.
    """
    def __init__(self, label: str):
        self.label = label


@pytest.fixture
def sample_tree() -> Dict[str, Any]:
    return {
        "node_id": "root",
        "node_type": "head",
        "node": DummyNode("Root Node"),
        "childrens": [
            {
                "node_id": "intermediate_1",
                "node_type": "intermediate",
                "node": DummyNode("Intermediate Node 1"),
                "childrens": [
                    {
                        "node_id": "leaf_1",
                        "node_type": "leaf",
                        "node": DummyNode("Leaf Node 1"),
                    },
                    {
                        "node_id": "leaf_2",
                        "node_type": "leaf",
                        "node": DummyNode("Leaf Node 2"),
                    },
                ]
            },
            {
                "node_id": "intermediate_2",
                "node_type": "intermediate",
                "node": DummyNode("Intermediate Node 2"),
                "childrens": []
            }
        ]
    }


def test_construct_node_info_map_structure(sample_tree):
    """
    Verifies the recursive construction and structural correctness of node info map.
    """
    result = construct_node_info_map(sample_tree)

    assert isinstance(result, dict)
    assert result["node_type"] == "head"
    assert result["node"].label == "Root Node"
    assert "childrens" in result

    childrens = result["childrens"]
    assert isinstance(childrens, dict)
    assert "intermediate_1" in childrens
    assert "intermediate_2" in childrens

    # Intermediate 1 children
    inter1_children = childrens["intermediate_1"]["childrens"]
    assert "leaf_1" in inter1_children
    assert inter1_children["leaf_1"]["node_type"] == "leaf"
    assert inter1_children["leaf_1"]["node"].label == "Leaf Node 1"
    assert inter1_children["leaf_2"]["node"].label == "Leaf Node 2"

def test_leaf_nodes_have_no_children(sample_tree):
    """
    Ensures that leaf nodes do not include unnecessary 'childrens' keys.
    """
    result = construct_node_info_map(sample_tree)
    leaf_1 = result["childrens"]["intermediate_1"]["childrens"]["leaf_1"]
    assert "childrens" not in leaf_1


def test_node_metadata_accuracy(sample_tree):
    """
    Verifies that the metadata fields are correctly extracted.
    """
    result = construct_node_info_map(sample_tree)
    inter2 = result["childrens"]["intermediate_2"]
    assert inter2["node_type"] == "intermediate"
    assert isinstance(inter2["node"], DummyNode)
    assert inter2["node"].label == "Intermediate Node 2"
