from datetime import datetime
import random
import string
from typing import Self

from Target_Of_Evaluation.Scope.controllers.mindmap_manager import find_duplicates
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import math
import re
import sqlite3
import controllers.DatabaseCreator as DB

import utils.interface_utils as interfaces
from controllers.schema_manager import update_all_instances, get_unique_instances, get_first_instance
from controllers.tablemodel import ScopeHomeMindmap, ScopeMindmaps, MindmapNodeType

# Global dictionaries to store nodes
intermediate_nodes_dict = {}  # Stores intermediate nodes
leaf_nodes_dict = {}  # Stores leaf nodes
unsaved_intermediate_nodes_dict = {}  
unsaved_leaf_nodes_dict = {}

class Node(QGraphicsItem):
    def __init__(self, x=0, y=0, name="New Node", desc="New Node Desc", parent=None):
        super().__init__()
        self.name = name
        self.desc = desc
        self.setAcceptHoverEvents(True)
        self.children = []
        self.parent = parent
        self.scope_id = ""
        self.node_type = ""
        self.level = 1 if self.parent is None else self.parent.level + 1
        self.node_id = f"{self.level}_{self.generate_random_alphanumeric()}"
        self.parent_id = "" if self.parent is None else self.parent.node_id
        self.font = QFont("Arial", 10)
        self.pos_x = x
        self.pos_y = y
        self.setPos(x, y)
        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemSendsGeometryChanges
            | QGraphicsItem.ItemIsSelectable
        )
        self.setZValue(10)
        self.normal_border_width = 1
        self.selected_border_width = 0
        self.border_color = QColor(Qt.black)
        self.selected_border_color = QColor(Qt.darkGray)
        self.selected_border_width if self.isSelected() else self.normal_border_width
        # Enable text editing on double click
        self.position_data = {}
        self.to_dict()

        # Calculate node size based on text
        self.padding = 20
        self.updateSize()

    def generate_random_alphanumeric(self):
        current_time = datetime.now()
        random.seed(current_time.timestamp())
        characters = string.ascii_lowercase + string.digits
        random_string = "".join(random.choices(characters, k=3))
        return random_string

    def set_position_data(self, data):
        self.position_data = data

    def boundingRect(self):
        return self.calculateRect()

    def calculateRect(self):
        metrics = QFontMetrics(self.font)
        text_width = metrics.width(self.name)
        text_height = metrics.height()
        rect = QRectF(
            -text_width / 4 - self.padding,
            -text_height / 4 - self.padding,
            text_width + 2 * self.padding,
            text_height + 2 * self.padding,
        )
        rect.setWidth(rect.width() if rect.width() > 120 else 120)
        return rect

    def updateSize(self):
        pass

    def paint(self, painter, option, widget):
        path = QPainterPath()
        border_width = None
        border_color = None
        rect = self.boundingRect()

        dashDotPen = QPen(Qt.black, 2, Qt.DashDotLine)
        normalPen = QPen(Qt.black, 1, Qt.SolidLine)
        if self.parent is None:
            path.addRoundedRect(rect, 155, 55)
            border_width = (
                self.selected_border_width
                if self.isSelected()
                else self.normal_border_width
            )
            border_color = (
                self.selected_border_color if self.isSelected() else self.border_color
            )
            # normalPen.setColor(border_color)
            normalPen.setWidth(border_width)
            painter.setPen(normalPen)
        else:
            rect.setHeight(50)
            path.addRoundedRect(rect, 0, 0)
            # ect.setWidth(rect.width()-20)
            # path.addRoundedRect(QRectF(10, 20, 50, 50))
            # path.addRect(-10, -20, 80, 60)
            border_width = (
                self.selected_border_width
                if self.isSelected()
                else self.normal_border_width
            )
            border_color = (
                self.selected_border_color if self.isSelected() else self.border_color
            )
            # dashDotPen.setColor(border_color)
            dashDotPen.setWidth(border_width)
            dashDotPen.setDashPattern([2, 2])
            painter.setPen(dashDotPen)

        painter.setBrush(
            QBrush(
                QColor(175, 211, 247) if self.isSelected() else QColor(245, 245, 255)
            )
        )  # Light blue background
        painter.drawPath(path)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.name)
        #self.setToolTip(f"{self.desc}-{self.node_id}")
        self.setToolTip(f"{self.desc}")

    def mouseClickEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.parent is None or self.node_type == "HEAD":
                dialog = AttributeDialog2(self, is_root=True)  # Use Attribute1 for head or no parent
            else:
                dialog = AttributeDialog(self)           # Use AttributeDialog for other nodes
            dialog.exec_()
        if event.button() == Qt.RightButton:
            pass

    def focusOutEvent(self, event):
        pass

    # self.text_item.setTextInteractionFlags(Qt.NoTextInteraction)
    # self.updateSize()
    # super().focusOutEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.drag_start_pos = event.pos()
        elif event.button() == Qt.RightButton:
            self.setSelected(True)

        super().mousePressEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Update the dictionary with the new position
            self.update_dict(new_pos=value)
        # print("Updated node positions:", self.position_data)
        return super().itemChange(change, value)

    def update_dict(self, new_pos=None):
        """Update the node dictionary with the current position."""
        pos = new_pos if new_pos else self.pos()
        self.position_data["pos_x"] = pos.x()
        self.position_data["pos_x"] = pos.y()

    def __repr__(self):
        return f"Node(node_id='{self.node_id}', scope_id ='{ self.scope_id}', parent_id ='{ self.parent_id}', level ='{ self.level}', node_text='{ self.name}', pos_x='{ self.pos().x()}', pos_y='{ self.pos().y()}')"

    def to_dict(self):
        self.position_data = {
            "node_id": self.node_id,
            "scope_id": self.scope_id,
            "parent_id": self.parent_id,
            "level": str(self.level),
            "node_text": self.name,
            "node_desc": self.desc,
            "node_type": self.node_type,
            "pos_x": str(self.pos().x()),
            "pos_y": str(self.pos().y()),
            "children": [child.to_dict() for child in self.children],
        }
        return self.position_data

class AttributeDialog(QDialog):
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Node Properties")
        # layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.name_label = QLabel("Name : ")
        self.name_input = QLineEdit(self.item.name)
        form_layout.addRow(self.name_label, self.name_input)

        self.desc_label = QLabel("Description : ")
        self.desc_input = QLineEdit(self.item.desc)
        form_layout.addRow(self.desc_label, self.desc_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_attributes)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def save_attributes(self):
        global intermediate_nodes_dict, leaf_nodes_dict
        global unsaved_intermediate_nodes_dict, unsaved_leaf_nodes_dict
        
        updated_name = self.name_input.text()
        updated_desc = self.desc_input.text()

        self.item.name = updated_name
        self.item.desc = updated_desc

        # Add to the appropriate dictionary
        if self.item.node_type == "INTERMEDIATE":
            intermediate_nodes_dict[self.item.node_id] = self.item.to_dict()
            unsaved_intermediate_nodes_dict[self.item.node_id] = {
            "node_text": updated_name,
            "node_desc": updated_desc
            }
            self.update_all_instances(updated_name, updated_desc, node_type="INTERMEDIATE")
            update_all_instances(ScopeMindmaps, {'node_text': updated_name, 'node_type':MindmapNodeType.INTERMEDIATE}, {'node_desc': updated_desc})
            
        elif self.item.node_type == "LEAF":
            leaf_nodes_dict[self.item.node_id] = self.item.to_dict()
            unsaved_leaf_nodes_dict[self.item.node_id] = {
            "node_text": updated_name,
            "node_desc": updated_desc
            }
            self.update_all_instances(updated_name, updated_desc, node_type="LEAF")
            update_all_instances(ScopeMindmaps, {'node_text': updated_name, 'node_type':MindmapNodeType.LEAF}, {'node_desc': updated_desc})
            
        # Print dictionary contents to verify 
        interfaces.unsaved_changes = True  

        self.accept()
    def update_all_instances(self, updated_name, updated_desc, node_type):
        """Update all instances of a node in the scene."""
        for scene in QApplication.instance().topLevelWidgets():
            if isinstance(scene, QGraphicsView):
                for item in scene.scene().items():
                    if isinstance(item, Node) and item.node_type == node_type and item.name == updated_name:
                        item.desc = updated_desc  # Update description
                        item.setToolTip(updated_desc)  # Update tooltip
                        item.update()  # Refresh display

class AttributeDialog2(QDialog):
    def __init__(self, item, is_root=False):
        super().__init__()
        self.item = item
        self.is_root = is_root
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Node Properties")
        form_layout = QFormLayout()

        self.name_label = QLabel("Scope Name:")
        self.name_input = QLineEdit(self.item.name)
        if self.is_root:
            self.name_input.installEventFilter(self)
        form_layout.addRow(self.name_label, self.name_input)
        self.name_input.setContextMenuPolicy(Qt.NoContextMenu)


        self.desc_label = QLabel("Description:")
        self.desc_input = QLineEdit(self.item.desc)
        form_layout.addRow(self.desc_label, self.desc_input)

        self.previous_text = self.item.name
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_attributes)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)



    def eventFilter(self, obj, event):
        if obj == self.name_input and event.type() == QEvent.KeyPress:
            text = self.name_input.text()

            # Match "SCOPE-<number>" at the start of the text
            match = re.match(r"^(SCOPE-\d+)", text)
            if match:
                scope_id = match.group(1)
                scope_id_length = len(scope_id)
            else:
                return super().eventFilter(obj, event)

            cursor_pos = self.name_input.cursorPosition()
            selected_text = self.name_input.selectedText()

            # Ensure the text always starts with "SCOPE-<number>"
            if not text.startswith(scope_id + " "):
                self.name_input.setText(scope_id + " ")
                self.name_input.setCursorPosition(scope_id_length + 1)
                return True

            # Handle Ctrl+A (Select All) — only select after scope_id
            if event.key() == Qt.Key_A and event.modifiers() == Qt.ControlModifier:
                self.name_input.setSelection(scope_id_length + 1, len(text))
                return True

            # Handle Ctrl+X (Cut) - prevent cutting scope ID
            if event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
                if self.name_input.selectionStart() < scope_id_length + 1:
                    return True

            if event.type() == QEvent.MouseButtonDblClick:
                self.name_input.setSelection(scope_id_length + 1, len(text))
                return True

            # Prevent scope_id deletion on typing after double-click
            if selected_text and selected_text.startswith(scope_id):
                self.name_input.setSelection(scope_id_length + 1, len(text))
                return True

            # Handle paste event
            if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                clipboard = QApplication.clipboard().text()
                if clipboard:
                    new_text = scope_id + " " + clipboard
                    self.name_input.setText(new_text)
                    self.name_input.setCursorPosition(scope_id_length + len(clipboard) + 1)
                    return True
            

            # **Fix 3: Block text insertion before scope_id**
            if event.type() == QEvent.KeyPress:
                if cursor_pos < scope_id_length:
                    self.name_input.setCursorPosition(scope_id_length)
                    return True  

                # **Fix 4: Prevent scope_id duplication**
                if cursor_pos == scope_id_length and event.text().strip():
                    new_text = scope_id + " " + text[scope_id_length:]  # Keep original scope_id intact
                    self.name_input.setText(new_text)
                    self.name_input.setCursorPosition(scope_id_length + 1)  # Move cursor after new input
                    return True  

            # Prevent deleting scope_id
            if event.key() in [Qt.Key_Backspace, Qt.Key_Delete]:
                if cursor_pos <= scope_id_length:  # Block deletion inside scope_id
                    return True  

                # Allow deletion if selection is only after scope_id
                if selected_text:
                    selection_start = self.name_input.selectionStart()
                    if selection_start < scope_id_length:  
                        return True  # Block deletion if selection includes scope_id
                    else:
                        return False  # Allow deletion

            # Prevent selecting scope_id
            if event.key() in [Qt.Key_Shift, Qt.Key_Home]:
                selection_start, selection_end = self.name_input.selectionStart(), self.name_input.selectionEnd()
                if selection_start < scope_id_length:  
                    self.name_input.deselect()
                    return True  

            # Prevent cursor from moving inside scope_id
            if event.key() in [Qt.Key_Left, Qt.Key_Home]:
                if cursor_pos <= scope_id_length:
                    self.name_input.setCursorPosition(scope_id_length)
                    return True  

            return super().eventFilter(obj, event)

        return super().eventFilter(obj, event)





    def save_attributes(self):
        text = self.name_input.text()
        
        # Ensure scope_id remains intact
        match = re.match(r"^(SCOPE-\d+)\s", text)
        if match:
            scope_id = match.group(1)
            scope_name = text[len(scope_id):].strip()  # Get only scope name
            self.previous_text = self.previous_text[len(scope_id):].strip()
        else:
            scope_id = self.item.scope_id  # Fallback to original scope_id
            scope_name = text.strip()

        print("scope mind map name  dup",scope_name)
        count = find_duplicates(self.previous_text, scope_name.strip())

        if count != 0:
            QMessageBox.warning(self, "Name Error", 
                                f"The scope name already exists or invalid. Please choose another name.")
            return  # Stop further execution      
        interfaces.unsaved_changes = True
        self.item.name = f"{scope_id} {scope_name}"
        self.item.desc = self.desc_input.text()
        self.accept()



class Connection(QGraphicsPathItem):
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setPen(QPen(QColor("#78909C"), 2, Qt.SolidLine, Qt.RoundCap))
        self.updatePath()
        self.setZValue(-100)

    def updatePath(self):
        path = QPainterPath()
        start = self.start_node.pos()
        end = self.end_node.pos()
        start = QPointF(start.x() + 45, start.y() + 25)
        end = QPointF(end.x() + 45, end.y() + 25)

        dx = end.x() - start.x()
        ctrl1 = QPointF(start.x() + dx * 0.05, start.y())
        ctrl2 = QPointF(start.x() + dx * 0.05, end.y())

        path.moveTo(start.x(), start.y())
        path.cubicTo(ctrl1, ctrl2, end)
        self.setPath(path)

    def update_positions(self):
        self.updatePath()


class MMScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scope_id = ""
        self.scope_name = ""
        self.scope_counter = 0
        self.connections = []
        self.load_existing_data = []
        if self.load_existing_data is None:
            self.add_root_node()
        # else:
        #     self.loadData(self.load_existing_data)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            for item in self.selectedItems():
                item.setSelected(False)
        return super().mousePressEvent(event)

    def add_root_node(self):
        self.root_node = None
        root_node_id = f"{self.scope_id}_node_0"
        root_node_name = f"{self.scope_id} {self.scope_name}"
        node = Node(50, 100, "New Mind Map", "New Mind Map Desc", None)
        node.node_id = root_node_id
        node.node_type = 'HEAD'
        node.name = root_node_name
        self.addItem(node)
        self.root_node = node
        self.root_node.setSelected(True)
        self.changed.connect(self.updateConnections)

    def contextMenuEvent(self, event):
        """Override the context menu event to show options."""
        context_menu = QMenu(parent=None)

        # Add actions to the context menu
        delNodeOpt = QAction("Delete Node", self)
        addInterChildNodeOpt = QAction("Add New Intermediate Node", self)
        addLeafChildNodeOpt = QAction("Add New Leaf Node", self)

        # Create a submenu for "Add Existing Intermediate Node"
        existingIntermediateMenu = QMenu("Add Existing Intermediate Node", context_menu)
        self.populateExistingIntermediateNodes(existingIntermediateMenu)  # Populate submenu

        existingLeafMenu = QMenu("Add Existing Leaf Node", context_menu)
        self.populateExistingLeafNodes(existingLeafMenu)

        # Connect actions to functions
        delNodeOpt.triggered.connect(self.deleteNode)
        addInterChildNodeOpt.triggered.connect(self.addIntermediateChildNode)
        addLeafChildNodeOpt.triggered.connect(self.addLeafChildNode)

        # Ensure a valid node is selected
        if (
            len(self.selectedItems()) > 0
            and self.selectedItems()[0] is not None
            and isinstance(self.selectedItems()[0], Node)
        ):
            selected_node = self.selectedItems()[0]

            # If it's a root node (head), allow adding child nodes but **DISABLE delete**
            if selected_node.node_type == 'HEAD':
                context_menu.addAction(addInterChildNodeOpt)
                context_menu.addMenu(existingIntermediateMenu)
                context_menu.addAction(addLeafChildNodeOpt)
                context_menu.addMenu(existingLeafMenu)
            
            # If it's an intermediate or leaf node, allow delete and child nodes
            else:
                if selected_node.node_type == 'INTERMEDIATE':
                    context_menu.addAction(addInterChildNodeOpt)
                    context_menu.addMenu(existingIntermediateMenu)
                    context_menu.addAction(addLeafChildNodeOpt)
                    context_menu.addMenu(existingLeafMenu)

                # Both intermediate and leaf nodes should have the delete option
                context_menu.addAction(delNodeOpt)

        # Show the menu at the cursor position
        context_menu.exec_(event.screenPos())


    def addIntermediateChildNode(self):
        selected = self.selectedItems()
        self.scope_counter += 1
        if selected and isinstance(selected[0], Node):
            parent = selected[0]
            child = Node(0, 0, "Intermediate Child", "child desc", parent)
            child.level = parent.level + 1
            new_node_id = f"{self.scope_id}_node_{self.scope_counter}"
            child.node_id = new_node_id
            child.node_type = 'INTERMEDIATE'
            parent.children.append(child)
            #if "head" != parent.node_type:
            #    parent.node_type = "intermediate"
            self.clearSelection()
            child.setSelected(True)
            self.addItem(child)

            # Position child
            angle = len(parent.children) * (2 * 3.14159 / 8)
            distance = 150
            child.setPos(
                parent.pos()
                + QPointF(math.cos(angle) * distance, math.sin(angle) * distance)
            )

            # Add connection
            conn = Connection(parent, child)
            self.addItem(conn)
            self.connections.append(conn)
            self.updateConnections()
            interfaces.unsaved_changes = True

    def addLeafChildNode(self):
        selected = self.selectedItems()
        self.scope_counter += 1
        if selected and isinstance(selected[0], Node):
            parent = selected[0]
            child = Node(0, 0, "Leaf Child", "child desc", parent)
            child.level = parent.level + 1
            new_node_id = f"{self.scope_id}_node_{self.scope_counter}"
            child.node_id = new_node_id
            child.node_type = 'LEAF'
            parent.children.append(child)
            #if "head" != parent.node_type:
            #    parent.node_type = "intermediate"
            self.clearSelection()
            child.setSelected(True)
            self.addItem(child)

            # Position child
            angle = len(parent.children) * (2 * 3.14159 / 8)
            distance = 150
            child.setPos(
                parent.pos()
                + QPointF(math.cos(angle) * distance, math.sin(angle) * distance)
            )

            # Add connection
            conn = Connection(parent, child)
            self.addItem(conn)
            self.connections.append(conn)
            self.updateConnections()
            interfaces.unsaved_changes = True

    def deleteNode(self):
        selected = self.selectedItems()
        if selected and isinstance(selected[0], Node):
            node = selected[0]

            # Collect all connections related to this node and its children
            connections_to_remove = []
            for conn in self.connections[:]:  
                if conn.start_node == node or conn.end_node == node:
                    connections_to_remove.append(conn)

            # Remove connections first
            for conn in connections_to_remove:
                self.connections.remove(conn)  # Remove from connection list
                self.removeItem(conn)  # Remove from scene

            # Recursively remove all child nodes before deleting the selected node
            for child in node.children[:]:  # Copy list to avoid modification issues
                self.removeNodeRecursive(child)

            # Remove node reference from parent
            if node.parent:
                node.parent.children.remove(node)

            # Finally, remove the node itself from the scene
            self.removeItem(node)

            # Force UI update to clear any leftover references
            self.update()
            self.updateConnections()
            interfaces.unsaved_changes = True

    def populateExistingIntermediateNodes(self, menu):
        """Fetch and populate existing intermediate nodes from the database and global dictionary."""
        
        # Use a set to avoid duplicates
        unique_nodes = set()

        # Fetch intermediate nodes from the database
        unique_nodes_list = get_unique_instances(ScopeMindmaps.node_text, {'node_type':MindmapNodeType.INTERMEDIATE})
        for unique_node in unique_nodes_list: unique_nodes.add(unique_node)

        # Add global dictionary nodes
        for node_id, node_data in intermediate_nodes_dict.items():
            unique_nodes.add(node_data["node_text"])

        # If no intermediate nodes exist, show a disabled message
        if not unique_nodes:
            noNodesAction = QAction("No Existing Nodes", self)
            noNodesAction.setEnabled(False)
            menu.addAction(noNodesAction)
            return

        # Add unique intermediate nodes to the submenu
        for node_text in unique_nodes:
            action = QAction(node_text, self)
            action.triggered.connect(lambda checked, n=node_text: self.addSelectedIntermediateNode(n))
            menu.addAction(action)

            
        
    def populateExistingLeafNodes(self, menu):
        """Fetch and populate existing leaf nodes from the database and global dictionary."""
        
        # Use a set to avoid duplicates
        unique_nodes = set()

        unique_nodes_list = get_unique_instances(ScopeMindmaps.node_text, {'node_type':MindmapNodeType.LEAF})
        for unique_node in unique_nodes_list: unique_nodes.add(unique_node)

        # Add global dictionary nodes
        for node_id, node_data in leaf_nodes_dict.items():
            unique_nodes.add(node_data["node_text"])

        # If no leaf nodes exist, show a disabled message
        if not unique_nodes:
            noNodesAction = QAction("No Existing Nodes", self)
            noNodesAction.setEnabled(False)
            menu.addAction(noNodesAction)
            return

        # Add unique leaf nodes to the submenu
        for node_text in unique_nodes:
            action = QAction(node_text, self)
            action.triggered.connect(lambda checked, n=node_text: self.addSelectedLeafNode(n))
            menu.addAction(action)

    

    def addSelectedIntermediateNode(self, node_text):
        """Add selected existing intermediate node to the scene."""
        
        selected = self.selectedItems()
        if selected and isinstance(selected[0], Node):
            parent = selected[0]

            if any(data["node_text"] == node_text for data in unsaved_intermediate_nodes_dict.values()):
                node_desc = next(data["node_desc"] for data in unsaved_intermediate_nodes_dict.values() if data["node_text"] == node_text)
            else:
                # If not found in dictionary, fetch from DB
                result = get_first_instance(ScopeMindmaps, {'node_text':node_text, 'node_type':MindmapNodeType.INTERMEDIATE})
                node_desc = result.node_desc if result else "No description available"

            # Create a new node with existing text
            child = Node(0, 0, node_text, node_desc, parent)
            child.level = parent.level + 1
            child.node_type = "INTERMEDIATE"
            
            # Set a unique node_id
            self.scope_counter += 1
            child.node_id = f"{self.scope_id}_node_{self.scope_counter}"
            
            parent.children.append(child)
            self.clearSelection()
            child.setSelected(True)
            self.addItem(child)

            # Position child
            angle = len(parent.children) * (2 * 3.14159 / 8)
            distance = 150
            child.setPos(parent.pos() + QPointF(math.cos(angle) * distance, math.sin(angle) * distance))

            # Add connection
            conn = Connection(parent, child)
            self.addItem(conn)
            self.connections.append(conn)
            self.updateConnections()
            interfaces.unsaved_changes = True

    def addSelectedLeafNode(self, node_text):
        """Add selected existing leaf node to the scene."""
        
        selected = self.selectedItems()
        if selected and isinstance(selected[0], Node):
            parent = selected[0]

            if any(data["node_text"] == node_text for data in unsaved_leaf_nodes_dict.values()):
                node_desc = next(data["node_desc"] for data in unsaved_leaf_nodes_dict.values() if data["node_text"] == node_text)
            else:
                # If not found in dictionary, fetch from DB
                result = get_first_instance(ScopeMindmaps, {'node_text':node_text, 'node_type':MindmapNodeType.LEAF})
                node_desc = result.node_desc if result else "No description available"
            # Create a new node with existing text
            child = Node(0, 0, node_text, node_desc, parent)
            child.level = parent.level + 1
            child.node_type = "LEAF"
            
            # Set a unique node_id
            self.scope_counter += 1
            child.node_id = f"{self.scope_id}_node_{self.scope_counter}"
            
            parent.children.append(child)
            self.clearSelection()
            child.setSelected(True)
            self.addItem(child)

            # Position child
            angle = len(parent.children) * (2 * 3.14159 / 8)
            distance = 150
            child.setPos(parent.pos() + QPointF(math.cos(angle) * distance, math.sin(angle) * distance))

            # Add connection
            conn = Connection(parent, child)
            self.addItem(conn)
            self.connections.append(conn)
            self.updateConnections()
            interfaces.unsaved_changes = True
           

    def removeNodeRecursive(self, node):
        """ Recursively remove a node and its connections. """
        if not node:
            return

        # Remove all child nodes first
        for child in node.children[:]:
            self.removeNodeRecursive(child)

        # Remove connections related to this node
        connections_to_remove = [conn for conn in self.connections if conn.start_node == node or conn.end_node == node]
        for conn in connections_to_remove:
            self.connections.remove(conn)
            self.removeItem(conn)

        # Remove node from parent reference
        if node.parent:
            node.parent.children.remove(node)

        # Finally, remove the node itself
        self.removeItem(node)


    def updateConnections(self):
        for conn in self.connections:
            conn.updatePath()

    def getPostionData(self):
        return self.root_node.to_dict()

    def loadData(self, load_existing_data):
        json_data = load_existing_data
        node = self.setNodeattr(json_data, Node(0, 0, "", "", None), None)
        self.root_node = node
        self.addItem(self.root_node)
        self.root_node.setSelected(True)
        self.changed.connect(self.updateConnections)
        self.create_node_tree(json_data["children"], self.root_node)
        self.root_node.to_dict()

    def create_node_tree(self, json_data, parent):
        if isinstance(json_data, dict):
            node = self.setNodeattr(json_data, Node(0, 0, "", "", None), parent)
            # node.setSelected(True)
            self.addItem(node)
            #self.scope_counter += 1
            # Add connection
            conn = Connection(parent, node)
            self.addItem(conn)
            self.connections.append(conn)
            self.updateConnections()
            node.level = parent.level + 1
            parent.children.append(node)
            parent.position_data["children"].append(
                [child.to_dict() for child in parent.children]
            )
            if isinstance(json_data["children"], list):
                self.create_node_tree(json_data["children"], parent)

        elif isinstance(json_data, list):
            for child_data in json_data:
                node = self.setNodeattr(child_data, Node(0, 0, "", "", parent), parent)
                # node.setSelected(True)
                self.addItem(node)
                #self.scope_counter += 1
                # Add connection
                conn = Connection(parent, node)
                self.addItem(conn)
                self.connections.append(conn)
                self.updateConnections()
                node.level = parent.level + 1
                parent.children.append(node)
                parent.position_data["children"].append(
                    [child.to_dict() for child in parent.children]
                )
                if isinstance(child_data["children"], list):
                    self.create_node_tree(child_data["children"], node)

    # end def

    def setNodeattr(self, json_data, node: Node, parent):
        print(json_data)
        node.node_id = json_data["node_id"]
        node.scope_id = json_data["scope_id"]
        node.parent_id = json_data["parent_id"]
        node.level = int(json_data["level"])
        node.name = json_data["node_text"]
        node.desc = json_data["node_desc"]
        node.node_type = json_data["node_type"]
        node.pos_x = float(json_data["pos_x"])
        node.pos_y = float(json_data["pos_y"])
        node.setPos(node.pos_x, node.pos_y)
        number_str = re.search(r'_(\d+)$', node.node_id).group(1)
        number = int(number_str)
        self.scope_counter = number if number > self.scope_counter else self.scope_counter
        # node.to_dict()
        return node
