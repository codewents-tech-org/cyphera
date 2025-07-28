
import sys
from PyQt5.QtWidgets import QMessageBox   
import sqlite3
import controllers.DatabaseCreator as DB


def Update_AllTree_Leaf(value_updated_leafs_list = None, name_updated_leafs_list = None):
    try:
        if name_updated_leafs_list:
            for leaf_id in name_updated_leafs_list:
                leaf_name = ''
                leaf_rows = DB.execute_db(f"SELECT name FROM attack_leaf_home WHERE id='{leaf_id}'")
                if leaf_rows: 
                    leaf_name = leaf_rows[0][0]
                    query = f"""UPDATE technical_tree SET Text = '{leaf_id} {leaf_name}' WHERE Node_Type = 'leaf' AND Text like '{leaf_id} %';
                                UPDATE riskcontrol_tree SET Text = '{leaf_id} {leaf_name}' WHERE Node_Type = 'leaf' AND Text like '{leaf_id} %';
                                UPDATE riskcontrol_tree SET Text = '{leaf_id} {leaf_name}' WHERE Node_Type = 'technical leaf' AND Text like '{leaf_id} %';
                                UPDATE attack_tree SET Text = '{leaf_id} {leaf_name}' WHERE Node_Type = 'leaf' AND Text like '{leaf_id} %';
                                UPDATE attack_tree SET Text = '{leaf_id} {leaf_name}' WHERE Node_Type = 'technical leaf' AND Text like '{leaf_id} %';
                                UPDATE attack_tree SET Text = '{leaf_id} {leaf_name}' WHERE Node_Type = 'riskcontrol leaf' AND Text like '{leaf_id} %';
                                UPDATE attack_tree SET Text = '{leaf_id} {leaf_name}' WHERE Node_Type = 'riskcontrol technical leaf' AND Text like '{leaf_id} %';
                            """
                    DB.executescript_db(query)
        
        if value_updated_leafs_list:
            for leaf_id in value_updated_leafs_list:
                leaf_rows = DB.execute_db(f"SELECT time, expertise, knowledge, access, equipment, AFR_Level FROM attack_leaf_home WHERE id='{leaf_id}'")
                if leaf_rows: 
                    values = [value for value in leaf_rows[0][0:5]]
                    leaf_values = [int(value) for value in leaf_rows[0][0:5]]
                    leaf_af_value = sum(leaf_values)
                    leaf_af_level = leaf_rows[0][5]
                    
                    queries = [
                                f"""UPDATE technical_tree SET Value = '{str(leaf_af_value)}', AF_Text = '{leaf_af_level}', "Values" = "{str(values)}" WHERE Node_Type = 'leaf' AND Text like '{leaf_id} %' ESCAPE '\\'""",
                                f"""UPDATE riskcontrol_tree SET Value = '{str(leaf_af_value)}', AF_Text = '{leaf_af_level}', "Values" = "{str(values)}" WHERE Node_Type = 'leaf' AND Text like '{leaf_id} %' ESCAPE '\\'""",
                                f"""UPDATE riskcontrol_tree SET Value = '{str(leaf_af_value)}', AF_Text = '{leaf_af_level}', "Values" = "{str(values)}" WHERE Node_Type = 'technical leaf' AND Text like '{leaf_id} %' ESCAPE '\\'""",
                                f"""UPDATE attack_tree SET RF_Value = '{str(leaf_af_value)}', RF_Text = '{leaf_af_level}', "Values" = "{str(values)}" WHERE Node_Type = 'leaf' AND Text like '{leaf_id} %' ESCAPE '\\'""",
                                f"""UPDATE attack_tree SET RF_Value = '{str(leaf_af_value)}', RF_Text = '{leaf_af_level}', "Values" = "{str(values)}" WHERE Node_Type = 'technical leaf' AND Text like '{leaf_id} %' ESCAPE '\\'""",
                                f"""UPDATE attack_tree SET RF_Value = '{str(leaf_af_value)}', RF_Text = '{leaf_af_level}', "Values" = "{str(values)}" WHERE Node_Type = 'riskcontrol leaf' AND Text like '{leaf_id} %' ESCAPE '\\'""",
                                f"""UPDATE attack_tree SET RF_Value = '{str(leaf_af_value)}', RF_Text = '{leaf_af_level}', "Values" = "{str(values)}" WHERE Node_Type = 'riskcontrol technical leaf' AND Text like '{leaf_id} %' ESCAPE '\\'""",
                            ]
                    for query in queries:
                        DB.update_db_db(query)
                    
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}") 
