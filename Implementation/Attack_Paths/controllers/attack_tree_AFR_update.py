

import controllers.DatabaseCreator as DB
import models.helper as helper
from itertools import product

import logging
logger = logging.getLogger(__name__)
class AttackTree_AFR_Update():
    def __init__(self, attack_tree):
        logger.info(f"Attack Tree AFR Update: {attack_tree}")
        available_attack_tree = DB.execute_db(f"SELECT * FROM attack_tree WHERE Node_ID like '{attack_tree}_node%'")
        if available_attack_tree:
            self.threat_node_map = {}
            self.node_counter = 0
            self.riskcontrol_tree_added = False
            self.riskcontrol_tree_added_list = []
            parent_id = ''
            self.head_node_id = f"{attack_tree}_node_0"
            def update_node_data(Node_ID, Parent_ID, Node_Type, Text, AF_Value, AF_Text, RF_Value, RF_Text, Gate_Type, values, Image_Type, x, y):
                    self.threat_node_map[Node_ID]={
                            "node_id": Node_ID, 
                            "parent_id": Parent_ID, 
                            "node_type": Node_Type, 
                            "node_name": Text, 
                            "af_value": AF_Value, 
                            "af_level": AF_Text, 
                            "rf_value": RF_Value, 
                            "rf_level": RF_Text, 
                            "gate_type": Gate_Type, 
                            "values": values, 
                            "image_type": Image_Type, 
                            "children":[],
                            "x": x, 
                            "y": y
                    }
            for (Node_ID, Parent_ID, Node_Type, Text, AF_Value, AF_Text, RF_Value, RF_Text, Gate_Type, Values, Image_Type, x, y) in available_attack_tree:
                if Node_Type.startswith('riskcontrol '):
                    self.riskcontrol_tree_added = True
                    self.riskcontrol_tree_added_list.append(Node_ID)
                update_node_data(Node_ID, Parent_ID, Node_Type, Text, AF_Value, AF_Text, RF_Value, RF_Text, Gate_Type, Values, Image_Type, x, y)

            self.Calculate_AFR_Value()
            # print(self.threat_node_map[self.head_node_id])
            data_to_insert = [
                                (
                                    node_info["node_id"],
                                    node_info["parent_id"],
                                    node_info["node_type"],
                                    node_info["node_name"],
                                    node_info["af_value"],
                                    node_info["af_level"],
                                    node_info["rf_value"],
                                    node_info["rf_level"],
                                    node_info["gate_type"],
                                    node_info["values"],
                                    node_info["image_type"],
                                    node_info["x"],
                                    node_info["y"]
                                )
                                for node_info in self.threat_node_map.values()
                            ]
            sql_command = '''
                INSERT OR REPLACE INTO attack_tree 
                (Node_ID, Parent_ID, Node_Type, Text, AF_Value, AF_Text, RF_Value, RF_Text, Gate_Type, "Values", "Image_Type", "x", "y")
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            DB.executemany_db(sql_command, data_to_insert)
            
    def Calculate_AFR_Value(self):
        logger.info(f"Calculate AFR Value")
        thread_head_id = ''
        for node_id, node_info in self.threat_node_map.items():
            if node_info["parent_id"] != '':
                self.threat_node_map[node_info["parent_id"]]["children"].append(node_id)
            if node_info['node_type'] == 'head': thread_head_id = node_id
        if thread_head_id:
            self.update_root_node_value(thread_head_id)
            # self.Update_Head_Node_Image(self.threat_node_map[thread_head_id])

    def update_root_node_value(self, thread_head_id):
        logger.info(f"Update Root Node Value: {thread_head_id}")
        head_node = thread_head_id
        self.RFpaths = {}
        self.AFpaths = {}
        self.threat_node_map[head_node]["af_value"] = ''
        self.threat_node_map[head_node]["af_level"] = ''
        self.threat_node_map[head_node]["rf_value"] = ''
        self.threat_node_map[head_node]["rf_level"] = ''
        self.update_root_node_RF_value(head_node)
        if self.riskcontrol_tree_added:
            self.update_root_node_AF_value(head_node)
        logger.info(f"{head_node} Init AFR: {self.threat_node_map[head_node]['af_level']} Resid AFR: {self.threat_node_map[head_node]['rf_level']}")
        print(f"test : {head_node} Init AFR: {self.threat_node_map[head_node]['af_level']} Resid AFR: {self.threat_node_map[head_node]['rf_level']}")

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
        self.threat_node_map[head_node]["af_value"] = str(path_min_value)
        self.threat_node_map[head_node]["af_level"] = helper.Calculate_AFR_Level(path_min_value)

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
        if node_info["af_level"] == 'High' and node_info["rf_level"] == 'High':
                image = "head_node_high_high"
        elif node_info["af_level"] == 'High' and node_info["rf_level"] == 'Medium':
                image = "head_node_high_medium"
        elif node_info["af_level"] == 'High' and node_info["rf_level"] == 'Low':
                image = "head_node_high_low"
        elif node_info["af_level"] == 'High' and node_info["rf_level"] == 'Very Low':
                image = "head_node_high_verylow"
        elif node_info["af_level"] == 'Medium' and node_info["rf_level"] == 'High':
                image = "head_node_medium_high"
        elif node_info["af_level"] == 'Medium' and node_info["rf_level"] == 'Medium':
                image = "head_node_medium_medium"
        elif node_info["af_level"] == 'Medium' and node_info["rf_level"] == 'Low':
                image = "head_node_medium_low"
        elif node_info["af_level"] == 'Medium' and node_info["rf_level"] == 'Very Low':
                image = "head_node_medium_verylow"
        elif node_info["af_level"] == 'Low' and node_info["rf_level"] == 'High':
                image = "head_node_low_high"
        elif node_info["af_level"] == 'Low' and node_info["rf_level"] == 'Medium':
                image = "head_node_low_medium"
        elif node_info["af_level"] == 'Low' and node_info["rf_level"] == 'Low':
                image = "head_node_low_low"
        elif node_info["af_level"] == 'Low' and node_info["rf_level"] == 'Very Low':
                image = "head_node_low_verylow"
        elif node_info["af_level"] == 'Very Low' and node_info["rf_level"] == 'High':
                image = "head_node_verylow_high"
        elif node_info["af_level"] == 'Very Low' and node_info["rf_level"] == 'Medium':
                image = "head_node_verylow_medium"
        elif node_info["af_level"] == 'Very Low' and node_info["rf_level"] == 'Low':
                image = "head_node_verylow_low"
        elif node_info["af_level"] == 'Very Low' and node_info["rf_level"] == 'Very Low':
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
