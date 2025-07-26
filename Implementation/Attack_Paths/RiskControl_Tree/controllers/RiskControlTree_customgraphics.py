

import sys
from PyQt5.QtWidgets import (QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsItem, QFrame,
                             QGraphicsItemGroup, QMenu, QAction, QComboBox, QGraphicsView, QGraphicsProxyWidget
                            )   
from PyQt5.QtGui import QFont, QColor, QPen, QFontMetrics, QPainter, QBrush, QPainterPath, QTextOption
from PyQt5.QtCore import Qt, QRectF
import models.Parameters as P
import controllers.DatabaseCreator as DB
import sqlite3
import styles.tree_style as tree_style
import utils.interface_utils as interfaces
from controllers.schema_manager import get_instances
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome, AttackLeafNodes

import logging
logger = logging.getLogger(__name__)

class CustomGraphicsRemoveItem(QGraphicsProxyWidget):
    def __init__(self, node_id, parent=None, riskcontrol_tree_parent=None):
        logger.debug(f"CustomGraphicsRemoveItem.__init__ called with node_id={node_id}, parent={parent}, riskcontrol_tree_parent={riskcontrol_tree_parent}")
        super().__init__(parent)
        logger.info("CustomGraphicsRemoveItem")
        self.node_id = node_id
        self.riskcontrol_tree_parent = riskcontrol_tree_parent
        logger.debug("CustomGraphicsRemoveItem initialized: node_id=%s", self.node_id)

    def contextMenuEvent(self, event):
        logger.info("CustomGraphicsRemoveItem contextMenuEvent")
        logger.debug(f"CustomGraphicsRemoveItem.contextMenuEvent called for node_id={self.node_id} with event={event}")
        context_menu = QMenu()
        
        switch_action = QAction("remove node")
        switch_action.triggered.connect(lambda: self.riskcontrol_tree_parent.Remove_Node(self.node_id))
        context_menu.addAction(switch_action)
        logger.debug("CustomGraphicsRemoveItem context menu created with 'remove node' action.")

        pos = event.screenPos() if hasattr(event, 'screenPos') else None
        logger.debug(f"CustomGraphicsRemoveItem showing context menu at screenPos={pos}")
        context_menu.exec_(pos)
        logger.debug("CustomGraphicsRemoveItem context menu executed/completed.")


class EditableTextItem(QGraphicsTextItem):
    def __init__(self, text='', parent=None, fixed_width=200, node_id='', riskcontrol_tree_parent=None):
        logger.debug(f"EditableTextItem.__init__ called with text='{text}', parent={parent}, fixed_width={fixed_width}, node_id='{node_id}', riskcontrol_tree_parent={riskcontrol_tree_parent}")
        super().__init__(text, parent)
        logger.info("EditableTextItem initialized")
        self.riskcontrol_tree_parent = riskcontrol_tree_parent
        self.node_id = node_id
        self.fixed_width = fixed_width
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)

        # Set fixed width for the item
        self.setTextWidth(self.fixed_width)

        # Store the full text
        self.full_text = text
        logger.debug(f"EditableTextItem: set full_text = '{self.full_text}'")
        self.update_display_text()

    def contextMenuEvent(self, event):
        logger.debug("EditableTextItem.contextMenuEvent called")
        pass

    def update_display_text(self):
        logger.info("EditableTextItem.update_display_text called")
        logger.debug(f"EditableTextItem.update_display_text: self.full_text = '{self.full_text}'")
        self.setPlainText(self.full_text)

    def focusOutEvent(self, event):
        logger.debug(f"EditableTextItem.focusOutEvent called for node_id='{self.node_id}'")
        new_text = self.toPlainText()
        logger.debug(f"EditableTextItem.focusOutEvent: new_text='{new_text}', old full_text='{self.full_text}'")
        if new_text != self.full_text:  # Check if text has changed
            logger.info("EditableTextItem.focusOutEvent: Text changed, updating.")
            self.full_text = new_text
            self.update_display_text()
            if self.riskcontrol_tree_parent is not None:
                logger.debug("EditableTextItem.focusOutEvent: Triggering Auto_Update_Leaf_name")
                interfaces.unsaved_changes = True
                self.riskcontrol_tree_parent.Auto_Update_Leaf_name(self.node_id)
        else:
            logger.debug("EditableTextItem.focusOutEvent: No text change.")
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        logger.debug(f"EditableTextItem.keyPressEvent: key={event.key()} for node_id='{self.node_id}'")
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            new_text = self.toPlainText()
            logger.debug(f"EditableTextItem.keyPressEvent: new_text='{new_text}', old full_text='{self.full_text}'")
            if new_text != self.full_text:  # Check if text has changed
                logger.info("EditableTextItem.keyPressEvent: Text changed, updating.")
                self.full_text = new_text
                self.update_display_text()
            if self.riskcontrol_tree_parent is not None:
                logger.debug("EditableTextItem.keyPressEvent: Triggering Auto_Update_Leaf_name")
                interfaces.unsaved_changes = True
                self.riskcontrol_tree_parent.Auto_Update_Leaf_name(self.node_id)
            self.clearFocus()  # Optionally remove focus
        else:
            logger.debug("EditableTextItem.keyPressEvent: Default handler for key press.")
            super().keyPressEvent(event)

    def boundingRect(self, height = ''):
        logger.debug(f"EditableTextItem.boundingRect called with height='{height}' (ignored, fixed 40px)")
        rect = super().boundingRect()
        logger.debug(f"EditableTextItem.boundingRect: rect={rect}, fixed_width={self.fixed_width}")
        return QRectF(rect.x(), rect.y(), self.fixed_width, 40)

class CustomGraphicsEditItem(QGraphicsProxyWidget):
    def __init__(self, node_id, parent=None, riskcontrol_tree_parent=None):
        logger.info(f"CustomGraphicsEditItem.__init__ | node_id={node_id}, parent={parent}, riskcontrol_tree_parent={riskcontrol_tree_parent}")
        super().__init__(parent)
        self.node_id = node_id
        self.riskcontrol_tree_parent = riskcontrol_tree_parent

    def contextMenuEvent(self, event):
        logger.info(f"CustomGraphicsEditItem.contextMenuEvent | node_id={self.node_id}")

        # Create a context menu
        menu = QMenu()
        logger.debug("CustomGraphicsEditItem.contextMenuEvent | Created base menu")

        intermediatenode_action = QAction("Add Intermediate Node", menu)
        intermediatenode_action.triggered.connect(lambda: self.riskcontrol_tree_parent.Add_Child_Node(self.node_id, "intermediate"))
        menu.addAction(intermediatenode_action)
        logger.debug("CustomGraphicsEditItem.contextMenuEvent | Added 'Add Intermediate Node' action")

        leafnode_menu = QMenu("Add Leaf Node", menu)
        add_newleaf_action = QAction("New Leaf", leafnode_menu)
        add_newleaf_action.triggered.connect(lambda: self.riskcontrol_tree_parent.Add_Child_Node(self.node_id, "new_leaf"))
        logger.debug("CustomGraphicsEditItem.contextMenuEvent | Added 'New Leaf' action to leafnode_menu")

        add_existingleaf_menu = QMenu("Existing Leaf", leafnode_menu)
        saved_leaf_nodes = get_existing_leaf_nodes()
        logger.debug(f"CustomGraphicsEditItem.contextMenuEvent | Fetched saved_leaf_nodes: {saved_leaf_nodes}")

        # If no saved leaf nodes are found, disable the option
        if not saved_leaf_nodes:
            logger.debug("CustomGraphicsEditItem.contextMenuEvent | No saved_leaf_nodes found")
            no_leaf_action = QAction("Leaf Nodes not available", add_existingleaf_menu)
            no_leaf_action.setEnabled(False)
            add_existingleaf_menu.addAction(no_leaf_action)
        else:
            for leaf_name in saved_leaf_nodes:
                logger.debug(f"CustomGraphicsEditItem.contextMenuEvent | Adding existing leaf: {leaf_name}")
                leaf_action = QAction(leaf_name, add_existingleaf_menu)
                leaf_action.triggered.connect(lambda checked, name=leaf_name: self.riskcontrol_tree_parent.Add_Child_Node(self.node_id, "existing_leaf", name))
                add_existingleaf_menu.addAction(leaf_action)

        leafnode_menu.addAction(add_newleaf_action)
        leafnode_menu.addMenu(add_existingleaf_menu)
        menu.addMenu(leafnode_menu)
        logger.debug("CustomGraphicsEditItem.contextMenuEvent | Leaf node menus constructed and added to menu")

        add_existingtechnical_menu = QMenu("Add Technical Tree")
        saved_technical_tree = get_existing_technical_tree()
        logger.debug(f"CustomGraphicsEditItem.contextMenuEvent | Fetched saved_technical_tree: {saved_technical_tree}")

        # If no saved technical tree are found, disable the option
        if not saved_technical_tree:
            logger.debug("CustomGraphicsEditItem.contextMenuEvent | No saved_technical_tree found")
            no_technicaltree_action = QAction("Technical trees not available", add_existingtechnical_menu)
            no_technicaltree_action.setEnabled(False)
            add_existingtechnical_menu.addAction(no_technicaltree_action)
        else:
            for technical_name in saved_technical_tree:
                logger.debug(f"CustomGraphicsEditItem.contextMenuEvent | Adding technical tree: {technical_name}")
                technical_action = QAction(technical_name, add_existingtechnical_menu)
                technical_action.triggered.connect(lambda checked, name=technical_name: self.riskcontrol_tree_parent.Add_Technical_Tree(self.node_id, name))
                add_existingtechnical_menu.addAction(technical_action)
        menu.addMenu(add_existingtechnical_menu)
        logger.debug("CustomGraphicsEditItem.contextMenuEvent | Technical tree menus constructed and added to menu")

        removenode_action = QAction("remove node", menu)
        menu.addAction(removenode_action)
        removenode_action.triggered.connect(lambda: self.riskcontrol_tree_parent.Remove_Node(self.node_id))
        logger.debug("CustomGraphicsEditItem.contextMenuEvent | Added 'remove node' action")

        logger.info("CustomGraphicsEditItem.contextMenuEvent | Displaying context menu")
        menu.exec_(event.screenPos())

class CustomGraphicsNonEditItem(QGraphicsProxyWidget):
    def __init__(self, node_id, parent=None, riskcontrol_tree_parent=None):
        logger.info(f"CustomGraphicsNonEditItem.__init__ | node_id={node_id}, parent={parent}, riskcontrol_tree_parent={riskcontrol_tree_parent}")
        super().__init__(parent)
        self.node_id = node_id
        self.riskcontrol_tree_parent = riskcontrol_tree_parent
        
    def contextMenuEvent(self, event):
        logger.info(f"CustomGraphicsNonEditItem.contextMenuEvent | node_id={self.node_id}")

        # Create a context menu
        menu = QMenu()
        logger.debug("CustomGraphicsNonEditItem.contextMenuEvent | Created base menu")

        intermediatenode_action = QAction("Add Intermediate Node", menu)
        intermediatenode_action.triggered.connect(lambda: self.riskcontrol_tree_parent.Add_Child_Node(self.node_id, "intermediate"))
        menu.addAction(intermediatenode_action)
        logger.debug("CustomGraphicsNonEditItem.contextMenuEvent | Added 'Add Intermediate Node' action")

        leafnode_menu = QMenu("Add Leaf Node", menu)
        add_newleaf_action = QAction("New Leaf", leafnode_menu)
        add_newleaf_action.triggered.connect(lambda: self.riskcontrol_tree_parent.Add_Child_Node(self.node_id, "new_leaf"))
        logger.debug("CustomGraphicsNonEditItem.contextMenuEvent | Added 'New Leaf' action to leafnode_menu")

        add_existingleaf_menu = QMenu("Existing Leaf", leafnode_menu)
        saved_leaf_nodes = get_existing_leaf_nodes()
        logger.debug(f"CustomGraphicsNonEditItem.contextMenuEvent | Fetched saved_leaf_nodes: {saved_leaf_nodes}")

        # If no saved leaf nodes are found, disable the option
        if not saved_leaf_nodes:
            logger.debug("CustomGraphicsNonEditItem.contextMenuEvent | No saved_leaf_nodes found")
            no_leaf_action = QAction("Leaf Nodes not available", add_existingleaf_menu)
            no_leaf_action.setEnabled(False)
            add_existingleaf_menu.addAction(no_leaf_action)
        else:
            for leaf_name in saved_leaf_nodes:
                logger.debug(f"CustomGraphicsNonEditItem.contextMenuEvent | Adding existing leaf: {leaf_name}")
                leaf_action = QAction(leaf_name, add_existingleaf_menu)
                leaf_action.triggered.connect(lambda checked, name=leaf_name: self.riskcontrol_tree_parent.Add_Child_Node(self.node_id, "existing_leaf", name ))
                add_existingleaf_menu.addAction(leaf_action)

        leafnode_menu.addAction(add_newleaf_action)
        leafnode_menu.addMenu(add_existingleaf_menu)
        menu.addMenu(leafnode_menu)
        logger.debug("CustomGraphicsNonEditItem.contextMenuEvent | Leaf node menus constructed and added to menu")

        add_existingtechnical_menu = QMenu("Add Technical Tree")
        saved_technical_tree = get_existing_technical_tree()
        logger.debug(f"CustomGraphicsNonEditItem.contextMenuEvent | Fetched saved_technical_tree: {saved_technical_tree}")

        # If no saved technical tree are found, disable the option
        if not saved_technical_tree:
            logger.debug("CustomGraphicsNonEditItem.contextMenuEvent | No saved_technical_tree found")
            no_technicaltree_action = QAction("Technical trees not available", add_existingtechnical_menu)
            no_technicaltree_action.setEnabled(False)
            add_existingtechnical_menu.addAction(no_technicaltree_action)
        else:
            for technical_name in saved_technical_tree:
                logger.debug(f"CustomGraphicsNonEditItem.contextMenuEvent | Adding technical tree: {technical_name}")
                technical_action = QAction(technical_name, add_existingtechnical_menu)
                technical_action.triggered.connect(lambda checked, name=technical_name: self.riskcontrol_tree_parent.Add_Technical_Tree(self.node_id, name))
                add_existingtechnical_menu.addAction(technical_action)
        menu.addMenu(add_existingtechnical_menu)
        logger.debug("CustomGraphicsNonEditItem.contextMenuEvent | Technical tree menus constructed and added to menu")

        logger.info("CustomGraphicsNonEditItem.contextMenuEvent | Displaying context menu")
        # Show the context menu
        menu.exec_(event.screenPos())

class AFR_level(QGraphicsTextItem):
    def __init__(self, text=''):
        logger.info(f"AFR_level.__init__ | text={text}")
        super().__init__()
        # Set fixed width for the item
        self.setTextWidth(90)
        # Store the full text
        self.full_text = text
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        # Update display text and apply styling
        self.update_display_text()

    def setPlainText(self, text):
        logger.info(f"AFR_level.setPlainText | text={text}")
        self.full_text = text
        super().setPlainText(text)
        self.update_display_text()

    def update_display_text(self):
        logger.info(f"AFR_level.update_display_text | full_text={self.full_text}")
        font_metrics = QFontMetrics(self.font())
        elided_text = font_metrics.elidedText(self.full_text, Qt.ElideRight, 90, 0)
        super().setPlainText(elided_text)
        self.update()

    def paint(self, painter, option, widget=None):
        logger.debug(f"AFR_level.paint | Painting AFR level box: '{self.full_text}'")
        background_color, border_color, text_color = self.get_colors_based_on_text()
        background_color.setAlpha(50)
        rect = self.boundingRect()
        path = QPainterPath()
        corner_radius = 10
        path.addRoundedRect(rect, corner_radius, corner_radius)
        painter.setBrush(QBrush(background_color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)
        border_pen = QPen(border_color, 1)
        painter.setPen(border_pen)
        painter.drawPath(path)
        painter.setPen(text_color)
        text_option = QTextOption(Qt.AlignCenter)
        text_option.setWrapMode(QTextOption.NoWrap)
        painter.drawText(rect, self.full_text, text_option)

    def get_colors_based_on_text(self):
        logger.debug(f"AFR_level.get_colors_based_on_text | full_text={self.full_text}")
        if self.full_text == 'High':
            return QColor(tree_style.High_AFR_bg_color), QColor(tree_style.High_AFR_border_color), QColor(tree_style.High_AFR_Font_color) 
        elif self.full_text == 'Medium':
            return QColor(tree_style.Medium_AFR_bg_color), QColor(tree_style.Medium_AFR_border_color), QColor(tree_style.Medium_AFR_Font_color) 
        elif self.full_text == 'Low':
            return QColor(tree_style.Low_AFR_bg_color), QColor(tree_style.Low_AFR_border_color), QColor(tree_style.Low_AFR_Font_color)
        elif self.full_text == 'Very Low':
            return QColor(tree_style.VeryLow_AFR_bg_color), QColor(tree_style.VeryLow_AFR_border_color), QColor(tree_style.VeryLow_AFR_Font_color)
        else:
            return QColor(tree_style.node_bg), QColor(tree_style.node_bg), QColor(tree_style.node_bg)

class AFR_value(QGraphicsTextItem):
    def __init__(self, text=''):
        logger.info(f"AFR_value.__init__ | text={text}")
        super().__init__()
        self.full_text = text
        self.setFont(QFont("poppins", 9, QFont.Bold))
        self.update_text_color()

    def setPlainText(self, text):
        logger.info(f"AFR_value.setPlainText | text={text}")
        self.full_text = text
        super().setPlainText(text)
        self.update_text_color()

    def update_text_color(self):
        logger.info(f"AFR_value.update_text_color | full_text={self.full_text}")
        try:
            value = int(self.full_text)
        except Exception as e:
            logger.error(f"AFR_value.update_text_color | Error parsing value: {e}")
            value = 0
        if value >= 0 and value <= 13:
            color =  QColor(tree_style.High_AFR_Font_color) 
        elif value >= 14 and value <= 19:
            color =  QColor(tree_style.Medium_AFR_Font_color) 
        elif value >= 20 and value <= 24:
            color =  QColor(tree_style.Low_AFR_Font_color)
        else :
            color =  QColor(tree_style.VeryLow_AFR_Font_color)
        self.setDefaultTextColor(color)

class SidebarItem(QGraphicsTextItem):
    def __init__(self, text='', bg_color='white'):
        logger.info(f"SidebarItem.__init__ | text={text} bg_color={bg_color}")
        super().__init__()
        self.setTextWidth(10)
        self.sidebar_color = bg_color
        self.full_text = text
        self.update_display_text()

    def update_bg_color(self, color_bg):
        logger.info(f"SidebarItem.update_bg_color | color_bg={color_bg}")
        self.sidebar_color = color_bg
        self.update_display_text()

    def setPlainText(self, text):
        logger.info(f"SidebarItem.setPlainText | text={text}")
        self.full_text = text
        super().setPlainText(text)
        self.update_display_text()

    def update_display_text(self):
        logger.info(f"SidebarItem.update_display_text | full_text={self.full_text}")
        font_metrics = QFontMetrics(self.font())
        elided_text = font_metrics.elidedText(self.full_text, Qt.ElideRight, 90, 0)
        super().setPlainText(elided_text)
        self.update()

    def boundingRect(self):
        logger.debug("SidebarItem.boundingRect")
        return QRectF(0, 0, 10, 130)

    def paint(self, painter, option, widget=None):
        logger.debug(f"SidebarItem.paint | sidebar_color={self.sidebar_color}")
        background_color = QColor(self.sidebar_color)
        rect = self.boundingRect()
        path = QPainterPath()
        corner_radius = 10
        path.moveTo(rect.topLeft())
        path.moveTo(rect.bottomLeft())
        path.addRoundedRect(rect.adjusted(0, 0, 0, 0), corner_radius, corner_radius)
        painter.setBrush(QBrush(background_color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

class CustomGraphicsTextItem(QGraphicsTextItem):
    def __init__(self, text, width=100, height=50, parent=None, font=None):
        logger.info(f"CustomGraphicsTextItem.__init__ | text={text}, width={width}, height={height}")
        super().__init__(text, parent)
        self._fixed_width = width
        self._fixed_height = height
        if font:
            self.setFont(font)
        self.setTextWidth(self._fixed_width)
        self.setClippingEnabled(True)

    def setClippingEnabled(self, enabled):
        logger.info(f"CustomGraphicsTextItem.setClippingEnabled | enabled={enabled}")
        if enabled:
            self.setClipRect(QRectF(0, 0, self._fixed_width, self._fixed_height))
        else:
            self.setClipRect(None)

    def setClipRect(self, rect):
        logger.info(f"CustomGraphicsTextItem.setClipRect | rect={rect}")
        self._clip_rect = rect if rect is not None else None
        self.update()

    def paint(self, painter, option, widget):
        logger.debug("CustomGraphicsTextItem.paint")
        if self._clip_rect:
            painter.setClipRect(self._clip_rect)
        super().paint(painter, option, widget)

class CustomComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        logger.info(f"CustomComboBox.__init__ | args={args}, kwargs={kwargs}")
        super().__init__(*args, **kwargs)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.currentTextChanged.connect(self.set_text)

    def add_items(self, items):
        logger.info(f"CustomComboBox.add_items | items={items}")
        self.addItems(items)
        self.items = items

    def showPopup(self):
        logger.info("CustomComboBox.showPopup")
        super().showPopup()
        popup = self.view()
        max_width = max([
            popup.fontMetrics().width(popup.model().data(popup.model().index(i, 0)))
            for i in range(popup.model().rowCount())
        ]) if popup.model().rowCount() > 0 else 50
        popup.setFixedWidth(max_width + 20)  # Adding some padding
        logger.debug(f"CustomComboBox.showPopup | max_width={max_width}")

    def set_text(self, text):
        logger.info(f"CustomComboBox.set_text | text={text}")
        self.setCurrentText(text.split(" ")[0])

def get_existing_leaf_nodes():
    logger.info("[get_existing_leaf_nodes] Called.")
    try:
        leaf_rows = get_instances(AttackLeafHome)
        logger.debug(f"[get_existing_leaf_nodes] Retrieved {len(leaf_rows)} rows.")
        leaf_list = [f"{row.id} {row.name}" for row in leaf_rows]
        logger.info(f"[get_existing_leaf_nodes] Returning: {leaf_list}")
        return leaf_list
    except Exception as e:
        logger.error(f"[get_existing_leaf_nodes] Error fetching leaf nodes: {e}")
        return []

def get_existing_technical_tree():
    logger.info("[get_existing_technical_tree] Called.")
    try:
        technical_rows = get_instances(TechnicalTreeHome)
        logger.debug(f"[get_existing_technical_tree] Retrieved {len(technical_rows)} rows.")
        technical_list = [f"{row.id} {row.name}" for row in technical_rows]
        logger.info(f"[get_existing_technical_tree] Returning: {technical_list}")
        return technical_list
    except Exception as e:
        logger.error(f"[get_existing_technical_tree] Error fetching technical tree: {e}")
        return []


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        logger.info(f"CustomGraphicsView.__init__ | scene={scene} parent={parent}")
        super().__init__(scene, parent)
        self.zoom_factor = 1.15  # Set zoom factor
        logger.debug(f"CustomGraphicsView: Zoom factor set to {self.zoom_factor}")

    def wheelEvent(self, event):
        logger.debug(f"CustomGraphicsView.wheelEvent | angleDelta={event.angleDelta().y()}")
        # Zoom in or out
        if event.angleDelta().y() > 0:  # Wheel up, zoom in
            logger.info("CustomGraphicsView: Zooming IN")
            self.scale(self.zoom_factor, self.zoom_factor)
        else:  # Wheel down, zoom out
            logger.info("CustomGraphicsView: Zooming OUT")
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
