
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
import sqlite3
import models.Parameters as P
import controllers.DatabaseCreator as DB

db_cursor = ''
Panel_selector = ''
homePanel_selector = ''
modulePanel_Selector = ''
submodulePanel_Selector = ''
analysisaction_selector = ''
damage_scenario_menu = []

asset_security_properties_menu = ["Confidentiality", "Integrity", "Availability", "Authenticity", "Correctness", "Freshness", "Authorization", "Non-repudiation"]
DS_impact_menu = ['Severe', 'Major', 'Moderate', 'Negligible']
DS_impactcatagory_menu = ['Operational', 'Financial', 'Safety', 'Privacy']
RA_Responsible_menu = ['Ettiksoft', 'Customer', 'Supplier']
risktreatement = ["Avoid", "Reduce", "Retain", "Share"]

#===============================================================================================================
# TOE Module
#===============================================================================================================
assumptions_header = ['ID', 'Assumptions', 'Comments']
misusecases_header = ['ID', 'Name', 'Comments']
toe_configuration_header = ['ID', 'Name', 'Description', 'Comments']

#===============================================================================================================
# Analysis Module
#===============================================================================================================
# Assets column heading lists with icons
asset_header = ['ID', 'Name', 'Security Properties', 'Description', 'Comments']
# Damage Scenarios column heading lists with icons
DS_header = ['ID', 'Name', 'Impact', 'Impact Category', 'Reasoning', 'Comments']
# Threats column heading lists with icons
threat_header = ['ID', 'Name', 'Damage Scenarios', 'TOE Configuration', 'Misuse cases', 
                 'Initial AFR', 'Resid AFR', 'Asset', 'Security Properties', 
                 'Reasoning', 'Comments']
# Threat Scenarios column heading lists with icons
TS_header = ['ID', 'Threat', 'Damage Scenarios', 'TOE Configuration', 'Reasoning', 'Comments']

#===============================================================================================================
# Security Measurement Module
#===============================================================================================================
# Security control column heading lists with icons
securitycontrols_header = ['ID', 'Name', 'Security Goal', 'Description', 'Comments']

#===============================================================================================================
# Attack Paths Module
#===============================================================================================================
# Attack Tree column heading lists with icons
attacktree_header = ['ID', 'Name', 'Initial AFR', 'Resid AFR', 'TOE Configuration', 'Comments']

scope_header = ['ID', 'Name', 'Comments']

# Risk Control Tree column heading lists with icons
RiskControlTree_header = ['ID', 'Name', 'Mitigates', 'Assumptions', 'Comments']

# Attack Leaves column heading lists with icons
attackleaves_header = ['ID', 'Name', P.time_icon, P.Expertise_icon, P.Knowledge_icon, P.Access_icon, P.Equipment_icon, 
                       'AFR', 'Description', 'Comments']

# Techniacl Tree column heading lists with icons
technicaltree_header = ['ID', 'Name', 'Used in Threats', 'Used in Security Controls', 'TOE Configuration', 'Assumptions', 'Comments']

#===============================================================================================================
# Risk Assessment Module
#===============================================================================================================
# Security Claims column heading lists with icons
securityclaims_header = ['ID', 'Name', 'Assumptions', 'Responsible', 'TOE Configuration', 'Description', 'Comments']
# Security Goals column heading lists with icons
securitygoals_header = ['ID', 'Name', 'Responsible', 'TOE Configuration', 'Description', 'Comments']
# Risk Treatement column heading lists with icons
risktreatement_header = ['ID', 'Damage', 'Impact', 'Threat', 'Initial AFR', 'Initial Risk', 
                         'Resid AFR ', 'Resid Risk', 'TOE Configuration', 'Risk Treatment', 
                         'Security Claims', 'Security Goals', 'Mitigated By']

#===============================================================================================================
# Summary Module
#===============================================================================================================
# Traceability Graph column heading lists with icons
TraceabilityGraph_header = ["Damage Scenarios", "", "Threats", "", "Risks", "", "Security Goals and Claims", "", "Security Controls"]



attackpath_leaf_values_menu = [ 
                            ["0 (<= One day)", "1 (<= one week)", "4 (<= one month)", "17 (<= six months)", "19 (> six months)"],
                            ["0 (Layman)", "3 (Proficient)", "6 (Expert)", "8 (Multiple expert)"],
                            ["0 (Public)", "3 (Restricted)", "7 (Confidential)", "11 (Strictly Confidential)"],
                            ["0 (Unlimited)", "1 (Easy)", "4 (Moderate)", "10 (Difficult/none)"],
                            ["0 (Standard)", "4 (Specialized)", "7 (Bespoke)", "9 (Multiple Bespoke)"]
                            ]

AFR_Levels = ["High", "Medium", "Low", "Very Low"]
risk_map = {
        ("Severe", "Very Low"): 2,
        ("Severe", "Low"): 3,
        ("Severe", "Medium"): 4,
        ("Severe", "High"): 5,
        ("Major", "Very Low"): 1,
        ("Major", "Low"): 2,
        ("Major", "Medium"): 3,
        ("Major", "High"): 4,
        ("Moderate", "Very Low"): 1,
        ("Moderate", "Low"): 2,
        ("Moderate", "Medium"): 2,
        ("Moderate", "High"): 3,
        ("Negligible", "Very Low"): 1,
        ("Negligible", "Low"): 1,
        ("Negligible", "Medium"): 1,
        ("Negligible", "High"): 1
    }

Risk_Color_Indication = { 'high':'#88AB8E', 'medium':'#99AB8E', 'low':'#AAAB8E', 'very low':'#BBAB8E'}

def adjust_table_column(table_name, layout):
    if table_name == 'Asset':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 240)
        layout.setColumnWidth(3, 300)
        layout.setColumnWidth(4, 350)
        layout.setColumnWidth(5, 250)
    elif table_name == 'Damage Scenarios':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 240)
        layout.setColumnWidth(3, 150)
        layout.setColumnWidth(4, 200)
        layout.setColumnWidth(5, 300)
        layout.setColumnWidth(6, 250)
    elif table_name == 'Threats':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 300)
        layout.setColumnWidth(3, 210)
        layout.setColumnWidth(4, 200)
        layout.setColumnWidth(5, 180)
        layout.setColumnWidth(6, 140)
        layout.setColumnWidth(7, 140)
        layout.setColumnWidth(8, 120)
        layout.setColumnWidth(9, 190)
        layout.setColumnWidth(10,250)
        layout.setColumnWidth(11,250)
    elif table_name == 'Threat Scenarios':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 300)
        layout.setColumnWidth(3, 210)
        layout.setColumnWidth(4, 180)
        layout.setColumnWidth(5, 250)
        layout.setColumnWidth(6, 250)
    elif table_name == 'Scope':
        layout.setColumnWidth(0, 70)
        layout.setColumnWidth(1, 150)
        layout.setColumnWidth(2, 300)
        layout.setColumnWidth(3, 300)
    elif table_name == 'Assumptions':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 150)
        layout.setColumnWidth(2, 300)
        layout.setColumnWidth(3, 300)
    elif table_name == 'Misuse cases':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 100)
        layout.setColumnWidth(2, 300)
        layout.setColumnWidth(3, 300)
    elif table_name == 'TOE Configuration':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 100)
        layout.setColumnWidth(2, 300)
        layout.setColumnWidth(3, 300)    
        layout.setColumnWidth(4, 300)  
    elif table_name == 'AttackTree':
        layout.setColumnWidth(0, 70)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 350)
        layout.setColumnWidth(3, 150)
        layout.setColumnWidth(4, 150)
        layout.setColumnWidth(5, 300)
        layout.setColumnWidth(6, 300)
    elif table_name == 'RiskControlTree':
        layout.setColumnWidth(0, 70)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 350)
        layout.setColumnWidth(3, 200)
        layout.setColumnWidth(4, 200)
        layout.setColumnWidth(5, 300)
    elif table_name == 'TechnicalTree':
        layout.setColumnWidth(0, 70)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 200)
        layout.setColumnWidth(3, 200)
        layout.setColumnWidth(4, 300)
        layout.setColumnWidth(5, 300)
        layout.setColumnWidth(6, 300)
    elif table_name == 'AttackLeaves':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 350)
        layout.setColumnWidth(3, 10)
        layout.setColumnWidth(4, 10)
        layout.setColumnWidth(5, 10)
        layout.setColumnWidth(6, 10)
        layout.setColumnWidth(7, 10)
        layout.setColumnWidth(8, 150)
        layout.setColumnWidth(9, 300)
        layout.setColumnWidth(10, 300)
    elif table_name == 'SecurityClaims':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 250)
        layout.setColumnWidth(3, 200)
        layout.setColumnWidth(4, 300)
        layout.setColumnWidth(5, 250)
        layout.setColumnWidth(6, 250)
        layout.setColumnWidth(7, 250)
    elif table_name == 'RiskTreatment':
        layout.setColumnWidth(0, 20)
        layout.setColumnWidth(1, 80)
        layout.setColumnWidth(2, 200)
        layout.setColumnWidth(3, 100)
        layout.setColumnWidth(4, 220)
        layout.setColumnWidth(5, 180)
        layout.setColumnWidth(6, 180)
        layout.setColumnWidth(7, 180)
        layout.setColumnWidth(8, 180)
        layout.setColumnWidth(9, 200)
        layout.setColumnWidth(10, 200)
        layout.setColumnWidth(11, 200)
        layout.setColumnWidth(12, 200)
        layout.setColumnWidth(12, 150)
    else:
        pass

def asset_generate_id(table):
    try:
        existing_ids = DB.execute_db("SELECT asset_id FROM assets UNION SELECT id FROM asset_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_asset_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_asset_ids):
            existing_max_id = max([int(data.removeprefix('AST-')) for data in existing_asset_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('AST-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"AST-{available_max_id + 1}"
        else:
            new_id = f"AST-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error generating ID: {e}")
        return ""

def DS_generate_id(table):
    try:
        existing_ids = DB.execute_db("SELECT ds_id FROM damage_scenarios UNION SELECT id FROM ds_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_ds_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_ds_ids):
            existing_max_id = max([int(data.removeprefix('DS-')) for data in existing_ds_ids])
        if 0 < len(available_ids):
            available_max_id = max([int(data.removeprefix('DS-')) for data in available_ids])

        if existing_max_id < available_max_id:
            new_id = f"DS-{available_max_id + 1}"
        else:
            new_id = f"DS-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error generating ID: {e}")
        return ""

def threat_generate_id(table):
    try:
        existing_ids = DB.execute_db("SELECT threat_id FROM threat UNION SELECT threat_id FROM threat_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount())]
        existing_ds_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_ds_ids):
            existing_max_id = max([int(data.removeprefix('TH-')) for data in existing_ds_ids])
        if 0 < len(available_ids):
            available_max_id = max([int(data.removeprefix('TH-')) for data in available_ids])

        if existing_max_id < available_max_id:
            new_id = f"TH-{available_max_id + 1}"
        else:
            new_id = f"TH-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error generating ID: {e}")
        return ""

def TS_generate_id(table):
    try:
        existing_ids = DB.execute_db("SELECT ts_id FROM threat_scenarios UNION SELECT ts_id FROM ts_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount())]
        existing_ds_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_ds_ids):
            existing_max_id = max([int(data.removeprefix('TS-')) for data in existing_ds_ids])
        if 0 < len(available_ids):
            available_max_id = max([int(data.removeprefix('TS-')) for data in available_ids])

        if existing_max_id < available_max_id:
            new_id = f"TS-{available_max_id + 1}"
        else:
            new_id = f"TS-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error generating ID: {e}")
        return ""

def scope_generate_id(table):
    try:
        existing_ids =  DB.execute_db("SELECT scope_id FROM scope_home_mindmap UNION SELECT id FROM scope_home_mindmap_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_toe_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_toe_ids):
            existing_max_id = max([int(data.removeprefix('SCOPE-')) for data in existing_toe_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('SCOPE-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"SCOPE-{available_max_id + 1}"
        else:
            new_id = f"SCOPE-{existing_max_id + 1}"
        return new_id

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error generating ID: {e}")
        return ""

def assum_generate_id(table):
    try:
        existing_ids =  DB.execute_db("SELECT assumption_id FROM assumptions UNION SELECT id FROM assum_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_assum_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_assum_ids):
            existing_max_id = max([int(data.removeprefix('AS-')) for data in existing_assum_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('AS-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"AS-{available_max_id + 1}"
        else:
            new_id = f"AS-{existing_max_id + 1}"
        return new_id

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error generating ID: {e}")
        return ""
    
def misusecases_generate_id(table):
    try:
        existing_ids =  DB.execute_db("SELECT misuse_cases_id FROM misuse_cases UNION SELECT id FROM misusecases_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_assum_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_assum_ids):
            existing_max_id = max([int(data.removeprefix('MC-')) for data in existing_assum_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('MC-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"MC-{available_max_id + 1}"
        else:
            new_id = f"MC-{existing_max_id + 1}"
        return new_id

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error generating ID: {e}")
        return ""

def toec_generate_id(table):
    try:
        existing_ids =  DB.execute_db("SELECT toe_configuration_id FROM toe_configuration UNION SELECT id FROM trash_toe")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_assum_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_assum_ids):
            existing_max_id = max([int(data.removeprefix('Cfg-')) for data in existing_assum_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('Cfg-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"Cfg-{available_max_id + 1}"
        else:
            new_id = f"Cfg-{existing_max_id + 1}"
        return new_id

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error generating ID: {e}")
        return ""

def securityclaims_generate_id(table):
    try:
        existing_ids = DB.execute_db("SELECT id FROM SecurityClaims UNION SELECT id FROM SClaims_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_asset_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_asset_ids):
            existing_max_id = max([int(data.removeprefix('SC-')) for data in existing_asset_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('SC-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"SC-{available_max_id + 1}"
        else:
            new_id = f"SC-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error generating ID: {e}")
        return ""

def securitygoals_generate_id(table):
    try:
        existing_ids = DB.execute_db("SELECT id FROM SecurityGoals UNION SELECT id FROM SGoals_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_asset_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_asset_ids):
            existing_max_id = max([int(data.removeprefix('SG-')) for data in existing_asset_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('SG-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"SG-{available_max_id + 1}"
        else:
            new_id = f"SG-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error generating ID: {e}")
        return ""

def securitycontrols_generate_id(table):
    try:
        existing_ids = DB.execute_db("SELECT id FROM security_controls UNION SELECT id FROM security_controls_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_asset_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_asset_ids):
            existing_max_id = max([int(data.removeprefix('Ctrl-')) for data in existing_asset_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('Ctrl-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"Ctrl-{available_max_id + 1}"
        else:
            new_id = f"Ctrl-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error generating ID: {e}")
        return ""

def intermediate_node_generate_id():
    try:
        att_existing_ids = DB.execute_db("SELECT id FROM intermediate_node_trash")
        existing_node_ids = []
        for node_id in att_existing_ids:  
            if node_id not in existing_node_ids: existing_node_ids.append(node_id[0])
        
        existing_max_id = 0
        if 0 < len(existing_node_ids):
            existing_max_id = max([int(data.removeprefix('Nd-')) for data in existing_node_ids])
         
        new_id = f"Nd-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error generating ID: {e}")
        return ""
    

def leaf_node_generate_id():
    try:
        att_existing_ids = DB.execute_db("SELECT id FROM leaf_node_trash")
        leaves_existing_ids = DB.execute_db("SELECT id FROM attack_leaf_home")
        existing_node_ids = []
        for node_id in att_existing_ids:  
            if node_id not in existing_node_ids: existing_node_ids.append(node_id[0])
        for node_id in leaves_existing_ids:  
            if node_id not in existing_node_ids: existing_node_ids.append(node_id[0])
        
        existing_max_id = 0
        if 0 < len(existing_node_ids):
            existing_max_id = max([int(data.removeprefix('Lf-')) for data in existing_node_ids])
         
        new_id = f"Lf-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error generating ID: {e}")
        return ""

def attack_leaves_generate_id(table):
    try:
        existing_ids = DB.execute_db("SELECT id FROM attack_leaf_home UNION SELECT id FROM leaf_node_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_asset_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_asset_ids):
            existing_max_id = max([int(data.removeprefix('Lf-')) for data in existing_asset_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('Lf-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"Lf-{available_max_id + 1}"
        else:
            new_id = f"Lf-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error generating ID: {e}")
        return ""

def technicalattack_generate_id(table):
    try:
        existing_ids = DB.execute_db("SELECT id FROM technical_tree_home UNION SELECT id FROM tat_trash")
        available_ids = [table.item(row, 1).text() for row in range(table.rowCount()-1)]
        existing_asset_ids = [row[0] for row in existing_ids]
        available_max_id = 0 
        existing_max_id = 0
        if 0 < len(existing_asset_ids):
            existing_max_id = max([int(data.removeprefix('TAT-')) for data in existing_asset_ids])
        if 0 < len(available_ids):
           available_max_id = max([int(data.removeprefix('TAT-')) for data in available_ids])
         
        if existing_max_id < available_max_id:
            new_id = f"TAT-{available_max_id + 1}"
        else:
            new_id = f"TAT-{existing_max_id + 1}"
        return new_id
    except sqlite3.Error as e:
        QMessageBox.critical(None,"Database Error", f"Error generating ID: {e}")
        return ""

def Calculate_AFR_Level(value):
    afr_level = ''
    if value >= 0 and value <= 13:
        afr_level = "High"
    elif value >= 14 and value <= 19:
        afr_level = "Medium"
    elif value >= 20 and value <= 24:
        afr_level = "Low"
    else:
        afr_level = "Very Low"
    return afr_level

def Apply_AFR_Level_Color(item, afr_level):
    item.setAlignment(Qt.AlignCenter)
    if afr_level == 'High':
        item.setStyleSheet(f"background-color: {P.AFRLevel_High_bg};")
    elif afr_level == 'Medium':
        item.setStyleSheet(f"background-color: {P.AFRLevel_Medium_bg};")
    elif afr_level == 'Low':
        item.setStyleSheet(f"background-color: {P.AFRLevel_Low_bg};")
    elif afr_level == 'Very Low':
        item.setStyleSheet(f"background-color: {P.AFRLevel_VeryLow_bg};")