
import pytest
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import QPointF
from Attack_Paths.controllers.dynamic_arrow import DynamicArrow
from styles.tree_style import arrow_highlight_color, arrow_color


@pytest.fixture
def scene():
    return QGraphicsScene()


@pytest.fixture
def items():
    parent = QGraphicsRectItem(0, 0, 100, 50)
    child = QGraphicsRectItem(0, 0, 100, 50)
    parent.setPos(100, 100)
    child.setPos(200, 300)
    return parent, child


def test_arrow_added_to_scene(scene, items):
    parent, child = items
    scene.addItem(parent)
    scene.addItem(child)

    arrow = DynamicArrow(
        start_item=parent,
        end_item=child,
        scene=scene,
        parent_id="A",
        child_id="B",
        selected_path={"A", "B"}
    )

    # 3 lines + 1 arrowhead = 4 items expected
    items_in_scene = [item for item in scene.items() if item != parent and item != child]
    assert len(items_in_scene) == 4


def test_arrow_color_highlight(scene, items):
    parent, child = items
    scene.addItem(parent)
    scene.addItem(child)

    arrow = DynamicArrow(
        start_item=parent,
        end_item=child,
        scene=scene,
        parent_id="X",
        child_id="Y",
        selected_path={"X", "Y"}
    )

    # Line colors should match highlight color
    for line in arrow.lines:
        assert line.pen().color().name().lower() == arrow_highlight_color.lower()
    assert arrow.arrow_head.brush().color().name().lower() == arrow_highlight_color.lower()


def test_arrow_color_normal(scene, items):
    parent, child = items
    scene.addItem(parent)
    scene.addItem(child)

    arrow = DynamicArrow(
        start_item=parent,
        end_item=child,
        scene=scene,
        parent_id="X",
        child_id="Y",
        selected_path={"Z"}
    )

    for line in arrow.lines:
        assert line.pen().color().name().lower() == arrow_color.lower()
    assert arrow.arrow_head.brush().color().name().lower() == arrow_color.lower()


def test_arrow_reposition_updates_scene(scene, items):
    parent, child = items
    scene.addItem(parent)
    scene.addItem(child)

    arrow = DynamicArrow(
        start_item=parent,
        end_item=child,
        scene=scene,
        parent_id="A",
        child_id="B",
        selected_path={"A", "B"}
    )

    initial_positions = [line.line().p2() for line in arrow.lines]

    # Move child
    child.setPos(200, 400)
    arrow.update_position()

    updated_positions = [line.line().p2() for line in arrow.lines]

    assert initial_positions != updated_positions
