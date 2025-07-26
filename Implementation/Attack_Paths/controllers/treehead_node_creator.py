"""
Module: Tree Head Node Creator      \n 
File: treehead_node_creator.py      \n
Layer: UI / Graphics Scene Nodes    \n
Component ID:       \n
Requirement IDs:    \n
Author: Vijaya Karagi      \n
Created On: 2025-07-02     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Represents the top-most (head) node of a given hierarchical tree (e.g. ControlTree, TechnicalTree).

Description:
------------
The `TreeHeadNodeBox` visually represents the root node of a tree. It is styled with a sidebar
color that changes based on the tree type. The node contains a label, an optional description,
and a gate-type selector (e.g., AND/OR). It supports context menus and basic user interaction.

Responsibilities
----------------
- Visually render the head node using predefined styles
- Allow users to edit node description
- Handle gate-type button styling and logic
- Emit basic signals for text editing (and future expandability)

Dependencies:
-------------
- PyQt5
- styles.tree_style
- Attack_Paths.components: NodeBackgroundItem, CustomTextEdit, FixedHeightTextItem
- Attack_Paths.models.tree_dict_validation
- Attack_Paths.controllers.get_node_list

Classes:
-------------
- TreeHeadNodeBox(QGraphicsObject): Visual UI component for tree root node

Signals:
-------------
- removeRequested(tree_id: str)

Limitations
-----------
- No gate-switching logic implemented (button is static)
- Only supports one gate button, no child management
- Signal set is minimal (no addLeaf/addIntermediate emitters connected)

Improvements
------------
- Connect gate button to toggle logic
- Add support for attachable child trees (like attack head nodes)
- Support expanded menu options (e.g. convert tree type)

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-02           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from PyQt5.QtWidgets import (
    QGraphicsItem, QGraphicsLineItem, QGraphicsProxyWidget,
    QGraphicsSimpleTextItem, QPushButton, QGraphicsObject
)
from PyQt5.QtCore import Qt, QRectF, QVariant, pyqtSignal, QRectF
from PyQt5.QtGui import QPen, QFont
import sys
import styles.tree_style as TS
from Attack_Paths.components.custom_node_box import NodeBackgroundItem
from Attack_Paths.models.tree_dict_validation import validate_node_config
from Attack_Paths.components.node_context_menus import build_graphics_node_context_menu
from Attack_Paths.components.customnode_text_editor import CustomTextEdit, FixedHeightTextItem
from Attack_Paths.controllers.get_node_list import (
    get_existing_leaf_nodes, get_existing_riskcontrol_tree, get_existing_technical_tree
)

class TreeHeadNodeBox(QGraphicsObject):
    """Custom group container with styled rounded box and left-attached sidebar."""
    removeRequested = pyqtSignal(str)

    required_fields = {"tree_id":"", "node_label":"", "node_Text": "", "x":0, "y":0, "gate_type":"", "tree_type":""}

    def __init__(self, node_config: dict, tree_type: str = ""):
        """
        Initializes the tree head node box with specified configuration.

        Args:
            node_config (dict): Node data fields from database or UI input.
            tree_type (str): Type of tree the node belongs to.
        """
        super().__init__()
        self.tree_type = tree_type
        self.arrow_update_callback = None
        validate_node_config(node_config, self.required_fields.keys(), tree_type)

        # Merge with provided config
        config = {**self.required_fields, **node_config}
        # Assign attributes
        for key in self.required_fields:
            setattr(self, key, config[key])

        self.setFlag(self.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setPos(config["x"], config["y"])
        self.font = QFont(TS.node_font_family, 12, QFont.Normal)

        # Style Constants
        self.total_width = 300
        self.total_height = 130
        self.sidebar_width = 10

        # Create the background item
        sidebar_color = TS.intermediatenode_sidebar_color 
        if config["tree_type"] == "ControlTree":
            sidebar_color = TS.controlnode_sidebar_color
        elif config["tree_type"] == "TechnicalTree":
            sidebar_color = TS.technicalnode_sidebar_color
        self.background = NodeBackgroundItem(self.total_width, self.total_height, self.sidebar_width, sidebar_color, parent=self)

        # Title label
        self.title = QGraphicsSimpleTextItem(config["node_label"], parent=self)
        self.title.setFont(QFont(TS.node_font_family, 10, QFont.Bold))
        self.title.setPos(self.sidebar_width + 10, 5)

        self.node_text = FixedHeightTextItem(config["node_Text"], max_height=60, parent=self)
        self.node_text.setFont(QFont(TS.node_font_family, 8, QFont.Normal))
        self.node_text.setTextWidth(self.total_width - self.sidebar_width - 20)
        self.node_text.set_line_spacing(0.7)  # Set line spacing to 70%
        self.node_text.setPos(self.sidebar_width + 10, 25)

        # Horizontal line
        self.hline = QGraphicsLineItem(self.sidebar_width, 90, self.total_width - self.sidebar_width, 90, parent=self)
        self.hline.setPen(QPen(Qt.gray, 1))

        self.gate_button = QPushButton(config["gate_type"])
        self.gate_button.setFont(QFont(TS.node_font_family, 10, QFont.Bold))
        self.gate_button.setStyleSheet(TS.attackpaths_disablegate_style)
        self.gate_button.setFixedWidth(40)
        self.gate_button_proxy = QGraphicsProxyWidget(self)
        self.gate_button_proxy.setWidget(self.gate_button)
        self.gate_button_proxy.setPos(self.sidebar_width + 120, 100)

    def paint(self, painter, option, widget=None):
        """
        Dummy painter function. All painting is handled by child items like NodeBackgroundItem.
        """
        pass

    def boundingRect(self) -> QRectF:
        """
        Returns the bounding rectangle of this graphics item.

        Returns:
            QRectF: Bounding dimensions of the node.
        """
        return QRectF(0, 0, self.total_width, self.total_height)

    def contextMenuEvent(self, event):
        """
        Creates and shows a context menu on right-click.

        Args:
            event (QGraphicsSceneContextMenuEvent): Event containing the screen position.
        """
        self.available_leaf_nodes = get_existing_leaf_nodes()
        self.available_technical_trees = get_existing_technical_tree()
        self.available_control_trees = get_existing_riskcontrol_tree()

        menu = build_graphics_node_context_menu(self, insert_enable=False)
        menu.exec_(event.screenPos())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: QVariant) -> QVariant:
        """
        Triggered when the item's position is changed.

        Args:
            change (QGraphicsItem.GraphicsItemChange): Type of change.
            value (QVariant): New value.

        Returns:
            QVariant: Value to pass to the base class.
        """
        if change == QGraphicsItem.ItemPositionHasChanged and self.arrow_update_callback:
            self.arrow_update_callback(self.tree_id)
        return super().itemChange(change, value)
