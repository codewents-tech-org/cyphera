import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QSizePolicy, QMessageBox, QGraphicsScene, QGraphicsPolygonItem, QComboBox  
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush, QPen, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QLineF
import models.Parameters as P
import models.helper as helper
import math
import controllers.DatabaseCreator as DB

from Attack_Paths.controllers.Attackpaths_CustomArrowLine import CustomArrowLine
import models.ScrollBarStyle as SBS
import styles.tree_panel_style as tree_panel_style
import styles.tree_style as tree_style
from Attack_Paths.controllers.Update_AllTrees_data import GetAndUpdate_Changed_leaf_list, Update_AllTree
from controllers.schema_manager import get_instances, get_first_instance, create_instance, update_instance, delete_instances_like
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome, AttackLeafNodes
from itertools import product
import utils.interface_utils as interfaces
import logging
logger = logging.getLogger(__name__)

class TechnicalATClass(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Technical Tree Class")
        self.parent = parent 
        
        self.nodes = {}
        self.arrows = {}
        self.selected_path = []
        self.node_counter = 0
        self.node_images = P.assets 

    # Create a tree tab for Technical tree action
    def Create_TechnicalTree_Tab(self, technical_id, technical_name):
        logger.info(f"Create Technical Tree {technical_id} Tab")
        self.technical_id = technical_id
        self.technical_name = technical_name
        for index in range(self.parent.inner_tab_widget.count()):
            if self.parent.inner_tab_widget.tabText(index) == f"{technical_id}":
                self.parent.inner_tab_widget.setCurrentIndex(index)
                self.Load_TechnicalTree()
                return

        self.nodes = {}
        self.arrows = {}
        self.node_counter = 0
        self.node_images = P.assets

        # Create Action tab and its layout
        self.action_tab = QWidget()
        self.action_tab_layout = QVBoxLayout(self.action_tab)
        self.action_tab_layout.setContentsMargins(2,0,2,2)
        self.action_tab.setStyleSheet(tree_panel_style.action_panel_style)

        self.Setup_GraphicsScene()
        
        # Add the action tab to the tab widget
        self.parent.inner_tab_widget.addTab(self.action_tab, f"{self.technical_id}")
        self.parent.inner_tab_widget.setCurrentWidget(self.action_tab)

    # Create a canvas for the Technical tree
    def Setup_GraphicsScene(self):
        # Create a QGraphicsScene
        self.scene = QGraphicsScene()

        # Use the CustomGraphicsView instead of QGraphicsView
        self.graphics_view = CG.CustomGraphicsView(self.scene, self)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphics_view.setEnabled(True)
        self.graphics_view.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.graphics_view.setStyleSheet(SBS.GraphicsView_ScrollBar_style)
        self.graphics_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.graphics_view.setStyleSheet(tree_panel_style.tree_style)

        # Set background as a dotted design
        dot_pattern = QPixmap(20, 20)  # Create a 20x20 dot pattern
        dot_pattern.fill(Qt.transparent)  # Make the background transparent

        # Draw dots on the pattern
        painter = QPainter(dot_pattern)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#EAEAEA")))  # Dots color
        painter.drawEllipse(10, 10, 4, 4)  # Dot size and position
        painter.end()

        # Apply the dot pattern as the background brush
        self.graphics_view.setBackgroundBrush(QBrush(dot_pattern))

        # Add the QScrollArea to the action tab layout
        self.action_tab_layout.addWidget(self.graphics_view)

    # Create a head node for the Technical tree
    def Create_Head_Node(self, x, y):
        logger.info("Create Head Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        technical_id = f"{self.technical_id}_{node_id}"

        node_data = NC.Create_HeadNode(self, technical_id, self.technical_id, self.technical_name, x, y)

        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["af_value_box"])
        self.scene.addItem(node_data["af_level_box"])
        self.scene.addItem(node_data["gate"])
        
        # Store node details
        self.nodes[technical_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "values": {},
            "gate":  node_data["gate"],
            "children": [],
            "parent": '',
            "gate_type":  node_data["gate_type"],
            "children_count": node_data["children_count"],
            "tags": ["head"],
            "arrows": [],
            "image_type": "head_node",
            "x":x,
            "y":y
        }
        
        return technical_id

    # Change a head node gate
    def Switch_Gate(self, node_id):
        logger.info("Switch Gate")
        node = self.nodes.get(node_id)
        if not node:
            return
        
        current_gate_type = node["gate_type"]
        new_gate_type = "or_gate" if current_gate_type == "and_gate" else "and_gate"
        current_gate = node.get("gate")
        if current_gate:
            gate_text = 'AND' if new_gate_type == "and_gate" else "OR"
            current_gate.widget().setText(gate_text)
        
        self.nodes[node_id]["gate_type"] = new_gate_type
       
        self.update_root_node_value()
        self.Update_Arrows_for_All_Nodes()
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    # Create a child node for the Technical tree
    def Add_Child_Node(self, parent_id, node_type, leaf_id=''):
        logger.info("Add Child Node")
        parent = self.nodes[parent_id]
        child_y = parent["y"] + 200
        child_x = parent["x"]

        # Create child node
        if node_type == "intermediate":
            child_id = self.Create_Intermediate_Node(child_x, child_y, node_type)
        elif node_type == "new_leaf":
            child_id = self.Create_Leaf_Node(child_x, child_y)
        elif node_type == "existing_leaf":
            child_id = self.Add_Existing_Leaf_Node(child_x, child_y, leaf_id)

        # Update parent and child relationships
        parent["children"].append(child_id)
        self.nodes[child_id]["parent"] = parent_id
        parent["children_count"] += 1
        self.Create_Arrow(parent["image"], (self.nodes[child_id]["image"]), parent_id, child_id)
        if node_type == "existing_leaf": self.Update_Leaf_Value(child_id, 0)
        if node_type == "new_leaf": self.update_root_node_value()
        
        head_node_id = f'{self.technical_id}_node_0'
        self.Realign_Node_Positions(head_node_id)
        self.Update_Arrows_for_All_Nodes()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.graphics_view.update()
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
        return child_id

    # Create a child intermediate node for the Technical tree
    def Create_Intermediate_Node(self, x, y, node_type):
        logger.info("Create Intermediate Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        db_node_counter = helper.intermediate_node_generate_id()

        # ORM: Insert into intermediate_node_trash table
        # from models import IntermediateNodeTrash  # adjust import/model name if needed
        # trash_entry = IntermediateNodeTrash(id=db_node_counter)
        # create_instance(trash_entry)

        technical_id = f"{self.technical_id}_{node_id}"

        node_data = NC.Create_IntermediateNode(self, technical_id, db_node_counter, x, y)

        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["af_value_box"])
        self.scene.addItem(node_data["af_level_box"])
        self.scene.addItem(node_data["gate"])

        # Store node details
        self.nodes[technical_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "values": {},
            "gate":  node_data["gate"],
            "children": [],
            "parent": '',
            "gate_type":  node_data["gate_type"],
            "children_count": node_data["children_count"],
            "tags": [node_type],
            "arrows": [],
            "image_type": "head_node",
            "x": x,
            "y": y
        }

        return technical_id

    # Create a child leaf node for the Technical tree
    def Create_Leaf_Node(self, x, y):
        logger.info("Create Leaf Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        db_node_counter = helper.leaf_node_generate_id()

        # ORM: Insert into leaf_node_trash table
        # from models import LeafNodeTrash  # adjust import/model name if needed
        # trash_entry = LeafNodeTrash(id=db_node_counter)
        # create_instance(trash_entry)

        technical_id = f"{self.technical_id}_{node_id}"

        node_data = NC.Create_LeafNode(self, technical_id, db_node_counter, x, y)

        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["valueline"])
        self.scene.addItem(node_data["af_value_box"])
        self.scene.addItem(node_data["af_level_box"])
        for index, combobox in node_data["values"].items():
            self.scene.addItem(combobox)
        for index, icons in node_data["values_icon"].items():
            self.scene.addItem(icons)

        # Store node details
        self.nodes[technical_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "valueline": node_data["valueline"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "values": node_data["values"],
            "values_icon": node_data["values_icon"],
            "gate":  '',
            "children": [],
            "parent": '',
            "gate_type":  '',
            "children_count": node_data["children_count"],
            "tags": ['leaf'],
            "arrows": [],
            "image_type": "node",
            "x": x,
            "y": y
        }

        return technical_id

    # Add a child existing leaf node for the Technical tree
    def Add_Existing_Leaf_Node(self, x, y, leaf_text):
        logger.info("Add Existing Leaf Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1

        # ORM: Fetch from attack_leaf_home by ID
        leaf_id_query = leaf_text.strip().split(' ')[0]
        row = get_first_instance(AttackLeafNodes, {"id": leaf_id_query})
        if not row:
            logger.error(f"Attack leaf with id {leaf_id_query} not found!")
            return None

        leaf_id = row.id
        leaf_name = row.name
        # Adjust these indices if your ORM model differs; you can use field names directly:
        leaf_values = [row.time, row.expertise, row.knowledge, row.access, row.equipment]
        leaf_af_value = str(sum([int(i) for i in leaf_values]))
        leaf_af_level = row.AFR_Level
        technical_id = f"{self.technical_id}_{node_id}"

        node_data = NC.Create_LeafNode(
            self, technical_id, leaf_id, x, y, 'node',
            leaf_name, leaf_af_value, leaf_af_level, leaf_values
        )

        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["valueline"])
        self.scene.addItem(node_data["af_value_box"])
        self.scene.addItem(node_data["af_level_box"])
        for index, combobox in node_data["values"].items():
            self.scene.addItem(combobox)
        for index, icons in node_data["values_icon"].items():
            self.scene.addItem(icons)

        # Store node details
        self.nodes[technical_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "valueline": node_data["valueline"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "values": node_data["values"],
            "values_icon": node_data["values_icon"],
            "gate":  '',
            "children": [],
            "parent": '',
            "gate_type":  '',
            "children_count": node_data["children_count"],
            "tags": ['leaf'],
            "arrows": [],
            "image_type": "leaf_node",
            "x": x,
            "y": y
        }

        return technical_id

    # Calculate AFR value and highlight the contributed path to AFR value calculation for the Technical tree
    def update_root_node_value(self):
        logger.info("Update Root Node Value")
        head_node = f"{self.technical_id}_node_0"
        self.paths = {}
        possible_paths = self.Get_Node_Paths(head_node)
        # print('possible_paths : ', possible_paths)
        for path in possible_paths:
            leaf_list = path.split(', ')
            leaf_value_lists = []
            Path_sum_value = 0
            leaf_max_values = []
            for leaf in leaf_list:
                leaf_value_lists.append(self.Get_leafNode_Values(leaf))
            if leaf_value_lists: leaf_max_values = [max(values) for values in zip(*leaf_value_lists)]
            else: leaf_max_values = [0, 0, 0, 0, 0]
            # print(path, '\t', leaf_max_values)
            Path_sum_value = sum(leaf_max_values)
            self.paths[path] = {'leaf_list': leaf_list, 'value':Path_sum_value}
        # print(self.paths)
        if possible_paths:
            path_leaf_list, path_info = min(self.paths.items(), key=lambda item: item[1]['value'])
            path_min_value = path_info['value']
        else:
            path_leaf_list = ''
            path_min_value = 0
        # print('output data: ', path_leaf_list, '\t', path_min_value)
        self.nodes[head_node]["af_value_box"].setPlainText(str(path_min_value))
        self.nodes[head_node]["af_level_box"].setPlainText(helper.Calculate_AFR_Level(path_min_value))

        self.selected_path = []
        for node, node_info in self.nodes.items():
            if "leaf" in node_info["tags"]:
                if node in path_leaf_list: 
                    self.Update_Node_Image(node, True)
                    self.selected_path.append(node)
                    self.Get_Selected_Path(node)
                else: 
                    self.Update_Node_Image(node, False)
        # print(self.selected_path)
        for node, node_info in self.nodes.items():
            if node in self.selected_path: node_info["image_type"] = "selected_path_node"
            else: node_info["image_type"] = "node"

    # list all nodes of the contributed path to AFR value calculation
    def Get_Selected_Path(self, node_id):
        node = self.nodes[node_id]
        leaf_path_list = []
        if node["parent"]:
            if node["parent"] not in self.selected_path: self.selected_path.append(node["parent"])
            self.Get_Selected_Path(node["parent"])   

    # list all path Combination of the root node
    def Get_Node_Paths(self, node_id):
        node = self.nodes[node_id]
        leaf_path_list = []
        for child_id in node["children"]:
            if "leaf" in self.nodes[child_id]["tags"]: 
                leaf_path_list.append(child_id)
            else:
                node_leaf_path = self.Get_Node_Paths(child_id)
                if node_leaf_path: 
                    leaf_path_list.append(node_leaf_path)
        # print(f'node {node_id} : ', leaf_path_list)
        if node['gate_type'] == 'and_gate':
            output_list_data = []
            if leaf_path_list:
                output_list = []
                all_list_or_str = ''
                if all(isinstance(element, list) for element in leaf_path_list): all_list_or_str = 'lists'
                elif all(isinstance(element, str) for element in leaf_path_list): all_list_or_str = 'string'
                else: 
                    leaf_path_list = [
                        element if isinstance(element, list) else [element]
                        for element in leaf_path_list
                    ]
                    all_list_or_str = 'lists'
                if all_list_or_str == 'lists':
                    for combo in product(*leaf_path_list): output_list.append(list(combo)) 
                    for combo in output_list:
                        new_leaf_ids = str([element for element in combo ]).removeprefix('[').removesuffix(']').replace("'","").replace('"',"")
                        output_list_data.append(new_leaf_ids)
                elif all_list_or_str == 'string':
                    new_leaf_ids = str([element for element in leaf_path_list ]).removeprefix('[').removesuffix(']').replace("'","").replace('"',"")
                    output_list_data.append(new_leaf_ids)
                # print(f'node {node_id} and_gate: ', output_list_data)
            return output_list_data
                
        elif node['gate_type'] == 'or_gate':
            output_list = []
            for lists in leaf_path_list: 
                if type(lists) == list: 
                    for leaf_list in lists: 
                        output_list.append(leaf_list)
                else:   output_list.append(lists)
            # print(f'node {node_id} or_gate: ', output_list)
            return output_list
        
        else: return leaf_path_list

    # Get value of each node
    def Get_leafNode_Values(self, node_id):
        logger.info("Get Leaf Node Values")
        node = self.nodes[node_id]
        # If the node is a leaf node
        if "leaf" in node["tags"]:
            values = []
            for i in range(5):
                proxy_widget = node["values"].get(i)
                if proxy_widget and isinstance(proxy_widget.widget(), QComboBox):
                    combo_box = proxy_widget.widget()
                    try:
                        value = int(combo_box.currentText().split()[0])
                    except (IndexError, ValueError): value = 0
                else:
                    value = 0
                values.append(value)
            return values

    # Change leaf node image
    def Update_Node_Image(self, node_id, included):
        node = self.nodes[node_id]

        if included: 
            widget = node["image"].widget() 
            widget.setStyleSheet(tree_style.selectedleafnode_box_style)
            self.nodes[node_id]["image_type"] = "selected_path_node"
        else: 
            widget = node["image"].widget() 
            widget.setStyleSheet(tree_style.leafnode_box_style)
            self.nodes[node_id]["image_type"] = "node"

    # Collect all removeable selected node and child nodes
    def Get_Remove_Node_List(self, node_id):
        if node_id in self.nodes:
            child_list = self.nodes[node_id]["children"]
            for child_id in child_list: self.remove_node_list.append(child_id)
            for child_id in child_list:
                self.Get_Remove_Node_List(child_id)

    # remove all selected node and child nodes
    def Remove_Node(self, node_id):
        logger.info("Remove Node")
        self.remove_node_list = []
        self.Get_Remove_Node_List(node_id)
        for child_id in self.remove_node_list:
            if child_id in self.nodes:
                self.Remove_Node_Data(child_id)
                del self.nodes[child_id]
        removed_node_parent = self.nodes[node_id]["parent"]
        self.Remove_Node_Data(node_id) 
        del self.nodes[node_id]
        if removed_node_parent:
            for n_id in self.remove_node_list:
                for child_id in self.nodes[removed_node_parent]["children"]:
                    if child_id == n_id or child_id == node_id:
                        self.nodes[removed_node_parent]["children"].remove(child_id)
            for child_id in self.nodes[removed_node_parent]["children"]:
                    if child_id == node_id: self.nodes[removed_node_parent]["children"].remove(child_id)
            self.update_root_node_value()
        head_node_id = f'{self.technical_id}_node_0'
        self.Realign_Node_Positions(head_node_id)
        self.Update_Arrows_for_All_Nodes()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.graphics_view.update()
        self.remove_node_list = []
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    # remove node
    def Remove_Node_Data(self, child_id):
        logger.info("Remove Node data")
        items_to_remove = [
            self.nodes[child_id]["image"],
            self.nodes[child_id]["sidebar"],
            self.nodes[child_id]["id"],
            self.nodes[child_id]["text"],
            self.nodes[child_id]["line"],
            self.nodes[child_id]["af_value_box"],
            self.nodes[child_id]["af_level_box"]
        ]
        
        for item in items_to_remove:
            if item.scene() == self.scene:
                self.scene.removeItem(item)
            else: pass
        
        if 'leaf' in self.nodes[child_id]["tags"]:
            # Remove QGraphicsProxyWidgets (combo boxes icons) from the scene
            for value_icon in self.nodes[child_id]["values_icon"].values():
                if value_icon.scene() == self.scene:
                    self.scene.removeItem(value_icon)
                else: pass
            
            if self.nodes[child_id]["valueline"]:
                v_line = self.nodes[child_id]["valueline"]
                if v_line.scene() == self.scene:
                    self.scene.removeItem(v_line)
                else: pass


        # Remove QGraphicsProxyWidgets (combo boxes) from the scene
        for value_entry in self.nodes[child_id]["values"].values():
            if value_entry.scene() == self.scene:
                self.scene.removeItem(value_entry)
            else: pass
        
        # If the node has a gate, remove it
        if self.nodes[child_id]["gate"]:
            gate = self.nodes[child_id]["gate"]
            if gate.scene() == self.scene:
                self.scene.removeItem(gate)
            else: pass
        
        # Remove arrows associated with the node
        for arrow in self.nodes[child_id]["arrows"]:
            if isinstance(arrow, tuple) and len(arrow) > 0:
                self.scene.removeItem(arrow[0])
                self.scene.removeItem(arrow[1])
                self.scene.removeItem(arrow[2])
                self.scene.removeItem(arrow[3])

    # Create Arrow for the flow display
    def Create_Arrow(self, start_item, end_item, parent_id, child_id):
        start_rect = start_item.boundingRect()
        end_rect = end_item.boundingRect()
        
        start_pos = start_item.scenePos()
        start_bottom_middle = QPointF(start_pos.x() + start_rect.width() / 2, start_pos.y() + start_rect.height())
        end_pos = end_item.scenePos()
        mid_y = (start_bottom_middle.y() + end_pos.y()) / 2
        vertical_end_point = QPointF(start_bottom_middle.x(), mid_y) 
        horizontal_point = QPointF(end_pos.x() + end_rect.width() / 2, mid_y)
        end_point = QPointF(horizontal_point.x(), end_pos.y())

        # Create the lines for the arrow (vertical -> horizontal -> vertical)
        vertical_line_1 = QLineF(start_bottom_middle, vertical_end_point)  # First vertical segment
        horizontal_line = QLineF(vertical_end_point, horizontal_point)  # Horizontal segment
        vertical_line_2 = QLineF(horizontal_point, end_point)  # Second vertical segment

        Selected_horizontal_line_color = P.AttackPath_highlight if (parent_id in self.selected_path and child_id in self.selected_path) else P.Black
        Selected_vertical_line_color = P.AttackPath_highlight if parent_id in self.selected_path else P.Black
        arrow_line_vertical_1 = CustomArrowLine(vertical_line_1.x1(), vertical_line_1.y1(), vertical_line_1.x2(), vertical_line_1.y2(), selected_color=Selected_vertical_line_color)
        arrow_line_horizontal = CustomArrowLine(horizontal_line.x1(), horizontal_line.y1(), horizontal_line.x2(), horizontal_line.y2(), selected_color=Selected_horizontal_line_color)
        arrow_line_vertical_2 = CustomArrowLine(vertical_line_2.x1(), vertical_line_2.y1(), vertical_line_2.x2(), vertical_line_2.y2(), selected_color=Selected_horizontal_line_color)
        
        dx = end_point.x() - horizontal_point.x()
        dy = end_point.y() - horizontal_point.y()
        angle = math.atan2(dy, dx)
        
        arrow_size = 8
        arrowhead = QPolygonF()
        arrowhead.append(end_point)
        arrowhead.append(end_point + QPointF(math.sin(angle - math.pi / 3) * arrow_size, -math.cos(angle - math.pi / 3) * arrow_size))
        arrowhead.append(end_point + QPointF(math.sin(angle - math.pi + math.pi / 3) * arrow_size, -math.cos(angle - math.pi + math.pi / 3) * arrow_size))
        
        arrow_head = QGraphicsPolygonItem(arrowhead)
        arrow_head.setBrush(QBrush(QColor(Selected_horizontal_line_color)))
        arrow_head.setPen(QPen(QColor(Selected_horizontal_line_color), 2))

        self.scene.addItem(arrow_line_vertical_1)
        self.scene.addItem(arrow_line_horizontal)
        self.scene.addItem(arrow_line_vertical_2)
        self.scene.addItem(arrow_head)

        self.nodes[parent_id]["arrows"].append((arrow_line_vertical_1, arrow_line_horizontal, arrow_line_vertical_2, arrow_head))
        self.nodes[child_id]["arrows"].append((arrow_line_vertical_1, arrow_line_horizontal, arrow_line_vertical_2, arrow_head))

    # Update AFR value of the leaf node
    def Update_Leaf_Value(self, node_id, idx):
        logger.info("Update Leaf Value")
        node = self.nodes[node_id]
        # Check if the node is tagged as a leaf
        if "leaf" in node["tags"]:
            values = []

            # Iterate over the 5 value entries (QComboBox widgets)
            for i in range(5):
                try:
                    # Access the QGraphicsProxyWidget which contains the QComboBox
                    proxy_widget = node["values"][i]
                    
                    # Ensure the proxy widget is valid and contains a QComboBox
                    if proxy_widget and isinstance(proxy_widget.widget(), QComboBox):
                        value_entry = proxy_widget.widget()
                        value_text = value_entry.currentText().split()[0]  # Extract the numerical part
                        value = int(value_text)
                        values.append(value)
                    else:
                        values.append(0)
                except (IndexError, ValueError):
                    # In case of an error, append a default value
                    values.append(0)

            # Calculate the total value by summing up the values from the QComboBox widgets
            node_value_sum = sum(values)

            # Update the 'value_box' QGraphicsTextItem with the new total value
            node["af_value_box"].setPlainText(str(node_value_sum))
            node["af_level_box"].setPlainText(helper.Calculate_AFR_Level(node_value_sum))  # Update to use setPlainText

            self.update_root_node_value()
            self.Update_Arrows_for_All_Nodes()
        
        self.Auto_Update_Leaf_value(node_id)
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    
    # Save Technical tree
    def Save_Tree(self): 
        logger.info("Save Technical Tree")
        self.Update_All_Node_Positions()
        AST.Save_TechnicalTree(self, self.technical_id, self.nodes)
        interfaces.previous_tree = self
        interfaces.unsaved_changes = False
    
    # Refresh Technical tree
    def Load_TechnicalTree(self):
        logger.info("Load Technical Tree")
        try:
            self.nodes = {}
            self.arrows = {}
            self.node_counter = 0
            self.selected_path = []
            self.scene.clear()
            rows = get_instances(
                TechnicalTreeHome,
                filters=None  # Because we want LIKE, not an equality filter
            )
            
            def update_dictionary(technical_id, node_data, node_type, x, y):
                if node_data["image_type"] == "selected_path_node":
                    self.selected_path.append(technical_id)
                    if node_type == 'leaf':
                        widget = node_data["image"].widget() 
                        widget.setStyleSheet(tree_style.selectedleafnode_box_style)
                else:
                    if node_type == 'leaf':
                        widget = node_data["image"].widget() 
                        widget.setStyleSheet(tree_style.leafnode_box_style)
                
                # Store node details
                self.nodes[technical_id] = {
                    "image": node_data["image"],
                    "sidebar": node_data["sidebar"],
                    "text": node_data["text"],
                    "id": node_data["id"],
                    "line": node_data["line"],
                    "af_value_box": node_data["af_value_box"],
                    "af_level_box": node_data["af_level_box"],
                    "values": node_data["values"],
                    "gate":  node_data["gate"],
                    "children": node_data["children"],
                    "parent": node_data["parent"],
                    "gate_type":  node_data["gate_type"],
                    "children_count": node_data["children_count"],
                    "tags": [node_type],
                    "arrows": [],
                    "image_type": node_data["image_type"],
                    "x":x,
                    "y":y
                }
                
                if node_type == 'head':
                    self.scene.addItem(node_data["image"])
                    self.scene.addItem(node_data["sidebar"])
                    self.scene.addItem(node_data["id"])
                    self.scene.addItem(node_data["text"])
                    self.scene.addItem(node_data["line"])
                    self.scene.addItem(node_data["af_value_box"])
                    self.scene.addItem(node_data["af_level_box"])
                    self.scene.addItem(node_data["gate"])
                elif node_type == 'intermediate':
                    self.scene.addItem(node_data["image"])
                    self.scene.addItem(node_data["sidebar"])
                    self.scene.addItem(node_data["id"])
                    self.scene.addItem(node_data["text"])
                    self.scene.addItem(node_data["line"])
                    self.scene.addItem(node_data["af_value_box"])
                    self.scene.addItem(node_data["af_level_box"])
                    self.scene.addItem(node_data["gate"])
                elif node_type == 'leaf':
                    self.scene.addItem(node_data["image"])
                    self.scene.addItem(node_data["sidebar"])
                    self.scene.addItem(node_data["id"])
                    self.scene.addItem(node_data["text"])
                    self.scene.addItem(node_data["line"])
                    self.scene.addItem(node_data["valueline"])
                    self.scene.addItem(node_data["af_value_box"])
                    self.scene.addItem(node_data["af_level_box"])
                    for index, icons in node_data["values_icon"].items():
                        self.scene.addItem(icons)
                    for index, combobox in node_data["values"].items():
                        self.scene.addItem(combobox)
                    self.nodes[technical_id]['valueline'] = node_data["valueline"]
                    self.nodes[technical_id]['values_icon'] = node_data["values_icon"]

            
            if rows:
                node_map = {}
                for row in rows:
                    technical_id = row[0]
                    node_map[row[0]] = {"node_id": row[0], "parent_id": row[1], "node_type": row[2], "text": row[3], 
                                "af_value": row[4], "af_level": row[5], "gate_type": row[6], "values": row[7], 
                                "image_type": row[8], 'x': row[9], 'y': row[10]}
                    
                    if node_map[technical_id]["node_type"] == 'head':
                        node_data = NC.Create_HeadNode(self, node_map[technical_id]["node_id"], self.technical_id, self.technical_name, node_map[technical_id]["x"], node_map[technical_id]["y"], node_map[technical_id]["gate_type"], node_map[technical_id]["af_value"], node_map[technical_id]["af_level"])
                        node_data["values"] = {}
                        node_data["children"] = []
                        node_data["parent"] = node_map[technical_id]["parent_id"]
                        node_data["image_type"] = node_map[technical_id]["image_type"]
                        update_dictionary(node_map[technical_id]["node_id"], node_data, 'head', node_map[technical_id]["x"], node_map[technical_id]["y"])
                    elif node_map[technical_id]["node_type"] == 'intermediate':
                        node_id = node_map[technical_id]["text"].strip().split(' ')[0]
                        node_text = node_map[technical_id]["text"].strip().removeprefix(f"{node_id} ")
                        node_data = NC.Create_IntermediateNode(self, node_map[technical_id]["node_id"], node_id, node_map[technical_id]["x"], node_map[technical_id]["y"], node_text, '', '', node_map[technical_id]["gate_type"])
                        node_data["values"] = {}
                        node_data["children"] = []
                        node_data["parent"] = node_map[technical_id]["parent_id"]
                        node_data["image_type"] = node_map[technical_id]["image_type"]
                        update_dictionary(node_map[technical_id]["node_id"], node_data, 'intermediate', node_map[technical_id]["x"], node_map[technical_id]["y"])
                    elif node_map[technical_id]["node_type"] == 'leaf':
                        node_id = node_map[technical_id]["text"].strip().replace("'", '').split(' ')[0]
                        node_text = node_map[technical_id]["text"].strip().removeprefix(f"{node_id} ")
                        values = node_map[technical_id]["values"].strip().replace("[", '').replace("]", '').replace("'", '').split(', ')
                        node_data = NC.Create_LeafNode(self, node_map[technical_id]["node_id"], node_id, node_map[technical_id]["x"], node_map[technical_id]["y"], node_map[technical_id]["image_type"], node_text, node_map[technical_id]["af_value"], node_map[technical_id]["af_level"], values)
                        node_data["children"] = []
                        node_data["parent"] = node_map[technical_id]["parent_id"]
                        node_data["image_type"] = node_map[technical_id]["image_type"]
                        update_dictionary(node_map[technical_id]["node_id"], node_data, 'leaf', node_map[technical_id]["x"], node_map[technical_id]["y"])
                    else: pass
                
                # Third pass: Create connections
                for node_info in node_map.values():
                    node_id = node_info["node_id"]
                    parent_id = node_info["parent_id"]
                    if parent_id and parent_id in node_map:
                        parent_node_id = node_map[parent_id]["node_id"]
                        if parent_node_id in self.nodes:
                            self.nodes[parent_node_id]['children'].append(node_id)
                            self.Create_Arrow(self.nodes[parent_node_id]["image"], self.nodes[node_id]["image"], parent_node_id, node_id)
                            if node_map[parent_node_id]['node_type']  == 'leaf': raise ValueError("Tree data is incorrect.")
                        elif parent_node_id and parent_node_id not in self.nodes: raise ValueError("Tree data is incorrect.")
                        else: pass
                    elif parent_id and parent_id not in node_map: raise ValueError("Tree data is incorrect.")
                    
                existing_ids = []
                for row in rows:  
                    if row[0] not in existing_ids: existing_ids.append(row[0])
                if 0 < len(existing_ids):
                    existing_max_id = max([int(data.removeprefix(f'{self.technical_id}_node_')) for data in existing_ids])
                    self.node_counter = existing_max_id + 1
            else: 
                self.Create_Head_Node(0, 0)
            
            head_node_id = f'{self.technical_id}_node_0'
            self.Realign_Node_Positions(head_node_id)
            self.Update_Arrows_for_All_Nodes()
            interfaces.previous_tree = self
            interfaces.unsaved_changes = False
        except Exception as e:
            self.nodes = {}
            self.arrows = {}
            self.node_counter = 0
            self.selected_path = []
            self.scene.clear()
            self.Create_Head_Node(0, 0)
            
            head_node_id = f'{self.technical_id}_node_0'
            self.Realign_Node_Positions(head_node_id)
            self.Update_Arrows_for_All_Nodes()
            interfaces.previous_tree = self
            interfaces.unsaved_changes = True
            QMessageBox.critical(None, "Load Error", f"Failed to load the tree")

    # update all arrows of the Technical tree
    def Update_Arrows_for_All_Nodes(self):
        self.Clear_Arrows()
        for parent_id, node_info in self.nodes.items():
            node = node_info.get("image")
            if node:
                for child_id in node_info.get("children", []):
                    if child_id not in self.selected_path:
                        child_node = self.nodes.get(child_id)
                        if child_node and "image" in child_node:
                            self.Create_Arrow(node, child_node["image"], parent_id, child_id)
                        else: pass
        for parent_id, node_info in self.nodes.items():
            node = node_info.get("image")
            if node:
                for child_id in node_info.get("children", []):
                    if child_id in self.selected_path:
                        child_node = self.nodes.get(child_id)
                        if child_node and "image" in child_node:
                            self.Create_Arrow(node, child_node["image"], parent_id, child_id)
                        else: pass

    # clear all arrows of the Technical tree
    def Clear_Arrows(self):
        for node_id, node_info in self.nodes.items():
            for arrow in self.nodes[node_id]["arrows"]:
                if isinstance(arrow, tuple) and len(arrow) > 0:
                    # Assuming the first element of the tuple is the QGraphicsItem
                    self.scene.removeItem(arrow[0])
                    
                    self.scene.removeItem(arrow[1])
                    self.scene.removeItem(arrow[2])
                    self.scene.removeItem(arrow[3])
            self.nodes[node_id]["arrows"] = []

    # update all changed leaf data of the Technical tree
    def Update_Leaf_Data(self):
        logger.info("Update Leaf Data")
        self.value_updated_leafs_list = []
        self.name_updated_leafs_list = []
        for node_id, node_data in self.nodes.items():
            if "leaf" in node_data["tags"]:
                leaf_id = node_data['id'].toPlainText()
                leaf_name = node_data['text'].toPlainText()
                leaf_values = []
                for i in range(5):
                    try:
                        proxy_widget = node_data["values"][i]
                        if proxy_widget and isinstance(proxy_widget.widget(), QComboBox):
                            value_entry = proxy_widget.widget()
                            value_text = value_entry.currentText()
                            leaf_values.append(value_text)
                        else:
                            leaf_values.append('0')
                    except (IndexError, ValueError):
                        leaf_values.append('0')
                leaf_af_level = node_data['af_level_box'].toPlainText()
                GetAndUpdate_Changed_leaf_list(self, leaf_id, leaf_name, leaf_af_level, leaf_values)
        Update_AllTree(value_updated_leafs_list = list(set(self.value_updated_leafs_list)), name_updated_leafs_list = list(set(self.name_updated_leafs_list)))

    # auto update all same leaf value in the Technical tree
    def Auto_Update_Leaf_value(self, node_id):
        logger.info("Auto Update Leaf Value")
        leaf_id = self.nodes[node_id]['id'].toPlainText()
        leaf_name = self.nodes[node_id]['text'].toPlainText()
        leaf_af_value = self.nodes[node_id]['af_value_box'].toPlainText()
        leaf_af_level = self.nodes[node_id]['af_level_box'].toPlainText()
        leaf_values = []
        for i in range(5):
            try:
                proxy_widget = self.nodes[node_id]["values"][i]
                if proxy_widget and isinstance(proxy_widget.widget(), QComboBox):
                    value_entry = proxy_widget.widget()
                    value_text = value_entry.currentText()
                    leaf_values.append(value_text)
                else:
                    leaf_values.append('0')
            except (IndexError, ValueError):
                leaf_values.append('0')
        for node_id, node_data in self.nodes.items():
            if leaf_id == node_data["id"].toPlainText():
                for i in range(5):
                    try:
                        proxy_widget = self.nodes[node_id]["values"][i]
                        if proxy_widget and isinstance(proxy_widget.widget(), QComboBox):
                            value_entry = proxy_widget.widget()
                            value_text = value_entry.set_text(leaf_values[i])
                    except (IndexError, ValueError): pass
                self.nodes[node_id]["text"].setPlainText(leaf_name)
                self.nodes[node_id]["af_value_box"].setPlainText(leaf_af_value)
                self.nodes[node_id]["af_level_box"].setPlainText(leaf_af_level)
        
                self.update_root_node_value()
                self.Update_Arrows_for_All_Nodes()
                
    # auto update all same leaf name in the Technical tree
    def Auto_Update_Leaf_name(self, node_id):
        logger.info("Auto Update Leaf Name")
        leaf_id = self.nodes[node_id]['id'].toPlainText()
        leaf_name = self.nodes[node_id]['text'].toPlainText()
        for node_id, node_data in self.nodes.items():
            if leaf_id == node_data["id"].toPlainText():
                self.nodes[node_id]["text"].setPlainText(leaf_name)
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    # update all node x position in the Technical tree
    def Update_All_Node_Positions(self):
        for node_id, node_info in self.nodes.items():
            self.nodes[node_id]['x'] = node_info['image'].scenePos().x()

    # auto update all same leaf value in the Technical tree
    def Auto_Update_Leaf_value_from_AttackLeave(self):
        logger.info("Auto Update Leaf Value from Attack Leave")
        for node_id, node_data in self.nodes.items():
            if node_data['tags'][0]:
                leaf_id = node_data['id'].toPlainText()
                row = get_first_instance(AttackLeafNodes, {"id": leaf_id})
                if row:
                    available_leaf = (
                        row.name,
                        row.time,
                        row.expertise,
                        row.knowledge,
                        row.access,
                        row.equipment,
                        row.AFR_Level
                    )
                else:
                    available_leaf = None  # Handle the "not found" case as needed
                leaf_name = available_leaf[0]
                values = [value for value in available_leaf[1:6]]
                leaf_values = [int(value) for value in available_leaf[1:6]]
                leaf_af_value = sum(leaf_values)
                leaf_af_level = available_leaf[6]
                node_data["text"].setPlainText(leaf_name)
                node_data["af_value_box"].setPlainText(leaf_af_value)
                node_data["af_level_box"].setPlainText(leaf_af_level)
                for i in range(5):
                    try:
                        proxy_widget = node_data["values"][i]
                        if proxy_widget and isinstance(proxy_widget.widget(), QComboBox):
                            value_entry = proxy_widget.widget()
                            value_text = value_entry.set_text(values[i])
                    except (IndexError, ValueError): pass
                
                self.update_root_node_value()
                self.Update_Arrows_for_All_Nodes()

    # realign all node x position in the Technical tree
    def Realign_Node_Positions(self, node_id, child_x=0):
        if node_id in self.nodes:
            child_list = self.nodes[node_id]["children"]
            child_y = self.nodes[node_id]["y"] + 200
            old_child_x = child_x
            for child_id in child_list:
                NC.Reposition_Nodes(self.nodes[child_id], self.nodes[child_id]['tags'][0], child_x, child_y)
                if self.nodes[child_id]['children']:
                    child_x = self.Realign_Node_Positions(child_id, child_x)
                else: child_x += 320
            parent_x = old_child_x + (child_x - old_child_x - 320)/2
            if self.nodes[node_id]["children"]:
                start_parent_x = self.nodes[self.nodes[node_id]["children"][0]]['x']
                last_parent_x = self.nodes[self.nodes[node_id]["children"][-1]]['x']
                parent_x = start_parent_x + (last_parent_x - start_parent_x)/2
            NC.Reposition_Nodes(self.nodes[node_id], self.nodes[node_id]['tags'][0], parent_x, self.nodes[node_id]["y"])
        return child_x



