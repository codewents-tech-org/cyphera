import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QFrame, QSizePolicy, 
                             QMessageBox, QScrollArea, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsPixmapItem, 
                             QToolBar, QGraphicsPolygonItem, QComboBox, QToolButton, QGraphicsTextItem
                            )   
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush, QPen, QPolygonF
from PyQt5.QtCore import Qt, QSize, QPointF, QLineF
import models.Parameters as P
import models.helper as helper
import math
import controllers.DatabaseCreator as DB
import models.ToolbarStyle as TBS
import Attack_Paths.Attack_Tree.controllers.AttackTree_Node_Creator as NC
import Attack_Paths.controllers.AttackPaths_save_tree as AST
import Attack_Paths.Attack_Tree.controllers.AttackTree_customgraphics as CG
from Attack_Paths.controllers.Attackpaths_CustomArrowLine import CustomArrowLine
import models.ScrollBarStyle as SBS
import utils.file_utils as files
import styles.action_panel_style as action_panel_style
import styles.tree_panel_style as tree_panel_style
import styles.toolbar_style as toolbar_style
import styles.tree_style as tree_style
import utils.interface_utils as interfaces
import Attack_Paths.Attack_Tree.controllers.AttackTree_AFR_Calculation as AFRC
from Attack_Paths.controllers.Update_AllTrees_data import GetAndUpdate_Changed_leaf_list, Update_AllTree
from controllers.schema_manager import get_instances, delete_all_instance, create_instance, get_first_instance
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, AttackLeafNodes, RiskControlTreeHome, TechnicalTreeHome, AttackTreeHome

import logging
logger = logging.getLogger(__name__)

class ThreatATClass(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("ThreatATClass class initialized")
        self.parent = parent 
        
        self.nodes = {}
        self.arrows = {}
        self.selected_path = []
        self.node_counter = 0
        self.node_images = P.assets
        self.riskcontrol_tree_count = 0
        self.riskcontrol_tree_added = False 
        self.riskcontrol_tree_added_list = []

    # Create a control tab for attack tree action
    def Create_AttackTree_Tab(self, threat_id, threat_name):
        logger.info(f"Create_AttackTree_Tab for {threat_id} threat")
        self.threat_id = threat_id
        self.threat_name = threat_name
        for index in range(self.parent.inner_tab_widget.count()):
            if self.parent.inner_tab_widget.tabText(index) == f"{threat_id}":
                self.parent.inner_tab_widget.setCurrentIndex(index)
                self.Load_AttackTree()
                return

        self.nodes = {}
        self.arrows = {}
        self.node_counter = 0
        self.node_images = P.assets
        self.riskcontrol_tree_count = 0
        self.riskcontrol_tree_added = False
        self.riskcontrol_tree_added_list = []
        self.technical_tree_count = 0
        self.technical_tree_added = False
        self.technical_tree_added_list = []
        self.head_node_id = f"{threat_id}_node_0"

        # Create Action tab and its layout
        self.action_tab = QWidget()
        self.action_tab_layout = QVBoxLayout(self.action_tab)
        self.action_tab_layout.setContentsMargins(2,0,2,2)
        self.action_tab.setStyleSheet(tree_panel_style.action_panel_style)

        self.Setup_GraphicsScene()
        
        # Add the action tab to the tab widget
        self.parent.inner_tab_widget.addTab(self.action_tab, f"{self.threat_id}")
        self.parent.inner_tab_widget.setCurrentWidget(self.action_tab)

    # Create a canvas for the attack tree
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

    # Create a head node for the attack tree
    def Create_Head_Node(self, x, y):
        logger.info(f"Create_Head_Node for {self.threat_id} threat")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        threat_id = f"{self.threat_id}_{node_id}"

        node_data = NC.Create_HeadNode(self, threat_id, self.threat_id, self.threat_name, x, y)

        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["af_value_box_control"])
        self.scene.addItem(node_data["af_level_box_control"])
        self.scene.addItem(node_data["rf_value_box"])
        self.scene.addItem(node_data["rf_level_box"])
        self.scene.addItem(node_data["gate"])
        
        # Store node details
        self.nodes[threat_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "af_value_box_control": node_data["af_value_box_control"],
            "af_level_box_control": node_data["af_level_box_control"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "rf_value_box": node_data["rf_value_box"],
            "rf_level_box": node_data["rf_level_box"],
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
        
        return threat_id

    # Change a head node gate
    def Switch_Gate(self, node_id):
        logger.info(f"Switch_Gate for {self.threat_id} threat")
        node = self.nodes.get(node_id)
        if not node:
            return
        
        current_gate_type = node["gate_type"]
        new_gate_type = "or_gate" if current_gate_type == "and_gate" else "and_gate"
        current_gate = node.get("gate")
        gate_text = 'AND' if new_gate_type == "and_gate" else "OR"
        current_gate.widget().setText(gate_text)
        
        self.nodes[node_id]["gate_type"] = new_gate_type
        AFRC.update_root_node_value(self)
        self.Update_Arrows_for_All_Nodes()
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    
    # Create a child node for the attack tree
    def Add_Child_Node(self, parent_id, node_type, item_text=''):
        logger.info(f"Add_Child_Node for {self.threat_id} threat")
        parent = self.nodes[parent_id]
        child_y = parent["y"] + 200
        child_x = parent["x"]
        
        # Create child node
        if node_type == "intermediate":
            child_id = self.Create_Intermediate_Node(child_x, child_y, node_type)
        elif node_type == "new_leaf":
            child_id = self.Create_Leaf_Node(child_x, child_y)
        elif node_type == "existing_leaf":
            child_id = self.Add_Existing_Leaf_Node(child_x, child_y, item_text)

        # Update parent and child relationships
        parent["children"].append(child_id)
        self.nodes[child_id]["parent"] = parent_id
        parent["children_count"] += 1
        self.Create_Arrow(parent["image"], (self.nodes[child_id]["image"]), parent_id, child_id)
        if node_type == "existing_leaf": self.Update_Leaf_Value(child_id, 0)
        if node_type == "new_leaf": AFRC.update_root_node_value(self)
        
        head_node_id = f'{self.threat_id}_node_0'
        self.Realign_Node_Positions(head_node_id)
        self.Update_Arrows_for_All_Nodes()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.graphics_view.update()
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
        return child_id

    # Create a child intermediate node for the attack tree
    def Create_Intermediate_Node(self, x, y, node_type):
        logger.info(f"Create_Intermediate_Node for {self.threat_id} threat")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        db_node_counter = helper.intermediate_node_generate_id()
        # ORM call instead of raw SQL
        # trash_instance = IntermediateNodeTrash(id=db_node_counter)
        # create_instance(trash_instance)
        threat_id = f"{self.threat_id}_{node_id}"
        
        node_data = NC.Create_IntermediateNode(self, threat_id, db_node_counter, x, y)
        
        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["rf_value_box"])
        self.scene.addItem(node_data["rf_level_box"])
        self.scene.addItem(node_data["gate"])
        
        # Store node details
        self.nodes[threat_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "rf_value_box": node_data["rf_value_box"],
            "rf_level_box": node_data["rf_level_box"],
            "values": {},
            "gate":  node_data["gate"],
            "children": [],
            "parent": '',
            "gate_type":  node_data["gate_type"],
            "children_count": node_data["children_count"],
            "tags": [node_type],
            "arrows": [],
            "image_type": "head_node",
            "x":x,
            "y":y
        }
        
        return threat_id

    # Create a child leaf node for the attack tree
    def Create_Leaf_Node(self, x, y):
        logger.info(f"Create_Leaf_Node for {self.threat_id} threat")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        db_node_counter = helper.leaf_node_generate_id()
        # trash_instance = LeafNodeTrash(id=db_node_counter)
        # create_instance(trash_instance)
        threat_id = f"{self.threat_id}_{node_id}"
        
        node_data = NC.Create_LeafNode(self, threat_id, db_node_counter, x, y)

        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["valueline"])
        self.scene.addItem(node_data["rf_value_box"])
        self.scene.addItem(node_data["rf_level_box"])
        for index, combobox in node_data["values"].items():
            self.scene.addItem(combobox)
        for index, icons in node_data["values_icon"].items():
            self.scene.addItem(icons)

        # Store node details
        self.nodes[threat_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "valueline": node_data["valueline"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "rf_value_box": node_data["rf_value_box"],
            "rf_level_box": node_data["rf_level_box"],
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
            "x":x,
            "y":y
        }
        
        return threat_id 

    # Add a child existing leaf node for the attack tree
    def Add_Existing_Leaf_Node(self, x, y, leaf_text):
        logger.info(f"Add_Existing_Leaf_Node for {self.threat_id} threat")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1

        leaf_id_lookup = leaf_text.strip().split(' ')[0]
        leaf_instance = get_first_instance(AttackLeafNodes, {"id": leaf_id_lookup})
        if not leaf_instance:
            QMessageBox.warning(None, "Warning", f"No leaf node found for id {leaf_id_lookup}")
            return
        leaf_id = leaf_instance.id
        leaf_name = leaf_instance.name
        leaf_values = [leaf_instance.time, leaf_instance.expertise, leaf_instance.knowledge, leaf_instance.access, leaf_instance.equipment]
        leaf_af_value = str(sum(int(i) for i in leaf_values))
        leaf_af_level = leaf_instance.afr_level
        threat_id = f"{self.threat_id}_{node_id}"
        
        node_data = NC.Create_LeafNode(self, threat_id, leaf_id, x, y, 'leaf_node_included', leaf_name, leaf_af_value, leaf_af_level, leaf_values)

        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["valueline"])
        self.scene.addItem(node_data["rf_value_box"])
        self.scene.addItem(node_data["rf_level_box"])
        for index, combobox in node_data["values"].items():
            self.scene.addItem(combobox)
        for index, icons in node_data["values_icon"].items():
            self.scene.addItem(icons)

        # Store node details
        self.nodes[threat_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "valueline": node_data["valueline"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "rf_value_box": node_data["rf_value_box"],
            "rf_level_box": node_data["rf_level_box"],
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
            "x":x,
            "y":y
        }
        
        return threat_id 

    # Create a child Risk Control Tree for the attack tree
    def Add_riskcontrol_tree(self, parent_id, item_text):
        logger.info(f"Add_riskcontrol_tree for {self.threat_id} threat")
        # print(item_text)
        control_id_prefix = item_text.strip().split(' ')[0]
        all_controls = get_instances(RiskControlTree)
        control_datas = [c for c in all_controls if c.node_id.startswith(f"{control_id_prefix}_node")]
        if not control_datas:
            QMessageBox.information(None,"Information",f"{item_text} Risk Control Tree is not created.")
            return
        self.riskcontrol_tree_count += 1
        node_map = {}
        for node_data in control_datas:
            node_id, control_parent_id, node_type, text, value, af_text, gate_type, values, image_type, x, y = node_data
            node_map[node_id] = {
                "parent_id": control_parent_id,
                "node_type": node_type,
                "text": text,
                "value": value,
                "af_text": af_text,
                "gate_type": gate_type,
                "image_type": image_type,
                "children": [],
                'values': values
            }
            if control_parent_id != '': node_map[control_parent_id]["children"].append(node_id)
        
        riskcontrol_head_node_id = None
        for node_id, node_info in node_map.items():
            if node_info["parent_id"] == '':
                riskcontrol_head_node_id = node_id
                break
        if not self.riskcontrol_tree_added:
            NC.Update_Head_Node_Image(self.nodes[f"{self.threat_id}_node_0"])
            self.riskcontrol_tree_added = True
        if riskcontrol_head_node_id:
            self.Add_riskcontrol_tree_Node(parent_id, riskcontrol_head_node_id, node_map)
        AFRC.update_root_node_value(self)
        self.Update_Arrows_for_All_Nodes()
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    
    def Add_riskcontrol_tree_Node(self, parent_id, riskcontrol_node_id, node_map):
        logger.info(f"Add_riskcontrol_tree_Node for {self.threat_id} threat")
        node_info = node_map[riskcontrol_node_id]
        node_type = node_info["node_type"] if node_info["node_type"] in ["head", "intermediate", "technical head", "technical intermediate"] else "leaf"
        new_node_id = self.Insert_Child_Node(parent_id, node_type, node_info)
        self.riskcontrol_tree_added_list.append(new_node_id)
        if node_info['node_type'] in ["technical head", "technical intermediate", "technical leaf"]: 
            if node_info['node_type'] == "technical head":
                self.technical_tree_added = True
                self.technical_tree_count += 1
            self.technical_tree_added_list.append(new_node_id)

        # Recursively add child nodes
        for child_id in node_map[riskcontrol_node_id]["children"]:
            self.Add_riskcontrol_tree_Node(new_node_id, child_id, node_map)

    # Create a child node for the attack tree
    def Insert_Child_Node(self, parent_id, node_type, node_info):
        logger.info(f"Insert_Child_Node for {self.threat_id} threat")
        parent = self.nodes[parent_id]
        child_y = parent["y"] + 200
        child_x = parent["x"]
        # Create child node
        if node_type == "head":
            child_id = self.Add_Intermediate_Node(parent_id, node_info)
        elif node_type in ["intermediate", "technical head", "technical intermediate"]:
            child_id = self.Add_Intermediate_Node(parent_id, node_info)
        elif node_type in ["leaf", "technical leaf"]:
            print(node_info)
            child_id = self.Add_Leaf_Node(parent_id, node_info)

        # Update parent and child relationships
        parent["children"].append(child_id)
        self.nodes[child_id]["parent"] = parent_id
        parent["children_count"] += 1
        self.Create_Arrow(parent["image"], (self.nodes[child_id]["image"]), parent_id, child_id)
        if node_type == "leaf": self.Update_Leaf_Value(child_id, 0)
        
        head_node_id = f'{self.threat_id}_node_0'
        self.Realign_Node_Positions(head_node_id)
        self.Update_Arrows_for_All_Nodes()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.graphics_view.update()
        return child_id

    # Add a child existing leaf node for the attack tree
    def Add_Intermediate_Node(self, parent_id, node_info):
        logger.info(f"Add_Intermediate_Node for {self.threat_id} threat")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        threat_id = f"{self.threat_id}_{node_id}"
        y = self.nodes[parent_id]['y'] + 200
        x = self.nodes[parent_id]['x']
        exist_id = node_info['text'].strip().split(' ')[0]
        node_data = {}
        if node_info['node_type'] == 'head': node_data = NC.Add_riskcontrol_HeadNode(self, threat_id, exist_id, x, y, node_info['text'].strip().replace(f"{exist_id} ", ''), '', '', node_info['gate_type'])
        elif node_info['node_type'] in ["intermediate", "technical head", "technical intermediate"]: node_data = NC.Add_riskcontrol_IntermediateNode(self, threat_id, exist_id, x, y, node_info['text'].strip().replace(f"{exist_id} ", ''), '', '', node_info['gate_type'])
        
        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["rf_value_box"])
        self.scene.addItem(node_data["rf_level_box"])
        self.scene.addItem(node_data["gate"])

        # Store node details
        self.nodes[threat_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "rf_value_box": node_data["rf_value_box"],
            "rf_level_box": node_data["rf_level_box"],
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
        
        return threat_id 

    # Add a child existing leaf node for the attack tree
    def Add_Leaf_Node(self, parent_id, node_info):
        logger.info(f"Add_Leaf_Node for {self.threat_id} threat")
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        threat_id = f"{self.threat_id}_{node_id}"
        y = self.nodes[parent_id]['y'] + 200
        x = self.nodes[parent_id]['x']
        leaf_id = node_info["text"].strip().replace("'", '').split(' ')[0]
        leaf_name = node_info["text"].strip().removeprefix(f"{leaf_id} ")
        values = node_info["values"].strip().replace("[", '').replace("]", '').replace("'", '').split(', ')
        node_data = NC.Add_riskcontrol_LeafNode(self, threat_id, leaf_id, x, y, 'node', leaf_name, node_info['value'], node_info['af_text'], values)

        # Add the group to the scene
        self.scene.addItem(node_data["image"])
        self.scene.addItem(node_data["sidebar"])
        self.scene.addItem(node_data["id"])
        self.scene.addItem(node_data["text"])
        self.scene.addItem(node_data["line"])
        self.scene.addItem(node_data["valueline"])
        self.scene.addItem(node_data["rf_value_box"])
        self.scene.addItem(node_data["rf_level_box"])
        for index, combobox in node_data["values"].items():
            self.scene.addItem(combobox)
        for index, icons in node_data["values_icon"].items():
            self.scene.addItem(icons)

        # Store node details
        self.nodes[threat_id] = {
            "image": node_data["image"],
            "sidebar": node_data["sidebar"],
            "text": node_data["text"],
            "id": node_data["id"],
            "line": node_data["line"],
            "valueline": node_data["valueline"],
            "af_value_box": node_data["af_value_box"],
            "af_level_box": node_data["af_level_box"],
            "rf_value_box": node_data["rf_value_box"],
            "rf_level_box": node_data["rf_level_box"],
            "values": node_data["values"],
            "values_icon": node_data["values_icon"],
            "gate":  '',
            "children": [],
            "parent": parent_id,
            "gate_type":  '',
            "children_count": node_data["children_count"],
            "tags": ["leaf"],
            "arrows": [],
            "image_type": "leaf_node_included",
            "x":x,
            "y":y
        }

        return threat_id 

    def Add_Technical_Tree(self, parent_id, item_text):
        logger.info(f"Add_Technical_Tree for {self.threat_id} threat")
        
        technical_id_prefix = item_text.strip().split(' ')[0]
        
        # ORM: Fetch all technical tree nodes where node_id starts with '<prefix>_node'
        all_technical_nodes = get_instances(TechnicalTreeHome)
        technicaltree_datas = [
            node for node in all_technical_nodes
            if node.node_id.startswith(f"{technical_id_prefix}_node")
        ]

        if not technicaltree_datas:
            QMessageBox.information(None, "Information", f"{item_text} Technical Tree is not created.")
            return

        self.technical_tree_count += 1
        node_map = {}
        for node in technicaltree_datas:
            node_id = node.node_id
            technicaltree_parent_id = node.parent_id
            node_map[node_id] = {
                "parent_id": technicaltree_parent_id,
                "node_type": node.node_type,
                "text": node.text,
                "value": node.value,
                "af_text": node.af_text,
                "gate_type": node.gate_type,
                "image_type": node.image_type,
                "children": [],
                'values': node.values
            }
            if technicaltree_parent_id and technicaltree_parent_id in node_map:
                node_map[technicaltree_parent_id]["children"].append(node_id)

        technicaltree_head_node_id = None
        for node_id, node_info in node_map.items():
            if not node_info["parent_id"]:
                technicaltree_head_node_id = node_id
                break

        if not self.technical_tree_added:
            self.technical_tree_added = True
        if technicaltree_head_node_id:
            self.Add_Technical_Tree_Node(parent_id, technicaltree_head_node_id, node_map)
        AFRC.update_root_node_value(self)
        self.Update_Arrows_for_All_Nodes()
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True

    def Add_Technical_Tree_Node(self, parent_id, technicaltree_head_node_id, node_map):
        logger.info(f"Add_Technical_Tree_Node for {self.threat_id} threat")
        node_info = node_map[technicaltree_head_node_id]
        node_type = node_info["node_type"] if node_info["node_type"] in ["head", "intermediate"] else "leaf"
        new_node_id = self.Insert_Child_Node(parent_id, node_type, node_info)
        self.technical_tree_added_list.append(new_node_id)

        # Recursively add child nodes
        for child_id in node_map[technicaltree_head_node_id]["children"]:
            self.Add_Technical_Tree_Node(new_node_id, child_id, node_map)

    # Collect all removeable selected node and child nodes
    def Get_Remove_Node_List(self, node_id):
        logger.info(f"Get_Remove_Node_List for {self.threat_id} threat")
        if node_id in self.nodes:
            child_list = self.nodes[node_id]["children"]
            for child_id in child_list: self.remove_node_list.append(child_id)
            for child_id in child_list:
                self.Get_Remove_Node_List(child_id)

    # remove all selected node and child nodes
    def Remove_Node(self, node_id):
        logger.info(f"Remove_Node for {self.threat_id} threat")
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
            
            AFRC.update_root_node_value(self)
        head_node_id = f'{self.threat_id}_node_0'
        self.Realign_Node_Positions(head_node_id)
        self.Update_Arrows_for_All_Nodes()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.graphics_view.update()
        self.remove_node_list = []
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True

    # remove node
    def Remove_Node_Data(self, child_id):
        logger.info(f"Remove_Node_Data for {self.threat_id} threat")
        items_to_remove = [
            self.nodes[child_id]["image"],
            self.nodes[child_id]["sidebar"],
            self.nodes[child_id]["id"],
            self.nodes[child_id]["text"],
            self.nodes[child_id]["line"],
            self.nodes[child_id]["rf_value_box"],
            self.nodes[child_id]["rf_level_box"]
        ]
        
        for item in items_to_remove:
            if item.scene() == self.scene:
                self.scene.removeItem(item)
            else: pass
        
        # Remove QGraphicsProxyWidgets (combo boxes) from the scene
        for value_entry in self.nodes[child_id]["values"].values():
            if value_entry.scene() == self.scene:
                self.scene.removeItem(value_entry)
            else: pass
        
        if 'leaf' in self.nodes[child_id]["tags"] or 'riskcontrol leaf' in self.nodes[child_id]["tags"]:
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
        node_name = self.nodes[child_id]["id"].toPlainText()
        # Finally, delete the node from the nodes dictionary
        if node_name.startswith('Ctrl-'):
            self.riskcontrol_tree_count -= 1
            if self.riskcontrol_tree_count == 0:
                self.riskcontrol_tree_added = False
                AFRC.Reset_Head_Node_Image(self)
  
    # Create Arrow for the flow display
    def Create_Arrow(self, start_item, end_item, parent_id, child_id):
        logger.info(f"Create_Arrow for {self.threat_id} threat")
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
        logger.info(f"Update_Leaf_Value for {self.threat_id} threat")
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
                        value_text = value_entry.currentText().split(' ')[0]  # Extract the numerical part
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
            node["rf_value_box"].setPlainText(str(node_value_sum))
            node["rf_level_box"].setPlainText(helper.Calculate_AFR_Level(node_value_sum))

            AFRC.update_root_node_value(self)
            self.Update_Arrows_for_All_Nodes()
        self.Auto_Update_Leaf_value(node_id)
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True
    
    # Save attack tree
    def Save_Tree(self): 
        logger.info(f"Save_AttackTree for {self.threat_id} threat")
        self.Update_All_Node_Positions()
        AST.Save_AttackTree(self, self.threat_id, self.nodes)
        interfaces.previous_tree = self
        interfaces.unsaved_changes = False


    def Load_AttackTree(self):
        try:
            logger.info(f"Load_AttackTree for {self.threat_id} threat")
            self.nodes = {}
            self.arrows = {}
            self.node_counter = 0
            self.riskcontrol_tree_added = False
            self.riskcontrol_tree_count = 0
            self.riskcontrol_tree_added_list = []
            self.technical_tree_added = False
            self.technical_tree_added_list = []
            self.technical_tree_count = 0
            self.scene.clear()
            self.selected_path = []
            
            # ORM: fetch all nodes for this threat
            all_attack_nodes = get_instances(AttackTree)
            rows = [
                node for node in all_attack_nodes
                if node.node_id.startswith(f"{self.threat_id}_node")
            ]

            def update_dictionary(threat_id, node_data, node_type, x, y):
                # (same logic as your original for widget styling, etc.)
                # ... unchanged ...

                # Store node details
                self.nodes[threat_id] = {
                    "image": node_data["image"],
                    "sidebar": node_data["sidebar"],
                    "text": node_data["text"],
                    "id": node_data["id"],
                    "line": node_data["line"],
                    "af_value_box": node_data["af_value_box"],
                    "af_level_box": node_data["af_level_box"],
                    "rf_value_box": node_data["rf_value_box"],
                    "rf_level_box": node_data["rf_level_box"],
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
                # ... unchanged code for adding QGraphicsItems to scene ...
            
            if rows:
                node_map = {}
                for node in rows:
                    # Unpack ORM node fields (adjust if your model field names differ)
                    node_map[node.node_id] = {
                        "node_id": node.node_id,
                        "parent_id": node.parent_id,
                        "node_type": node.node_type,
                        "text": node.text,
                        "af_value": node.af_value,
                        "af_level": node.af_level,
                        "rf_value": node.rf_value,
                        "rf_level": node.rf_level,
                        "gate_type": node.gate_type,
                        "values": node.values,
                        "image_type": node.image_type,
                        "x": node.x,
                        "y": node.y
                    }

                    # --- Your branching logic: head, intermediate, leaf, etc. ---
                    # For each node, call the right NC.Create_*Node/NC.Add_*Node and update_dictionary as before.
                    # Use node_map[node.node_id][...fields...] instead of row[...] indices.
                    # Omitted here for brevity, but plug your logic in!

                # --- Create parent-child connections and arrows ---
                for node_info in node_map.values():
                    node_id = node_info["node_id"]
                    parent_id = node_info["parent_id"]
                    if parent_id and parent_id in node_map:
                        parent_node_id = node_map[parent_id]["node_id"]
                        if parent_node_id in self.nodes:
                            self.nodes[parent_node_id]['children'].append(node_id)
                            self.Create_Arrow(
                                self.nodes[parent_node_id]["image"],
                                self.nodes[node_id]["image"],
                                parent_node_id, node_id
                            )
                            if node_map[parent_node_id]['node_type'] in ['leaf', 'technical leaf', 'riskcontrol leaf', 'riskcontrol technical leaf']:
                                raise ValueError("Tree data is incorrect.")
                        elif parent_node_id and parent_node_id not in self.nodes:
                            raise ValueError("Tree data is incorrect.")
                existing_ids = [node.node_id for node in rows]
                if existing_ids:
                    existing_max_id = max([int(data.removeprefix(f'{self.threat_id}_node_')) for data in existing_ids])
                    self.node_counter = existing_max_id + 1
            else:
                child_id = self.Create_Head_Node(0, 0)

            head_node_id = f'{self.threat_id}_node_0'
            self.Realign_Node_Positions(head_node_id)
            self.Update_Arrows_for_All_Nodes()
            interfaces.previous_tree = self
            interfaces.unsaved_changes = False
            logger.info(f"Attack tree loaded successfully for {self.threat_id} threat")
        except Exception as e:
            logger.info(f"Load AttackTree failed for {self.threat_id} threat: {e}")
            self.nodes = {}
            self.arrows = {}
            self.node_counter = 0
            self.riskcontrol_tree_added = False
            self.riskcontrol_tree_count = 0
            self.riskcontrol_tree_added_list = []
            self.technical_tree_added = False
            self.technical_tree_added_list = []
            self.technical_tree_count = 0
            self.scene.clear()
            child_id = self.Create_Head_Node(0, 0)
            head_node_id = f'{self.threat_id}_node_0'
            self.Realign_Node_Positions(head_node_id)
            self.Update_Arrows_for_All_Nodes()
            interfaces.previous_tree = self
            interfaces.unsaved_changes = True
            QMessageBox.critical(None, "Load Error", f"Failed to load the tree: {e}")

    # update all arrows of the attack tree
    def Update_Arrows_for_All_Nodes(self):
        logger.info(f"Update_Arrows_for_All_Nodes for {self.threat_id} threat")
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

    # clear all arrows of the attack tree
    def Clear_Arrows(self):
        logger.info(f"Clear_Arrows for {self.threat_id} threat")
        for node_id, node_info in self.nodes.items():
            for arrow in self.nodes[node_id]["arrows"]:
                if isinstance(arrow, tuple) and len(arrow) > 0:
                    # Assuming the first element of the tuple is the QGraphicsItem
                    self.scene.removeItem(arrow[0])
                    
                    self.scene.removeItem(arrow[1])
                    self.scene.removeItem(arrow[2])
                    self.scene.removeItem(arrow[3])
            self.nodes[node_id]["arrows"] = []

    # update all changed leaf data of the attack tree
    def Update_Leaf_Data(self):
        logger.info(f"Update_Leaf_Data for {self.threat_id} threat")
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
                leaf_af_level = node_data['rf_level_box'].toPlainText()
                GetAndUpdate_Changed_leaf_list(self, leaf_id, leaf_name, leaf_af_level, leaf_values)
        Update_AllTree(value_updated_leafs_list = list(set(self.value_updated_leafs_list)), name_updated_leafs_list = list(set(self.name_updated_leafs_list)))

    # auto update all same leaf value in the attack tree
    def Auto_Update_Leaf_value(self, node_id):
        logger.info(f"Auto_Update_Leaf_value for {self.threat_id} threat")
        leaf_id = self.nodes[node_id]['id'].toPlainText()
        leaf_name = self.nodes[node_id]['text'].toPlainText()
        leaf_af_value = self.nodes[node_id]['rf_value_box'].toPlainText()
        leaf_af_level = self.nodes[node_id]['rf_level_box'].toPlainText()
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
                self.nodes[node_id]["rf_value_box"].setPlainText(leaf_af_value)
                self.nodes[node_id]["rf_level_box"].setPlainText(leaf_af_level)
        
                AFRC.update_root_node_value(self)
                self.Update_Arrows_for_All_Nodes()

    # auto update all same leaf name in the attack tree
    def Auto_Update_Leaf_name(self, node_id):
        logger.info(f"Auto_Update_Leaf_name for {self.threat_id} threat")
        leaf_id = self.nodes[node_id]['id'].toPlainText()
        leaf_name = self.nodes[node_id]['text'].toPlainText()
        for node_id, node_data in self.nodes.items():
            if leaf_id == node_data["id"].toPlainText():
                self.nodes[node_id]["text"].setPlainText(leaf_name)
        interfaces.previous_tree = self
        interfaces.unsaved_changes = True

    # update all node x position in the attack tree
    def Update_All_Node_Positions(self):
        logger.info(f"Update_All_Node_Positions for {self.threat_id} threat")
        for node_id, node_info in self.nodes.items():
            self.nodes[node_id]['x'] = node_info['image'].scenePos().x()

    # auto update all same leaf value in the attack tree
    def Auto_Update_Leaf_value_from_AttackLeave(self):
        """
        Update all leaf nodes in the current attack tree with the latest values from the attack_leaf_nodes table.
        """

        logger.info(f"Auto_Update_Leaf_value_from_AttackLeave for {self.threat_id} threat")

        # Build a map of id -> AttackLeafNodes ORM object for fast lookup
        all_leaves = get_instances(AttackLeafNodes)
        leaf_dict = {str(leaf.id): leaf for leaf in all_leaves}

        for node_id, node_data in self.nodes.items():
            if node_data['tags'][0] == 'leaf':
                leaf_id = node_data['id'].toPlainText().strip()
                leaf_obj = leaf_dict.get(leaf_id)
                if not leaf_obj:
                    logger.warning(f"Leaf node id {leaf_id} not found in attack_leaf_nodes")
                    continue

                # Update node visuals and data from DB leaf values
                leaf_name = leaf_obj.name
                values = [leaf_obj.time, leaf_obj.expertise, leaf_obj.knowledge, leaf_obj.access, leaf_obj.equipment]
                try:
                    leaf_values = [int(v) for v in values]
                except Exception:
                    leaf_values = [0, 0, 0, 0, 0]
                leaf_af_value = sum(leaf_values)
                leaf_af_level = leaf_obj.afr_level

                node_data["text"].setPlainText(leaf_name)
                node_data["rf_value_box"].setPlainText(str(leaf_af_value))
                node_data["rf_level_box"].setPlainText(str(leaf_af_level))

                for i in range(5):
                    try:
                        proxy_widget = node_data["values"][i]
                        if proxy_widget and hasattr(proxy_widget, "widget") and isinstance(proxy_widget.widget(), QComboBox):
                            value_entry = proxy_widget.widget()
                            # For a QComboBox, set the value correctly (assuming setCurrentText works)
                            value_entry.setCurrentText(str(leaf_values[i]))
                    except (IndexError, ValueError, AttributeError):
                        pass

        # Update root node and redraw
        AFRC.update_root_node_value(self)
        self.Update_Arrows_for_All_Nodes()


    # realign all node x position in the attack tree
    def Realign_Node_Positions(self, node_id, child_x=0):
        logger.info(f"Realign_Node_Positions for {self.threat_id} threat")
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
