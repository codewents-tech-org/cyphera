import pytest
from unittest.mock import patch
from Attack_Paths.controllers import afr_data_process


# === MOCK CLASSES ===
class MockLabel:
    def __init__(self, value: str):
        self._value = value

    def text(self):
        return self._value


class MockLeaf:
    def __init__(self, values=None):
        if values is None:
            values = ["1", "2", "3", "4", "5"]
        self.values_label = [MockLabel(v) for v in values]


class MockGateButton:
    def __init__(self, value: str = "AND"):
        self._value = value

    def text(self):
        return self._value


class MockHead:
    def __init__(self, gate="AND"):
        self.gate_button = MockGateButton(gate)


# === TESTS ===

def test_extract_node_info_leaf():

    node = {"node_id": "L1", "node_type": "leaf", "node": MockLeaf()}
    result = afr_data_process.extract_node_info(node)
    assert result["node_type"] == "leaf"
    assert result["values"] == ["1", "2", "3", "4", "5"]


def test_extract_node_info_with_children():

    tree = {
        "node_id": "H1",
        "node_type": "head",
        "node": MockHead("OR"),
        "childrens": [
            {
                "node_id": "L1",
                "node_type": "leaf",
                "node": MockLeaf()
            }
        ]
    }

    result = afr_data_process.extract_node_info(tree)
    assert result["node_type"] == "head"
    assert result["gate"] == "OR"
    assert "L1" in result["childrens"]
    assert result["childrens"]["L1"]["values"] == ["1", "2", "3", "4", "5"]


def test_process_tree_data_execution_unmocked():

    tree = {
        "node_id": "root",
        "node_type": "head",
        "node": MockHead("OR"),
        "childrens": [
            {
                "node_id": "leaf1",
                "node_type": "leaf",
                "node": MockLeaf(["1", "1", "1", "1", "1"])
            }
        ]
    }

    def dummy_afr_values(tree, tree_type):
        return {
            "init_afr": {"path": ["root", "leaf1"], "afr_vector": [1, 1, 1, 1, 1], "afr_sum": 5},
            "resid_afr": None
        }

    afr_data_process.calculate_afr_values = dummy_afr_values

    emitted = {"tree": tree, "tree_type": "technical_tree"}
    result = afr_data_process.process_tree_data(emitted)

    assert result["init_afr"]["afr_sum"] == 5
    assert result["resid_afr"] is None


def test_process_tree_data_input_validation():

    with pytest.raises(ValueError):
        afr_data_process.process_tree_data(None)

    with pytest.raises(ValueError):
        afr_data_process.process_tree_data({"tree": None, "tree_type": "attack_tree"})

    with pytest.raises(ValueError):
        afr_data_process.process_tree_data({"tree": {}, "tree_type": ""})


def test_calculate_afr_data_input_validation():

    with pytest.raises(ValueError):
        afr_data_process.calculate_afr_data("not-a-dict", "attack_tree")

    with pytest.raises(ValueError):
        afr_data_process.calculate_afr_data({}, 123)

    with pytest.raises(ValueError):
        afr_data_process.calculate_afr_data({}, "")


def test_process_tree_data_calculation_failure(monkeypatch):
    """Ensure exception block is triggered and logged on AFR calculation failure."""

    tree = {
        "node_id": "H1",
        "node_type": "head",
        "node": MockHead("AND"),
        "childrens": [
            {
                "node_id": "L1",
                "node_type": "leaf",
                "node": MockLeaf(["1", "2", "3", "4", "5"])
            }
        ]
    }

    # Patch backend to raise an exception
    def broken_backend(*args, **kwargs):
        raise RuntimeError("Simulated AFR failure")

    monkeypatch.setattr(afr_data_process, "calculate_afr_values", broken_backend)

    emitted = {"tree": tree, "tree_type": "technical_tree"}

    with pytest.raises(RuntimeError, match="Simulated AFR failure"):
        afr_data_process.process_tree_data(emitted)
