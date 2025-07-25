

import controllers.DatabaseCreator as DB
import models.helper as helper
from itertools import product
import logging
logger = logging.getLogger(__name__)

from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalAttackTree
from controllers.schema_manager import (
    get_instances, get_first_instance, create_instance, update_instance, delete_all_instance, bulk_insert_instances
)



class AttackTechnicalTreeUpdater:
    def __init__(self, attack_tree_id):
        self.attack_tree_id = attack_tree_id
        self.threat_node_map = {}
        self.node_counter = 0
        self.riskcontrol_tree_added_list = []
        self.technical_tree_added_list = []
        self.head_node_id = f"{attack_tree_id}_node_0"

        # Step 1: Load attack tree nodes
        all_nodes = get_instances(AttackTree, filters={"Node_ID": f"{attack_tree_id}_node%"})
        if not all_nodes:
            print(f"[WARN] No attack tree nodes found for {attack_tree_id}")
            return

        self.node_counter = self._compute_next_node_id(all_nodes)

        for node in all_nodes:
            if node.Node_Type.startswith("riskcontrol head"):
                self._handle_riskcontrol_branch(node)
            elif node.Node_Type == "technical head":
                self._handle_technical_branch(node)
            elif node.Node_Type in ['technical leaf', 'technical intermediate', 'riskcontrol leaf',
                                    'riskcontrol intermediate', 'riskcontrol technical head',
                                    'riskcontrol technical leaf', 'riskcontrol technical intermediate']:
                continue
            else:
                self._update_node_data(node)

        self.Calculate_AFR_Value()

        # Step 2: Delete old attack tree
        delete_all_instance(AttackTree, filters={"node_id": f"{attack_tree_id}_node%"})

        # Step 3: Insert updated tree
        self._save_attack_tree()

    def _compute_next_node_id(self, nodes):
        existing_ids = [n.Node_ID for n in nodes]
        existing_max = 0
        for nid in existing_ids:
            try:
                suffix = int(nid.removeprefix(f"{self.attack_tree_id}_node_"))
                existing_max = max(existing_max, suffix)
            except Exception:
                continue
        return existing_max + 1

    def _update_node_data(self, node):
        self.threat_node_map[node.Node_ID] = {
            "node_id": node.Node_ID,
            "parent_id": node.Parent_ID,
            "node_type": node.Node_Type,
            "node_name": node.Text,
            "afr_value": node.AF_Value,
            "afr_level": node.AF_Text,
            "rf_value": node.RF_Value,
            "rf_level": node.RF_Text,
            "gate_type": node.Gate_Type,
            "values": node.Values,
            "image_type": node.Image_Type,
            "children": [],
            "x": node.x,
            "y": node.y
        }

    def _handle_riskcontrol_branch(self, node):
        riskcontrol_prefix = node.Text.strip().split(" ")[0]
        rc_nodes = get_instances(RiskControlTree, filters={"node_id": f"{riskcontrol_prefix}_node%"})
        node_map = {n.Node_ID: {
            "parent_id": n.Parent_ID,
            "node_type": n.Node_Type,
            "text": n.Text,
            "value": n.AF_Value,
            "af_text": n.AF_Text,
            "gate_type": n.Gate_Type,
            "image_type": n.Image_Type,
            "values": n.Values,
            "children": []
        } for n in rc_nodes}
        for n in rc_nodes:
            if n.Parent_ID:
                node_map[n.Parent_ID]["children"].append(n.Node_ID)
        head_node = next((n.Node_ID for n in rc_nodes if not n.Parent_ID), None)
        if head_node:
            self.Update_Attack_RiskControlTree_Nodes(node.Node_ID, node.Parent_ID, head_node, node_map, self.attack_tree_id)

    def _handle_technical_branch(self, node):
        tech_prefix = node.Text.strip().split(" ")[0]
        tech_nodes = get_instances(TechnicalAttackTree, filters={"node_id": f"{tech_prefix}_node%"})
        node_map = {n.Node_ID: {
            "parent_id": n.Parent_ID,
            "node_type": n.Node_Type,
            "text": n.Text,
            "value": n.AF_Value,
            "af_text": n.AF_Text,
            "gate_type": n.Gate_Type,
            "image_type": n.Image_Type,
            "values": n.Values,
            "children": []
        } for n in tech_nodes}
        for n in tech_nodes:
            if n.Parent_ID:
                node_map[n.Parent_ID]["children"].append(n.Node_ID)
        head_node = next((n.Node_ID for n in tech_nodes if not n.Parent_ID), None)
        if head_node:
            self.Update_Attack_TechnicalTree_Nodes(node.Node_ID, node.Parent_ID, head_node, node_map, self.attack_tree_id)

    def _save_attack_tree(self):
        insert_objects = []
        for node_info in self.threat_node_map.values():
            insert_objects.append(AttackTree(
                Node_ID=node_info["node_id"],
                Parent_ID=node_info["parent_id"],
                Node_Type=node_info["node_type"],
                Text=node_info["node_name"],
                AF_Value=node_info["afr_value"],
                AF_Text=node_info["afr_level"],
                RF_Value=node_info["rf_value"],
                RF_Text=node_info["rf_level"],
                Gate_Type=node_info["gate_type"],
                Values=node_info["values"],
                Image_Type=node_info["image_type"],
                x=node_info["x"],
                y=node_info["y"]
            ))

        bulk_insert_instances(insert_objects)
    def Update_Attack_RiskControlTree_Nodes(self, child_new_id, parent_id, riskcontrol_node_id, node_map, tree):
        logger.info(f"Update_Attack_RiskControlTree_Nodes: {riskcontrol_node_id}")
        node_info = node_map[riskcontrol_node_id]
        new_node_id = self.Add_riskcontrol_Child_Node(child_new_id, parent_id, node_info, tree)
        self.riskcontrol_tree_added_list.append(new_node_id)
        # Recursively add child nodes
        for child_id in node_map[riskcontrol_node_id]["children"]:
                child_new_id = f"{tree}_node_{self.node_counter}"
                self.node_counter += 1
                self.Update_Attack_RiskControlTree_Nodes(child_new_id, new_node_id, child_id, node_map, tree)

    # Create a child node for the attack tree
    def Add_riskcontrol_Child_Node(self, child_id, parent_id, node_info, tree):
        logger.info(f"Add_riskcontrol_Child_Node: {node_info['text']}")
        parent = self.threat_node_map[parent_id]
        node_type = f"riskcontrol {node_info['node_type']}"
        self.threat_node_map[child_id] = {
                "node_id": child_id, 
                "parent_id": parent_id, 
                "node_type": node_type, 
                "node_name": node_info['text'], 
                "afr_value": '', 
                "afr_level": '', 
                "rf_value": node_info['value'], 
                "rf_level": node_info['af_text'], 
                "gate_type": node_info['gate_type'], 
                "values": node_info['values'], 
                "image_type": node_info['image_type'], 
                "children":[],
                "x": 0, 
                "y": 0
        }
        return child_id

    def Update_Attack_TechnicalTree_Nodes(self, child_new_id, parent_id, technical_node_id, node_map, tree):
        logger.info(f"Update_Attack_TechnicalTree_Nodes: {technical_node_id}")
        node_info = node_map[technical_node_id]
        new_node_id = self.Add_Technical_Child_Node(child_new_id, parent_id, node_info, tree)
        self.technical_tree_added_list.append(new_node_id)
        # Recursively add child nodes
        for child_id in node_map[technical_node_id]["children"]:
                child_new_id = f"{tree}_node_{self.node_counter}"
                self.node_counter += 1
                self.Update_Attack_TechnicalTree_Nodes(child_new_id, new_node_id, child_id, node_map, tree)

    # Create a child node for the attack tree
    def Add_Technical_Child_Node(self, child_id, parent_id, node_info, tree):
        logger.info(f"Add_Technical_Child_Node: {node_info['text']}")
        parent = self.threat_node_map[parent_id]
        node_type = f"technical {node_info['node_type']}"
        self.threat_node_map[child_id] = {
                "node_id": child_id, 
                "parent_id": parent_id, 
                "node_type": node_type, 
                "node_name": node_info['text'], 
                "afr_value": '', 
                "afr_level": '', 
                "rf_value": node_info['value'], 
                "rf_level": node_info['af_text'], 
                "gate_type": node_info['gate_type'], 
                "values": node_info['values'], 
                "image_type": node_info['image_type'], 
                "children":[],
                "x": 0, 
                "y": 0
        }
        return child_id

    def Calculate_AFR_Value(self):
        logger.info(f"Calculate_AFR_Value")
        thread_head_id = ''
        for node_id, node_info in self.threat_node_map.items():
            if node_info["parent_id"] != '':
                self.threat_node_map[node_info["parent_id"]]["children"].append(node_id)
            if node_info['node_type'] == 'head': thread_head_id = node_id
        if thread_head_id:
            self.update_root_node_value(thread_head_id)
            # self.Update_Head_Node_Image(self.threat_node_map[thread_head_id])

    def update_root_node_value(self, thread_head_id):
        logger.info(f"update_root_node_value: {thread_head_id}")
        head_node = thread_head_id
        self.RFpaths = {}
        self.AFpaths = {}
        self.threat_node_map[head_node]["afr_value"] = ''
        self.threat_node_map[head_node]["afr_level"] = ''
        self.threat_node_map[head_node]["rf_value"] = ''
        self.threat_node_map[head_node]["rf_level"] = ''
        self.update_root_node_RF_value(head_node)
        if self.riskcontrol_tree_added:
            self.update_root_node_AF_value(head_node)
        logger.info(f"{head_node} Init AFR: {self.threat_node_map[head_node]['afr_level']} Resid AFR: {self.threat_node_map[head_node]['rf_level']}")
        print(f"test : {head_node} Init AFR: {self.threat_node_map[head_node]['afr_level']} Resid AFR: {self.threat_node_map[head_node]['rf_level']}")

    def update_root_node_RF_value(self, head_node):
        possible_paths = self.Get_Node_AF_Paths(head_node)
        # print(f'{head_node} Initial possible_paths : ', possible_paths)
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
            self.RFpaths[path] = {'leaf_list': leaf_list, 'value':Path_sum_value}
        # print(self.paths)
        if possible_paths:
            path_leaf_list, path_info = min(self.RFpaths.items(), key=lambda item: item[1]['value'])
            path_min_value = path_info['value']
        else:
            path_leaf_list = ''
            path_min_value = 0
        print('RF output data: ', path_leaf_list, '\t', path_min_value)
        self.threat_node_map[head_node]["afr_value"] = str(path_min_value)
        self.threat_node_map[head_node]["afr_level"] = helper.Calculate_AFR_Level(path_min_value)

        self.selected_path = []
        for node, node_info in self.threat_node_map.items():
            if node_info["node_type"] in ["leaf", "technical leaf", "riskcontrol leaf", "riskcontrol technical leaf"]:
                if node in path_leaf_list: 
                    self.Update_Node_Image(node, True)
                    self.selected_path.append(node)
                    self.Get_Selected_Path(node)
                else: self.Update_Node_Image(node, False)
        # print(self.selected_path)
        for node, node_info in self.threat_node_map.items():
            if node in self.selected_path: node_info["image_type"] = "selected_path_node"
            else: node_info["image_type"] = "node"

    def update_root_node_AF_value(self, head_node):
        possible_paths = self.Get_Node_RF_Paths(head_node)
        # print(f'{head_node} Residial possible_paths : ', possible_paths)
        for path in possible_paths:
            leaf_list = path.split(', ')
            leaf_value_lists = []
            Path_sum_value = 0
            leaf_max_values = []
            for leaf in leaf_list:
                temp_value = self.Get_leafNode_Values(leaf)
                if temp_value: leaf_value_lists.append(temp_value)
            if leaf_value_lists: leaf_max_values = [max(values) for values in zip(*leaf_value_lists)]
            else: leaf_max_values = [0, 0, 0, 0, 0]
            # print(path, '\t', leaf_max_values)
            Path_sum_value = sum(leaf_max_values)
            self.AFpaths[path] = {'leaf_list': leaf_list, 'value':Path_sum_value}
        # print(self.paths)
        if possible_paths:
            path_leaf_list, path_info = min(self.AFpaths.items(), key=lambda item: item[1]['value'])
            path_min_value = path_info['value']
        else:
            path_leaf_list = ''
            path_min_value = 0
        # print('AF output data: ', path_leaf_list, '\t', path_min_value)
        self.threat_node_map[head_node]["rf_value"] = str(path_min_value)
        self.threat_node_map[head_node]["rf_level"] = helper.Calculate_AFR_Level(path_min_value)

        self.selected_path = []
        for node, node_info in self.threat_node_map.items():
            if node_info["node_type"] in ["leaf", "technical leaf", "riskcontrol leaf", "riskcontrol technical leaf"]:
                if node in path_leaf_list: 
                    self.Update_Node_Image(node, True)
                    self.selected_path.append(node)
                    self.Get_Selected_Path(node)
                else: self.Update_Node_Image(node, False)
        # print(self.selected_path)
        for node, node_info in self.threat_node_map.items():
            if node in self.selected_path: node_info["image_type"] = "selected_path_node"
            else: node_info["image_type"] = "node"

    # list all nodes of the contributed path to AFR value calculation
    def Get_Selected_Path(self, node_id):
        node = self.threat_node_map[node_id]
        leaf_path_list = []
        if node["parent_id"]:
            if node["parent_id"] not in self.selected_path: self.selected_path.append(node["parent_id"])
            self.Get_Selected_Path(node["parent_id"])   

    # list all path Combination of the root node
    def Get_Node_AF_Paths(self, node_id):
        node = self.threat_node_map[node_id]
        leaf_path_list = []
        for child_id in node["children"]:
            if self.threat_node_map[child_id]["node_type"] in ["leaf", "technical leaf"]: 
                leaf_path_list.append(child_id)
            else:
                node_leaf_path = self.Get_Node_AF_Paths(child_id)
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
    def Get_Node_RF_Paths(self, node_id):
        node = self.threat_node_map[node_id]
        leaf_path_list = []
        for child_id in node["children"]:
            if self.threat_node_map[child_id]["node_type"] in ["leaf", "technical leaf", "riskcontrol leaf", "riskcontrol technical leaf"]: 
                leaf_path_list.append(child_id)
            else:
                node_leaf_path = self.Get_Node_RF_Paths(child_id)
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
        node = self.threat_node_map[node_id]
        # If the node is a leaf node
        if node["node_type"] in ["leaf", "technical leaf", "riskcontrol leaf", "riskcontrol technical leaf"]:
            values = []
            values_str = node["values"]
            values_str_list = values_str.strip().removeprefix('[').removesuffix(']').replace("'", '').split(', ')
            values = [int(value) for value in values_str_list]
            return values

    def Update_Head_Node_Image(self, node_info):
        if node_info["afr_level"] == 'High' and node_info["rf_level"] == 'High':
                image = "head_node_high_high"
        elif node_info["afr_level"] == 'High' and node_info["rf_level"] == 'Medium':
                image = "head_node_high_medium"
        elif node_info["afr_level"] == 'High' and node_info["rf_level"] == 'Low':
                image = "head_node_high_low"
        elif node_info["afr_level"] == 'High' and node_info["rf_level"] == 'Very Low':
                image = "head_node_high_verylow"
        elif node_info["afr_level"] == 'Medium' and node_info["rf_level"] == 'High':
                image = "head_node_medium_high"
        elif node_info["afr_level"] == 'Medium' and node_info["rf_level"] == 'Medium':
                image = "head_node_medium_medium"
        elif node_info["afr_level"] == 'Medium' and node_info["rf_level"] == 'Low':
                image = "head_node_medium_low"
        elif node_info["afr_level"] == 'Medium' and node_info["rf_level"] == 'Very Low':
                image = "head_node_medium_verylow"
        elif node_info["afr_level"] == 'Low' and node_info["rf_level"] == 'High':
                image = "head_node_low_high"
        elif node_info["afr_level"] == 'Low' and node_info["rf_level"] == 'Medium':
                image = "head_node_low_medium"
        elif node_info["afr_level"] == 'Low' and node_info["rf_level"] == 'Low':
                image = "head_node_low_low"
        elif node_info["afr_level"] == 'Low' and node_info["rf_level"] == 'Very Low':
                image = "head_node_low_verylow"
        elif node_info["afr_level"] == 'Very Low' and node_info["rf_level"] == 'High':
                image = "head_node_verylow_high"
        elif node_info["afr_level"] == 'Very Low' and node_info["rf_level"] == 'Medium':
                image = "head_node_verylow_medium"
        elif node_info["afr_level"] == 'Very Low' and node_info["rf_level"] == 'Low':
                image = "head_node_verylow_low"
        elif node_info["afr_level"] == 'Very Low' and node_info["rf_level"] == 'Very Low':
                image = "head_node_verylow_verylow"
        else:
               image = "head_node"

        node_info['image_type'] = image

    # Change leaf node image
    def Update_Node_Image(self, node_id, included):
        node = self.threat_node_map[node_id]

        # Determine the new image based on the 'included' status
        if included: node["image_type"] = "selected_path_node"
        else: node["image_type"] = "node"
