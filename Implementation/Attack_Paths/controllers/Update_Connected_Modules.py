
import sys
import controllers.DatabaseCreator as DB
import models.helper as helper

import logging
logger = logging.getLogger(__name__)

def Update_Threat_Table():
    threat_rows = DB.execute_db("SELECT threat_id FROM threat")
    threat_list = []
    for row in threat_rows: threat_list.append(row[0])
    for threat in threat_list:
        attacktree_rows = DB.execute_db(f"SELECT Node_Type, AF_Text, RF_Text FROM attack_tree WHERE Node_ID like '{threat}_node_0'")
        attacktree_head = []
        for row in attacktree_rows: 
            if row[0] == 'head': attacktree_head = row
        # print(attacktree_head)
        # Fetch the specific row with the matching threat_id
        row = DB.execute_db_query(f"SELECT * FROM threat WHERE threat_id = ?", (threat,))
        if row:  # Ensure the row exists
            row_data = list(row[0])  # Convert tuple to list to modify values
            if attacktree_head:
                row_data[5] = attacktree_head[1]  # Update the AF level
                row_data[6] = attacktree_head[2]  # Update the RF level
            else:
                row_data[5] = ''  # Update the AF level
                row_data[6] = ''  # Update the RF level
            # print(row_data)
            # Unpack the updated row data
            id, name, damage_scenarios,misuse_cases, toe_configuration, InitialAFR, ResidAFR, asset, security_properties, reasoning, comments = row_data
            # Use UPDATE query instead of INSERT OR REPLACE for only updating the necessary fields
            DB.update_db("""UPDATE threat SET InitialAFR = ?, ResidAFR = ? WHERE threat_id = ?""", (InitialAFR, ResidAFR, id))

def Update_AttackTree_Table():
    threat_rows = DB.execute_db("SELECT id FROM attack_tree_home")
    threat_list = []
    for row in threat_rows: threat_list.append(row[0])
    for threat in threat_list:
        attacktree_rows = DB.execute_db(f"SELECT Node_Type, AF_Text, RF_Text FROM attack_tree WHERE Node_ID like '{threat}_node_0'")
        attacktree_head = []
        for row in attacktree_rows: 
            if row[0] == 'head': attacktree_head = row
        # Fetch the specific row with the matching threat_id
        row = DB.execute_db_query(f"SELECT * FROM attack_tree_home WHERE id = ?", (threat,))
        if row:  # Ensure the row exists
            row_data = list(row[0])  # Convert tuple to list to modify values
            if attacktree_head:
                row_data[2] = attacktree_head[1]  # Update the AF level
                row_data[3] = attacktree_head[2]  # Update the RF level
            else:
                row_data[2] = ''  # Update the AF level
                row_data[3] = ''  # Update the RF level
            
            # Unpack the updated row data
            id, name, InitialAFR, ResidAFR, toe_configuration, comments = row_data
            # Use UPDATE query instead of INSERT OR REPLACE for only updating the necessary fields
            DB.update_db("""UPDATE attack_tree_home SET InitialAFR = ?, ResidAFR = ? WHERE id = ?""", (InitialAFR, ResidAFR, id))

def Update_RiskControlTree_Table():
    control_rows = DB.execute_db("SELECT id, name FROM security_controls")
    control_map = {}
    for control in control_rows: control_map[control[0]] = control[1]
    control_list = []
    for row in control_rows: control_list.append(row[0])
    for control in control_list:
        text = f"{control} Risk_Control - {control_map[control]}"
        attacktree_rows = DB.execute_db(f"SELECT Node_ID FROM attack_tree WHERE Text like '{text}'")
        attacktree_control_map = ''
        for row in attacktree_rows: 
            if attacktree_control_map == '': attacktree_control_map = str(row[0].strip().split('_')[0])
            else: attacktree_control_map += ', ' + str(row[0].strip().split('_')[0])
        # Fetch the specific row with the matching threat_id
        row = DB.execute_db_query(f"SELECT * FROM riskcontrol_tree_home WHERE id = ?", (control,))
        if row:  # Ensure the row exists
            row_data = list(row[0])  # Convert tuple to list to modify values
            if attacktree_control_map:
                row_data[2] = attacktree_control_map
            else:
                row_data[2] = attacktree_control_map
            
            # Unpack the updated row data
            id, name, mitigates, assumptions, comment = row_data
            # Use UPDATE query instead of INSERT OR REPLACE for only updating the necessary fields
            DB.update_db("""UPDATE riskcontrol_tree_home SET mitigates = ? WHERE id = ?""", (mitigates, id))

def Update_TechnicalTree_Table():
    technical_rows = DB.execute_db("SELECT id, name FROM technical_tree_home")
    technical_map = {}
    for technical in technical_rows: technical_map[technical[0]] = technical[1] if technical[1] else technical[0]
    technical_list = []
    for row in technical_rows: technical_list.append(row[0])
    for technical in technical_list:
        text = f"{technical} {technical_map[technical]}"
        
        attacktree_rows = DB.execute_db(f"SELECT Node_ID FROM attack_tree WHERE Text like '{text}'")
        attacktree_technical_map = set()
        attacktree_technical_map_str  = ''
        for row in attacktree_rows: 
            # if attacktree_technical_map == '': attacktree_technical_map = str(row[0].strip().split('_')[0])
            # else: attacktree_technical_map += ', ' + str(row[0].strip().split('_')[0])
            node_id_prefix = row[0].strip().split('_')[0] if '_' in row[0] else row[0].strip()
            attacktree_technical_map.add(node_id_prefix)  # Ensures uniqueness
        attacktree_technical_map_str = ', '.join(sorted(attacktree_technical_map))
        
        RiskControlTree_rows = DB.execute_db(f"SELECT Node_ID FROM riskcontrol_tree WHERE Text like '{text}'")
        RiskControlTree_technical_map = set()
        RiskControlTree_technical_map_str = ''
        for row in RiskControlTree_rows: 
            # if RiskControlTree_technical_map == '': RiskControlTree_technical_map = str(row[0].strip().split('_')[0])
            # else: RiskControlTree_technical_map += ', ' + str(row[0].strip().split('_')[0])
            node_id_prefix = row[0].strip().split('_')[0] if '_' in row[0] else row[0].strip()
            RiskControlTree_technical_map.add(node_id_prefix)  # Ensures uniqueness
        RiskControlTree_technical_map_str = ', '.join(sorted(RiskControlTree_technical_map))
        
        # Fetch the specific row with the matching threat_id
        row = DB.execute_db_query(f"SELECT * FROM technical_tree_home WHERE id = ?", (technical,))
        if row:  # Ensure the row exists
            row_data = list(row[0])  # Convert tuple to list to modify values
            if RiskControlTree_technical_map_str:
                row_data[3] = RiskControlTree_technical_map_str
            else:
                row_data[3] = RiskControlTree_technical_map_str
            if attacktree_technical_map_str:
                row_data[2] = attacktree_technical_map_str 
            else:
                row_data[2] = attacktree_technical_map_str 
            
            # Unpack the updated row data
            id, name, used_in_threat, used_in_riskcontrol, toe_configuration, assumptions, comment = row_data
            # Use UPDATE query instead of INSERT OR REPLACE for only updating the necessary fields
            DB.update_db("""UPDATE technical_tree_home SET used_in_threat = ?, used_in_riskcontrol = ? WHERE id = ?""", (used_in_threat, used_in_riskcontrol, id))

def Update_RiskTreatment_Table():
    # Fetch the specific row with the matching threat_id
    attacktree_rows = DB.execute_db(f'SELECT Node_ID, Text FROM attack_tree where Node_Type like "riskcontrol head"')
    attacktree_linked_controls_CT = {}
    for node_id, text in attacktree_rows:
        threat = node_id.split('_')[0]
        control = text.split(' ')[0]
        if control not in attacktree_linked_controls_CT.keys(): attacktree_linked_controls_CT[control] = threat
        else : attacktree_linked_controls_CT[control] += f", {threat}"
    
    attacktree_linked_controls_RT = {}
    for node_id, text in attacktree_rows:
        threat = node_id.split('_')[0]
        control = text.split(' ')[0]
        if threat not in attacktree_linked_controls_RT.keys(): attacktree_linked_controls_RT[threat] = control
        else : attacktree_linked_controls_RT[threat] += f", {control}"
    # print(attacktree_linked_controls_RT)
    rows = DB.execute_db(f"SELECT * FROM RiskData")
    for row in rows:
        row_data = list(row)
        if row[3].split(' ')[0] in attacktree_linked_controls_RT.keys():
            row_data[12] = attacktree_linked_controls_RT[row[3].split(' ')[0]]
        else : row_data[12] = ''
        id, damage, impact, threat, init_AFR_level, init_AFR_value, resid_AFR_level, resid_AFR_value, toe_configuration, risk_treatment, security_claims, security_goals, mitigated_by = row_data
        threat_id = threat.split(' - ')[0]
        AFR_level_data = DB.execute_db_query(f"SELECT InitialAFR, ResidAFR FROM attack_tree_home WHERE id = ?", (threat_id,))
        if AFR_level_data:
            init_AFR_level = AFR_level_data[0][0]
            init_AFR_value = helper.risk_map.get((impact, init_AFR_level)) if (init_AFR_level in helper.AFR_Levels and impact in helper.DS_impact_menu) else ''
            resid_AFR_level = AFR_level_data[0][1]
            resid_AFR_value = helper.risk_map.get((impact, resid_AFR_level)) if (resid_AFR_level in helper.AFR_Levels and impact in helper.DS_impact_menu) else ''
            DB.update_db("""UPDATE RiskData SET init_AFR_level=?, init_AFR_value=?, resid_AFR_level=?, resid_AFR_value=?, mitigated_by = ? WHERE threat = ? AND damage = ?""", (init_AFR_level, init_AFR_value, resid_AFR_level, resid_AFR_value, mitigated_by, threat, damage))

