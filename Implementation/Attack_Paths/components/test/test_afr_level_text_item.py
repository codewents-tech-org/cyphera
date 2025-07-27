# test_afr_level_text_item.py

import pytest
from PyQt5.QtGui import QColor, QFontMetrics, QPainter, QImage
from PyQt5.QtCore import Qt, QRectF
from Attack_Paths.components.afr_level_text_item import AFR_level
import styles.tree_style as tree_style

@pytest.fixture
def afr_level_item():
    return AFR_level()

@pytest.mark.parametrize("text,expected_key", [
    ("High", "High_AFR_bg_color"),
    ("Medium", "Medium_AFR_bg_color"),
    ("Low", "Low_AFR_bg_color"),
    ("Very Low", "VeryLow_AFR_bg_color"),
    ("Unknown", "node_bg"),  # fallback case
])
def test_color_mapping(text, expected_key):
    afr = AFR_level(text)
    bg_color, border_color, font_color = afr.get_colors_based_on_text()
    expected = QColor(getattr(tree_style, expected_key))
    assert isinstance(bg_color, QColor)
    assert bg_color.name() == expected.name()


def test_bounding_rect_size(afr_level_item):
    """Ensure the bounding box is fixed to 80x30."""
    rect = afr_level_item.boundingRect()
    assert isinstance(rect, QRectF)
    assert rect.width() == 80
    assert rect.height() == 30


def test_ellipsized_text_truncation():
    """Test that long text gets truncated with ellipsis."""
    long_text = "This is a very long AFR level text"
    afr = AFR_level(long_text)
    metrics = QFontMetrics(afr.font())
    elided = metrics.elidedText(long_text, Qt.ElideRight, 80, 0)

    assert afr.toPlainText() == elided
    assert "..." in elided or len(elided) < len(long_text)


def test_set_plain_text_updates_internal_state():
    """Test setPlainText correctly sets full_text and renders elided."""
    afr = AFR_level()
    afr.setPlainText("High")
    assert afr.full_text == "High"
    assert afr.toPlainText() == "High"  # Should not ellipsize short strings

def test_paint_runs_without_error(qtbot):
    """Ensure paint method executes without throwing error."""
    afr = AFR_level("Medium")

    # Create a 100x50 image to simulate paint target
    image = QImage(100, 50, QImage.Format_ARGB32)
    image.fill(Qt.transparent)

    painter = QPainter(image)
    try:
        afr.paint(painter, option=None)
    finally:
        painter.end()  # ensure resources are released

    assert True  # If no exceptions, test passes