import pytest
from unittest.mock import MagicMock

from Attack_Paths.models.afr_level_calculation import calculate_afr_Level
from Attack_Paths.controllers import root_afr_data_update


@pytest.fixture
def mock_tree_node():
    """Fixture: Fake PyQt-like node with required AFR update fields."""
    node = MagicMock()
    node.af_value = MagicMock()
    node.af_level = MagicMock()
    node.rf_value = MagicMock()
    node.rf_level = MagicMock()
    return {
        "node": node,
        "node_id": "T1_root",
        "node_type": "head"
    }


@pytest.fixture
def mock_afr_output():
    """Fixture: Simulated AFR processing result."""
    return {
        "init_afr": {
            "afr_sum": 15,
            "afr_vector": [3, 2, 4, 3, 3],
            "path": ["T1_root", "L1"]
        },
        "resid_afr": {
            "afr_sum": 6,
            "afr_vector": [1, 1, 2, 1, 1],
            "path": ["T1_root", "L2"]
        }
    }


def test_head_node_afr_update_normal(monkeypatch, mock_tree_node, mock_afr_output):
    """Test normal update of AFR and Residual AFR values on head node."""

    # Patch process_tree_data to return mock results
    monkeypatch.setattr(
        root_afr_data_update,
        "process_tree_data",
        lambda emitted: mock_afr_output
    )

    # Run update
    root_afr_data_update.head_node_afr_update(mock_tree_node, "attack_tree")

    # Validate .setText and .setPlainText calls
    mock_node = mock_tree_node["node"]
    mock_node.af_value.setText.assert_called_once_with("15")
    mock_node.af_level.setPlainText.assert_called_once_with(calculate_afr_Level(15))
    mock_node.rf_value.setText.assert_called_once_with("6")
    mock_node.rf_level.setPlainText.assert_called_once_with(calculate_afr_Level(6))


def test_head_node_afr_update_with_inf(monkeypatch, mock_tree_node):
    """Test handling of 'inf' AFR values by substituting with 0."""
    afr_output = {
        "init_afr": {
            "afr_sum": float("inf"),
            "afr_vector": [],
            "path": []
        },
        "resid_afr": {
            "afr_sum": float("inf"),
            "afr_vector": [],
            "path": []
        }
    }

    monkeypatch.setattr(
        root_afr_data_update,
        "process_tree_data",
        lambda emitted: afr_output
    )

    root_afr_data_update.head_node_afr_update(mock_tree_node, "attack_tree")

    mock_node = mock_tree_node["node"]
    mock_node.af_value.setText.assert_called_once_with("0")
    mock_node.af_level.setPlainText.assert_called_once_with(calculate_afr_Level(0))
    mock_node.rf_value.setText.assert_called_once_with("0")
    mock_node.rf_level.setPlainText.assert_called_once_with(calculate_afr_Level(0))


def test_head_node_afr_update_without_residual(monkeypatch, mock_tree_node):
    """Test behavior when resid_afr is None (e.g. for technical trees)."""
    afr_output = {
        "init_afr": {
            "afr_sum": 10,
            "afr_vector": [2, 2, 2, 2, 2],
            "path": ["T1_root"]
        },
        "resid_afr": None
    }

    monkeypatch.setattr(
        root_afr_data_update,
        "process_tree_data",
        lambda emitted: afr_output
    )

    root_afr_data_update.head_node_afr_update(mock_tree_node, "technical_tree")

    mock_node = mock_tree_node["node"]
    mock_node.af_value.setText.assert_called_once_with("10")
    mock_node.af_level.setPlainText.assert_called_once_with(calculate_afr_Level(10))
    mock_node.rf_value.setText.assert_not_called()
    mock_node.rf_level.setPlainText.assert_not_called()
