# get_node_list.py

import logging
logger = logging.getLogger(__name__)
import sqlite3
from controllers.schema_manager import get_instances
from controllers.tablemodel import AttackLeafNodes, RiskControlTreeHome, TechnicalTreeHome

def get_existing_leaf_nodes():
    logger.info(f"get_existing_leaf_nodes")
    try:
        leaf_rows = get_instances(AttackLeafNodes, {'is_deleted': False})
        if not leaf_rows:    return {}
        return {row.id:row.name for row in leaf_rows}
    except sqlite3.Error as e:
        return {}

def get_existing_riskcontrol_tree():
    logger.info(f"get_existing_riskcontrol_tree")
    try:
        print(f"get_existing_riskcontrol_tree : ", get_instances(RiskControlTreeHome))
        riskcontrol_rows = get_instances(RiskControlTreeHome, {'is_deleted': False})
        print(f"Risk Control Trees: {riskcontrol_rows}")
        if not riskcontrol_rows:    return {}
        return {row.id:row.name for row in riskcontrol_rows}
    except sqlite3.Error as e:
        return {}

def get_existing_technical_tree():
    logger.info(f"get_existing_technical_tree")
    try:
        technical_rows = get_instances(TechnicalTreeHome, {'is_deleted': False})
        print(f"Technical Trees: {technical_rows}")
        if not technical_rows:    return {}
        return {row.id:row.name for row in technical_rows}
    except sqlite3.Error as e:
        return {}
