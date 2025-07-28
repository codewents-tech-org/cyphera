import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QFrame, QSizePolicy, 
                             QMessageBox, QScrollArea, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsPixmapItem, 
                             QToolBar, QGraphicsPolygonItem, QComboBox, QToolButton
                            )   
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush, QPen, QPolygonF
from PyQt5.QtCore import Qt, QSize, QPointF, QLineF
import models.Parameters as P
import models.helper as helper
import math
import controllers.DatabaseCreator as DB
import models.ToolbarStyle as TBS
import Attack_Paths.RiskControl_Tree.controllers.RiskControlTree_Node_Creator as NC
import Attack_Paths.controllers.AttackPaths_save_tree as AST
import Attack_Paths.RiskControl_Tree.controllers.RiskControlTree_customgraphics as CG
from Attack_Paths.controllers.Attackpaths_CustomArrowLine import CustomArrowLine
import models.ScrollBarStyle as SBS
import utils.file_utils as files
import styles.action_panel_style as action_panel_style
import styles.tree_panel_style as tree_panel_style
import styles.toolbar_style as toolbar_style
import styles.tree_style as tree_style
from itertools import product
from Attack_Paths.controllers.Update_AllTrees_data import GetAndUpdate_Changed_leaf_list, Update_AllTree
import utils.interface_utils as interfaces
from controllers.schema_manager import get_instances, get_first_instance
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome, AttackLeafNodes
import logging
logger = logging.getLogger(__name__)

class ControlCTClass(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Risk Control Tree Control Class")
        self.parent = parent 
        
        self.nodes = {}
        self.arrows = {}
        self.selected_path = []
        self.node_counter = 0
        self.node_images = P.assets 

    # Create a control tab for Risk Control Tree action
    def Create_RiskControlTree_Tab(self, control_id, control_name):
        logger.info(f"Create Risk Control Tree {control_id} Tab")
        self.control_id = control_id
        self.control_name = control_name
        for index in range(self.parent.inner_tab_widget.count()):
            if self.parent.inner_tab_widget.tabText(index) == f"{control_id}":
                self.parent.inner_tab_widget.setCurrentIndex(index)
                self.Load_RiskControlTree()
                return

        self.nodes = {}
        self.arrows = {}
        self.node_counter = 0
        self.node_images = P.assets
        self.technical_tree_count = 0
        self.technical_tree_added = False
        self.technical_tree_added_list = []
        self.head_node_id = f"{control_id}_node_0"

        # Create Action tab and its layout
        self.action_tab = QWidget()
        self.action_tab_layout = QVBoxLayout(self.action_tab)
        self.action_tab_layout.setContentsMargins(2,0,2,2)
        self.action_tab.setStyleSheet(tree_panel_style.action_panel_style)

        self.Setup_GraphicsScene()
        
        # Add the action tab to the tab widget
        self.parent.inner_tab_widget.addTab(self.action_tab, f"{self.control_id}")
        self.parent.inner_tab_widget.setCurrentWidget(self.action_tab)

    # Create a canvas for the Risk Control Tree
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

    # Create a head node for the Risk Control Tree
    def Create_Head_Node(self, x, y):
        logger.info("Create Head Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        control_id = f"{self.control_id}_{node_id}"

        node_data = NC.Create_HeadNode(self, control_id, self.control_id, self.control_name, x, y)

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
        self.nodes[control_id] = {
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
        
        return control_id

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
    # Create a child node for the Risk Control Tree
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
        
        head_node_id = f'{self.control_id}_node_0'
        self.Realign_Node_Positions(head_node_id)
        self.Update_Arrows_for_All_Nodes()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.graphics_view.update()
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
        return child_id

    def Create_Intermediate_Node(self, x: int, y: int, node_type: str) -> str:
        """
        Creates a new intermediate node, adds it to the scene and internal tracking, and stores its trash info in the DB.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            node_type (str): Type tag for the node.

        Returns:
            str: The unique control_id for the node.
        """
        logger.info("Create Intermediate Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1

        db_node_counter = helper.intermediate_node_generate_id()

        # Use ORM instead of raw SQL for trash entry
        # trash_entry = IntermediateNodeTrash(id=db_node_counter)
        # create_instance(trash_entry)

        control_id = f"{self.control_id}_{node_id}"

        node_data = NC.Create_IntermediateNode(self, control_id, db_node_counter, x, y)

        # Add all relevant node graphics to the scene
        for key in ("image", "sidebar", "id", "text", "line", "af_value_box", "af_level_box", "gate"):
            if node_data.get(key):
                self.scene.addItem(node_data[key])

        # Store node details in self.nodes
        self.nodes[control_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "values": {},
            "gate": node_data["gate"],
            "children": [],
            "parent": '',
            "gate_type": node_data["gate_type"],
            "children_count": node_data["children_count"],
            "tags": [node_type],
            "arrows": [],
            "image_type": "head_node",
            "x": x,
            "y": y
        }

        return control_id

    def Create_Leaf_Node(self, x: int, y: int) -> str:
        """
        Creates a new leaf node for the Risk Control Tree, adds it to the scene and node map,
        and stores its trash info in the DB.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            str: The unique control_id for the new leaf node.
        """
        logger.info("Create Leaf Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1

        db_node_counter = helper.leaf_node_generate_id()

        # Use ORM for trash entry
        # trash_entry = LeafNodeTrash(id=db_node_counter)
        # create_instance(trash_entry)

        control_id = f"{self.control_id}_{node_id}"

        node_data = NC.Create_LeafNode(self, control_id, db_node_counter, x, y)

        # Add basic graphics to scene
        for key in ("image", "sidebar", "id", "text", "line", "valueline", "af_value_box", "af_level_box"):
            if node_data.get(key):
                self.scene.addItem(node_data[key])

        for combobox in node_data.get("values", {}).values():
            self.scene.addItem(combobox)
        for icon in node_data.get("values_icon", {}).values():
            self.scene.addItem(icon)

        # Store node details
        self.nodes[control_id] = {
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
            "gate": '',
            "children": [],
            "parent": '',
            "gate_type": '',
            "children_count": node_data["children_count"],
            "tags": ['leaf'],
            "arrows": [],
            "image_type": "leaf_node",
            "x": x,
            "y": y
        }
        return control_id
    
    # Add a child existing leaf node for the Risk Control Tree
    def Add_Existing_Leaf_Node(self, x, y, leaf_text):
        logger.info("Add Existing Leaf Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1

        leaf_id = leaf_text.strip().split(' ')[0]
        # ORM: get the leaf record
        leaf_data = get_first_instance(AttackLeafNodes, filters={'id': leaf_id})
        if not leaf_data:
            QMessageBox.warning(None, "Missing Data", f"No attack leaf found with id {leaf_id}")
            return None
        leaf_name = leaf_data.name
        leaf_values = [leaf_data.time, leaf_data.expertise, leaf_data.knowledge, leaf_data.access, leaf_data.equipment]
        leaf_af_value = str(sum([int(i) for i in leaf_values]))
        leaf_af_level = leaf_data.AFR_Level
        control_id = f"{self.control_id}_{node_id}"

        node_data = NC.Create_LeafNode(self, control_id, leaf_id, x, y, 'leaf_node_included', leaf_name, leaf_af_value, leaf_af_level, leaf_values)

        for key in ["image", "sidebar", "id", "text", "line", "valueline", "af_value_box", "af_level_box"]:
            self.scene.addItem(node_data[key])
        for combobox in node_data["values"].values():
            self.scene.addItem(combobox)
        for icon in node_data["values_icon"].values():
            self.scene.addItem(icon)

        self.nodes[control_id] = {
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
            "gate": '',
            "children": [],
            "parent": '',
            "gate_type": '',
            "children_count": node_data["children_count"],
            "tags": ['leaf'],
            "arrows": [],
            "image_type": "leaf_node",
            "x": x,
            "y": y
        }
        return control_id
    
    # Create a child Risk Control Tree for the attack tree
    def Add_Technical_Tree(self, parent_id, item_text):
        logger.info("Add Technical Tree")
        tech_tree_id = item_text.strip().split(' ')[0]

        # --- ORM fetch ---
        technicaltree_datas = get_instances(TechnicalTreeHome, filters={"node_id__like": f"{tech_tree_id}_node%"})
        # If not using __like, fallback to raw or adjust as needed:
        # technicaltree_datas = DB.execute_db(f"SELECT * FROM technical_tree WHERE Node_ID LIKE '{tech_tree_id}_node%'")
        if not technicaltree_datas:
            QMessageBox.information(None, "Information", f"{item_text} Risk Control Tree is not created.")
            return
        self.technical_tree_count += 1
        node_map = {}
        for node_data in technicaltree_datas:
            # ORM: access as attributes, not tuple
            node_id = node_data.node_id
            technicaltree_parent_id = node_data.parent_id
            node_type = node_data.node_type
            text = node_data.text
            value = node_data.value
            af_text = node_data.af_text
            gate_type = node_data.gate_type
            image_type = node_data.image_type
            x = node_data.x
            y = node_data.y
            values = node_data.values

            node_map[node_id] = {
                "parent_id": technicaltree_parent_id,
                "node_type": node_type,
                "text": text,
                "value": value,
                "af_text": af_text,
                "gate_type": gate_type,
                "image_type": image_type,
                "children": [],
                "values": values
            }
            if technicaltree_parent_id != '': 
                node_map[technicaltree_parent_id]["children"].append(node_id)

        technicaltree_head_node_id = None
        for node_id, node_info in node_map.items():
            if node_info["parent_id"] == '':
                technicaltree_head_node_id = node_id
                break
        if not self.technical_tree_added:
            self.technical_tree_added = True
        if technicaltree_head_node_id:
            self.Add_Technical_Tree_Node(parent_id, technicaltree_head_node_id, node_map)
        self.update_root_node_value()
        self.Update_Arrows_for_All_Nodes()
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    
    # Create a child node for the attack tree
    def Add_Technical_Child_Node(self, parent_id, node_type, node_info):
        logger.info("Add Technical Child Node")
        parent = self.nodes[parent_id]
        child_y = parent["y"] + 200
        child_x = parent["x"]
        # Create child node
        if node_type == "head":
            child_id = self.Add_TechnicalIntermediate_Node(parent_id, node_info)
        elif node_type == "intermediate":
            child_id = self.Add_TechnicalIntermediate_Node(parent_id, node_info)
        elif node_type == "leaf":
            child_id = self.Add_TechnicalLeaf_Node(parent_id, node_info)

        # Update parent and child relationships
        parent["children"].append(child_id)
        self.nodes[child_id]["parent"] = parent_id
        parent["children_count"] += 1
        self.Create_Arrow(parent["image"], (self.nodes[child_id]["image"]), parent_id, child_id)
        if node_type == "leaf": self.Update_Leaf_Value(child_id, 0)
        
        head_node_id = f'{self.control_id}_node_0'
        self.Realign_Node_Positions(head_node_id)
        self.Update_Arrows_for_All_Nodes()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.graphics_view.update()
        return child_id

    # Add a child existing leaf node for the attack tree
    def Add_TechnicalIntermediate_Node(self, parent_id, node_info):
        logger.info("Add Technical Intermediate Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        control_id = f"{self.control_id}_{node_id}"
        y = self.nodes[parent_id]['y'] + 200
        x = self.nodes[parent_id]['x']
        exist_id = node_info['text'].strip().split(' ')[0]
        node_data = {}
        if node_info['node_type'] == 'head': node_data = NC.Add_Technical_HeadNode(self, control_id, exist_id, x, y, node_info['text'].strip().replace(f"{exist_id} ", ''), '', '', node_info['gate_type'])
        elif node_info['node_type'] == 'intermediate': node_data = NC.Add_Technical_IntermediateNode(self, control_id, exist_id, x, y, node_info['text'].strip().replace(f"{exist_id} ", ''), '', '', node_info['gate_type'])
        
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
        self.nodes[control_id] = {
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
            "parent": parent_id,
            "gate_type":  node_data["gate_type"],
            "children_count": node_data["children_count"],
            "tags": ["intermediate"],
            "arrows": [],
            "image_type": "head_node",
            "x":x,
            "y":y
        }

        return control_id 

    # Add a child existing leaf node for the attack tree
    def Add_TechnicalLeaf_Node(self, parent_id, node_info):
        logger.info("Add Technical Leaf Node")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        control_id = f"{self.control_id}_{node_id}"
        y = self.nodes[parent_id]['y'] + 200
        x = self.nodes[parent_id]['x']
        leaf_id = node_info["text"].strip().replace("'", '').split(' ')[0]
        leaf_name = node_info["text"].strip().removeprefix(f"{leaf_id} ")
        values = node_info["values"].strip().replace("[", '').replace("]", '').replace("'", '').split(', ')
        node_data = NC.Add_Technical_LeafNode(self, control_id, leaf_id, x, y, 'leaf_node_included', leaf_name, node_info['value'], node_info['af_text'], values)

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
        self.nodes[control_id] = {
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
            "parent": parent_id,
            "gate_type":  '',
            "children_count": node_data["children_count"],
            "tags": ["leaf"],
            "arrows": [],
            "image_type": "leaf_node",
            "x":x,
            "y":y
        }

        return control_id 

    # Calculate AFR value and highlight the contributed path to AFR value calculation for the Risk Control Tree
    def update_root_node_value(self):
        logger.info("Update Root Node Value")
        head_node = f"{self.control_id}_node_0"
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
                else: self.Update_Node_Image(node, False)
        # print(self.selected_path)
        for node, node_info in self.nodes.items():
            if node in self.selected_path: node_info["image_type"] = "selected_path_node"
            else: node_info["image_type"] = "node"

    # list all nodes of the contributed path to AFR value calculation
    def Get_Selected_Path(self, node_id):
        logger.info("Get Selected Path")
        node = self.nodes[node_id]
        leaf_path_list = []
        if node["parent"]:
            if node["parent"] not in self.selected_path: self.selected_path.append(node["parent"])
            self.Get_Selected_Path(node["parent"])   

    # list all path Combination of the root node
    def Get_Node_Paths(self, node_id):
        logger.info("Get Node Paths")
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
        logger.info("Update Node Image")
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
        logger.info("Get Remove Node List")
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
        head_node_id = f'{self.control_id}_node_0'
        self.Realign_Node_Positions(head_node_id)
        self.Update_Arrows_for_All_Nodes()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.graphics_view.update()
        self.remove_node_list = []
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    # remove node
    def Remove_Node_Data(self, child_id):
        logger.info("Remove Node Data")
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
        
        node_name = self.nodes[child_id]["id"].toPlainText()
        # Finally, delete the node from the nodes dictionary
        if node_name.startswith('TAT-'):
            self.technical_tree_count -= 1
            if self.technical_tree_count == 0:
                self.technical_tree_added = False

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
    
    # Save Risk Control Tree
    def Save_Tree(self): 
        logger.info("Save Risk Control Tree")
        self.Update_All_Node_Positions()
        AST.Save_RiskControlTree(self, self.control_id, self.nodes)
        interfaces.previous_tree = self
        interfaces.unsaved_changes = False


    def Load_RiskControlTree(self):
        logger.info("Load Risk Control Tree")
        try:
            self.nodes = {}
            self.arrows = {}
            self.node_counter = 0
            self.scene.clear()
            self.technical_tree_added = False
            self.technical_tree_added_list = []
            self.technical_tree_count = 0
            self.selected_path = []

            # ORM: fetch all nodes for this control_id
            node_prefix = f"{self.control_id}_node"
            rows = get_instances(RiskControlTree, filters=None)
            rows = [row for row in rows if row.Node_ID.startswith(node_prefix)]

            def update_dictionary(control_id, node_data, node_type, x, y):
                if node_data["image_type"] == "selected_path_node":
                    self.selected_path.append(control_id)
                    if node_type == 'leaf':
                        widget = node_data["image"].widget()
                        widget.setStyleSheet(tree_style.selectedleafnode_box_style)
                else:
                    if node_type == 'leaf':
                        widget = node_data["image"].widget()
                        widget.setStyleSheet(tree_style.leafnode_box_style)
                # Store node details
                self.nodes[control_id] = {
                    "image": node_data["image"],
                    "sidebar": node_data["sidebar"],
                    "text": node_data["text"],
                    "id": node_data["id"],
                    "line": node_data["line"],
                    "af_value_box": node_data["af_value_box"],
                    "af_level_box": node_data["af_level_box"],
                    "values": node_data["values"],
                    "gate": node_data["gate"],
                    "children": node_data["children"],
                    "parent": node_data["parent"],
                    "gate_type": node_data["gate_type"],
                    "children_count": node_data["children_count"],
                    "tags": [node_type],
                    "arrows": [],
                    "image_type": node_data["image_type"],
                    "x": x,
                    "y": y
                }
                # Add to scene as before...

                if node_type == 'head':
                    for key in ["image", "sidebar", "id", "text", "line", "af_value_box", "af_level_box", "gate"]:
                        self.scene.addItem(node_data[key])
                elif node_type == 'intermediate':
                    for key in ["image", "sidebar", "id", "text", "line", "af_value_box", "af_level_box", "gate"]:
                        self.scene.addItem(node_data[key])
                elif node_type == 'leaf':
                    for key in ["image", "sidebar", "id", "text", "line", "valueline", "af_value_box", "af_level_box"]:
                        self.scene.addItem(node_data[key])
                    for icons in node_data.get("values_icon", {}).values():
                        self.scene.addItem(icons)
                    for combobox in node_data.get("values", {}).values():
                        self.scene.addItem(combobox)
                    self.nodes[control_id]['valueline'] = node_data["valueline"]
                    self.nodes[control_id]['values_icon'] = node_data["values_icon"]

            if rows:
                node_map = {}
                for row in rows:
                    control_id = row.Node_ID
                    node_map[control_id] = {
                        "node_id": row.Node_ID,
                        "parent_id": row.Parent_ID,
                        "node_type": row.Node_Type,
                        "text": row.Text,
                        "af_value": row.Value,
                        "af_level": row.AF_Text,
                        "gate_type": row.Gate_Type,
                        "values": row.Values,
                        "image_type": row.Image_Type,
                        "x": row.x,
                        "y": row.y
                    }

                    # Node creation
                    if node_map[control_id]["node_type"] == 'head':
                        node_data = NC.Create_HeadNode(self, node_map[control_id]["node_id"], self.control_id, self.control_name, node_map[control_id]["x"], node_map[control_id]["y"], node_map[control_id]["gate_type"], node_map[control_id]["af_value"], node_map[control_id]["af_level"])
                        node_data["values"] = {}
                        node_data["children"] = []
                        node_data["parent"] = node_map[control_id]["parent_id"]
                        node_data["image_type"] = node_map[control_id]["image_type"]
                        update_dictionary(node_map[control_id]["node_id"], node_data, 'head', node_map[control_id]["x"], node_map[control_id]["y"])
                    elif node_map[control_id]["node_type"] == 'technical head':
                        self.technical_tree_added = True
                        self.technical_tree_added_list.append(control_id)
                        self.technical_tree_count += 1
                        node_id = node_map[control_id]["text"].strip().split(' ')[0]
                        node_text = node_map[control_id]["text"].strip().removeprefix(f"{node_id} ")
                        node_data = NC.Add_Technical_HeadNode(self, node_map[control_id]["node_id"], node_id, node_map[control_id]["x"], node_map[control_id]["y"], node_text, '', '', node_map[control_id]["gate_type"])
                        node_data["values"] = {}
                        node_data["children"] = []
                        node_data["parent"] = node_map[control_id]["parent_id"]
                        node_data["image_type"] = node_map[control_id]["image_type"]
                        update_dictionary(node_map[control_id]["node_id"], node_data, 'intermediate', node_map[control_id]["x"], node_map[control_id]["y"])
                    elif node_map[control_id]["node_type"] == 'intermediate':
                        node_id = node_map[control_id]["text"].strip().split(' ')[0]
                        node_text = node_map[control_id]["text"].strip().removeprefix(f"{node_id} ")
                        node_data = NC.Create_IntermediateNode(self, node_map[control_id]["node_id"], node_id, node_map[control_id]["x"], node_map[control_id]["y"], node_text, '', '', node_map[control_id]["gate_type"])
                        node_data["values"] = {}
                        node_data["children"] = []
                        node_data["parent"] = node_map[control_id]["parent_id"]
                        node_data["image_type"] = node_map[control_id]["image_type"]
                        update_dictionary(node_map[control_id]["node_id"], node_data, 'intermediate', node_map[control_id]["x"], node_map[control_id]["y"])
                    elif node_map[control_id]["node_type"] == 'technical intermediate':
                        self.technical_tree_added = True
                        self.technical_tree_added_list.append(control_id)
                        self.technical_tree_count += 1
                        node_id = node_map[control_id]["text"].strip().split(' ')[0]
                        node_text = node_map[control_id]["text"].strip().removeprefix(f"{node_id} ")
                        node_data = NC.Add_Technical_IntermediateNode(self, node_map[control_id]["node_id"], node_id, node_map[control_id]["x"], node_map[control_id]["y"], node_text, '', '', node_map[control_id]["gate_type"])
                        node_data["values"] = {}
                        node_data["children"] = []
                        node_data["parent"] = node_map[control_id]["parent_id"]
                        node_data["image_type"] = node_map[control_id]["image_type"]
                        update_dictionary(node_map[control_id]["node_id"], node_data, 'intermediate', node_map[control_id]["x"], node_map[control_id]["y"])
                    elif node_map[control_id]["node_type"] == 'leaf':
                        node_id = node_map[control_id]["text"].strip().replace("'", '').split(' ')[0]
                        node_text = node_map[control_id]["text"].strip().removeprefix(f"{node_id} ")
                        values = node_map[control_id]["values"].strip().replace("[", '').replace("]", '').replace("'", '').split(', ')
                        node_data = NC.Create_LeafNode(self, node_map[control_id]["node_id"], node_id, node_map[control_id]["x"], node_map[control_id]["y"], node_map[control_id]["image_type"], node_text, node_map[control_id]["af_value"], node_map[control_id]["af_level"], values)
                        node_data["children"] = []
                        node_data["parent"] = node_map[control_id]["parent_id"]
                        node_data["image_type"] = node_map[control_id]["image_type"]
                        update_dictionary(node_map[control_id]["node_id"], node_data, 'leaf', node_map[control_id]["x"], node_map[control_id]["y"])
                    elif node_map[control_id]["node_type"] == 'technical leaf':
                        self.technical_tree_added = True
                        self.technical_tree_added_list.append(control_id)
                        self.technical_tree_count += 1
                        node_id = node_map[control_id]["text"].strip().replace("'", '').split(' ')[0]
                        node_text = node_map[control_id]["text"].strip().removeprefix(f"{node_id} ")
                        values = node_map[control_id]["values"].strip().replace("[", '').replace("]", '').replace("'", '').split(', ')
                        node_data = NC.Add_Technical_LeafNode(self, node_map[control_id]["node_id"], node_id, node_map[control_id]["x"], node_map[control_id]["y"], node_map[control_id]["image_type"], node_text, node_map[control_id]["af_value"], node_map[control_id]["af_level"], values)
                        node_data["children"] = []
                        node_data["parent"] = node_map[control_id]["parent_id"]
                        node_data["image_type"] = node_map[control_id]["image_type"]
                        update_dictionary(node_map[control_id]["node_id"], node_data, 'leaf', node_map[control_id]["x"], node_map[control_id]["y"])
                    else:
                        pass

                # Connection phase
                for node_info in node_map.values():
                    node_id = node_info["node_id"]
                    parent_id = node_info["parent_id"]
                    if parent_id and parent_id in node_map:
                        parent_node_id = node_map[parent_id]["node_id"]
                        if parent_node_id in self.nodes:
                            self.nodes[parent_node_id]['children'].append(node_id)
                            self.Create_Arrow(self.nodes[parent_node_id]["image"], self.nodes[node_id]["image"], parent_node_id, node_id)
                            if node_map[parent_node_id]['node_type'] in ['leaf', 'technical leaf']:
                                raise ValueError("Tree data is incorrect.")
                        elif parent_node_id and parent_node_id not in self.nodes:
                            raise ValueError("Tree data is incorrect.")
                        else:
                            pass
                    elif parent_id and parent_id not in node_map:
                        raise ValueError("Tree data is incorrect.")

                # Node counter update
                existing_ids = [row.Node_ID for row in rows]
                if existing_ids:
                    existing_max_id = max([int(data.removeprefix(f'{self.control_id}_node_')) for data in existing_ids])
                    self.node_counter = existing_max_id + 1
            else:
                self.Create_Head_Node(0, 0)

            head_node_id = f'{self.control_id}_node_0'
            self.Realign_Node_Positions(head_node_id)
            self.Update_Arrows_for_All_Nodes()
            interfaces.previous_tree = self
            interfaces.unsaved_changes = False
        except Exception as e:
            self.nodes = {}
            self.arrows = {}
            self.node_counter = 0
            self.technical_tree_added = False
            self.technical_tree_added_list = []
            self.technical_tree_count = 0
            self.scene.clear()
            self.Create_Head_Node(0, 0)

            head_node_id = f'{self.control_id}_node_0'
            self.Realign_Node_Positions(head_node_id)
            self.Update_Arrows_for_All_Nodes()
            interfaces.previous_tree = self
            interfaces.unsaved_changes = True
            QMessageBox.critical(None, "Load Error", f"Failed to load the tree")

    # update all arrows of the Risk Control Tree
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

    # clear all arrows of the Risk Control Tree
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

    # update all changed leaf data of the Risk Control Tree
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

    # auto update all same leaf value in the Risk Control Tree
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

    # auto update all same leaf name in the Risk Control Tree
    def Auto_Update_Leaf_name(self, node_id):
        logger.info("Auto Update Leaf Name")
        leaf_id = self.nodes[node_id]['id'].toPlainText()
        leaf_name = self.nodes[node_id]['text'].toPlainText()
        for node_id, node_data in self.nodes.items():
            if leaf_id == node_data["id"].toPlainText():
                self.nodes[node_id]["text"].setPlainText(leaf_name)
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    # update all node x position in the Risk Control Tree
    def Update_All_Node_Positions(self):
        logger.info("Update All Node Positions")
        for node_id, node_info in self.nodes.items():
            self.nodes[node_id]['x'] = node_info['image'].scenePos().x()


    def Auto_Update_Leaf_value_from_AttackLeave(self):
        logger.info("Auto Update Leaf Value from Attack Leave (ORM)")
        for node_id, node_data in self.nodes.items():
            # If this node is a leaf (still check your own logic for tags)
            if node_data.get('tags') and node_data['tags'][0]:
                leaf_id = node_data['id'].toPlainText()
                # ORM: Fetch leaf by ID
                available_leaf = get_first_instance(AttackLeafHome, filters={"id": leaf_id})
                if not available_leaf:
                    continue

                # Get data from ORM object
                leaf_name = available_leaf.name
                values = [
                    available_leaf.time,
                    available_leaf.expertise,
                    available_leaf.knowledge,
                    available_leaf.access,
                    available_leaf.equipment
                ]
                leaf_values = [int(v) for v in values]
                leaf_af_value = sum(leaf_values)
                leaf_af_level = available_leaf.AFR_Level

                # Update node_data UI widgets
                node_data["text"].setPlainText(str(leaf_name))
                node_data["af_value_box"].setPlainText(str(leaf_af_value))
                node_data["af_level_box"].setPlainText(str(leaf_af_level))

                # Update value comboboxes if present
                for i in range(5):
                    try:
                        proxy_widget = node_data["values"][i]
                        if proxy_widget and isinstance(proxy_widget.widget(), QComboBox):
                            value_entry = proxy_widget.widget()
                            # Assumes your QComboBox subclass has set_text or similar method
                            value_entry.set_text(str(values[i]))
                    except (IndexError, ValueError, KeyError):
                        pass

        self.update_root_node_value()
        self.Update_Arrows_for_All_Nodes()

    # realign all node x position in the Risk Control Tree
    def Realign_Node_Positions(self, node_id, child_x=0):
        logger.info("Realign Node Positions")
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



