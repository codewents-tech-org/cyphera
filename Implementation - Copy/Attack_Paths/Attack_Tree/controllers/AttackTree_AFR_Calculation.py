
import sys
from PyQt5.QtWidgets import QComboBox   
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import models.helper as helper
import models.Parameters as P
from itertools import product
import styles.tree_style as tree_style

import logging
logger = logging.getLogger(__name__)

# Change leaf node image
def Update_Node_Image(tree, node_id, included):
    logger.info(f"Updating node image: {node_id} to {included}")
    node = tree.nodes[node_id]

    # Determine the new image based on the 'included' status
    if included: 
        widget = node["image"].widget()  # This retrieves the QPushButton inside node_box
        widget.setStyleSheet(tree_style.selectedleafnode_box_style)
        # new_image_type = node["image"].update_button_bg(tree_style.node_border_color)
    else: 
        widget = node["image"].widget()  # This retrieves the QPushButton inside node_box
        widget.setStyleSheet(tree_style.leafnode_box_style)
        # new_image_type = node["image"].update_button_bg(tree_style.node_bg)

def Reset_Head_Node_Image(tree):
    logger.info(f"Resetting head node image")
    for node_id, node_info in tree.nodes.items():
        if "head" in node_info["tags"]:
            # node_pixmap = QPixmap(P.assets["head_node"]).scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # node_info["image"].setPixmap(node_pixmap)
            node_info["image_type"] = "head_node"  # Update image type to track

            node_info["af_value_box_control"].setPlainText('')
            node_info["af_level_box_control"].setPlainText('')
        break

def Head_Node_Image_Update(tree, node_id, af_level, rf_level):
        logger.info(f"Updating head node image")
        image = ''
        if af_level == 'High' and rf_level == 'High':
            image = "head_node_high_high"
        elif af_level == 'High' and rf_level == 'Medium':
            image = "head_node_high_medium"
        elif af_level == 'High' and rf_level == 'Low':
            image = "head_node_high_low"
        elif af_level == 'High' and rf_level == 'Very Low':
            image = "head_node_high_verylow"
        elif af_level == 'Medium' and rf_level == 'High':
            image = "head_node_medium_high"
        elif af_level == 'Medium' and rf_level == 'Medium':
            image = "head_node_medium_medium"
        elif af_level == 'Medium' and rf_level == 'Low':
            image = "head_node_medium_low"
        elif af_level == 'Medium' and rf_level == 'Very Low':
            image = "head_node_medium_verylow"
        elif af_level == 'Low' and rf_level == 'High':
            image = "head_node_low_high"
        elif af_level == 'Low' and rf_level == 'Medium':
            image = "head_node_low_medium"
        elif af_level == 'Low' and rf_level == 'Low':
            image = "head_node_low_low"
        elif af_level == 'Low' and rf_level == 'Very Low':
            image = "head_node_low_verylow"
        elif af_level == 'Very Low' and rf_level == 'High':
            image = "head_node_verylow_high"
        elif af_level == 'Very Low' and rf_level == 'Medium':
            image = "head_node_verylow_medium"
        elif af_level == 'Very Low' and rf_level == 'Low':
            image = "head_node_verylow_low"
        elif af_level == 'Very Low' and rf_level == 'Very Low':
            image = "head_node_verylow_verylow"
        if image:
            # node_pixmap = QPixmap(P.assets[image]).scaled(400, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # tree.nodes[node_id]["image"].setPixmap(node_pixmap)
            tree.nodes[node_id]["image_type"] = 'selected_path_node'


    # Calculate AFR value and highlight the contributed path to AFR value calculation for the Risk Control Tree

def update_root_node_value(tree):
    logger.info(f"Updating root node value")
    head_node = f"{tree.threat_id}_node_0"
    tree.RFpaths = {}
    tree.AFpaths = {}
    af_level = rf_level = ''
    if tree.riskcontrol_tree_added:
        af_level = update_root_node_AF_value(tree, head_node)
    rf_level = update_root_node_RF_value(tree, head_node)
    # Head_Node_Image_Update(tree, head_node, af_level, rf_level)
    # print(rf_level, af_level)
    logger.info(f"Root node value updated as Resid ARF: {rf_level} and Initial AFR: {af_level}")

def update_root_node_RF_value(tree, head_node):
    possible_paths = Get_Node_AF_Paths(tree, head_node)
    # print('possible_paths : ', possible_paths)
    for path in possible_paths:
        leaf_list = path.split(', ')
        leaf_value_lists = []
        Path_sum_value = 0
        leaf_max_values = []
        for leaf in leaf_list:
            leaf_value_lists.append(Get_leafNode_Values(tree, leaf))
        if leaf_value_lists: leaf_max_values = [max(values) for values in zip(*leaf_value_lists)]
        else: leaf_max_values = [0, 0, 0, 0, 0]
        # print(path, '\t', leaf_max_values)
        Path_sum_value = sum(leaf_max_values)
        tree.RFpaths[path] = {'leaf_list': leaf_list, 'value':Path_sum_value}
    # print(self.paths)
    if possible_paths:
        path_leaf_list, path_info = min(tree.RFpaths.items(), key=lambda item: item[1]['value'])
        path_min_value = path_info['value']
    else:
        path_leaf_list = ''
        path_min_value = 0
    # print('RF output data: ', path_leaf_list, '\t', path_min_value)
    tree.nodes[head_node]["rf_value_box"].setPlainText(str(path_min_value))
    tree.nodes[head_node]["rf_level_box"].setPlainText(helper.Calculate_AFR_Level(path_min_value))

    tree.selected_path = []
    for node, node_info in tree.nodes.items():
        if "leaf" in node_info["tags"]:
            if node in path_leaf_list: 
                Update_Node_Image(tree, node, True)
                tree.selected_path.append(node)
                Get_Selected_Path(tree, node)
            else: Update_Node_Image(tree, node, False)
    print(tree.selected_path)
    for node, node_info in tree.nodes.items():
        if node in tree.selected_path: node_info["image_type"] = "selected_path_node"
        else: node_info["image_type"] = "node"
    return helper.Calculate_AFR_Level(path_min_value)

def update_root_node_AF_value(tree, head_node):
    possible_paths = Get_Node_RF_Paths(tree, head_node)
    # print('possible_paths : ', possible_paths)
    for path in possible_paths:
        leaf_list = path.split(', ')
        leaf_value_lists = []
        Path_sum_value = 0
        leaf_max_values = []
        for leaf in leaf_list:
            leaf_value_lists.append(Get_leafNode_Values(tree, leaf))
        if leaf_value_lists: leaf_max_values = [max(values) for values in zip(*leaf_value_lists)]
        else: leaf_max_values = [0, 0, 0, 0, 0]
        # print(path, '\t', leaf_max_values)
        Path_sum_value = sum(leaf_max_values)
        tree.AFpaths[path] = {'leaf_list': leaf_list, 'value':Path_sum_value}
    # print(self.paths)
    if possible_paths:
        path_leaf_list, path_info = min(tree.AFpaths.items(), key=lambda item: item[1]['value'])
        path_min_value = path_info['value']
    else:
        path_leaf_list = ''
        path_min_value = 0
    # print('AF output data: ', path_leaf_list, '\t', path_min_value)
    tree.nodes[head_node]["af_value_box"] = str(path_min_value)
    tree.nodes[head_node]["af_level_box"] = helper.Calculate_AFR_Level(path_min_value)
    tree.nodes[head_node]["af_value_box_control"].setPlainText(str(path_min_value))
    tree.nodes[head_node]["af_level_box_control"].setPlainText(helper.Calculate_AFR_Level(path_min_value))
    
    return helper.Calculate_AFR_Level(path_min_value)

# list all nodes of the contributed path to AFR value calculation
def Get_Selected_Path(tree, node_id):
    node = tree.nodes[node_id]
    leaf_path_list = []
    if node["parent"]:
        if node["parent"] not in tree.selected_path: tree.selected_path.append(node["parent"])
        Get_Selected_Path(tree, node["parent"])   

# list all path Combination of the root node
def Get_Node_AF_Paths(tree, node_id):
    node = tree.nodes[node_id]
    leaf_path_list = []
    for child_id in node["children"]:
        if "leaf" in tree.nodes[child_id]["tags"]: 
            leaf_path_list.append(child_id)
        else:
            node_leaf_path = Get_Node_AF_Paths(tree, child_id)
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

# list all path Combination of the root node
def Get_Node_RF_Paths(tree, node_id):
    node = tree.nodes[node_id]
    leaf_path_list = []
    for child_id in node["children"]:
        if "leaf" in tree.nodes[child_id]["tags"] and child_id not in tree.riskcontrol_tree_added_list and tree.riskcontrol_tree_added: 
            leaf_path_list.append(child_id)
        else:
            node_leaf_path = Get_Node_RF_Paths(tree, child_id)
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
def Get_leafNode_Values(tree, node_id):
    node = tree.nodes[node_id]
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

