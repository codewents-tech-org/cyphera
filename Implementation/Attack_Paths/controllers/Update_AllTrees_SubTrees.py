
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import controllers.DatabaseCreator as DB
from Attack_Paths.Attack_Tree.controllers.Attack_RiskControlTree_Update import AttackRiskControlTreeUpdater
from Attack_Paths.Attack_Tree.controllers.Attack_TechnicanTree_Update import AttackTechnicalTreeUpdater
from Attack_Paths.RiskControl_Tree.controllers.RiskControl_TechnicanTree_Update import riskcontrol_TechnicalTree_Update
import logging
from controllers.schema_manager import get_instances
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree

logger = logging.getLogger(__name__)


def Update_ControlTree_ExistingTechnicalTree(technical_id):
    try:
        # Find all riskcontrol_tree nodes that are 'technical head' and Text starts with '{technical_id} '
        # We'll filter in Python after fetching all technical heads, unless schema_manager supports ilike/startswith
        technical_heads = get_instances(
            RiskControlTree, 
            filters={"Node_Type": 'technical head'}
        )
        control_lists = set()
        for node in technical_heads:
            if node.Text.startswith(f"{technical_id} "):
                control_lists.add(node.Node_ID.split('_')[0])
        for control_id in control_lists:
            riskcontrol_TechnicalTree_Update(control_id)
    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")


def Update_AttackTree_ExistingTechnicalTree(technical_id):
    try:
        # Fetch all attack_tree nodes where Node_Type is 'technical head' or 'riskcontrol technical head'
        # and Text starts with '{technical_id} '
        attack_heads = get_instances(
            AttackTree,
            filters=None  # We'll filter manually on Node_Type and Text
        )
        threat_lists = set()
        for node in attack_heads:
            if node.Node_Type in ('technical head', 'riskcontrol technical head') and node.Text.startswith(f"{technical_id} "):
                threat_lists.add(node.Node_ID.split('_')[0])
        for threat_id in threat_lists:
            AttackTechnicalTreeUpdater(threat_id)
    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
 

def Update_AttackTree_ExistingControlTree(control_id):
    try:
        # Fetch all attack_tree nodes where Node_Type is 'riskcontrol head' and Text starts with '{control_id} '
        attack_heads = get_instances(
            AttackTree,
            filters={"Node_Type": 'riskcontrol head'}
        )
        threat_lists = set()
        for node in attack_heads:
            if node.Text.startswith(f"{control_id} "):
                threat_lists.add(node.Node_ID.split('_')[0])
        for threat_id in threat_lists:
            AttackRiskControlTreeUpdater(threat_id)
    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

