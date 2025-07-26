"""
Module: Intermediate Node Creator      \n 
File: intermediate_node_creator.py      \n
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
Defines the graphical component representing an intermediate node in attack or control trees.

Description:
------------
This node allows insertion of new nodes, editing of textual descriptions, and toggling
of logical gates. It supports context menus, emits Qt signals to trigger UI actions, and
integrates with backend data for leaf/control/technical tree connections.

Responsibilities
----------------
- Render a structured, stylized box with editable and dynamic fields
- Provide gate toggle (AND/OR) functionality
- Handle right-click context menus and emit corresponding signals
- Support editing and signaling updated node text

Dependencies:
-------------
- PyQt5.QtWidgets / QtCore / QtGui
- styles.tree_style for visual theming
- custom components:
    - NodeBackgroundItem
    - CustomTextEdit
    - build_graphics_node_context_menu
    - get_node_list queries

Classes:
-------------
- IntermediateNodeBox(QGraphicsObject)

Signals:
-------------
- addIntermediateRequested(tree_id: str)
- addLeafRequested(tree_id: str, name: Optional[str] = None)
- addRiskControlTreeRequested(tree_id: str, name: str)
- addTechnicalTreeRequested(tree_id: str, name: str)
- gateSwitchRequested(tree_id: str)
- removeRequested(tree_id: str)
- textEditedRequested(dict)

Limitations
-----------
- Fixed width/height layout
- No inline label editing
- No resizing, collapsing, or accessibility hooks

Improvements
------------
- Refactor shared logic to a base class with HeadNodeBox
- Add mouse hover/drag interaction or focus indicators
- Support RTL text and multilingual labels

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
    QGraphicsSimpleTextItem, QTextEdit, QPushButton, QGraphicsObject
)
from PyQt5.QtCore import Qt, QRectF, QVariant, pyqtSignal, QRectF
from PyQt5.QtGui import QPen, QFont
import sys
import styles.tree_style as TS
from Attack_Paths.components.custom_node_box import NodeBackgroundItem
from Attack_Paths.models.tree_dict_validation import validate_node_config
from Attack_Paths.components.node_context_menus import build_graphics_node_context_menu
from Attack_Paths.components.customnode_text_editor import CustomTextEdit
from Attack_Paths.controllers.get_node_list import (
    get_existing_leaf_nodes, get_existing_riskcontrol_tree, get_existing_technical_tree
)

class IntermediateNodeBox(QGraphicsObject):
    """Custom intermediate node box for tree structures with styled layout and dynamic behavior."""
    addIntermediateRequested = pyqtSignal(dict)
    addLeafRequested = pyqtSignal(dict)
    addRiskControlTreeRequested = pyqtSignal(dict, str)
    addTechnicalTreeRequested = pyqtSignal(dict, str)
    gateSwitchRequested = pyqtSignal(str)
    removeRequested = pyqtSignal(str)
    textEditedRequested = pyqtSignal(dict)

    required_fields = {"tree_id":"", "node_label":"", "node_Text": "", "x":0, "y":0, "gate_type":""}

    def __init__(self, node_config: dict, tree_type: str = ""):
        """
        Initializes the intermediate node box with specified configuration.

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
        self.background = NodeBackgroundItem(self.total_width, self.total_height, self.sidebar_width, TS.intermediatenode_sidebar_color, parent=self)

        # Title label
        self.title = QGraphicsSimpleTextItem(config["node_label"], parent=self)
        self.title.setFont(QFont(TS.node_font_family, 10, QFont.Bold))
        self.title.setPos(self.sidebar_width + 10, 5)

        self.node_text = CustomTextEdit(config["node_Text"])
        self.node_text.setLineWrapMode(QTextEdit.WidgetWidth)
        self.node_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.node_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.node_text.setAcceptRichText(True)
        self.node_text.setStyleSheet(TS.node_textbox_style)
        self.node_text.setFixedHeight(60)  # ~2 lines visually
        self.node_text.set_line_spacing(0.8)  # Set line spacing to 80% of default
        self.node_text.textEdited.connect(self.emit_text_edited)


        # Embed in proxy
        self.text_proxy = QGraphicsProxyWidget(self)
        self.text_proxy.setWidget(self.node_text)
        self.text_proxy.setFont(self.font)
        self.text_proxy.setPos(self.sidebar_width + 10, 25)

        # Horizontal line
        self.hline = QGraphicsLineItem(self.sidebar_width, 90, self.total_width - self.sidebar_width, 90, parent=self)
        self.hline.setPen(QPen(Qt.gray, 1))

        self.gate_button = QPushButton(config["gate_type"])
        self.gate_button.setFont(QFont(TS.node_font_family, 10, QFont.Bold))
        self.gate_button.setStyleSheet(TS.attackpaths_gate_style)
        self.gate_button.setCursor(Qt.PointingHandCursor)
        self.gate_button.setFixedWidth(40)
        self.gate_button_proxy = QGraphicsProxyWidget(self)
        self.gate_button_proxy.setWidget(self.gate_button)
        self.gate_button_proxy.setPos(self.sidebar_width + 120, 100)
        self.gate_button.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Handles double-click on the gate button to toggle AND/OR logic.

        Args:
            source (QObject): Sender of the event.
            event (QEvent): Event object.

        Returns:
            bool: True if the event was handled.
        """
        if source == self.gate_button and event.type() == event.MouseButtonDblClick:
            self.gate_button.setText("AND" if self.gate_button.text() == "OR" else "OR")
            self.gateSwitchRequested.emit(self.tree_id)
            return True
        return False
    
    def paint(self, painter, option, widget=None):
        """
        Dummy paint function; actual visuals handled by child components.
        """
        pass

    def boundingRect(self) -> QRectF:
        """
        Defines the bounding box for this graphics object.

        Returns:
            QRectF: Size of the node box.
        """
        return QRectF(0, 0, self.total_width, self.total_height)

    def contextMenuEvent(self, event):
        """
        Builds and shows the context menu when user right-clicks the node.

        Args:
            event (QGraphicsSceneContextMenuEvent): Context menu event with cursor position.
        """
        self.available_leaf_nodes = get_existing_leaf_nodes()
        self.available_technical_trees = get_existing_technical_tree()
        self.available_control_trees = get_existing_riskcontrol_tree()

        menu = build_graphics_node_context_menu(self)
        menu.exec_(event.screenPos())

    def emit_add_riskcontrol_tree(self, name):
        """
        Emits signal to add a Risk Control Tree to this node.

        Args:
            name (str): Tree name.
        """
        self.addRiskControlTreeRequested.emit(self.tree_id, name)

    def emit_add_technical_tree(self, name):
        """
        Emits signal to add a Technical Tree to this node.

        Args:
            name (str): Tree name.
        """
        self.addTechnicalTreeRequested.emit(self.tree_id, name)

    def emit_text_edited(self, new_text):
        """
        Emits signal when the node's editable text was modified by the user.

        Args:
            new_text (str): Updated user text.
        """
        node_label = self.title.text()
        self.textEditedRequested.emit({"node": self, "node_label":node_label, "text": new_text})

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
