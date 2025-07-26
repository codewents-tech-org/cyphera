
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import controllers.DatabaseCreator as DB
from Attack_Paths.controllers.riskcontrol_tree_AFR_update import RiskControlTree_Update
from Attack_Paths.controllers.attack_tree_AFR_update import AttackTree_AFR_Update
from Attack_Paths.controllers.technical_tree_AFR_update import TechnicalTree_Update
from Attack_Paths.controllers.Refresh_AllTree_Leaf_Data import Update_AllTree_Leaf
import logging
logger = logging.getLogger(__name__)

def GetAndUpdate_Changed_leaf_list(self, leaf_id, leaf_name, leaf_af_level, leaf_values):
        logger.info(f"Updating Attack Leaf: {leaf_id}")
        try:
                available_leaf_values = DB.execute_db(f"SELECT time, expertise, knowledge, access, equipment, name FROM attack_leaf_home WHERE id='{leaf_id}'")
                if available_leaf_values:
                        values = [value for value in available_leaf_values[0][0:5]]
                        name = available_leaf_values[0][5]
                        if name != leaf_name and values != leaf_values: 
                                if leaf_id not in self.value_updated_leafs_list: self.value_updated_leafs_list.append(leaf_id)
                                if leaf_id not in self.name_updated_leafs_list: self.name_updated_leafs_list.append(leaf_id)
                                DB.update_db("UPDATE attack_leaf_home SET name = ?, time = ?,  expertise = ?,knowledge = ?,access = ?,equipment = ?,AFR_Level = ? WHERE id = ?", 
                                (leaf_name, leaf_values[0] , leaf_values[1], leaf_values[2], leaf_values[3], leaf_values[4], leaf_af_level, leaf_id))
                        elif values != leaf_values: 
                                if leaf_id not in self.value_updated_leafs_list: self.value_updated_leafs_list.append(leaf_id)
                                DB.update_db("UPDATE attack_leaf_home SET time = ?,  expertise = ?,knowledge = ?,access = ?,equipment = ?,AFR_Level = ? WHERE id = ?", 
                                (leaf_values[0] , leaf_values[1], leaf_values[2], leaf_values[3], leaf_values[4], leaf_af_level, leaf_id))
                        elif name != leaf_name: 
                                if leaf_id not in self.name_updated_leafs_list: self.name_updated_leafs_list.append(leaf_id)
                                DB.update_db("UPDATE attack_leaf_home SET name = ? WHERE id = ?", (leaf_name, leaf_id))
                else:
                        DB.update_db("INSERT INTO attack_leaf_home VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                        (leaf_id, leaf_name, leaf_values[0] , leaf_values[1], leaf_values[2], leaf_values[3], leaf_values[4], leaf_af_level, '', ''))
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error loading data: {e}") 

def Update_AllTree(value_updated_leafs_list = None, name_updated_leafs_list = None):
        Update_AllTree_Leaf(value_updated_leafs_list, name_updated_leafs_list)
        if value_updated_leafs_list:
                Update_Existing_TechnicalTree_Leaf(value_updated_leafs_list)
                Update_Existing_RiskControlTree_Leaf(value_updated_leafs_list)
                Update_Existing_AttackTree_Leaf(value_updated_leafs_list)

def Update_Existing_TechnicalTree_Leaf(value_updated_leafs_list):
        logger.info("Updating Existing Technical Tree Leaf")
        try:
                # Dynamically build the LIKE conditions and placeholders
                like_conditions = [f"Text LIKE ?" for _ in value_updated_leafs_list]
                
                query = f"""SELECT Node_ID FROM technical_tree WHERE Node_Type = 'leaf' AND ({' OR '.join(like_conditions)})"""
                # Build the LIKE patterns for each leaf_id in the list
                patterns = [f"{leaf_id} %" for leaf_id in value_updated_leafs_list]
                tech_node_lists = DB.execute_db_query(query, patterns)
                tech_lists = set()
                for (tech_node,) in tech_node_lists: tech_lists.add(tech_node.split('_')[0])
                for tech_id in tech_lists: TechnicalTree_Update(tech_id)    
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error loading data: {e}") 

def Update_Existing_RiskControlTree_Leaf(value_updated_leafs_list):
        logger.info("Updating Existing Risk Control Tree Leaf")
        try:
                # Dynamically build the LIKE conditions and placeholders
                like_conditions = [f"Text LIKE ?" for _ in value_updated_leafs_list]

                query = f"""SELECT Node_ID FROM riskcontrol_tree WHERE Node_Type IN ('leaf', 'technical leaf') AND ({' OR '.join(like_conditions)})"""
                # Build the LIKE patterns for each leaf_id in the list
                patterns = [f"{leaf_id} %" for leaf_id in value_updated_leafs_list]
                control_node_lists = DB.execute_db_query(query, patterns)
                control_lists = set()
                for (control_node,) in control_node_lists: control_lists.add(control_node.split('_')[0])
                for control_id in control_lists: RiskControlTree_Update(control_id)
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error loading data: {e}") 

def Update_Existing_AttackTree_Leaf(value_updated_leafs_list):
        logger.info("Updating Existing Attack Tree Leaf")
        try:
                # Dynamically build the LIKE conditions and placeholders
                like_conditions = [f"Text LIKE ?" for _ in value_updated_leafs_list]

                query = f"""SELECT Node_ID FROM attack_tree WHERE Node_Type IN ('leaf', 'riskcontrol leaf', 'technical leaf', 'riskcontrol technical leaf') AND ({' OR '.join(like_conditions)})"""
                # Build the LIKE patterns for each leaf_id in the list
                patterns = [f"{leaf_id} %" for leaf_id in value_updated_leafs_list]
                thread_node_lists = DB.execute_db_query(query, patterns)
                threat_lists = set()
                for (threat_node,) in thread_node_lists: threat_lists.add(threat_node.split('_')[0])
                for threat_id in threat_lists: AttackTree_AFR_Update(threat_id)      
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error loading data: {e}") 


