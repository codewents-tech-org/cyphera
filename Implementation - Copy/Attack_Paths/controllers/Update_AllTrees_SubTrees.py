
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import controllers.DatabaseCreator as DB
# from Attack_Paths.Attack_Tree.controllers.Attack_RiskControlTree_Update import Attack_RiskControlTree_Update
# from Attack_Paths.Attack_Tree.controllers.Attack_TechnicanTree_Update import Attack_TechnicalTree_Update
# from Attack_Paths.RiskControl_Tree.controllers.RiskControl_TechnicanTree_Update import riskcontrol_TechnicalTree_Update
import logging
logger = logging.getLogger(__name__)


def Update_ControlTree_ExistingTechnicalTree(technical_id):
        try:
                query = f"""SELECT Node_ID FROM riskcontrol_tree WHERE Node_Type = 'technical head' AND Text LIKE '{technical_id} %'"""
                control_node_lists = DB.execute_db(query)
                control_lists = set()
                for (control_node,) in control_node_lists: control_lists.add(control_node.split('_')[0])
                for control_id in control_lists: riskcontrol_TechnicalTree_Update(control_id)  
        except sqlite3.Error as e:
                QMessageBox.critical(None, "Database Error", f"Error loading data: {e}") 

def Update_AttackTree_ExistingTechnicalTree(technical_id):
        try:
                query = f"""SELECT Node_ID FROM attack_tree WHERE Node_Type IN ('technical head', 'riskcontrol technical head') AND Text LIKE '{technical_id} %'"""
                threat_node_lists = DB.execute_db(query)
                threat_lists = set()
                for (threat_node,) in threat_node_lists: threat_lists.add(threat_node.split('_')[0])
                for threat_id in threat_lists: Attack_TechnicalTree_Update(threat_id)  
        except sqlite3.Error as e:
                QMessageBox.critical(None, "Database Error", f"Error loading data: {e}") 

def Update_AttackTree_ExistingControlTree(control_id):
        try:
                query = f"""SELECT Node_ID FROM attack_tree WHERE Node_Type = 'riskcontrol head' AND Text LIKE '{control_id} %'"""
                threat_node_lists = DB.execute_db(query)
                threat_lists = set()
                for (threat_node,) in threat_node_lists: threat_lists.add(threat_node.split('_')[0])
                for threat_id in threat_lists: Attack_RiskControlTree_Update(threat_id)  
        except sqlite3.Error as e:
                QMessageBox.critical(None, "Database Error", f"Error loading data: {e}") 
