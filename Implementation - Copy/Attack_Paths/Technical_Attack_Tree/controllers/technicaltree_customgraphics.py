

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
from controllers.schema_manager import get_instances, get_first_instance
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome, AttackLeafNodes
import logging
logger = logging.getLogger(__name__)

class CustomGraphicsRemoveItem(QGraphicsProxyWidget):
    def __init__(self, node_id, parent=None, technical_tree_parent=None):
        super().__init__(parent)
        logger.info("CustomGraphicsRemoveItem")
        self.node_id = node_id
        self.technical_tree_parent = technical_tree_parent

    def contextMenuEvent(self, event):
        logger.info("CustomGraphicsRemoveItem contextMenuEvent")
        context_menu = QMenu()
        
        switch_action = QAction("remove node")
        switch_action.triggered.connect(lambda: self.technical_tree_parent.Remove_Node(self.node_id))
        context_menu.addAction(switch_action)
        
        context_menu.exec_(event.screenPos())

class EditableTextItem(QGraphicsTextItem):
    def __init__(self, text='', parent=None, fixed_width=200, node_id='', technical_tree_parent=None):
        super().__init__(text, parent)
        logger.info("EditableTextItem")
        self.technical_tree_parent=technical_tree_parent
        self.node_id = node_id
        self.fixed_width = fixed_width
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)

        # Set fixed width for the item
        self.setTextWidth(self.fixed_width)

        # Store the full text
        self.full_text = text
        self.update_display_text()

    def contextMenuEvent(self, event):
        pass

    def update_display_text(self):
        logger.info("update_display_text")
        # Display the full text
        self.setPlainText(self.full_text)

    def focusOutEvent(self, event):
        new_text = self.toPlainText()
        if new_text != self.full_text:  # Check if text has changed
            self.full_text = new_text
            self.update_display_text()
            if self.technical_tree_parent is not None:
                interfaces.unsaved_changes = True
                self.technical_tree_parent.Auto_Update_Leaf_name(self.node_id)

        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            new_text = self.toPlainText()
            if new_text != self.full_text:  # Check if text has changed
                self.full_text = new_text
                self.update_display_text()
            if self.technical_tree_parent is not None:
                interfaces.unsaved_changes = True
                self.technical_tree_parent.Auto_Update_Leaf_name(self.node_id)
            self.clearFocus()  # Optionally remove focus
        else:
            super().keyPressEvent(event)

    def boundingRect(self, height = ''):
        # Ensure bounding rect is fixed width and adjusts for full text
        rect = super().boundingRect()
        
        return QRectF(rect.x(), rect.y(), self.fixed_width, 40)

class CustomGraphicsEditItem(QGraphicsProxyWidget):
    def __init__(self, node_id, parent=None, technical_tree_parent=None):
        super().__init__(parent)
        logger.info("CustomGraphicsEditItem")
        self.node_id = node_id
        self.technical_tree_parent = technical_tree_parent

    def contextMenuEvent(self, event):
        logger.info("CustomGraphicsEditItem contextMenuEvent")
        # Create a context menu
        menu = QMenu()
        
        intermediatenode_action = QAction("Add Intermediate Node", menu)
        intermediatenode_action.triggered.connect(lambda: self.technical_tree_parent.Add_Child_Node(self.node_id, "intermediate"))
        menu.addAction(intermediatenode_action)
        
        leafnode_menu = QMenu("Add Leaf Node", menu)
        add_newleaf_action = QAction("New Leaf", leafnode_menu)
        add_newleaf_action.triggered.connect(lambda: self.technical_tree_parent.Add_Child_Node(self.node_id, "new_leaf"))
        
        add_existingleaf_menu = QMenu("Existing Leaf", leafnode_menu)
        saved_leaf_nodes = get_existing_leaf_nodes()
        
        # If no saved leaf nodes are found, disable the option
        if not saved_leaf_nodes:
            no_leaf_action = QAction("Leaf Nodes not available", add_existingleaf_menu)
            no_leaf_action.setEnabled(False)
            add_existingleaf_menu.addAction(no_leaf_action)
        # Add each saved leaf node as an action
        else:
            for leaf_name in saved_leaf_nodes:
                leaf_action = QAction(leaf_name, add_existingleaf_menu)
                leaf_action.triggered.connect(lambda checked, name=leaf_name: self.technical_tree_parent.Add_Child_Node(self.node_id, "existing_leaf", name ))
                add_existingleaf_menu.addAction(leaf_action)
        
        leafnode_menu.addAction(add_newleaf_action)
        leafnode_menu.addMenu(add_existingleaf_menu)
        menu.addMenu(leafnode_menu)

        removenode_action = QAction("remove node", menu)
        menu.addAction(removenode_action)
        removenode_action.triggered.connect(lambda: self.technical_tree_parent.Remove_Node(self.node_id))
        
        # Show the context menu
        menu.exec_(event.screenPos())

class CustomGraphicsNonEditItem(QGraphicsProxyWidget):
    def __init__(self, node_id, parent=None, technical_tree_parent=None):
        super().__init__(parent)
        logger.info("CustomGraphicsNonEditItem")
        self.node_id = node_id
        self.technical_tree_parent = technical_tree_parent
        
    def contextMenuEvent(self, event):
        logger.info("CustomGraphicsNonEditItem contextMenuEvent")
        # Create a context menu
        menu = QMenu()
        
        intermediatenode_action = QAction("Add Intermediate Node", menu)
        intermediatenode_action.triggered.connect(lambda: self.technical_tree_parent.Add_Child_Node(self.node_id, "intermediate"))
        menu.addAction(intermediatenode_action)
        
        leafnode_menu = QMenu("Add Leaf Node", menu)
        add_newleaf_action = QAction("New Leaf", leafnode_menu)
        add_newleaf_action.triggered.connect(lambda: self.technical_tree_parent.Add_Child_Node(self.node_id, "new_leaf"))
        
        add_existingleaf_menu = QMenu("Existing Leaf", leafnode_menu)
        saved_leaf_nodes = get_existing_leaf_nodes()
        
        # If no saved leaf nodes are found, disable the option
        if not saved_leaf_nodes:
            no_leaf_action = QAction("Leaf Nodes not available", add_existingleaf_menu)
            no_leaf_action.setEnabled(False)
            add_existingleaf_menu.addAction(no_leaf_action)
        # Add each saved leaf node as an action
        else:
            for leaf_name in saved_leaf_nodes:
                leaf_action = QAction(leaf_name, add_existingleaf_menu)
                leaf_action.triggered.connect(lambda checked, name=leaf_name: self.technical_tree_parent.Add_Child_Node(self.node_id, "existing_leaf", name ))
                add_existingleaf_menu.addAction(leaf_action)
        
        leafnode_menu.addAction(add_newleaf_action)
        leafnode_menu.addMenu(add_existingleaf_menu)
        menu.addMenu(leafnode_menu)
        
        # Show the context menu
        menu.exec_(event.screenPos())

class AFR_level(QGraphicsTextItem):
    def __init__(self, text=''):
        super().__init__()
        logger.info("AFR_level")
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
        logger.info("setPlainText")
        """
        Override setPlainText to handle text changes and update styles dynamically.
        """
        # Update the full text
        self.full_text = text

        # Call the parent class method to update the displayed text
        super().setPlainText(text)

        # Update styles
        self.update_display_text()

    def update_display_text(self):
        logger.info("update_display_text")
        # Use font metrics to calculate whether truncation is needed
        font_metrics = QFontMetrics(self.font())
        elided_text = font_metrics.elidedText(self.full_text, Qt.ElideRight, 90, 0)
        super().setPlainText(elided_text)

        # Trigger a repaint to apply the new style
        self.update()

    def paint(self, painter, option, widget=None):
        # Determine colors based on the text value
        background_color, border_color, text_color = self.get_colors_based_on_text()
        background_color.setAlpha(50)
        # Draw the background with rounded edges
        rect = self.boundingRect()
        path = QPainterPath()
        corner_radius = 10
        path.addRoundedRect(rect, corner_radius, corner_radius)
        painter.setBrush(QBrush(background_color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        # Draw the border
        border_pen = QPen(border_color, 1)
        painter.setPen(border_pen)
        painter.drawPath(path)

        # Set up the text alignment
        painter.setPen(text_color)  # Set the text color
        text_option = QTextOption(Qt.AlignCenter)  # Align text to center
        text_option.setWrapMode(QTextOption.NoWrap)

        # Draw the text manually
        painter.drawText(rect, self.full_text, text_option)

    def get_colors_based_on_text(self):
        """
        Determine the background, border, and text colors based on the text content.
        """
        if self.full_text == 'High':
            return QColor(tree_style.High_AFR_bg_color), QColor(tree_style.High_AFR_border_color), QColor(tree_style.High_AFR_Font_color) 
        elif self.full_text == 'Medium':
            return QColor(tree_style.Medium_AFR_bg_color), QColor(tree_style.Medium_AFR_border_color), QColor(tree_style.Medium_AFR_Font_color) 
        elif self.full_text == 'Low':
            return QColor(tree_style.Low_AFR_bg_color), QColor(tree_style.Low_AFR_border_color), QColor(tree_style.Low_AFR_Font_color)
        elif self.full_text == 'Very Low':
            return QColor(tree_style.VeryLow_AFR_bg_color), QColor(tree_style.VeryLow_AFR_border_color), QColor(tree_style.VeryLow_AFR_Font_color)
        else:
            # Default colors if no match
            return QColor(tree_style.node_bg), QColor(tree_style.node_bg), QColor(tree_style.node_bg)

class AFR_value(QGraphicsTextItem):
    def __init__(self, text=''):
        super().__init__()
        logger.info("AFR_value")
        # Store the full text
        self.full_text = text

        # Set default font and size
        self.setFont(QFont("poppins", 9, QFont.Bold))

        # Update the text color based on the value
        self.update_text_color()

    def setPlainText(self, text):
        logger.info("setPlainText")
        """
        Override the setPlainText method to update the color dynamically.
        """
        self.full_text = text
        super().setPlainText(text)
        self.update_text_color()

    def update_text_color(self):
        """
        Determine the background, border, and text colors based on the text content.
        """
        value = int(self.full_text)
        if value >= 0 and value <= 13:
            color =  QColor(tree_style.High_AFR_Font_color) 
        elif value >= 14 and value <= 19:
            color =  QColor(tree_style.Medium_AFR_Font_color) 
        elif value >= 20 and value <= 24:
            color =  QColor(tree_style.Low_AFR_Font_color)
        else :
            color =  QColor(tree_style.VeryLow_AFR_Font_color)
        
        # Apply the color
        self.setDefaultTextColor(color)

class SidebarItem(QGraphicsTextItem):
    def __init__(self, text='', bg_color='white'):
        super().__init__()
        logger.info("SidebarItem")
        # Set fixed width for the item
        self.setTextWidth(10)
        self.sidebar_color = bg_color

        # Store the full text
        self.full_text = text

        # Update display text and apply styling
        self.update_display_text()

    def update_bg_color(self, color_bg):
        logger.info("update_bg_color")
        self.sidebar_color = color_bg
        self.update_display_text()

    def setPlainText(self, text):
        logger.info("setPlainText")
        """
        Override setPlainText to handle text changes and update styles dynamically.
        """
        # Update the full text
        self.full_text = text

        # Call the parent class method to update the displayed text
        super().setPlainText(text)

        # Update styles
        self.update_display_text()

    def update_display_text(self):
        logger.info("update_display_text")
        # Use font metrics to calculate whether truncation is needed
        font_metrics = QFontMetrics(self.font())
        elided_text = font_metrics.elidedText(self.full_text, Qt.ElideRight, 90, 0)
        super().setPlainText(elided_text)

        # Trigger a repaint to apply the new style
        self.update()


    def boundingRect(self):
        """
        Set the fixed size for the item (height 130px and width 10px).
        """
        return QRectF(0, 0, 10, 130)  # Fixed width of 10px and height of 130px


    def paint(self, painter, option, widget=None):
        # Determine colors based on the text value
        background_color = QColor(self.sidebar_color)

        # Draw the background with rounded left corner
        rect = self.boundingRect()
        path = QPainterPath()
        corner_radius = 10

        # Create a rounded rectangle, rounding only the left corners
        path.moveTo(rect.topLeft())
        path.moveTo(rect.bottomLeft())
        path.addRoundedRect(rect.adjusted(0, 0, 0, 0), corner_radius, corner_radius)  # Only round left corners
        painter.setBrush(QBrush(background_color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

class CustomGraphicsTextItem(QGraphicsTextItem):
    def __init__(self, text, width=100, height=50, parent=None, font=None):
        super().__init__(text, parent)
        logger.info("CustomGraphicsTextItem")
        self._fixed_width = width
        self._fixed_height = height

        # Set font if provided
        if font:
            self.setFont(font)

        # Set the text width (enables word wrapping)
        self.setTextWidth(self._fixed_width)

        # Enable clipping to restrict height
        self.setClippingEnabled(True)

    def setClippingEnabled(self, enabled):
        """Enable or disable clipping for the fixed height."""
        if enabled:
            self.setClipRect(QRectF(0, 0, self._fixed_width, self._fixed_height))
        else:
            self.setClipRect(None)

    def setClipRect(self, rect):
        """Set a clipping rectangle to constrain the visible area."""
        if rect is not None:
            self._clip_rect = rect
        else:
            self._clip_rect = None
        self.update()

    def paint(self, painter, option, widget):
        """Override paint to apply clipping."""
        if self._clip_rect:
            painter.setClipRect(self._clip_rect)
        super().paint(painter, option, widget)

class CustomComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("CustomComboBox")
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.currentTextChanged.connect(self.set_text)
    
    def add_items(self, items):
        self.addItems(items)
        self.items = items
        
    def showPopup(self):
        super().showPopup()
        popup = self.view()
        # Calculate the maximum width required for the items
        max_width = max([popup.fontMetrics().width(popup.model().data(popup.model().index(i, 0))) for i in range(popup.model().rowCount())])
        # Set the width of the popup to fit the widest item
        popup.setFixedWidth(max_width + 20)  # Adding some padding
    
    def set_text(self, text):
        self.setCurrentText(text.split(" ")[0])


def get_existing_leaf_nodes():
    logger.info("get_existing_leaf_nodes (ORM)")
    try:
        leaf_objs = get_instances(AttackLeafNodes)
        return [f"{leaf.id} {leaf.name}" for leaf in leaf_objs]
    except Exception as e:
        logger.error(f"Error fetching leaf nodes: {e}")
        return []


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.zoom_factor = 1.15  # Set zoom factor

    def wheelEvent(self, event):
        # Zoom in or out
        if event.angleDelta().y() > 0:  # Wheel up, zoom in
            self.scale(self.zoom_factor, self.zoom_factor)
        else:  # Wheel down, zoom out
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)

