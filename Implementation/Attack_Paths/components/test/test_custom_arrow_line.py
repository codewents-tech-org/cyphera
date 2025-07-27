
import pytest
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QColor, QPen
from Attack_Paths.components.custom_arrow_line import CustomArrowLine


@pytest.fixture
def scene():
    return QGraphicsScene()


def test_arrow_line_added_to_scene(scene):
    """Test that a CustomArrowLine can be added to a QGraphicsScene."""
    line = CustomArrowLine(0, 0, 100, 100, selected_color="#FF0000")
    scene.addItem(line)

    assert line in scene.items()
    assert isinstance(line, CustomArrowLine)


def test_arrow_line_geometry():
    """Test that the line has correct coordinates."""
    line = CustomArrowLine(10, 20, 30, 40, selected_color="#00FF00")
    qline = line.line()
    assert qline.x1() == 10
    assert qline.y1() == 20
    assert qline.x2() == 30
    assert qline.y2() == 40


def test_arrow_line_color():
    """Test that the pen has the correct color."""
    color = "#123456"
    line = CustomArrowLine(0, 0, 50, 50, selected_color=color)
    pen: QPen = line.pen()
    qcolor: QColor = pen.color()
    assert qcolor.name().lower() == color.lower()


def test_arrow_line_zvalue():
    """Ensure that the line draws beneath nodes (Z = -1)."""
    line = CustomArrowLine(0, 0, 50, 50)
    assert line.zValue() == -1
