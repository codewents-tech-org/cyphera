"""
Module: Head Node Creator      \n 
File: head_node_creator.py      \n
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
Defines the graphical head node used in hierarchical tree editors (e.g., Attack Trees).

Description:
------------
This component represents a structured, styled, and signal-driven node
that acts as a container for AFR/AF values, labels, gate logic, and context menus.
Supports rendering via child components and interactive editing.

Responsibilities
----------------
- Display and format head node contents
- Emit signals for context actions (add leaf, add control tree, etc.)
- Display AFR and RF values with color-coded visual cues
- Provide context menu support via `node_context_menus`

Dependencies:
-------------
- PyQt5.QtWidgets / QtCore / QtGui
- custom components:
    - AFR_level
    - NodeBackgroundItem
    - FixedHeightTextItem
    - node_context_menus.build_graphics_node_context_menu
    - get_node_list (database access layer)

Classes:
-------------
- headNodeBox(QGraphicsObject):
    - Visual representation of the tree head node with signals and dynamic content.

Signals:
-------------
- addIntermediateRequested(tree_id: str)
- addLeafRequested(tree_id: str, name: Optional[str] = None)
- addRiskControlTreeRequested(tree_id: str, name: str)
- addTechnicalTreeRequested(tree_id: str, name: str)
- gateSwitchRequested(tree_id: str)
- arrowUpdateCallbackRequest = pyqtSignal(str)

Limitations
-----------
- Fixed dimensions (300x130)
- Only supports OR/AND gate toggling
- Assumes specific schema fields (e.g., rf_value, af_level)

Improvements
------------
- Make layout dynamic/responsive
- Add node-level validation feedback
- Support node drag/drop or move/resize
- Allow advanced node settings (e.g., custom gates, icons)

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
from Attack_Paths.components.afr_level_text_item import AFR_level  # Assuming this is the correct import path
import styles.tree_style as TS
from Attack_Paths.components.custom_node_box import NodeBackgroundItem
from Attack_Paths.models.tree_dict_validation import validate_node_config
from Attack_Paths.components.node_context_menus import build_graphics_node_context_menu
from Attack_Paths.components.customnode_text_editor import FixedHeightTextItem
from Attack_Paths.controllers.get_node_list import (
    get_existing_leaf_nodes, get_existing_riskcontrol_tree, get_existing_technical_tree
)

class headNodeBox(QGraphicsObject):
    """Custom group container with styled rounded box and left-attached sidebar."""
    addIntermediateRequested = pyqtSignal(dict)
    addLeafRequested = pyqtSignal(dict)
    addRiskControlTreeRequested = pyqtSignal(dict, str)
    addTechnicalTreeRequested = pyqtSignal(dict, str)
    gateSwitchRequested = pyqtSignal(str)

    required_fields = {"tree_id":"", "node_label":"", "node_Text": "", "x":0, "y":0, "af_value":"", "af_level":"", "rf_value":"", "rf_level":"", "gate_type":""}

    def __init__(self, node_config: dict, tree_type: str = ""):
        """
        Initializes a headNodeBox instance with config and visual layout.

        Args:
            node_config (dict): Node data with required fields.
            tree_type (str): Type of tree ("AttackTree", "RiskControlTree", etc.).
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
        self.font = QFont(TS.node_font_family, 10, QFont.Normal)

        # Style Constants
        self.total_width = 300
        self.total_height = 130
        self.sidebar_width = 10

        # Create the background item
        self.background = NodeBackgroundItem(self.total_width, self.total_height, self.sidebar_width, TS.headnode_sidebar_color, parent=self)

        # Title label
        self.title = QGraphicsSimpleTextItem(config["node_label"], parent=self)
        self.title.setFont(QFont(TS.node_font_family, 10, QFont.Bold))
        self.title.setPos(self.sidebar_width + 10, 5)

        self.node_text = FixedHeightTextItem(config["node_Text"], max_height=40, parent=self)
        self.node_text.setFont(QFont(TS.node_font_family, 8, QFont.Normal))
        self.node_text.setTextWidth(self.total_width - self.sidebar_width - 20)
        self.node_text.set_line_spacing(0.7)  # Set line spacing to 70%
        self.node_text.setPos(self.sidebar_width + 10, 25)

        # Horizontal line
        self.hline = QGraphicsLineItem(self.sidebar_width, 70, self.total_width - self.sidebar_width, 70, parent=self)
        self.hline.setPen(QPen(Qt.gray, 1))

        if tree_type == "AttackTree":
            # RF Value Label
            self.rf_value = QGraphicsSimpleTextItem(config["rf_value"], parent=self)
            self.rf_value.setFont(QFont(TS.node_font_family, 10, QFont.Bold))
            self.rf_value.setPos(self.sidebar_width + 40, 70)
            if config["rf_value"] == "":
                self.rf_value.setVisible(False)

            # RF Level Label (stacked or adjust position if needed)
            self.rf_level = AFR_level(config["rf_level"])
            self.rf_level.setParentItem(self)
            self.rf_level.setPos(self.sidebar_width + 15, 95)  # Offset vertically to avoid overlap
            if config["rf_level"] == "":
                self.rf_level.setVisible(False)

        self.gate_button = QPushButton(config["gate_type"])
        self.gate_button.setFont(QFont(TS.node_font_family, 10, QFont.Bold))
        self.gate_button.setStyleSheet(TS.attackpaths_gate_style)
        self.gate_button.setCursor(Qt.PointingHandCursor)
        self.gate_button.setFixedWidth(40)
        self.gate_button_proxy = QGraphicsProxyWidget(self)
        self.gate_button_proxy.setWidget(self.gate_button)
        self.gate_button_proxy.setPos(self.sidebar_width + 120, 100)
        self.gate_button.installEventFilter(self)

        # AF Value Label
        self.af_value = QGraphicsSimpleTextItem(config["af_value"], parent=self)
        self.af_value.setFont(QFont(TS.node_font_family, 10, QFont.Bold))
        self.af_value.setPos(self.sidebar_width + 220, 70)

        # AF Level Label (stacked or adjust position if needed)
        self.af_level = AFR_level(config["af_level"])
        self.af_level.setParentItem(self)
        self.af_level.setPos(self.sidebar_width + 195, 95)  # Offset vertically to avoid overlap

    def eventFilter(self, source, event):
        """
        Handles double-click to toggle gate type between AND and OR.

        Args:
            source: QObject (QPushButton)
            event: QEvent

        Returns:
            bool: True if handled.
        """
        if source == self.gate_button and event.type() == event.MouseButtonDblClick:
            self.gate_button.setText("AND" if self.gate_button.text() == "OR" else "OR")
            self.gateSwitchRequested.emit(self.tree_id)
            return True
        return False
    
    def paint(self, painter, option, widget=None):
        """
        No-op since painting is handled by NodeBackgroundItem.
        """
        pass

    def boundingRect(self) -> QRectF:
        """
        Returns bounding box for the node.

        Returns:
            QRectF: Rectangle enclosing the node content.
        """
        return QRectF(0, 0, self.total_width, self.total_height)

    def contextMenuEvent(self, event):
        """
        Populates and executes a right-click context menu.

        Args:
            event (QGraphicsSceneContextMenuEvent): Mouse event with position.
        """
        self.available_leaf_nodes = get_existing_leaf_nodes()
        self.available_technical_trees = get_existing_technical_tree()
        self.available_control_trees = get_existing_riskcontrol_tree()

        menu = build_graphics_node_context_menu(self, is_rootnode=True)
        menu.exec_(event.screenPos())
    
    def emit_add_riskcontrol_tree(self, name):
        """
        Emits signal to attach a Risk Control Tree by name.
        """
        self.addRiskControlTreeRequested.emit(self.tree_id, name)

    def emit_add_technical_tree(self, name):
        """
        Emits signal to attach a Technical Tree by name.
        """
        self.addTechnicalTreeRequested.emit(self.tree_id, name)

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