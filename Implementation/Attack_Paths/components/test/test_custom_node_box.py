# test_custom_node_box.py

import pytest
from PyQt5.QtGui import QPainter, QImage, QColor
from PyQt5.QtCore import Qt, QRectF
from Attack_Paths.components.custom_node_box import NodeBackgroundItem


@pytest.fixture
def node_background_item():
    return NodeBackgroundItem(width=300, height=130, sidebar_width=10, sidebar_color="#ff0000")


def test_bounding_rect_size(node_background_item):
    """
    Ensure boundingRect() returns the expected QRectF dimensions.
    """
    rect = node_background_item.boundingRect()
    assert isinstance(rect, QRectF)
    assert rect.width() == 300
    assert rect.height() == 130


def test_sidebar_color_assignment():
    """
    Verify sidebar color is properly assigned to internal state.
    """
    node = NodeBackgroundItem(300, 130, sidebar_width=10, sidebar_color="#123456")
    assert node.sidebar_color.lower() == "#123456"


def test_paint_does_not_crash(qtbot):
    """
    Ensure paint() executes without throwing exceptions using a QImage painter.
    """
    item = NodeBackgroundItem(300, 130, sidebar_width=10, sidebar_color="#00ff00")

    # Create a QImage as paint surface
    image = QImage(400, 200, QImage.Format_ARGB32)
    image.fill(Qt.transparent)

    painter = QPainter(image)
    try:
        item.paint(painter, option=None)
    finally:
        painter.end()  # Must always end painter

    assert True  # If paint executes without crashing, test passes
