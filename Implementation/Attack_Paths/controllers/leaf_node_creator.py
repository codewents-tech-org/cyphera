"""
Module: Leaf Node Creator      \n 
File: leaf_node_creator.py      \n
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
Visual representation and interaction logic for a leaf node within attack/control trees.

Description:
------------
A `LeafNodeBox` is a visual UI object representing a leaf in hierarchical trees.
It includes:
  - Editable text
  - Icon-based attribute entry
  - AFR calculation based on selected values
  - Real-time UI refresh for AFR value & level

Responsibilities
----------------
- Display five editable values using ClickableLabel
- Recalculate AFR dynamically on value change
- Display associated AFR level color-coded
- Emit signals for UI interaction and backend communication

Dependencies:
-------------
- PyQt5 for rendering and signals
- styles.tree_style for visual style
- file_utils for icons
- calculate_afr_Level for dynamic scoring
- custom components: NodeBackgroundItem, ClickableLabel, AFR_level

Classes:
-------------
- LeafNodeBox(QGraphicsObject)

Signals:
-------------
- removeRequested(tree_id: str)
- textEditedRequested(dict)
- valueChangedRequested(dict)

Limitations
-----------
- AFR calculation assumes 5 values and fixed positions
- No built-in drag or zoom
- Leaf node values are integers only

Improvements
------------
- Support dynamic number of leaf value categories
- Add tooltips or icons for better accessibility
- Integrate inline validation or scoring tooltip

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
    QGraphicsSimpleTextItem, QTextEdit, QGraphicsObject, QLabel
)
from PyQt5.QtCore import Qt, QRectF, QVariant, pyqtSignal, QRectF
from PyQt5.QtGui import QPen, QFont, QPixmap
import sys
import styles.tree_style as TS
from Attack_Paths.components.custom_node_box import NodeBackgroundItem
from Attack_Paths.models.tree_dict_validation import validate_node_config
from Attack_Paths.components.node_context_menus import build_graphics_node_context_menu
from Attack_Paths.components.customnode_text_editor import CustomTextEdit
from Attack_Paths.components.leaf_value_clickable import ClickableLabel
from Attack_Paths.components.afr_level_text_item import AFR_level  
from Attack_Paths.models.afr_level_calculation import calculate_afr_Level
import utils.file_utils as files
from Attack_Paths.controllers.get_node_list import (
    get_existing_leaf_nodes, get_existing_riskcontrol_tree, get_existing_technical_tree
)

class LeafNodeBox(QGraphicsObject):
    """Custom group container with styled rounded box and left-attached sidebar."""
    removeRequested = pyqtSignal(str)
    textEditedRequested = pyqtSignal(dict)
    valueChangedRequested = pyqtSignal(dict)

    required_fields = {"tree_id":"", "node_label":"", "node_Text": "", "x":0, "y":0, "af_value":"", "af_level":"", "values":["0", "0", "0", "0", "0"]}

    def __init__(self, node_config: dict, tree_type: str = ""):
        """
        Initializes the leaf node box with specified configuration.

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
        self.background = NodeBackgroundItem(self.total_width, self.total_height, self.sidebar_width, TS.leafnode_sidebar_color, parent=self)

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
        self.node_text.setFixedHeight(40)  # ~2 lines visually
        self.node_text.set_line_spacing(0.8)  # Set line spacing to 80% of default
        self.node_text.textEdited.connect(self.emit_text_edited)

        # Embed in proxy
        self.text_proxy = QGraphicsProxyWidget(self)
        self.text_proxy.setWidget(self.node_text)
        self.text_proxy.setFont(self.font)
        self.text_proxy.setPos(self.sidebar_width + 10, 25)

        # Horizontal line
        self.hline = QGraphicsLineItem(self.sidebar_width, 70, self.total_width - self.sidebar_width, 70, parent=self)
        self.hline.setPen(QPen(Qt.gray, 1))

        # Setup
        value_positions = [self.sidebar_width + 10, self.sidebar_width + 40, self.sidebar_width + 70, self.sidebar_width + 100, self.sidebar_width + 130]
        value_icons = [files.time_icon, files.Expertise_icon, files.Knowledge_icon, files.Access_icon, files.Equipment_icon]
        self.values_label = []

        for idx, vx in enumerate(value_positions):
            # Icon Row (X1)
            icon_label = QLabel()
            icon_label.setStyleSheet("background-color: transparent;")
            icon_label.setPixmap(QPixmap(value_icons[idx]))
            icon_label.setFixedSize(30, 30)
            icon_label.setAlignment(Qt.AlignCenter)

            icon_proxy = QGraphicsProxyWidget()
            icon_proxy.setWidget(icon_label)
            icon_proxy.setPos(vx, 80)
            icon_proxy.setParentItem(self)

            # Clickable Label Row (X2)
            text_label = ClickableLabel(index=idx)
            text_label.setText(config["values"][idx])
            text_label.setFixedSize(30, 20)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setFont(QFont(TS.node_font_family, 8, QFont.Normal))
            text_label.valueSelected.connect(self.emit_value_changed)
            self.values_label.append(text_label)

            label_proxy = QGraphicsProxyWidget()
            label_proxy.setWidget(text_label)
            label_proxy.setPos(vx, 105)  # X2 row just below icon
            label_proxy.setParentItem(self)

        # Vertical line
        self.vline = QGraphicsLineItem(self.sidebar_width + 180, 70, self.sidebar_width + 180, self.total_height, parent=self)
        self.vline.setPen(QPen(Qt.gray, 1))

        # AF Value Label
        self.af_value = QGraphicsSimpleTextItem(config["af_value"], parent=self)
        self.af_value.setFont(QFont(TS.node_font_family, 10, QFont.Bold))
        self.af_value.setPos(self.sidebar_width + 220, 70)

        # AF Level Label (stacked or adjust position if needed)
        self.af_level = AFR_level(config["af_level"])
        self.af_level.setParentItem(self)
        self.af_level.setPos(self.sidebar_width + 195, 95)  # Offset vertically to avoid overlap

    def paint(self, painter, option, widget=None):
        """
        No-op painter. Background and visuals are handled by children like NodeBackgroundItem.
        """
        pass

    def boundingRect(self) -> QRectF:
        """
        Returns the bounding rectangle of the entire node container.

        Returns:
            QRectF: Geometry bounds of the node.
        """
        return QRectF(0, 0, self.total_width, self.total_height)

    def contextMenuEvent(self, event):
        """
        Populates and shows a context menu for the leaf node.

        Args:
            event (QGraphicsSceneContextMenuEvent): Context event with mouse position.
        """
        self.available_leaf_nodes = get_existing_leaf_nodes()
        self.available_technical_trees = get_existing_technical_tree()
        self.available_control_trees = get_existing_riskcontrol_tree()

        menu = build_graphics_node_context_menu(self, insert_enable=False)
        menu.exec_(event.screenPos())
    
    def emit_text_edited(self, new_text):
        """
        Emits a signal when the node's text content is changed.

        Args:
            new_text (str): The updated node description.
        """
        node_label = self.title.text()
        self.textEditedRequested.emit({"node": self, "node_label":node_label, "text": new_text})

    def emit_value_changed(self, new_value):
        """
        Recalculates AFR and level based on updated values,
        then emits a signal to notify UI/backend.

        Args:
            new_value (str): The value that was changed by user.
        """
        values = []
        afr_value = 0
        for value in self.values_label:
            values.append(value.text())
        afr_value = sum(map(int, values))
        self.af_value.setText(str(afr_value))
        afr_level = calculate_afr_Level(afr_value)
        self.af_level.setPlainText(afr_level)
        node_label = self.title.text()
        self.valueChangedRequested.emit({"node": self, "node_label":node_label, "afr_data": {"values":values, "af_value":afr_value, "af_level":afr_level}})

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

    def highlight_box_border(self, color: str):
        self.background.set_border_color(color)
