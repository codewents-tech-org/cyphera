import pytest
from Attack_Paths.models.afr_level_calculation import calculate_afr_Level

@pytest.mark.parametrize("input_value,expected_level", [
    (0, "High"),
    (5, "High"),
    (13, "High"),
    (14, "Medium"),
    (16, "Medium"),
    (19, "Medium"),
    (20, "Low"),
    (22, "Low"),
    (24, "Low"),
    (25, "Very Low"),
    (100, "Very Low"),
])
def test_calculate_afr_level(input_value, expected_level):
    """Test AFR level classification based on score thresholds."""
    result = calculate_afr_Level(input_value)
    assert result == expected_level
