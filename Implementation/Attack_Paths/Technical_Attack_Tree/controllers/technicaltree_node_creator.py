
import sys
from PyQt5.QtWidgets import QLabel, QGraphicsTextItem, QGraphicsLineItem, QGraphicsProxyWidget, QMessageBox, QPushButton
from PyQt5.QtGui import QFont, QPixmap, QPen, QColor
from PyQt5.QtCore import Qt
import Attack_Paths.Technical_Attack_Tree.controllers.technicaltree_customgraphics as TATCG
import controllers.DatabaseCreator as DB
import models.helper as helper
import components.table.multioption_selector as MOS
import models.Highlight_style as HS
import sqlite3
import controllers.AttackTree_Update_Data as AUD
import styles.tree_style as tree_style
import utils.file_utils as files
from Attack_Paths.controllers.riskcontrol_tree_AFR_update import RiskControlTree_Update
from Attack_Paths.controllers.attack_tree_AFR_update import AttackTree_AFR_Update
from Attack_Paths.controllers.technical_tree_AFR_update import TechnicalTree_Update
from controllers.schema_manager import get_instances, get_first_instance, create_instance, update_instance
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome, AttackLeafNodes, TechnicalAttackTree
import logging
logger = logging.getLogger(__name__)

def Create_HeadNode(tree_parent, tree_id, node_ID, node_label, x, y, gate_type = "and_gate", af_value='0', af_level='High'):
        logger.info(f"Creating Head Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Embed the button in the QGraphicsScene using QGraphicsProxyWidget
        node_box = TATCG.CustomGraphicsNonEditItem(tree_id, parent=None, technical_tree_parent=tree_parent)
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = TATCG.SidebarItem(bg_color=tree_style.headnode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = TATCG.CustomGraphicsTextItem(node_label, 280, 40)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        # af_value_box = TATCG.AFR_value(af_value)
        af_value_box = QGraphicsTextItem(af_value)
        af_value_box.setPos(x+220, y+70)
        af_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        af_level_box = TATCG.AFR_level(af_level)
        af_level_box.setPos(x+190, y+100)
        
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
                "af_value_box": af_value_box, 
                "af_level_box": af_level_box, 
                "gate": proxy_gate_button,
                "gate_type": gate_type,
                "children_count": 0}

def Create_IntermediateNode(tree_parent, tree_id, node_ID, x, y, node_name='Node Name', af_value='', af_level='', gate_type = "and_gate"):
        logger.info(f"Creating Intermediate Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Embed the button in the QGraphicsScene using QGraphicsProxyWidget
        node_box = TATCG.CustomGraphicsEditItem(tree_id, parent=None, technical_tree_parent=tree_parent)
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = TATCG.SidebarItem(bg_color=tree_style.intermediatenode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = TATCG.EditableTextItem(node_name, fixed_width=280, node_id=tree_id, technical_tree_parent=tree_parent)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        af_value_box = QGraphicsTextItem(af_value)
        af_value_box.setPos(x+220, y+70)
        af_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        af_level_box = TATCG.AFR_level(af_level)
        af_level_box.setPos(x+190, y+100)
        
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
                "af_value_box": af_value_box, 
                "af_level_box": af_level_box, 
                "gate": proxy_gate_button,
                "gate_type": gate_type,
                "children_count": 0}

def Create_LeafNode(tree_parent, tree_id, node_ID, x, y, image_type="leaf_node", node_name='Node Name', af_value='0', af_level='High', input_values=['0','0','0','0','0']):
        logger.info(f"Creating Leaf Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Embed the button in the QGraphicsScene using QGraphicsProxyWidget
        node_box = TATCG.CustomGraphicsRemoveItem(tree_id, parent=None, technical_tree_parent=tree_parent)
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = TATCG.SidebarItem(bg_color=tree_style.leafnode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = TATCG.EditableTextItem(node_name, fixed_width=280, node_id=tree_id, technical_tree_parent=tree_parent)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        af_value_box = QGraphicsTextItem(af_value)
        af_value_box.setPos(x+220, y+70)
        af_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        af_level_box = TATCG.AFR_level(af_level)
        af_level_box.setPos(x+190, y+100)

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

                # Create and position combo boxes
                value_entry = MOS.CustomComboBox(helper.attackpath_leaf_values_menu[idx])
                value_entry.set_text(input_values[idx])  # Set initial value
                value_entry.setStyleSheet(HS.attakleaves_leaf_combobox_style)
                value_entry.setFixedWidth(30)
                value_entry.currentTextChanged.connect(
                        lambda index, node_id=tree_id, idx=idx: tree_parent.Update_Leaf_Value(node_id, idx)
                )

                value_proxy = QGraphicsProxyWidget()
                value_proxy.setWidget(value_entry)
                value_proxy.setPos(vx, vy+20)  # Position the combo box
                values[idx] = value_proxy  
                 
        # Update_AttackLeave(node_ID, node_name, af_level, input_values)

        # Add a line after node_text
        nodevalue_line = QGraphicsLineItem(x + 175, y + 75, x + 175, y + 125)  # Line from (x+15, y+45) to (x+295, y+45)
        nodevalue_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        return {"image": node_box, 
                "sidebar": sidebar_box, 
                "id": node_id, 
                "text": node_text, 
                "line": node_line,
                "valueline": nodevalue_line,
                "af_value_box": af_value_box, 
                "af_level_box": af_level_box, 
                "gate": '',
                "gate_type": '',
                "children_count": 0,
                'values_icon': icon_proxies,
                'values': values}


def Update_AttackLeaf(leaf_id, leaf_name, leaf_af_level, leaf_values):
    logger.info(f"Updating Attack Leaf: {leaf_id}")
    try:
        # 1. Check if leaf exists
        leaf = get_first_instance(AttackLeafNodes, {"id": leaf_id})
        update_fields = {
            "name": leaf_name,
            "time": leaf_values[0],
            "expertise": leaf_values[1],
            "knowledge": leaf_values[2],
            "access": leaf_values[3],
            "equipment": leaf_values[4],
            "AFR_Level": leaf_af_level
        }

        if leaf:
            update_instance(AttackLeafNodes, {"id": leaf_id}, update_fields)
        else:
            new_leaf = AttackLeafNodes(
                id=leaf_id,
                name=leaf_name,
                time=leaf_values[0],
                expertise=leaf_values[1],
                knowledge=leaf_values[2],
                access=leaf_values[3],
                equipment=leaf_values[4],
                AFR_Level=leaf_af_level,
                # fill other default columns if needed, like '', ''
            )
            create_instance(new_leaf)

        Update_Existing_TechnicalTree_Leaf()
        Update_Existing_RiskControlTree_Leaf()
        Update_Existing_AttackTree_Leaf()

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")


def Update_Existing_TechnicalTree_Leaf():
    logger.info("Updating Existing Technical Tree Leaf")
    try:
        # Find all leaf nodes
        leaves = get_instances(TechnicalAttackTree, {"node_type": "leaf"})
        for leaf in leaves:
            leaf_id = leaf.text.strip().split(' ')[0]
            available_leaf = get_first_instance(AttackLeafNodes, {"id": leaf_id})
            if not available_leaf:
                continue

            leaf_name = available_leaf.name
            values = [
                available_leaf.time,
                available_leaf.expertise,
                available_leaf.knowledge,
                available_leaf.access,
                available_leaf.equipment,
            ]
            leaf_values = [int(v) for v in values]
            leaf_af_value = sum(leaf_values)
            leaf_af_level = available_leaf.AFR_Level
            leaf_text = f"{leaf_id} {leaf_name}"

            # Update TechnicalTree entry
            update_instance(
                TechnicalTreeHome,
                {"node_id": leaf.node_id},
                {
                    "text": leaf_text,
                    "value": leaf_af_value,
                    "af_text": leaf_af_level,
                    "values": str(values)
                }
            )

        # Update heads
        heads = get_instances(TechnicalAttackTree, {"node_type": "head"})
        for head in heads:
            TechnicalTree_Update(head.text.strip().split(' ')[0])

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")


def Update_Existing_RiskControlTree_Leaf():
    logger.info("Updating Existing Risk Control Tree Leaf")
    try:
        leaves = get_instances(RiskControlTree, None)
        for leaf in leaves:
            if not leaf.node_type.endswith("leaf"):
                continue
            leaf_id = leaf.text.strip().split(' ')[0]
            available_leaf = get_first_instance(AttackLeafNodes, {"id": leaf_id})
            if not available_leaf:
                continue

            leaf_name = available_leaf.name
            values = [
                available_leaf.time,
                available_leaf.expertise,
                available_leaf.knowledge,
                available_leaf.access,
                available_leaf.equipment,
            ]
            leaf_values = [int(v) for v in values]
            leaf_af_value = sum(leaf_values)
            leaf_af_level = available_leaf.AFR_Level
            leaf_text = f"{leaf_id} {leaf_name}"

            update_instance(
                RiskControlTree,
                {"node_id": leaf.node_id},
                {
                    "text": leaf_text,
                    "value": leaf_af_value,
                    "af_text": leaf_af_level,
                    "values": str(values)
                }
            )

        heads = get_instances(RiskControlTree, {"node_type": "head"})
        for head in heads:
            RiskControlTree_Update(head.text.strip().split(' ')[0])

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")


def Update_Existing_AttackTree_Leaf():
    logger.info("Updating Existing Attack Tree Leaf")
    try:
        leaves = get_instances(AttackTree, None)
        for leaf in leaves:
            if not leaf.node_type.endswith("leaf"):
                continue
            leaf_id = leaf.text.strip().split(' ')[0]
            available_leaf = get_first_instance(AttackLeafNodes, {"id": leaf_id})
            if not available_leaf:
                continue

            leaf_name = available_leaf.name
            values = [
                available_leaf.time,
                available_leaf.expertise,
                available_leaf.knowledge,
                available_leaf.access,
                available_leaf.equipment,
            ]
            leaf_values = [int(v) for v in values]
            leaf_af_value = sum(leaf_values)
            leaf_af_level = available_leaf.AFR_Level
            leaf_text = f"{leaf_id} {leaf_name}"

            update_instance(
                AttackTree,
                {"node_id": leaf.node_id},
                {
                    "text": leaf_text,
                    "rf_value": leaf_af_value,
                    "rf_text": leaf_af_level,
                    "values": str(values)
                }
            )

        heads = get_instances(AttackTree, {"node_type": "head"})
        for head in heads:
            AttackTree_AFR_Update(head.text.strip().split(' ')[0])

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")


def Reposition_Nodes(Node_info, Node_Type, x, y):
        logger.info(f"Repositioning Nodes")
        if Node_Type == 'head':
               Node_info['image'].setPos(x , y)
               Node_info['sidebar'].setPos(x, y)
               Node_info['id'].setPos(x+15, y)
               Node_info['text'].setPos(x+15, y+25)
               Node_info['line'].setLine(x + 15, y + 70, x + 295, y + 70)
               Node_info['af_value_box'].setPos(x+220, y+70)
               Node_info['af_level_box'].setPos(x+190, y+100)
               Node_info['gate'].setPos(x+115, y+100)
        elif Node_Type == 'intermediate':
               Node_info['image'].setPos(x , y)
               Node_info['sidebar'].setPos(x, y)
               Node_info['id'].setPos(x+15, y)
               Node_info['text'].setPos(x+15, y+25)
               Node_info['line'].setLine(x + 15, y + 70, x + 295, y + 70)
               Node_info['af_value_box'].setPos(x+220, y+70)
               Node_info['af_level_box'].setPos(x+190, y+100)
               Node_info['gate'].setPos(x+115, y+100)
        elif Node_Type == 'leaf':
               value_positions = [(x+20, y+80), (x+50, y+80), (x+80, y+80), (x+110, y+80), (x+140, y+80)]
               Node_info['image'].setPos(x , y)
               Node_info['sidebar'].setPos(x, y)
               Node_info['id'].setPos(x+15, y)
               Node_info['text'].setPos(x+15, y+25)
               Node_info['line'].setLine(x + 15, y + 70, x + 295, y + 70)
               Node_info['valueline'].setLine(x + 175, y + 75, x + 175, y + 125)
               Node_info['af_value_box'].setPos(x+220, y+70)
               Node_info['af_level_box'].setPos(x+190, y+100)
               for idx, proxy in Node_info['values'].items():
                      proxy.setPos(value_positions[idx][0], value_positions[idx][1]+20)
               for idx, proxy in Node_info['values_icon'].items():
                      proxy.setPos(value_positions[idx][0], value_positions[idx][1])

        Node_info['x'] = x
        Node_info['y'] = y


