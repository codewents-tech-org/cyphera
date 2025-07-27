
import sys
from PyQt5.QtWidgets import QComboBox, QMessageBox, QComboBox
import controllers.DatabaseCreator as DB
# from Attack_Paths.controllers.Update_AllTrees_SubTrees import Update_AttackTree_ExistingControlTree, Update_AttackTree_ExistingTechnicalTree, Update_ControlTree_ExistingTechnicalTree
from Attack_Paths.controllers.Update_Connected_Modules import update_threat_table, update_technicaltree_table, update_riskcontroltree_table, update_attacktree_table, update_risktreatment_table

import logging
logger = logging.getLogger(__name__)
# Save Technical tree
def Save_TechnicalTree(tree, tree_id, nodes):
    logger.info(f"Saving {tree_id} technical tree")
    try:
        data_to_insert = []
        DB.update_db('DELETE FROM technical_tree WHERE Node_ID LIKE ?', (f'{tree_id}_node%',))
        for control, node_info in nodes.items():
            Values_list = node_info['values']
            values = []
            if Values_list:
                for i in range(len(Values_list)):
                    proxy_widget = Values_list[i]  # This is the QGraphicsProxyWidget
                    combo_box = proxy_widget.widget()  # Retrieve the actual widget, which could be a QComboBox

                    if isinstance(combo_box, QComboBox):
                        value = combo_box.currentText()  # Now you can access currentText() on the actual QComboBox
                        values.append(value)
                    else:
                        print(f"Expected QComboBox, got {type(combo_box)}")
            data_to_insert.append(  (control,
                                    str(nodes[control]["parent"]),
                                    str(nodes[control]["tags"][0]),
                                    str(nodes[control]["id"].toPlainText())+' '+str(nodes[control]["text"].toPlainText()),
                                    str(nodes[control]["af_value_box"].toPlainText()),
                                    str(nodes[control]["af_level_box"].toPlainText()),
                                    str(nodes[control]["gate_type"]),
                                    str(values),
                                    str(nodes[control]["image_type"]),
                                    nodes[control]['x'],
                                    nodes[control]['y']),
                                )
        
        sql_command = '''
            INSERT OR REPLACE INTO technical_tree 
            (Node_ID, Parent_ID, Node_Type, Text, Value, AF_Text, Gate_Type, "Values", "Image_Type", "x", "y")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        DB.executemany_db(sql_command, data_to_insert)
        
        logger.info(f"Updating all tree leaf data and attack leaves table")
        tree.Update_Leaf_Data()
        logger.info(f"Updating Technical tree in Control tree")
        Update_ControlTree_ExistingTechnicalTree(tree_id)
        logger.info(f"Updating Technical tree in Attack tree")
        Update_AttackTree_ExistingTechnicalTree(tree_id)
        logger.info(f"Updating Threat table")
        update_threat_table()
        logger.info(f"Updating Attack tree table")
        update_attacktree_table()
        logger.info(f"Updating Risk treatment table")
        update_risktreatment_table()
        # QMessageBox.information(None, "Save", f"{'technical_tree'.replace('_', ' ').title()} {tree_id} saved successfully")
    
    except Exception as e:
        # Handle exceptions and show an error message
        QMessageBox.critical(None, "Save Error", f"An error occurred while saving: {e}")

# Save Risk Control Tree
def Save_RiskControlTree(tree, tree_id, nodes):
    logger.info(f"Saving {tree_id} Risk Control Tree")
    try:
        DB.update_db('DELETE FROM riskcontrol_tree WHERE Node_ID LIKE ?', (f'{tree_id}_node%',))
        data_to_insert = []
        for control, node_info in nodes.items():
            Values_list = node_info['values']
            values = []
            if Values_list:
                for i in range(len(Values_list)):
                    proxy_widget = Values_list[i]  # This is the QGraphicsProxyWidget
                    combo_box = proxy_widget.widget()  # Retrieve the actual widget, which could be a QComboBox

                    if isinstance(combo_box, QComboBox):
                        value = combo_box.currentText()  # Now you can access currentText() on the actual QComboBox
                        values.append(value)
                    else:
                        print(f"Expected QComboBox, got {type(combo_box)}")
            
            if control in tree.technical_tree_added_list:  
                if nodes[control]["id"].toPlainText().startswith('TAT-'): node_tag = "technical " + 'head'
                else: node_tag = "technical " + nodes[control]["tags"][0]
            else:
                node_tag = nodes[control]["tags"][0] 
            
            data_to_insert.append(  (control,
                                    str(nodes[control]["parent"]),
                                    str(node_tag),
                                    str(nodes[control]["id"].toPlainText())+' '+str(nodes[control]["text"].toPlainText()),
                                    str(nodes[control]["af_value_box"].toPlainText()),
                                    str(nodes[control]["af_level_box"].toPlainText()),
                                    str(nodes[control]["gate_type"]),
                                    str(values),
                                    str(nodes[control]["image_type"]),
                                    nodes[control]['x'],
                                    nodes[control]['y']),
                                )
        
        sql_command = '''
            INSERT OR REPLACE INTO riskcontrol_tree 
            (Node_ID, Parent_ID, Node_Type, Text, Value, AF_Text, Gate_Type, "Values", "Image_Type", "x", "y")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        DB.executemany_db(sql_command, data_to_insert)
        
        logger.info(f"Updating all tree leaf data and attack leaves table")
        tree.Update_Leaf_Data()
        logger.info(f"Updating Risk Control Tree in Attack tree")
        Update_AttackTree_ExistingControlTree(tree_id)
        logger.info(f"Updating Technical tree table")
        update_technicaltree_table()
        logger.info(f"Updating Threat table")
        update_threat_table()
        logger.info(f"Updating Attack tree table")
        update_attacktree_table()
        logger.info(f"Updating Risk treatment table")
        update_risktreatment_table()
        # QMessageBox.information(None, "Save", f"{'riskcontrol_tree'.replace('_', ' ').title()} {tree_id} saved successfully")
    
    except Exception as e:
        # Handle exceptions and show an error message
        QMessageBox.critical(None, "Save Error", f"An error occurred while saving: {e}")

# Save Attack tree
def Save_AttackTree(tree, tree_id, nodes):
    logger.info(f"Saving {tree_id} attack tree")
    try:
        DB.update_db('DELETE FROM attack_tree WHERE Node_ID LIKE ?', (f'{tree_id}_node%',))
        data_to_insert = []
        for threat, node_info in nodes.items():
            Values_list = node_info['values']
            values = []
            if Values_list:
                for i in range(len(Values_list)):
                    proxy_widget = Values_list[i]  # This is the QGraphicsProxyWidget
                    combo_box = proxy_widget.widget()  # Retrieve the actual widget, which could be a QComboBox

                    if isinstance(combo_box, QComboBox):
                        value = combo_box.currentText()  # Now you can access currentText() on the actual QComboBox
                        values.append(value)
                    else:
                        print(f"Expected QComboBox, got {type(combo_box)}")
            if threat in tree.riskcontrol_tree_added_list:  
                if nodes[threat]["id"].toPlainText().startswith('Ctrl-'): node_tag = "riskcontrol " + 'head'
                elif threat in tree.technical_tree_added_list:
                    if nodes[threat]["id"].toPlainText().startswith('TAT-'): node_tag = "riskcontrol technical " + 'head'
                    else: node_tag = "riskcontrol technical " + nodes[threat]["tags"][0]
                else: node_tag = "riskcontrol " + nodes[threat]["tags"][0]
            else:
                if threat in tree.technical_tree_added_list:
                    if nodes[threat]["id"].toPlainText().startswith('TAT-'): node_tag = "technical " + 'head'
                    else: node_tag = "technical " + nodes[threat]["tags"][0]
                else: node_tag = nodes[threat]["tags"][0] 
            
            af_value_box = nodes[threat]["af_value_box"]
            af_level_box = nodes[threat]["af_level_box"]
            rf_value_box = nodes[threat]["rf_value_box"].toPlainText()
            rf_level_box = nodes[threat]["rf_level_box"].toPlainText()
            if threat == f'{tree_id}_node_0':
                if not tree.riskcontrol_tree_added:
                    af_value_box = nodes[threat]["rf_value_box"].toPlainText()
                    af_level_box = nodes[threat]["rf_level_box"].toPlainText()
                    rf_value_box = ''
                    rf_level_box = ''
            
            data_to_insert.append(  (threat,
                                    str(nodes[threat]["parent"]),
                                    str(node_tag),
                                    str(nodes[threat]["id"].toPlainText())+' '+str(nodes[threat]["text"].toPlainText()),
                                    str(af_value_box),
                                    str(af_level_box),
                                    str(rf_value_box),
                                    str(rf_level_box),
                                    str(nodes[threat]["gate_type"]),
                                    str(values),
                                    str(nodes[threat]["image_type"]),
                                    nodes[threat]['x'],
                                    nodes[threat]['y']),
                                )
        
        sql_command = '''
            INSERT OR REPLACE INTO attack_tree 
            (Node_ID, Parent_ID, Node_Type, Text, AF_Value, AF_Text, RF_Value, RF_Text, Gate_Type, "Values", "Image_Type", "x", "y")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        DB.executemany_db(sql_command, data_to_insert)

        logger.info(f"Updating all tree leaf data and attack leaves table")
        tree.Update_Leaf_Data()
        logger.info(f"Updating Risk Control Tree table")
        update_riskcontroltree_table()
        logger.info(f"Updating Technical tree table")
        update_technicaltree_table()
        logger.info(f"Updating Threat table")
        update_threat_table()
        logger.info(f"Updating attack tree table")
        update_attacktree_table()
        logger.info(f"Updating Risk treatment table")
        update_risktreatment_table()
        # QMessageBox.information(None, "Save", f"{'attack_tree'.replace('_', ' ').title()} {tree_id} saved successfully")
    
    except Exception as e:
        # Handle exceptions and show an error message
        QMessageBox.critical(None, "Save Error", f"An error occurred while saving: {e}")
