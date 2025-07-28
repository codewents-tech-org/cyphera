import pytest
from Attack_Paths.models.init_afr_calculation import AFRPathEvaluator  # Adjust path if needed


@pytest.fixture
def sample_valid_tree():
    return {
        "TH-1_node_0": {
            "node": "node_box_TH-1_node_0",
            "node_type": "head",
            "gate": "AND",
            "af_value": "0",
            "af_level": "High",
            "rf_value": "0",
            "rf_level": "High",
            "childrens": {
                "TH-1_node_1": {
                    "node": "node_box_TH-1_node_1",
                    "node_type": "intermediate",
                    "gate": "OR",
                    "childrens": {
                        "TH-1_node_2": {
                            "node": "node_box_TH-1_node_2",
                            "node_type": "leaf",
                            "values": ["1", "6", "3", "5", "0"]
                        },
                        "TH-1_node_3": {
                            "node": "node_box_TH-1_node_3",
                            "node_type": "leaf",
                            "values": ["0", "6", "0", "5", "0"]
                        }
                    }
                },
                "TH-1_node_4": {
                    "node": "node_box_TH-1_node_4",
                    "node_type": "leaf",
                    "values": ["1", "6", "2", "5", "0"]
                }
            }
        }
    }

@pytest.fixture
def sample_invalid_tree():
    return {
        "TH-1_node_0": {
            "node_type": "head",
            "gate": "AND",
            "childrens": {
                "TH-1_node_1": {
                    "node_type": "intermediate",
                    "gate": "OR",
                    "childrens": {
                        "TH-1_node_2": {
                            "node_type": "leaf",
                            "values": ["1", "6", "3", "5", "0"]
                        },
                        "TH-1_node_3": {
                            "node_type": "leaf",
                            "values": ["0", "6", "0", "5", "0"]
                        }
                    }
                },
                "TH-1_node_4": {
                    "node_type": "leaf",
                    "values": ["1", "6", "2", "5", "0"]
                },
                "TH-1_node_5": {
                    "node_type": "leaf"  # 🚫 No values key → should be skipped
                },
                "TH-1_node_6": {
                    "node_type": "intermediate",  # 🚫 Not a leaf
                    "childrens": {}
                }
            }
        }
    }


def test_optimal_path_output(sample_valid_tree):
    evaluator = AFRPathEvaluator(sample_valid_tree)
    best_path, afr_vector, afr_sum = evaluator.find_optimal_path()

    expected_path = ['TH-1_node_0', 'TH-1_node_1', 'TH-1_node_3', 'TH-1_node_4']
    expected_vector = [1, 6, 2, 5, 0]
    expected_sum = 14

    assert best_path == expected_path, f"Expected path: {expected_path}, got {best_path}"
    assert afr_vector == expected_vector, f"Expected vector: {expected_vector}, got {afr_vector}"
    assert afr_sum == expected_sum, f"Expected sum: {expected_sum}, got {afr_sum}"

def test_compute_combined_afr_no_values_case(sample_invalid_tree):
    """Ensure that path without any valid leaf values returns infinity and empty vector."""
    evaluator = AFRPathEvaluator(sample_invalid_tree)

    path = ["TH-1_node_5", "TH-1_node_6"]  # No valid leaf values
    afr_sum, afr_vector = evaluator.compute_combined_afr(path)

    assert afr_vector == []
    assert afr_sum == float('inf')
