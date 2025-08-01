
import sys
from PyQt5.QtWidgets import QLabel, QGraphicsTextItem, QGraphicsLineItem, QGraphicsProxyWidget, QPushButton
from PyQt5.QtGui import QFont, QPixmap, QPen, QColor
from PyQt5.QtCore import Qt
import Attack_Paths.RiskControl_Tree.controllers.RiskControlTree_customgraphics as CTCG
import models.helper as helper
import components.table.multioption_selector as MOS
import models.Highlight_style as HS
import styles.tree_style as tree_style
import utils.file_utils as files

import logging
logger = logging.getLogger(__name__)

def Create_HeadNode(tree_parent, tree_id, node_ID, node_label, x, y, gate_type="and_gate", af_value='0', af_level='High'):
    logger.info(f"[Create_HeadNode] CALLED with node_ID={node_ID}, node_label={node_label}, x={x}, y={y}, gate_type={gate_type}, af_value={af_value}, af_level={af_level}")

    # Node button setup
    node_button = QPushButton()
    node_button.setFixedSize(300, 130)
    node_button.setStyleSheet(tree_style.headnode_box_style)
    logger.debug(f"[Create_HeadNode] node_button created and styled for node_ID={node_ID}")

    # Main graphics box
    node_box = CTCG.CustomGraphicsNonEditItem(tree_id, parent=None, riskcontrol_tree_parent=tree_parent)
    node_box.setWidget(node_button)
    node_box.setPos(x, y)
    logger.debug(f"[Create_HeadNode] node_box created at ({x}, {y}) for node_ID={node_ID}")

    # Sidebar
    sidebar_box = CTCG.SidebarItem(bg_color=tree_style.headnode_sidebar_color)
    sidebar_box.setPos(x, y)
    logger.debug(f"[Create_HeadNode] sidebar_box created at ({x}, {y})")

    # Node ID label
    node_id = QGraphicsTextItem(node_ID)
    node_id.setPos(x + 15, y)
    node_id.setFont(tree_style.node_id_font)
    logger.debug(f"[Create_HeadNode] node_id label set at ({x+15}, {y})")

    # Node text label
    node_text = CTCG.CustomGraphicsTextItem(node_label, 280, 40)
    node_text.setPos(x + 15, y + 25)
    logger.debug(f"[Create_HeadNode] node_text set at ({x+15}, {y+25})")

    # Horizontal line under node text
    node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)
    node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))
    logger.debug(f"[Create_HeadNode] node_line set from ({x+15}, {y+70}) to ({x+295}, {y+70})")

    # AF value box
    af_value_box = QGraphicsTextItem(af_value)
    af_value_box.setPos(x + 220, y + 70)
    af_value_box.setFont(QFont("poppins", 9, QFont.Bold))
    logger.debug(f"[Create_HeadNode] af_value_box set at ({x+220}, {y+70}) with value {af_value}")

    # AF level box
    af_level_box = CTCG.AFR_level(af_level)
    af_level_box.setPos(x + 190, y + 100)
    logger.debug(f"[Create_HeadNode] af_level_box set at ({x+190}, {y+100}) with level {af_level}")

    # Gate button
    gate_text = 'AND' if gate_type == "and_gate" else 'OR'
    gate_button = QPushButton(gate_text)
    gate_button.setFixedSize(70, 25)
    gate_button.setStyleSheet(HS.attackpaths_gate_style)
    logger.debug(f"[Create_HeadNode] gate_button created as '{gate_text}'")

    # Proxy for gate button
    proxy_gate_button = QGraphicsProxyWidget()
    proxy_gate_button.setWidget(gate_button)
    proxy_gate_button.setPos(x + 115, y + 100)
    proxy_gate_button.mouseDoubleClickEvent = lambda event: tree_parent.Switch_Gate(tree_id)
    logger.debug(f"[Create_HeadNode] proxy_gate_button set at ({x+115}, {y+100})")

    logger.info(f"[Create_HeadNode] Finished setup for node_ID={node_ID}, returning node dict")

    return {
        "image": node_box,
        "sidebar": sidebar_box,
        "id": node_id,
        "text": node_text,
        "line": node_line,
        "af_value_box": af_value_box,
        "af_level_box": af_level_box,
        "gate": proxy_gate_button,
        "gate_type": gate_type,
        "children_count": 0
    }

def Create_IntermediateNode(tree_parent, tree_id, node_ID, x, y, node_name='Node Name', af_value='', af_level='', gate_type="and_gate"):
    logger.info(f"[Create_IntermediateNode] CALLED with node_ID={node_ID}, node_name={node_name}, x={x}, y={y}, gate_type={gate_type}, af_value={af_value}, af_level={af_level}")

    node_button = QPushButton()
    node_button.setFixedSize(300, 130)
    node_button.setStyleSheet(tree_style.headnode_box_style)
    logger.debug(f"[Create_IntermediateNode] node_button created and styled for node_ID={node_ID}")

    node_box = CTCG.CustomGraphicsEditItem(tree_id, parent=None, riskcontrol_tree_parent=tree_parent)
    node_box.setWidget(node_button)
    node_box.setPos(x, y)
    logger.debug(f"[Create_IntermediateNode] node_box created at ({x}, {y}) for node_ID={node_ID}")

    sidebar_box = CTCG.SidebarItem(bg_color=tree_style.intermediatenode_sidebar_color)
    sidebar_box.setPos(x, y)
    logger.debug(f"[Create_IntermediateNode] sidebar_box created at ({x}, {y})")

    node_id = QGraphicsTextItem(node_ID)
    node_id.setPos(x + 15, y)
    node_id.setFont(tree_style.node_id_font)
    logger.debug(f"[Create_IntermediateNode] node_id label set at ({x+15}, {y})")

    node_text = CTCG.EditableTextItem(node_name, fixed_width=280, node_id=tree_id, riskcontrol_tree_parent=tree_parent)
    node_text.setPos(x + 15, y + 25)
    logger.debug(f"[Create_IntermediateNode] node_text (editable) set at ({x+15}, {y+25})")

    node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)
    node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))
    logger.debug(f"[Create_IntermediateNode] node_line set from ({x+15}, {y+70}) to ({x+295}, {y+70})")

    af_value_box = QGraphicsTextItem(af_value)
    af_value_box.setPos(x + 220, y + 70)
    af_value_box.setFont(QFont("poppins", 9, QFont.Bold))
    logger.debug(f"[Create_IntermediateNode] af_value_box set at ({x+220}, {y+70}) with value {af_value}")

    af_level_box = CTCG.AFR_level(af_level)
    af_level_box.setPos(x + 190, y + 100)
    logger.debug(f"[Create_IntermediateNode] af_level_box set at ({x+190}, {y+100}) with level {af_level}")

    gate_text = 'AND' if gate_type == "and_gate" else 'OR'
    gate_button = QPushButton(gate_text)
    gate_button.setFixedSize(70, 25)
    gate_button.setStyleSheet(HS.attackpaths_gate_style)
    logger.debug(f"[Create_IntermediateNode] gate_button created as '{gate_text}'")

    proxy_gate_button = QGraphicsProxyWidget()
    proxy_gate_button.setWidget(gate_button)
    proxy_gate_button.setPos(x + 115, y + 100)
    proxy_gate_button.mouseDoubleClickEvent = lambda event: tree_parent.Switch_Gate(tree_id)
    logger.debug(f"[Create_IntermediateNode] proxy_gate_button set at ({x+115}, {y+100})")

    logger.info(f"[Create_IntermediateNode] Finished setup for node_ID={node_ID}, returning node dict")

    return {
        "image": node_box,
        "sidebar": sidebar_box,
        "id": node_id,
        "text": node_text,
        "line": node_line,
        "af_value_box": af_value_box,
        "af_level_box": af_level_box,
        "gate": proxy_gate_button,
        "gate_type": gate_type,
        "children_count": 0
    }

def Create_LeafNode(tree_parent, tree_id, node_ID, x, y, image_type="leaf_node", node_name='Node Name', af_value='0', af_level='High', input_values=['0','0','0','0','0']):
    logger.info(f"[Create_LeafNode] CALLED with node_ID={node_ID}, node_name={node_name}, x={x}, y={y}, af_value={af_value}, af_level={af_level}, input_values={input_values}")

    node_button = QPushButton()
    node_button.setFixedSize(300, 130)
    node_button.setStyleSheet(tree_style.headnode_box_style)
    logger.debug(f"[Create_LeafNode] node_button created and styled for node_ID={node_ID}")

    node_box = CTCG.CustomGraphicsRemoveItem(tree_id, parent=None, riskcontrol_tree_parent=tree_parent)
    node_box.setWidget(node_button)
    node_box.setPos(x, y)
    logger.debug(f"[Create_LeafNode] node_box created at ({x}, {y}) for node_ID={node_ID}")

    sidebar_box = CTCG.SidebarItem(bg_color=tree_style.leafnode_sidebar_color)
    sidebar_box.setPos(x, y)
    logger.debug(f"[Create_LeafNode] sidebar_box created at ({x}, {y})")

    node_id = QGraphicsTextItem(node_ID)
    node_id.setPos(x + 15, y)
    node_id.setFont(tree_style.node_id_font)
    logger.debug(f"[Create_LeafNode] node_id label set at ({x+15}, {y})")

    node_text = CTCG.EditableTextItem(node_name, fixed_width=280, node_id=tree_id, riskcontrol_tree_parent=tree_parent)
    node_text.setPos(x + 15, y + 25)
    logger.debug(f"[Create_LeafNode] node_text (editable) set at ({x+15}, {y+25})")

    node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)
    node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))
    logger.debug(f"[Create_LeafNode] node_line set from ({x+15}, {y+70}) to ({x+295}, {y+70})")

    af_value_box = QGraphicsTextItem(af_value)
    af_value_box.setPos(x + 220, y + 70)
    af_value_box.setFont(QFont("poppins", 9, QFont.Bold))
    logger.debug(f"[Create_LeafNode] af_value_box set at ({x+220}, {y+70}) with value {af_value}")

    af_level_box = CTCG.AFR_level(af_level)
    af_level_box.setPos(x + 190, y + 100)
    logger.debug(f"[Create_LeafNode] af_level_box set at ({x+190}, {y+100}) with level {af_level}")

    value_positions = [(x+20, y+80), (x+50, y+80), (x+80, y+80), (x+110, y+80), (x+140, y+80)]
    value_icons = [files.time_icon, files.Expertise_icon, files.Knowledge_icon, files.Access_icon, files.Equipment_icon]
    values = {}
    icon_proxies = {}

    for idx, (vx, vy) in enumerate(value_positions): 
        logger.debug(f"[Create_LeafNode] Setting up value icon and combobox for idx={idx} at pos=({vx},{vy}) icon={value_icons[idx]} value={input_values[idx]}")
        icon_proxy = QGraphicsProxyWidget()
        icon_label = QLabel()
        icon_label.setStyleSheet('background-color: transparent')
        pixmap = QPixmap(value_icons[idx])
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignLeft)
        icon_proxy.setWidget(icon_label)
        icon_proxy.setPos(vx, vy)
        icon_proxies[idx] = icon_proxy

        value_entry = MOS.CustomComboBox(helper.attackpath_leaf_values_menu[idx])
        value_entry.set_text(input_values[idx])
        value_entry.setStyleSheet(HS.attakleaves_leaf_combobox_style)
        value_entry.setFixedWidth(30)
        value_entry.currentTextChanged.connect(
            lambda index, node_id=tree_id, idx=idx: tree_parent.Update_Leaf_Value(node_id, idx)
        )

        value_proxy = QGraphicsProxyWidget()
        value_proxy.setWidget(value_entry)
        value_proxy.setPos(vx, vy+20)
        values[idx] = value_proxy

    logger.debug(f"[Create_LeafNode] All value icons and combo boxes set for node_ID={node_ID}")

    nodevalue_line = QGraphicsLineItem(x + 175, y + 75, x + 175, y + 125)
    nodevalue_line.setPen(QPen(QColor(tree_style.node_border_color), 1))
    logger.debug(f"[Create_LeafNode] nodevalue_line set from ({x+175}, {y+75}) to ({x+175}, {y+125})")

    logger.info(f"[Create_LeafNode] Finished setup for node_ID={node_ID}, returning node dict")

    return {
        "image": node_box,
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
        'values': values
    }

def Add_Technical_HeadNode(tree_parent, tree_id, node_ID, x, y, node_name='Node Name', af_value='', af_level='', gate_type = "and_gate"):
    logger.info(f"[Add_Technical_HeadNode] CALLED with node_ID={node_ID}, node_name={node_name}, x={x}, y={y}, af_value={af_value}, af_level={af_level}, gate_type={gate_type}")

    node_button = QPushButton()
    node_button.setFixedSize(300, 130)
    node_button.setStyleSheet(tree_style.headnode_box_style)
    logger.debug(f"[Add_Technical_HeadNode] node_button created and styled for node_ID={node_ID}")

    node_box = CTCG.CustomGraphicsRemoveItem(tree_id, parent=None, riskcontrol_tree_parent=tree_parent)
    node_box.setWidget(node_button)
    node_box.setPos(x, y)
    logger.debug(f"[Add_Technical_HeadNode] node_box created at ({x}, {y}) for node_ID={node_ID}")

    sidebar_box = CTCG.SidebarItem(bg_color=tree_style.technicalnode_sidebar_color)
    sidebar_box.setPos(x, y)
    logger.debug(f"[Add_Technical_HeadNode] sidebar_box created at ({x}, {y})")

    node_id = QGraphicsTextItem(node_ID)
    node_id.setPos(x+15, y)
    node_id.setFont(tree_style.node_id_font)
    logger.debug(f"[Add_Technical_HeadNode] node_id label set at ({x+15}, {y})")

    node_text = CTCG.CustomGraphicsTextItem(node_name, 280, 40)
    node_text.setPos(x+15, y+25)
    logger.debug(f"[Add_Technical_HeadNode] node_text set at ({x+15}, {y+25})")

    node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)
    node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))
    logger.debug(f"[Add_Technical_HeadNode] node_line set from ({x+15}, {y+70}) to ({x+295}, {y+70})")

    af_value_box = QGraphicsTextItem(af_value)
    af_value_box.setPos(x+220, y+70)
    af_value_box.setFont(QFont("poppins", 9, QFont.Bold))
    logger.debug(f"[Add_Technical_HeadNode] af_value_box set at ({x+220}, {y+70}) with value {af_value}")

    af_level_box = CTCG.AFR_level(af_level)
    af_level_box.setPos(x+190, y+100)
    logger.debug(f"[Add_Technical_HeadNode] af_level_box set at ({x+190}, {y+100}) with level {af_level}")

    gate_text = 'AND' if gate_type == "and_gate" else 'OR'
    gate_button = QPushButton(gate_text)
    gate_button.setFixedSize(70, 25)
    gate_button.setStyleSheet(HS.attackpaths_gate_style)
    gate_button.setDisabled(True)
    logger.debug(f"[Add_Technical_HeadNode] gate_button created with text '{gate_text}' and set as disabled")

    proxy_gate_button = QGraphicsProxyWidget()
    proxy_gate_button.setWidget(gate_button)
    proxy_gate_button.setPos(x + 115, y + 100)
    logger.debug(f"[Add_Technical_HeadNode] proxy_gate_button set at ({x+115}, {y+100})")

    logger.info(f"[Add_Technical_HeadNode] Finished setup for node_ID={node_ID}, returning node dict")

    return {
        "image": node_box, 
        "sidebar": sidebar_box, 
        "id": node_id, 
        "text": node_text, 
        "line": node_line,
        "af_value_box": af_value_box, 
        "af_level_box": af_level_box, 
        "gate": proxy_gate_button,
        "gate_type": gate_type,
        "children_count": 0
    }

def Add_Technical_IntermediateNode(tree_parent, tree_id, node_ID, x, y, node_name='Node Name', af_value='', af_level='', gate_type = "and_gate"):
        logger.info(f"Adding Technical Intermediate Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Create QGraphicsPixmapItem
        node_box = QGraphicsProxyWidget()
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = CTCG.SidebarItem(bg_color=tree_style.intermediatenode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = CTCG.CustomGraphicsTextItem(node_name, 280, 40)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        af_value_box = QGraphicsTextItem(af_value)
        af_value_box.setPos(x+220, y+70)
        af_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        af_level_box = CTCG.AFR_level(af_level)
        af_level_box.setPos(x+190, y+100)
        
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
                "af_value_box": af_value_box, 
                "af_level_box": af_level_box, 
                "gate": proxy_gate_button,
                "gate_type": gate_type,
                "children_count": 0}

def Add_Technical_LeafNode(tree_parent, tree_id, node_ID, x, y, image_type="leaf_node", node_name='Node Name', af_value='0', af_level='High', input_values=['0','0','0','0','0']):
        logger.info(f"Adding Technical Leaf Node: {node_ID}")
        node_button = QPushButton()
        node_button.setFixedSize(300, 130)
        node_button.setStyleSheet(tree_style.headnode_box_style)
        
        # Create QGraphicsPixmapItem
        node_box = QGraphicsProxyWidget()
        node_box.setWidget(node_button)
        node_box.setPos(x, y)

        # Sidebar
        sidebar_box = CTCG.SidebarItem(bg_color=tree_style.leafnode_sidebar_color)
        sidebar_box.setPos(x, y)
        
        # Create QGraphicsTextItem for the node label
        node_id = QGraphicsTextItem(node_ID)
        node_id.setPos(x+15, y)
        node_id.setFont(tree_style.node_id_font)
        
        # Create QGraphicsTextItem for the node label
        node_text = CTCG.CustomGraphicsTextItem(node_name, 280, 40)
        node_text.setPos(x+15, y+25)

        # Add a line after node_text
        node_line = QGraphicsLineItem(x + 15, y + 70, x + 295, y + 70)  # Line from (x+15, y+45) to (x+295, y+45)
        node_line.setPen(QPen(QColor(tree_style.node_border_color), 1))  # Set line color and thickness

        # Create QGraphicsTextItem for af value box
        af_value_box = QGraphicsTextItem(af_value)
        af_value_box.setPos(x+220, y+70)
        af_value_box.setFont(QFont("poppins", 9, QFont.Bold))

        # Create QGraphicsTextItem for AF level box
        af_level_box = CTCG.AFR_level(af_level)
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
                "af_value_box": af_value_box, 
                "af_level_box": af_level_box, 
                "gate": '',
                "gate_type": '',
                "children_count": 0,
                'values_icon': icon_proxies,
                'values': values}

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
