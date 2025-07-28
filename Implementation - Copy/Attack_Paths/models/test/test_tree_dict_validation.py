import pytest
from Attack_Paths.models.tree_dict_validation import validate_node_config

REQUIRED_FIELDS = {
    "tree_id", "node_label", "node_Text", "x", "y", "af_value", "af_level", "rf_value", "rf_level", "gate_type", "tree_type"
}


def test_validation_passes_for_attack_tree():
    """Test that AttackTree with all required fields passes."""
    config = {
        "tree_id": "A001",
        "node_label": "Attack Node",
        "node_Text": "Root node",
        "x": 10,
        "y": 20,
        "af_value": "5",
        "af_level": "Low",
        "rf_value": "3",
        "rf_level": "High",
        "gate_type": "AND",
        "tree_type": "AttackTree"
    }

    validate_node_config(config, REQUIRED_FIELDS, "AttackTree")  # Should not raise


def test_validation_passes_for_technical_tree_without_rf():
    """TechnicalTree should not require rf_value or rf_level."""
    config = {
        "tree_id": "T001",
        "node_label": "Tech Node",
        "node_Text": "Tech desc",
        "x": 0,
        "y": 0,
        "af_value": "2",
        "af_level": "Medium",
        "gate_type": "OR",
        "tree_type": "TechnicalTree"
    }

    validate_node_config(config, REQUIRED_FIELDS, "TechnicalTree")  # Should not raise


def test_validation_fails_when_required_attack_fields_missing():
    """AttackTree missing a required key (like rf_value) should raise."""
    config = {
        "tree_id": "A002",
        "node_label": "Invalid Attack Node",
        "node_Text": "Missing RF field",
        "x": 0,
        "y": 0,
        "af_value": "1",
        "af_level": "High",
        "rf_level": "Low",  # Missing rf_value
        "gate_type": "AND",
        "tree_type": "AttackTree"
    }

    with pytest.raises(ValueError) as exc:
        validate_node_config(config, REQUIRED_FIELDS, "AttackTree")
    assert "rf_value" in str(exc.value)


def test_validation_fails_when_technical_tree_missing_required_non_rf():
    """TechnicalTree missing a non-RF field should raise error."""
    config = {
        "tree_id": "T002",
        "node_Text": "Missing label",
        "x": 0,
        "y": 0,
        "af_value": "3",
        "af_level": "High",
        "gate_type": "OR",
        "tree_type": "TechnicalTree"
    }

    with pytest.raises(ValueError) as exc:
        validate_node_config(config, REQUIRED_FIELDS, "TechnicalTree")
    assert "node_label" in str(exc.value)
