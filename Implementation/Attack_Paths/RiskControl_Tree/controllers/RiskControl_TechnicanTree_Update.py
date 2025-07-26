

import controllers.DatabaseCreator as DB
import models.helper as helper
from itertools import product
import logging

logger = logging.getLogger(__name__)

from controllers.schema_manager import get_instances, delete_all_instance, bulk_upsert_instances
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome, AttackLeafNodes


class riskcontrol_TechnicalTree_Update:
    def __init__(self, tree):
        logger.info(f'[INIT] riskcontrol_TechnicalTree_Update for tree: {tree}')
        available_tree = get_instances(RiskControlTree, None)
        logger.debug(f'[INIT] Raw available_tree: {available_tree}')
        logger.info(f'[INIT] Total available_tree nodes: {len(available_tree)}')
        available_tree = [
            node for node in available_tree if node.node_id.startswith(f"{tree}_node")
        ]
        logger.debug(f'[INIT] Filtered available_tree: {available_tree}')
        logger.info(f'[INIT] Filtered available_tree nodes for tree {tree}: {len(available_tree)}')
        if available_tree:
            self.control_node_map = {}
            self.node_counter = 0
            self.technical_tree_added = False
            self.technical_tree_added_list = []
            self.technical_head_added_list = []
            parent_id = ''
            self.head_node_id = f"{tree}_node_0"

            def update_node_data(Node_ID, Parent_ID, Node_Type, Text, RF_Value, RF_Text, Gate_Type, values, Image_Type, x, y):
                logger.debug(f'[update_node_data] Adding node {Node_ID}, Parent {Parent_ID}, Type {Node_Type}, Gate {Gate_Type}')
                self.control_node_map[Node_ID] = {
                    "node_id": Node_ID,
                    "parent_id": Parent_ID,
                    "node_type": Node_Type,
                    "node_name": Text,
                    "rf_value": RF_Value,
                    "rf_level": RF_Text,
                    "gate_type": Gate_Type,
                    "values": values,
                    "image_type": Image_Type,
                    "children": [],
                    "x": x,
                    "y": y
                }
                logger.debug(f'[update_node_data] Node data: {self.control_node_map[Node_ID]}')

            existing_ids_row = [node.node_id for node in available_tree]
            logger.info(f'[INIT] Existing IDs for tree: {existing_ids_row}')
            existing_max_id = 0
            if existing_ids_row:
                existing_max_id = max([int(data.removeprefix(f'{tree}_node_')) for data in existing_ids_row])
            self.node_counter = existing_max_id + 1
            logger.info(f'[INIT] node_counter starts at: {self.node_counter}')

            for node in available_tree:
                Node_ID = node.node_id
                Parent_ID = node.parent_id
                Node_Type = node.node_type
                Text = node.text
                RF_Value = node.value
                RF_Text = node.af_text
                Gate_Type = node.gate_type
                Values = node.values
                Image_Type = node.image_type
                x = node.x
                y = node.y
                node_id = f"{tree}_node_{self.node_counter}"
                logger.debug(f'[INIT] Scanning node {Node_ID} (type={Node_Type}) with parent {Parent_ID}')
                if Node_Type == 'technical head':
                    logger.info(f'[INIT] Adding technical tree for {tree} node {Node_ID}')
                    self.technical_tree_added = True
                    self.technical_tree_added_list.append(Node_ID)
                    self.technical_head_added_list.append(Node_ID)
                    technical = Text.strip().split(' ')[0]
                    logger.debug(f'[INIT] technical extracted as "{technical}" from text "{Text}"')
                    available_technical = get_instances(TechnicalTreeHome, None)
                    logger.info(f'[INIT] Got {len(available_technical)} technical trees for "{technical}"')
                    available_technical = [
                        t for t in available_technical if t.node_id.startswith(f"{technical}_node")
                    ]
                    logger.debug(f'[INIT] Filtered available_technical: {available_technical}')
                    node_map = {}
                    technical_head_node = ''
                    for tech_node in available_technical:
                        tech_id = tech_node.node_id
                        technical_parent_id = tech_node.parent_id
                        node_type = tech_node.node_type
                        text = tech_node.text
                        value = tech_node.value
                        af_text = tech_node.af_text
                        gate_type = tech_node.gate_type
                        image_type = tech_node.image_type
                        values = tech_node.values
                        c_x = tech_node.x
                        c_y = tech_node.y
                        node_map[tech_id] = {
                            "parent_id": technical_parent_id,
                            "node_type": node_type,
                            "text": text,
                            "value": value,
                            "af_text": af_text,
                            "gate_type": gate_type,
                            "image_type": image_type,
                            "children": [],
                            'values': values
                        }
                        if technical_parent_id:
                            node_map[technical_parent_id]["children"].append(tech_id)
                        else:
                            technical_head_node = tech_id
                        logger.debug(f'[INIT] technical node_map[{tech_id}]: {node_map[tech_id]}')
                    logger.info(f'[INIT] technical_head_node: {technical_head_node}')
                    if available_technical and technical_head_node:
                        self.Update_riskcontrol_TechnicalTree_Nodes(Node_ID, Parent_ID, technical_head_node, node_map, tree)
                elif Node_Type == 'technical leaf' or Node_Type == 'technical intermediate':
                    logger.info(f'[INIT] Node {Node_ID} of type {Node_Type} - skipped for now')
                else:
                    logger.info(f'[INIT] Non-technical node {Node_ID} being added')
                    update_node_data(Node_ID, Parent_ID, Node_Type, Text, RF_Value, RF_Text, Gate_Type, Values, Image_Type, x, y)

            logger.info('[INIT] Calling Calculate_AFR_Value()')
            self.Calculate_AFR_Value()
            for node_id, node_info in self.control_node_map.items():
                if node_id in self.technical_tree_added_list:
                    if node_id in self.technical_head_added_list:
                        logger.info(f'[POST] Setting node_type technical head for {node_id}')
                        node_info["node_type"] = f"technical head"
                    else:
                        logger.info(f'[POST] Setting node_type technical {node_info["node_type"]} for {node_id}')
                        nt = node_info["node_type"]
                        node_info["node_type"] = f"technical {nt}"

            # ORM: Delete all existing nodes for this tree
            logger.info(f'[DELETE] Deleting all RiskControlTree nodes for tree {tree}')
            delete_all_instance(RiskControlTree, {"node_id": f"{tree}_node%"})

            # Prepare ORM objects for bulk upsert
            node_objs = []
            for node_info in self.control_node_map.values():
                logger.info(f'[UPSERT] Upserting node {node_info["node_id"]}')
                obj = RiskControlTree(
                    node_id=node_info["node_id"],
                    parent_id=node_info["parent_id"],
                    node_type=node_info["node_type"],
                    text=node_info["node_name"],
                    value=node_info["rf_value"],
                    af_text=node_info["rf_level"],
                    gate_type=node_info["gate_type"],
                    values=node_info["values"],
                    image_type=node_info["image_type"],
                    x=node_info["x"],
                    y=node_info["y"]
                )
                node_objs.append(obj)
            logger.info(f'[UPSERT] Total upsert nodes: {len(node_objs)}')
            bulk_upsert_instances(RiskControlTree, [o.__dict__ for o in node_objs], key_field='node_id')

    def Update_riskcontrol_TechnicalTree_Nodes(self, child_new_id, parent_id, technical_node_id, node_map, tree):
        logger.info(f'[Update_riskcontrol_TechnicalTree_Nodes] Adding technical tree node {technical_node_id} for {tree}')
        logger.debug(f'[Update_riskcontrol_TechnicalTree_Nodes] Args: child_new_id={child_new_id}, parent_id={parent_id}, node_map={node_map}')
        node_info = node_map[technical_node_id]
        new_node_id = self.Add_Technical_Child_Node(child_new_id, parent_id, node_info, tree)
        self.technical_tree_added_list.append(new_node_id)
        logger.debug(f'[Update_riskcontrol_TechnicalTree_Nodes] Node {new_node_id} added, recursing children: {node_map[technical_node_id]["children"]}')
        for child_id in node_map[technical_node_id]["children"]:
            child_new_id = f"{tree}_node_{self.node_counter}"
            self.node_counter += 1
            logger.debug(f'[Update_riskcontrol_TechnicalTree_Nodes] Recursing child: {child_id} as {child_new_id}')
            self.Update_riskcontrol_TechnicalTree_Nodes(child_new_id, new_node_id, child_id, node_map, tree)

    def Add_Technical_Child_Node(self, child_id, parent_id, node_info, tree):
        logger.info(f'[Add_Technical_Child_Node] Adding child node {child_id} for {tree}')
        logger.debug(f'[Add_Technical_Child_Node] Args: parent_id={parent_id}, node_info={node_info}')
        parent = self.control_node_map.get(parent_id)
        self.control_node_map[child_id] = {
            "node_id": child_id,
            "parent_id": parent_id,
            "node_type": node_info['node_type'],
            "node_name": node_info['text'],
            "rf_value": node_info['value'],
            "rf_level": node_info['af_text'],
            "gate_type": node_info['gate_type'],
            "values": node_info['values'],
            "image_type": node_info['image_type'],
            "children": [],
            "x": 0,
            "y": 0
        }
        logger.debug(f'[Add_Technical_Child_Node] Node added: {self.control_node_map[child_id]}')
        return child_id

    def Calculate_AFR_Value(self):
        logger.info('[Calculate_AFR_Value] Calculating AFR value...')
        for node_id, node_info in self.control_node_map.items():
            logger.debug(f'[Calculate_AFR_Value] Checking node_id {node_id} parent {node_info["parent_id"]}')
            if node_info["parent_id"]:
                logger.debug(f'[Calculate_AFR_Value] Linking child {node_id} to parent {node_info["parent_id"]}')
                self.control_node_map[node_info["parent_id"]]["children"].append(node_id)
        logger.info(f'[Calculate_AFR_Value] Updating root node value for {self.head_node_id}')
        self.update_root_node_value(self.head_node_id)

    def update_root_node_value(self, thread_head_id):
        logger.info(f'[update_root_node_value] Calculating AFR value for root node {thread_head_id}')
        head_node = thread_head_id
        self.paths = {}
        self.update_root_node_RF_value(head_node)

    def update_root_node_RF_value(self, head_node):
        logger.info(f'[update_root_node_RF_value] For head node {head_node}')
        possible_paths = self.Get_Node_AF_Paths(head_node)
        logger.debug(f'[update_root_node_RF_value] possible_paths: {possible_paths}')
        for path in possible_paths:
            leaf_list = path.split(', ')
            logger.debug(f'[update_root_node_RF_value] Path: {path}, leaves: {leaf_list}')
            leaf_value_lists = []
            for leaf in leaf_list:
                values = self.Get_leafNode_Values(leaf)
                logger.debug(f'[update_root_node_RF_value] Leaf {leaf} values: {values}')
                leaf_value_lists.append(values)
            if leaf_value_lists:
                leaf_max_values = [max(values) for values in zip(*leaf_value_lists)]
            else:
                leaf_max_values = [0, 0, 0, 0, 0]
            Path_sum_value = sum(leaf_max_values)
            logger.debug(f'[update_root_node_RF_value] path {path} sum value: {Path_sum_value}')
            self.paths[path] = {'leaf_list': leaf_list, 'value': Path_sum_value}
        if possible_paths:
            path_leaf_list, path_info = min(self.paths.items(), key=lambda item: item[1]['value'])
            path_min_value = path_info['value']
        else:
            path_leaf_list = ''
            path_min_value = 0
        logger.info(f'[update_root_node_RF_value] Selected min value: {path_min_value}, path: {path_leaf_list}')
        self.control_node_map[head_node]["rf_value"] = str(path_min_value)
        self.control_node_map[head_node]["rf_level"] = helper.Calculate_AFR_Level(path_min_value)

        self.selected_path = []
        for node, node_info in self.control_node_map.items():
            if "leaf" == node_info["node_type"]:
                if node in path_leaf_list:
                    logger.debug(f'[update_root_node_RF_value] Leaf {node} in selected path')
                    self.Update_Node_Image(node, True)
                    self.selected_path.append(node)
                    self.Get_Selected_Path(node)
                else:
                    self.Update_Node_Image(node, False)
                    node_info["image_type"] = "node"
        for node, node_info in self.control_node_map.items():
            if node in self.selected_path:
                node_info["image_type"] = "selected_path_node"
            else:
                node_info["image_type"] = "node"

    def Get_Selected_Path(self, node_id):
        logger.debug(f'[Get_Selected_Path] Trace up for node {node_id}')
        node = self.control_node_map[node_id]
        if node["parent_id"]:
            if node["parent_id"] not in self.selected_path:
                logger.debug(f'[Get_Selected_Path] Adding parent {node["parent_id"]} to selected path')
                self.selected_path.append(node["parent_id"])
            self.Get_Selected_Path(node["parent_id"])

    def Get_Node_AF_Paths(self, node_id):
        logger.debug(f'[Get_Node_AF_Paths] for node {node_id}')
        node = self.control_node_map[node_id]
        leaf_path_list = []
        for child_id in node["children"]:
            if "leaf" == self.control_node_map[child_id]["node_type"]:
                leaf_path_list.append(child_id)
            else:
                node_leaf_path = self.Get_Node_AF_Paths(child_id)
                if node_leaf_path:
                    leaf_path_list.append(node_leaf_path)
        logger.debug(f'[Get_Node_AF_Paths] leaf_path_list: {leaf_path_list}')
        if node['gate_type'] == 'and_gate':
            output_list_data = []
            if leaf_path_list:
                output_list = []
                all_list_or_str = ''
                if all(isinstance(element, list) for element in leaf_path_list):
                    all_list_or_str = 'lists'
                elif all(isinstance(element, str) for element in leaf_path_list):
                    all_list_or_str = 'string'
                else:
                    leaf_path_list = [
                        element if isinstance(element, list) else [element]
                        for element in leaf_path_list
                    ]
                    all_list_or_str = 'lists'
                if all_list_or_str == 'lists':
                    for combo in product(*leaf_path_list):
                        output_list.append(list(combo))
                    for combo in output_list:
                        new_leaf_ids = str([element for element in combo]).removeprefix('[').removesuffix(']').replace("'", "").replace('"', "")
                        output_list_data.append(new_leaf_ids)
                elif all_list_or_str == 'string':
                    new_leaf_ids = str([element for element in leaf_path_list]).removeprefix('[').removesuffix(']').replace("'", "").replace('"', "")
                    output_list_data.append(new_leaf_ids)
            logger.debug(f'[Get_Node_AF_Paths] and_gate output: {output_list_data}')
            return output_list_data
        elif node['gate_type'] == 'or_gate':
            output_list = []
            for lists in leaf_path_list:
                if type(lists) == list:
                    for leaf_list in lists:
                        output_list.append(leaf_list)
                else:
                    output_list.append(lists)
            logger.debug(f'[Get_Node_AF_Paths] or_gate output: {output_list}')
            return output_list
        else:
            logger.debug(f'[Get_Node_AF_Paths] default leaf_path_list: {leaf_path_list}')
            return leaf_path_list

    def Get_leafNode_Values(self, node_id):
        node = self.control_node_map[node_id]
        if "leaf" == node["node_type"]:
            values = []
            values_str = node["values"]
            logger.debug(f'[Get_leafNode_Values] Raw values for {node_id}: {values_str}')
            values_str_list = values_str.strip().removeprefix('[').removesuffix(']').replace("'", '').split(', ')
            values = [int(value) for value in values_str_list]
            logger.debug(f'[Get_leafNode_Values] Parsed values for {node_id}: {values}')
            return values

    def Update_Node_Image(self, node_id, included):
        logger.debug(f'[Update_Node_Image] node {node_id}, included={included}')
        node = self.control_node_map[node_id]
        if included:
            node["image_type"] = "selected_path_node"
        else:
            node["image_type"] = "node"
