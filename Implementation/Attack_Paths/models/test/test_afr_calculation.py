import pytest
from unittest.mock import patch
from Attack_Paths.models.afr_calculation import calculate_afr_values


@pytest.fixture
def mock_tree_with_control_head():
    """Tree containing a 'control head' node for residual AFR evaluation."""
    return {
        "root": {
            "node_type": "internal",
            "gate": "OR",
            "childrens": {
                "head_1": {
                    "node_type": "control head",
                    "childrens": {
                        "leaf_a": {"node_type": "leaf", "values": ["9", "9", "9"]},
                        "leaf_b": {"node_type": "leaf", "values": ["7", "7", "7"]}
                    }
                },
                "leaf_c": {
                    "node_type": "leaf",
                    "values": ["1", "2", "3"]
                }
            }
        }
    }


@pytest.fixture
def mock_tree_without_control_head():
    """Tree with no control head; residual AFR should be skipped."""
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
def mock_evaluator_results():
    """Mocked return value for AFR and RAFR evaluators."""
    return (["path1", "path2"], [0.5, 0.8], 1.3)


@patch("Attack_Paths.models.afr_calculation.AFRPathEvaluator")
@patch("Attack_Paths.models.afr_calculation.RAFRPathEvaluator")
def test_calculate_afr_with_resid(mock_rafr, mock_afr, mock_tree_with_control_head, mock_evaluator_results):
    """Test AFR and residual AFR for a tree with a control head (attack tree)."""
    mock_afr.return_value.find_optimal_path.return_value = mock_evaluator_results
    mock_rafr.return_value.find_optimal_path.return_value = mock_evaluator_results

    result = calculate_afr_values(mock_tree_with_control_head, "attack_tree")

    assert result["init_afr"]["path"] == mock_evaluator_results[0], "Initial AFR path mismatch"
    assert result["resid_afr"]["afr_sum"] == mock_evaluator_results[2], "Residual AFR sum mismatch"
    mock_afr.assert_called_once()
    mock_rafr.assert_called_once()


@patch("Attack_Paths.models.afr_calculation.AFRPathEvaluator")
@patch("Attack_Paths.models.afr_calculation.RAFRPathEvaluator")
def test_calculate_afr_no_resid_control_head_missing(mock_rafr, mock_afr, mock_tree_without_control_head, mock_evaluator_results):
    """Residual AFR should be skipped when no control head is present."""
    mock_afr.return_value.find_optimal_path.return_value = mock_evaluator_results

    result = calculate_afr_values(mock_tree_without_control_head, "attack_tree")

    assert result["init_afr"]["afr_vector"] == mock_evaluator_results[1], "Initial AFR vector mismatch"
    assert result["resid_afr"]["afr_sum"] is None, "Residual AFR should be None when no control head"
    mock_rafr.assert_not_called()


@patch("Attack_Paths.models.afr_calculation.AFRPathEvaluator")
def test_calculate_afr_for_technical_tree(mock_afr, mock_tree_without_control_head, mock_evaluator_results):
    """Residual AFR should be skipped for technical tree."""
    mock_afr.return_value.find_optimal_path.return_value = mock_evaluator_results

    result = calculate_afr_values(mock_tree_without_control_head, "technical_tree")

    assert result["init_afr"]["path"] == mock_evaluator_results[0], "Technical tree initial AFR path mismatch"
    assert result["resid_afr"] is None, "Residual AFR should be None for technical tree"


@patch("Attack_Paths.models.afr_calculation.AFRPathEvaluator")
def test_calculate_afr_for_control_tree(mock_afr, mock_tree_with_control_head, mock_evaluator_results):
    """Residual AFR should be skipped for control tree even if it has a control head."""
    mock_afr.return_value.find_optimal_path.return_value = mock_evaluator_results

    result = calculate_afr_values(mock_tree_with_control_head, "control_tree")

    assert result["init_afr"]["afr_sum"] == mock_evaluator_results[2], "Control tree initial AFR sum mismatch"
    assert result["resid_afr"] is None, "Residual AFR should be None for control tree"
