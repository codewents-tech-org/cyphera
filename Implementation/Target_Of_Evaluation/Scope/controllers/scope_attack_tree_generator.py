from PyQt5.QtWidgets import QMessageBox
import controllers.DatabaseCreator as DB
import models.helper as helper
import re
from Attack_Paths.controllers.attack_tree_AFR_update import AttackTree_AFR_Update
import Attack_Paths.controllers.Update_Connected_Modules as APST
from Attack_Paths.controllers.Update_Connected_Modules import update_threat_table, update_attacktree_table, update_risktreatment_table
import logging
logger = logging.getLogger(__name__)

def update_node_text():
    logger.info("Node text updation")
    """
    Fetch all scope_id and scope_name from scope_home_mindmap, 
    then update the node_text in the scope_home_mindmap_node table for rows 
    where node_type is 'head' by updating the scope_name.
    """
    try:
        print("Fetching all scope_ids and scope_names from scope_home_mindmap...")
        DB.cursor.execute(
            """
            SELECT scope_id, scope_name FROM scope_home_mindmap
            """
        )
        scope_data = DB.cursor.fetchall()

        if not scope_data:
            print("Error: No data found in scope_home_mindmap.")
            return

        for scope_id, scope_name in scope_data:
            print(f"Processing scope_id: {scope_id} and scope_name: {scope_name}")

            DB.cursor.execute(
                """
                SELECT node_text FROM scope_home_mindmap_node WHERE scope_id = :scope_id AND node_type = "head"
                """,
                {"scope_id": scope_id}
            )
            rows = DB.cursor.fetchall()

            if not rows:
                print(f"No rows found with scope_id: {scope_id} and node_type 'head'.")
                continue

            # Step 4: Loop through the rows and update node_text
            for row in rows:
                node_text = row[0]  # Get the current node_text

                print(f"Current node_text for scope_id {scope_id}: {node_text}")

                # Check if node_text contains space, which separates scope_id and scope_name
                if not node_text or " " not in node_text:
                    print(f"Skipping node with scope_id: {scope_id} due to empty or malformed node_text.")
                    continue  

                # Split the node_text into current_scope_id and current_scope_name
                current_scope_id, current_scope_name = node_text.split(" ", 1)

                # Ensure the scope_id matches and update the scope_name only if needed
                if current_scope_id == scope_id:
                    if current_scope_name != scope_name:
                        new_node_text = f"{scope_id} {scope_name}"
                        DB.cursor.execute(
                            """
                            UPDATE scope_home_mindmap_node
                            SET node_text = :new_node_text
                            WHERE scope_id = :scope_id AND node_type = "head"
                            """,
                            {"new_node_text": new_node_text, "scope_id": scope_id}
                        )
                        DB.conn.commit()
                        logger.info(f"the Updated Node Text {new_node_text}")
                        print(f"Successfully updated node_text for scope_id: {scope_id}")
                    else:
                        print(f"Node text is already correct for scope_id: {scope_id}")
                else:
                    print(f"Skipping node with scope_id: {current_scope_id}, does not match.")

    except DB.sqlite3.Error as e:
        print(f"SQLite error: {e}")

def generate_attack_tree_from_mindmap(scope_id):
    try:
        logger.info("Generation of Attack tree from Mindmap")
        DB.cursor.execute("SELECT scope_id, threat FROM scope_home_mindmap_dumy WHERE scope_id = ?", (scope_id,))
        scope_data = DB.cursor.fetchall()

        if not scope_data or not scope_data[0]:
            print(f"No threats found for scope ID: {scope_id}")
            return

        # Create a dictionary mapping scope_id to threats (splitting multiple threats)
        scope_threat_mapping = {}
        for scope_id, threat in scope_data:
            if not threat:
                continue
            scope_key = f"SCOPE-{scope_id}" if not scope_id.startswith("SCOPE-") else scope_id
            threats = [t.strip() for t in threat.split(',')]  # Split multiple threats
            scope_threat_mapping[scope_key] = threats

        DB.cursor.execute("SELECT node_ID, parent_ID, node_type, node_text FROM scope_home_mindmap_node WHERE scope_id = ?", (scope_id,))
        mind_map_data = DB.cursor.fetchall()

        if not mind_map_data:
            return

        afr_calculation_enable = False
        leaf_availabele_for_calculation = False
        leaf_deleted = False

        # Process each row from mind_map_data
        for scope_id, threats in scope_threat_mapping.items():
            for threat in threats:  # Process each threat individually
                print(f"Processing Threat: {threat} for Scope ID: {scope_id}, ' ", len(mind_map_data))
                for row in mind_map_data:
                    node_id, parent_id, node_type, text = row

                    # Check if the node or parent ID is related to the current scope ID
                    scope_id_from_node = node_id if f"{scope_id}_" in node_id or f"{scope_id}-" in node_id or node_id == scope_id else None
                    scope_id_from_parent = parent_id if f"{scope_id}_" in parent_id or f"{scope_id}-" in parent_id or parent_id == scope_id else None

                    leaf_availabale_flag = False

                    if not scope_id_from_node and not scope_id_from_parent:
                        continue

                     # Replace scope_id with the current threat in Node_ID and Parent_ID
                    updated_node_id = node_id.replace(scope_id, threat) if scope_id_from_node else node_id
                    updated_parent_id = parent_id.replace(scope_id, threat) if scope_id_from_parent else parent_id
    
                    node_text = text.replace(scope_id, threat) if threat else text
                    print("--------", node_type, "-----------------")

                    values_str = "[]"  # Default values for non-leaf nodes
                    RF_Value = 0


                    if node_type == "leaf":
                        leaf_availabale_flag = True
                        DB.cursor.execute("SELECT id, time, expertise, knowledge, access, equipment FROM attack_leaf_home WHERE name = ?", (text,))
                        existing_leaf = DB.cursor.fetchone()

                        if existing_leaf:
                            leaf_id, time, expertise, knowledge, access, equipment = existing_leaf
                            leaf_values = [int(time), int(expertise), int(knowledge), int(access), int(equipment)]
                            leaf_af_value = sum(leaf_values)
                            RF_Text = helper.Calculate_AFR_Level(leaf_af_value)
                            RF_Value = leaf_af_value if leaf_af_value > 0 else 0
                            values_str = f"[{time}, {expertise}, {knowledge}, {access}, {equipment}]"
                            # if leaf_af_value > 0:
                            #     afr_calculation_enable = True
                        else:
                            leaf_id = helper.leaf_node_generate_id()
                            values_str = "[0, 0, 0, 0, 0]"
                            RF_Text = "High"
                            RF_Value = 0
                            DB.update_db("""
                                INSERT INTO attack_leaf_home (id, name, time, expertise, knowledge, access, equipment, AFR_level, reasoning, comments)
                                VALUES (?, ?, ?, ?, ?, ?, ?, 'High', '', '')
                            """, (leaf_id, text, 0, 0, 0, 0, 0))
                           
                        node_text = f"{leaf_id} {text}"
                        # afr_calculation_enable = bool(existing_leaf)
                    elif node_type == "intermediate":
                        intermediate_id = helper.intermediate_node_generate_id()
                        DB.cursor.execute("INSERT INTO intermediate_node_trash (id) VALUES (?)", (intermediate_id,))
                        values_str = "[]"
                        RF_Value = ''
                        RF_Text = ''
                        node_text = f"{intermediate_id} {text}"
                    elif node_type == "head":
                        threat_data = DB.execute_db(f"SELECT name FROM threat WHERE threat_id = '{threat}'")
                        threat_text = ''
                        if threat_data:
                            threat_text = f"{threat} {threat_data[0][0]}"

                        node_text = threat_text
                        RF_Value = ''
                        RF_Text = '' 

                    # RF_Text = "High" if node_type == "leaf" else ''
                    leaf_gate_type = ' ' if node_type == "leaf" else "and_gate"
                    image_type = "head_node" if node_type in ["head", "intermediate"] else "leaf_node"

                    final_values = values_str
                    
                    DB.cursor.execute("SELECT * FROM attack_tree WHERE Node_ID = ?", (updated_node_id,))
                    existing_row = DB.cursor.fetchone()

                    if existing_row:
                        if node_type == "leaf" and RF_Value > 0: 
                            leaf_availabele_for_calculation = True
                        
                        DB.update_db("""
                            UPDATE attack_tree
                            SET Parent_ID = ?, Node_Type = ?, Text = ?, "Values" = ?, RF_Value = ?, RF_Text = ?,  x = ?, y = ?
                            WHERE Node_ID = ?
                        """, (updated_parent_id, node_type, node_text, final_values, RF_Value, RF_Text, 0, 0, updated_node_id))

                    else:
                        if node_type == "leaf" and RF_Value > 0: 
                                afr_calculation_enable = True
                                leaf_availabele_for_calculation = True
                        if node_type == 'head':
                            RF_Value, RF_Text = '', ''            
                        DB.update_db("""
                            INSERT INTO attack_tree
                            (Node_ID, Parent_ID, Node_Type, Text, AF_Value, AF_Text, RF_Value, RF_Text, Gate_Type, Image_Type, x, y, "Values")
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            updated_node_id, updated_parent_id, node_type, node_text, '', '', RF_Value, RF_Text, leaf_gate_type,
                            "head_node" if node_type in ["head", "intermediate"] else "leaf_node", 0, 0, final_values
                            
                        ))
        DB.conn.commit()
        print("Attack tree updated successfully with data from Mind_map!")
        

        # Fetch all Node_IDs from attack_tree
        DB.cursor.execute("SELECT Node_ID FROM attack_tree")
        attack_tree_nodes = [row[0] for row in DB.cursor.fetchall()]

        # Process each Node_ID
        for node_id in attack_tree_nodes:
            print(f"Processing Node_ID: {node_id}")
            
            # Use regular expression to extract the 'TH-<number>' pattern
            match = re.search(r'TH-\d+', node_id)
            
            if match:
                extracted_threat = match.group(0)  # This will give 'TH-<number>'
                print(f"Extracted Threat: {extracted_threat}")
                
                # Check if the extracted threat exists in the threat column
                DB.cursor.execute("SELECT scope_id FROM scope_home_mindmap_dumy WHERE threat LIKE ?", ('%' + extracted_threat + '%',))
                result = DB.cursor.fetchone()
                
                if result:
                    scope_id = result[0]
                    print(f"Found scope_id: {scope_id} for Threat: {extracted_threat}")
                    
                    # Replace the extracted threat in Node_ID with scope_id
                    modified_node_id = node_id.replace(extracted_threat, scope_id)
                    print(f"Updated Node_ID: {modified_node_id}")
                    
                    
                    
                    # Check if the modified Node_ID exists in attack_tree
                    DB.cursor.execute("SELECT 1 FROM scope_home_mindmap_node WHERE node_id = ?", (modified_node_id,))
                    check_node = DB.cursor.fetchone()
                    print ("dsa", check_node)
                    if not check_node:
                        # If modified Node_ID does not exist, delete the original row
                        print(f"Modified Node_ID {modified_node_id} does not exist in attack_tree. Deleting original Node_ID {node_id}.")
                        DB.cursor.execute("SELECT Node_Type, RF_Value from attack_tree WHERE Node_ID = ?", (node_id,))
                        nodetype = DB.cursor.fetchone()
                        print ("dsad", nodetype)
                        if nodetype:
                            if nodetype[0] == "leaf" and int(nodetype[1]) > 0:
                                leaf_deleted = True
                        DB.cursor.execute("DELETE FROM attack_tree WHERE Node_ID = ?", (node_id,))
                else:
                    print(f"No scope_id found for Threat: {extracted_threat}, skipping replacement for Node_ID: {node_id}")
            else:
                print(f"No 'TH-' pattern found in Node_ID: {node_id}, skipping.")
        DB.conn.commit()
        print("All Node_IDs processed, updates applied, and unused rows deleted.")
        if afr_calculation_enable:
            update_attack_tree_afr(scope_threat_mapping)
        elif leaf_availabele_for_calculation and leaf_deleted:
            update_attack_tree_afr(scope_threat_mapping)  
        elif (leaf_deleted ) and leaf_availabale_flag== True:
            for scope_id, threats in scope_threat_mapping.items():
                for threat in threats:  # Process each threat individually
                    DB.execute_db_db("""
                            UPDATE attack_tree
                            SET AF_Value = '', AF_Text = ''
                            WHERE Node_ID = ?
                        """, ( f"{threat}_node_0",))
                    rows = DB.execute_db_query(f"UPDATE attack_tree SET Image_Type ='' WHERE Node_ID like ?", (f"{threat}_node%",)) 
            table_update()

        if len(mind_map_data)<=1 or leaf_availabale_flag== False:
            for scope_id, threats in scope_threat_mapping.items():
                for threat in threats:
                    updated_node_id = f"{threat}_node_0"
                    DB.update_db_db(f"""UPDATE attack_tree SET AF_Value='', AF_Text='', RF_Value = '', RF_Text = '' WHERE Node_ID = '{updated_node_id}'""")
            table_update()

    except Exception as e:
        print(f"Error: {e}")

def update_attack_tree_afr(scope_threat_mapping): 
    for scope_id, threats in scope_threat_mapping.items():
        for threat in threats:  # Process each threat individually
            AttackTree_AFR_Update(threat)
    table_update()

def table_update():    
    APST.update_threat_table()
    APST.update_attacktree_table()
    APST.update_risktreatment_table()



