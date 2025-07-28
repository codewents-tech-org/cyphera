
import sys
from PyQt5.QtWidgets import QLabel, QGraphicsTextItem, QGraphicsLineItem, QGraphicsProxyWidget, QPushButton
from PyQt5.QtGui import QFont, QPixmap, QPen, QColor
from PyQt5.QtCore import Qt
import Attack_Paths.Attack_Tree.controllers.AttackTree_customgraphics as ATCG
import models.helper as helper
import components.table.multioption_selector as MOS
import models.Highlight_style as HS
import styles.tree_style as tree_style
import utils.file_utils as files

import logging
logger = logging.getLogger(__name__)

def Create_HeadNode(tree_parent, tree_id, node_ID, node_label, x, y, gate_type = "and_gate", rf_value='0', rf_level='High', af_value='', af_level='', image_type="head_node"):
        logger.info(f"Creating Head Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Create QGraphicsPixmapItem
        node_box = ATCG.CustomGraphicsNonEditItem(tree_id, parent=None, attack_tree_parent=tree_parent)
        node_box.setWidget(node_button)
        node_box.setPos(x , y)

        # Sidebar
        sidebar_box = ATCG.SidebarItem(bg_color=tree_style.headnode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = ATCG.CustomGraphicsTextItem(node_label, 280, 40)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        af_value_box = QGraphicsTextItem(af_value)
        af_value_box.setPos(x+50, y+70)
        af_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        af_level_box = ATCG.AFR_level(af_level)
        af_level_box.setPos(x+20, y+100)

        # Create QGraphicsTextItem for rf value box
        rf_value = rf_value if rf_value != '' else '0'
        rf_value_box = QGraphicsTextItem(rf_value)
        rf_value_box.setPos(x+220, y+70)
        rf_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for RF level box
        rf_level = rf_level if rf_level != '' else 'High'
        rf_level_box = ATCG.AFR_level(rf_level)
        rf_level_box.setPos(x+190, y+100)

        gate_text = 'AND' if gate_type == "and_gate" else 'OR'
        gate_button = QPushButton(gate_text)
        gate_button.setFixedSize(70, 25)
        gate_button.setStyleSheet(HS.attackpaths_gate_style)
        
        # Embed the button in the QGraphicsScene using QGraphicsProxyWidget
        proxy_gate_button = QGraphicsProxyWidget()
        proxy_gate_button.setWidget(gate_button)
        proxy_gate_button.setPos(x + 115, y + 100)
        proxy_gate_button.mouseDoubleClickEvent = lambda event: tree_parent.Switch_Gate(tree_id)

        return {"image": node_box, 
                "sidebar": sidebar_box,
                "id": node_id, 
                "text": node_text, 
                "line": node_line,
                "af_value_box": af_value, 
                "af_level_box": af_level, 
                "rf_value_box": rf_value_box, 
                "rf_level_box": rf_level_box, 
                "gate": proxy_gate_button,
                "gate_type": gate_type,
                "children_count": 0,
                "af_value_box_control": af_value_box,
                "af_level_box_control": af_level_box}

def Create_IntermediateNode(tree_parent, tree_id, node_ID, x, y, node_name='Node Name', rf_value='', rf_level='', gate_type = "and_gate", af_value='', af_level=''):
        logger.info(f"Creating Intermediate Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Create QGraphicsPixmapItem
        node_box = ATCG.CustomGraphicsEditItem(tree_id, parent=None, attack_tree_parent=tree_parent)
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = ATCG.SidebarItem(bg_color=tree_style.intermediatenode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = ATCG.EditableTextItem(node_name, fixed_width=280, attack_tree_parent=tree_parent, node_id=tree_id)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        rf_value_box = QGraphicsTextItem(rf_value)
        rf_value_box.setPos(x+220, y+70)
        rf_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        rf_level_box = ATCG.AFR_level(rf_level)
        rf_level_box.setPos(x+190, y+100)
        
        gate_text = 'AND' if gate_type == "and_gate" else 'OR'
        gate_button = QPushButton(gate_text)
        gate_button.setFixedSize(70, 25)
        gate_button.setStyleSheet(HS.attackpaths_gate_style)
        
        # Embed the button in the QGraphicsScene using QGraphicsProxyWidget
        proxy_gate_button = QGraphicsProxyWidget()
        proxy_gate_button.setWidget(gate_button)
        proxy_gate_button.setPos(x + 115, y + 100)
        proxy_gate_button.mouseDoubleClickEvent = lambda event: tree_parent.Switch_Gate(tree_id)

        return {"image": node_box, 
                "sidebar": sidebar_box, 
                "id": node_id, 
                "text": node_text, 
                "line": node_line,
                "af_value_box": af_value, 
                "af_level_box": af_level, 
                "rf_value_box": rf_value_box, 
                "rf_level_box": rf_level_box, 
                "gate": proxy_gate_button,
                "gate_type": gate_type,
                "children_count": 0}

def Create_LeafNode(tree_parent, tree_id, node_ID, x, y, image_type="leaf_node", node_name='Node Name', rf_value='0', rf_level='High', input_values=['0','0','0','0','0'], af_value='', af_level=''):
        logger.info(f"Creating Leaf Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Create QGraphicsPixmapItem
        node_box = ATCG.CustomGraphicsRemoveItem(tree_id, parent=None, attack_tree_parent=tree_parent)
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = ATCG.SidebarItem(bg_color=tree_style.leafnode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = ATCG.EditableTextItem(node_name, fixed_width=280, node_id=tree_id, attack_tree_parent=tree_parent)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        rf_value_box = QGraphicsTextItem(rf_value)
        rf_value_box.setPos(x+220, y+70)
        rf_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        rf_level_box = ATCG.AFR_level(rf_level)
        rf_level_box.setPos(x+190, y+100)

        # Positions and ranges for QComboBox widgets
        value_positions = [(x+20, y+80), (x+50, y+80), (x+80, y+80), (x+110, y+80), (x+140, y+80)]
        value_icons = [files.time_icon, files.Expertise_icon, files.Knowledge_icon, files.Access_icon, files.Equipment_icon]
        values = {}
        icon_proxies = {}
        for idx, (vx, vy) in enumerate(value_positions):
                # Create and position icons
                icon_proxy = QGraphicsProxyWidget()

                # Use QLabel with QPixmap if you convert the SVG to a pixmap
                icon_label = QLabel()
                icon_label.setStyleSheet('background-color: transparent')
                pixmap = QPixmap(value_icons[idx])
                icon_label.setPixmap(pixmap)
                icon_label.setFixedSize(20, 20)  # Adjust size based on the desired icon dimensions
                icon_label.setAlignment(Qt.AlignLeft)
                
                icon_proxy.setWidget(icon_label)
                icon_proxy.setPos(vx, vy)  # Position the icon above the combo box
                icon_proxies[idx] = icon_proxy

                value_entry = MOS.CustomComboBox(helper.attackpath_leaf_values_menu[idx])
                value_entry.set_text(input_values[idx])
                value_entry.setStyleSheet(HS.attakleaves_leaf_combobox_style)
                value_entry.setFixedWidth(30)
                value_entry.currentTextChanged.connect(lambda index, node_id=tree_id, idx=idx: tree_parent.Update_Leaf_Value(tree_id, idx))

                # Create a QGraphicsProxyWidget to embed the QComboBox in the scene
                value_proxy = QGraphicsProxyWidget()
                value_proxy.setWidget(value_entry)
                value_proxy.setPos(vx, vy+20)
                value_proxy.setFocusPolicy(Qt.StrongFocus)
                
                values[idx]=value_proxy

        # Add a line after node_text
        nodevalue_line = QGraphicsLineItem(x + 175, y + 75, x + 175, y + 125)  # Line from (x+15, y+45) to (x+295, y+45)
        nodevalue_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        return {"image": node_box, 
                "sidebar": sidebar_box, 
                "id": node_id, 
                "text": node_text, 
                "line": node_line,
                "valueline": nodevalue_line,
                "af_value_box": af_value, 
                "af_level_box": af_level, 
                "rf_value_box": rf_value_box, 
                "rf_level_box": rf_level_box, 
                "gate": '',
                "gate_type": '',
                "children_count": 0,
                'values_icon': icon_proxies,
                'values': values}

def Add_riskcontrol_HeadNode(tree_parent, tree_id, node_ID, x, y, node_name='Node Name', rf_value='', rf_level='', gate_type = "and_gate", af_value='', af_level=''):
        logger.info(f"Creating riskcontrol Head Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Create QGraphicsPixmapItem
        node_box = ATCG.CustomGraphicsRemoveItem(tree_id, parent=None, attack_tree_parent=tree_parent)
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = ATCG.SidebarItem(bg_color=tree_style.controlnode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = ATCG.CustomGraphicsTextItem(node_name, 280, 40)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        rf_value_box = QGraphicsTextItem(rf_value)
        rf_value_box.setPos(x+220, y+70)
        rf_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        rf_level_box = QGraphicsTextItem(rf_level)
        rf_level_box.setPos(x+190, y+100)
        
        gate_text = 'AND' if gate_type == "and_gate" else 'OR'
        gate_button = QPushButton(gate_text)
        gate_button.setFixedSize(70, 25)
        gate_button.setStyleSheet(HS.attackpaths_gate_style)
        gate_button.setDisabled(True)
        
        # Embed the button in the QGraphicsScene using QGraphicsProxyWidget
        proxy_gate_button = QGraphicsProxyWidget()
        proxy_gate_button.setWidget(gate_button)
        proxy_gate_button.setPos(x + 115, y + 100)

        return {"image": node_box, 
                "sidebar": sidebar_box, 
                "id": node_id, 
                "text": node_text, 
                "line": node_line,
                "af_value_box": af_value, 
                "af_level_box": af_level, 
                "rf_value_box": rf_value_box, 
                "rf_level_box": rf_level_box, 
                "gate": proxy_gate_button,
                "gate_type": gate_type,
                "children_count": 0}

def Add_riskcontrol_IntermediateNode(tree_parent, tree_id, node_ID, x, y, node_name='Node Name', rf_value='', rf_level='', gate_type = "and_gate", af_value='', af_level=''):
        logger.info(f"Creating riskcontrol Intermediate Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Create QGraphicsPixmapItem
        node_box = QGraphicsProxyWidget()
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = ATCG.SidebarItem(bg_color=tree_style.intermediatenode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = ATCG.CustomGraphicsTextItem(node_name, 280, 40)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        rf_value_box = QGraphicsTextItem(rf_value)
        rf_value_box.setPos(x+220, y+70)
        rf_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        rf_level_box = ATCG.AFR_level(rf_level)
        rf_level_box.setPos(x+190, y+100)
        
        gate_text = 'AND' if gate_type == "and_gate" else 'OR'
        gate_button = QPushButton(gate_text)
        gate_button.setFixedSize(70, 25)
        gate_button.setStyleSheet(HS.attackpaths_gate_style)
        gate_button.setDisabled(True)
        
        # Embed the button in the QGraphicsScene using QGraphicsProxyWidget
        proxy_gate_button = QGraphicsProxyWidget()
        proxy_gate_button.setWidget(gate_button)
        proxy_gate_button.setPos(x + 115, y + 100)

        return {"image": node_box, 
                "sidebar": sidebar_box,
                "id": node_id, 
                "text": node_text, 
                "line": node_line,
                "af_value_box": af_value, 
                "af_level_box": af_level, 
                "rf_value_box": rf_value_box, 
                "rf_level_box": rf_level_box, 
                "gate": proxy_gate_button,
                "gate_type": gate_type,
                "children_count": 0}

def Add_riskcontrol_LeafNode(tree_parent, tree_id, node_ID, x, y, image_type="leaf_node", node_name='Node Name', rf_value='0', rf_level='High', input_values=['0','0','0','0','0'], af_value='', af_level=''):
        logger.info(f"Creating riskcontrol Leaf Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Create QGraphicsPixmapItem
        node_box = QGraphicsProxyWidget()
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = ATCG.SidebarItem(bg_color=tree_style.leafnode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = ATCG.CustomGraphicsTextItem(node_name, 280, 40)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        rf_value_box = QGraphicsTextItem(rf_value)
        rf_value_box.setPos(x+220, y+70)
        rf_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        rf_level_box = ATCG.AFR_level(rf_level)
        rf_level_box.setPos(x+190, y+100)

        # Positions and ranges for QComboBox widgets
        value_positions = [(x+20, y+80), (x+50, y+80), (x+80, y+80), (x+110, y+80), (x+140, y+80)]
        value_icons = [files.time_icon, files.Expertise_icon, files.Knowledge_icon, files.Access_icon, files.Equipment_icon]
        values = {}
        icon_proxies = {}
        for idx, (vx, vy) in enumerate(value_positions):
                # Create and position icons
                icon_proxy = QGraphicsProxyWidget()

                # Use QLabel with QPixmap if you convert the SVG to a pixmap
                icon_label = QLabel()
                icon_label.setStyleSheet('background-color: transparent')
                pixmap = QPixmap(value_icons[idx])
                icon_label.setPixmap(pixmap)
                icon_label.setFixedSize(20, 20)  # Adjust size based on the desired icon dimensions
                icon_label.setAlignment(Qt.AlignLeft)
                
                icon_proxy.setWidget(icon_label)
                icon_proxy.setPos(vx, vy)  # Position the icon above the combo box
                icon_proxies[idx] = icon_proxy

                value_entry = MOS.CustomComboBox(helper.attackpath_leaf_values_menu[idx])
                value_entry.set_text(input_values[idx])
                value_entry.setStyleSheet(HS.attakleaves_leaf_combobox_style)
                value_entry.setFixedWidth(30)
                value_entry.currentTextChanged.connect(lambda index, node_id=tree_id, idx=idx: tree_parent.Update_Leaf_Value(tree_id, idx))
                value_entry.setDisabled(True)
                # Create a QGraphicsProxyWidget to embed the QComboBox in the scene
                value_proxy = QGraphicsProxyWidget()
                value_proxy.setWidget(value_entry)
                value_proxy.setPos(vx, vy+20)
                value_proxy.setFocusPolicy(Qt.StrongFocus)
                
                values[idx]=value_proxy

        # Add a line after node_text
        nodevalue_line = QGraphicsLineItem(x + 175, y + 75, x + 175, y + 125)  # Line from (x+15, y+45) to (x+295, y+45)
        nodevalue_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        return {"image": node_box, 
                "sidebar": sidebar_box, 
                "id": node_id, 
                "text": node_text,
                "line": node_line,
                "valueline": nodevalue_line, 
                "af_value_box": af_value, 
                "af_level_box": af_level, 
                "rf_value_box": rf_value_box, 
                "rf_level_box": rf_level_box, 
                "gate": '',
                "gate_type": '',
                "children_count": 0,
                'values_icon': icon_proxies,
                'values': values}

def Update_Head_Node_Image(node_info):
        logger.info(f"Updating Head Node Image: {node_info['id'].toPlainText()}")
        if node_info["af_level_box_control"].toPlainText() == 'High' and node_info["rf_level_box"].toPlainText() == 'High':
                image = "head_node_high_high"
        elif node_info["af_level_box_control"].toPlainText() == 'High' and node_info["rf_level_box"].toPlainText() == 'Medium':
                image = "head_node_high_medium"
        elif node_info["af_level_box_control"].toPlainText() == 'High' and node_info["rf_level_box"].toPlainText() == 'Low':
                image = "head_node_high_low"
        elif node_info["af_level_box_control"].toPlainText() == 'High' and node_info["rf_level_box"].toPlainText() == 'Very Low':
                image = "head_node_high_verylow"
        elif node_info["af_level_box_control"].toPlainText() == 'Medium' and node_info["rf_level_box"].toPlainText() == 'High':
                image = "head_node_medium_high"
        elif node_info["af_level_box_control"].toPlainText() == 'Medium' and node_info["rf_level_box"].toPlainText() == 'Medium':
                image = "head_node_medium_medium"
        elif node_info["af_level_box_control"].toPlainText() == 'Medium' and node_info["rf_level_box"].toPlainText() == 'Low':
                image = "head_node_medium_low"
        elif node_info["af_level_box_control"].toPlainText() == 'Medium' and node_info["rf_level_box"].toPlainText() == 'Very Low':
                image = "head_node_medium_verylow"
        elif node_info["af_level_box_control"].toPlainText() == 'Low' and node_info["rf_level_box"].toPlainText() == 'High':
                image = "head_node_low_high"
        elif node_info["af_level_box_control"].toPlainText() == 'Low' and node_info["rf_level_box"].toPlainText() == 'Medium':
                image = "head_node_low_medium"
        elif node_info["af_level_box_control"].toPlainText() == 'Low' and node_info["rf_level_box"].toPlainText() == 'Low':
                image = "head_node_low_low"
        elif node_info["af_level_box_control"].toPlainText() == 'Low' and node_info["rf_level_box"].toPlainText() == 'Very Low':
                image = "head_node_low_verylow"
        elif node_info["af_level_box_control"].toPlainText() == 'Very Low' and node_info["rf_level_box"].toPlainText() == 'High':
                image = "head_node_verylow_high"
        elif node_info["af_level_box_control"].toPlainText() == 'Very Low' and node_info["rf_level_box"].toPlainText() == 'Medium':
                image = "head_node_verylow_medium"
        elif node_info["af_level_box_control"].toPlainText() == 'Very Low' and node_info["rf_level_box"].toPlainText() == 'Low':
                image = "head_node_verylow_low"
        elif node_info["af_level_box_control"].toPlainText() == 'Very Low' and node_info["rf_level_box"].toPlainText() == 'Very Low':
                image = "head_node_verylow_verylow"
        else:
               image = "head_node"
        # node_pixmap = QPixmap(P.assets[image]).scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # node_info["image"].setPixmap(node_pixmap)
        node_info["image_type"] = image  # Update image type to track

def Reposition_Nodes(Node_info, Node_Type, x, y):
        logger.info(f"Repositioning Node")
        if Node_Type == 'head':
               Node_info['image'].setPos(x , y)
               Node_info['sidebar'].setPos(x, y)
               Node_info['id'].setPos(x+15, y)
               Node_info['text'].setPos(x+15, y+25)
               Node_info['line'].setLine(x + 15, y + 70, x + 295, y + 70)
               Node_info['af_value_box_control'].setPos(x + 50, y + 70)
               Node_info['af_level_box_control'].setPos(x + 20, y + 100)
               Node_info['rf_value_box'].setPos(x+220, y+70)
               Node_info['rf_level_box'].setPos(x+190, y+100)
               Node_info['gate'].setPos(x+115, y+100)
        elif Node_Type == 'intermediate' or Node_Type == 'riskcontrol head' or Node_Type == 'riskcontrol intermediate':
               Node_info['image'].setPos(x , y)
               Node_info['sidebar'].setPos(x, y)
               Node_info['id'].setPos(x+15, y)
               Node_info['text'].setPos(x+15, y+25)
               Node_info['line'].setLine(x + 15, y + 70, x + 295, y + 70)
               Node_info['rf_value_box'].setPos(x+220, y+70)
               Node_info['rf_level_box'].setPos(x+190, y+100)
               Node_info['gate'].setPos(x+115, y+100)
        elif Node_Type == 'leaf' or Node_Type == 'riskcontrol leaf':
               value_positions = [(x+20, y+80), (x+50, y+80), (x+80, y+80), (x+110, y+80), (x+140, y+80)]
               Node_info['image'].setPos(x , y)
               Node_info['sidebar'].setPos(x, y)
               Node_info['id'].setPos(x+15, y)
               Node_info['text'].setPos(x+15, y+25)
               Node_info['line'].setLine(x + 15, y + 70, x + 295, y + 70)
               Node_info['valueline'].setLine(x + 175, y + 75, x + 175, y + 125)
               Node_info['rf_value_box'].setPos(x+220, y+70)
               Node_info['rf_level_box'].setPos(x+190, y+100)
               for idx, proxy in Node_info['values'].items():
                      proxy.setPos(value_positions[idx][0], value_positions[idx][1]+20)
               for idx, proxy in Node_info['values_icon'].items():
                      proxy.setPos(value_positions[idx][0], value_positions[idx][1])

        Node_info['x'] = x
        Node_info['y'] = y
