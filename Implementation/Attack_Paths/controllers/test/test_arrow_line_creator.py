
import pytest
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import QPointF
from Attack_Paths.controllers.arrow_line_creator import ArrowRenderer


@pytest.fixture
def scene():
    return QGraphicsScene()


@pytest.fixture
def node_items():
    parent = QGraphicsRectItem(0, 0, 100, 50)
    child = QGraphicsRectItem(0, 0, 100, 50)
    parent.setPos(50, 50)
    child.setPos(200, 200)
    return parent, child


@pytest.fixture
def nodes_dict(node_items):
    parent, child = node_items
    return {
        "A": {"item": parent, "arrows": []},
        "B": {"item": child, "arrows": []}
    }


def test_create_arrow(scene, nodes_dict):
    renderer = ArrowRenderer(scene, nodes_dict, selected_path={"A", "B"}, threat_id="T1")

    renderer.create_arrow(nodes_dict["A"]["item"], nodes_dict["B"]["item"], "A", "B")

    assert len(renderer.arrows) == 1
    assert len(nodes_dict["A"]["arrows"]) == 1
    assert len(nodes_dict["B"]["arrows"]) == 1


def test_update_arrow_position(scene, nodes_dict):
    renderer = ArrowRenderer(scene, nodes_dict, selected_path={"A", "B"}, threat_id="T1")
    renderer.create_arrow(nodes_dict["A"]["item"], nodes_dict["B"]["item"], "A", "B")

    # Move B
    nodes_dict["B"]["item"].setPos(300, 300)
    renderer.update_arrow_position("B")

    # Still 1 arrow object and updated in-place
    assert len(renderer.arrows) == 1
    assert len(nodes_dict["B"]["arrows"]) == 1


def test_set_selected_path(scene, nodes_dict):
    renderer = ArrowRenderer(scene, nodes_dict, selected_path={"A", "B"}, threat_id="T1")
    renderer.create_arrow(nodes_dict["A"]["item"], nodes_dict["B"]["item"], "A", "B")

    old_arrow = renderer.arrows[0]

    new_path = {"A"}  # Only one node in the path
    renderer.set_selected_path(new_path)

    # Arrow object should still exist
    assert old_arrow in renderer.arrows
    # Arrow should now be referencing new path
    assert old_arrow.selected_path == new_path
