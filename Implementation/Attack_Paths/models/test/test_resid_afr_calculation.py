import pytest
from typing import Dict, Any
import logging
from Attack_Paths.models.resid_afr_calculation import RAFRPathEvaluator  # Adjust import as needed


@pytest.fixture
def sample_tree() -> Dict[str, Any]:
    return {
        "root": {
            "node_type": "internal",
            "gate": "OR",
            "childrens": {
                "head_1": {
                    "node_type": "control head",
                    "childrens": {
                        "leaf_a": {
                            "node_type": "leaf",
                            "values": ["9", "9", "9"]
                        },
                        "leaf_b": {
                            "node_type": "leaf",
                            "values": ["7", "7", "7"]
                        }
                    }
                },
                "leaf_c": {
                    "node_type": "leaf",
                    "values": ["1", "2", "3"]
                }
            }
        }
    }


def test_excludes_control_head_branch(sample_tree):
    evaluator = RAFRPathEvaluator(sample_tree)
    path, vector, total = evaluator.find_optimal_path()

    assert "head_1" not in path
    assert "leaf_a" not in path
    assert "leaf_b" not in path
    assert "leaf_c" in path

    assert vector == [1, 2, 3]
    assert total == sum(vector)


def test_empty_tree():
    evaluator = RAFRPathEvaluator({"root": {"node_type": "internal", "childrens": {}}})
    path, vector, total = evaluator.find_optimal_path()
    assert path == []
    assert vector == []
    assert total == float("inf")


def test_nested_control_head():
    tree = {
        "root": {
            "node_type": "internal",
            "gate": "OR",
            "childrens": {
                "ch": {
                    "node_type": "control head",
                    "childrens": {
                        "sub": {
                            "node_type": "internal",
                            "gate": "AND",
                            "childrens": {
                                "leaf_x": {
                                    "node_type": "leaf",
                                    "values": ["10", "10", "10"]
                                }
                            }
                        }
                    }
                },
                "leaf_ok": {
                    "node_type": "leaf",
                    "values": ["2", "2", "2"]
                }
            }
        }
    }
    evaluator = RAFRPathEvaluator(tree)
    path, vector, total = evaluator.find_optimal_path()

    assert "ch" not in path
    assert "leaf_x" not in path
    assert "leaf_ok" in path
    assert vector == [2, 2, 2]
    assert total == 6

def test_missing_node_is_logged(caplog):
    tree = {
        "root": {
            "node_type": "internal",
            "childrens": {
                "l1": {
                    "node_type": "leaf",
                    "values": ["1", "2", "3"]
                }
            }
        }
    }
    evaluator = RAFRPathEvaluator(tree)

    # Manually invoke compute_combined_afr with invalid node ID
    with caplog.at_level(logging.WARNING):
        afr_sum, vector, path = evaluator.compute_combined_afr(["root", "missing_node", "l1"])

    assert "missing_node" not in path
    assert afr_sum == sum([1, 2, 3])
    assert "Node missing_node not found." in caplog.text

def test_invalid_leaf_values_handled(caplog):
    tree = {
        "root": {
            "node_type": "internal",
            "childrens": {
                "leaf_bad": {
                    "node_type": "leaf",
                    "values": ["1", "x", "3"]  # 'x' will trigger ValueError
                }
            }
        }
    }
    evaluator = RAFRPathEvaluator(tree)

    caplog.set_level(logging.ERROR)

    afr_sum, vector, path = evaluator.compute_combined_afr(["root", "leaf_bad"])

    assert afr_sum == float("inf")
    assert vector == []
    assert path == []
    assert any("Invalid values in node leaf_bad" in message for message in caplog.messages)

