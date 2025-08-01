import re
import controllers.DatabaseCreator as DB
# from Reports.Generate_Reports.models.treeimage_creator import TreeViewApp
from docx import Document
from docx.shared import Inches, Cm
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.oxml import OxmlElement
import styles.tree_style as tree_style
import ast
from controllers.schema_manager import get_instances
from controllers.tablemodel import AttackTree, TechnicalAttackTree, Threats, TechnicalTreeHome
from Attack_Paths.Technical_Attack_Tree.controllers.database_to_tat import build_ta_tree_json


def flatten_node_tree(node, base_id):
    flat_nodes = []
    counter = {"index": 0}

    def _walk(n, parent_id):
        node_idx = counter["index"]
        node_id = f"{base_id}_node_{node_idx}"
        counter["index"] += 1

        # Base node structure
        flat_node = {
            "node_id": node_id,
            "parent_id": parent_id,
            "node_type": n.get("node_type"),
            "node_label": n.get("node_label"),
            "node_Text": n.get("node_Text"),
            "af_value": n.get("af_value", ''),
            "af_level": n.get("af_level", ''),
            "gate": n.get("gate", ''),
            "values": n.get("values", [])
        }

        flat_nodes.append(flat_node)

        # Recurse into children
        for child in n.get("childrens", []):
            _walk(child, node_id)

    _walk(node, parent_id=None)
    return flat_nodes

def Update_TechnicalAttackTree_Dictionary(document):
    # TAT_rows = DB.execute_db("""SELECT id, name FROM technical_tree_home""")
    TAT_rows = []
    tat_data = get_instances(TechnicalTreeHome, {'is_deleted':False})
    if tat_data:
        for instance in tat_data:
            TAT_rows.append(tuple([instance.id, instance.name]))
    print(TAT_rows)
    TAT_id_list = set()
    TAT_map = {}
    if TAT_rows: 
        for (TAT_id, TAT_name) in TAT_rows: 
            TAT_id_list.add(TAT_id)
            TAT_map[TAT_id] = TAT_name
    # document = Document()
    for TAT_id in TAT_id_list:
        # TAT_rows = DB.execute_db(f"""SELECT Node_ID, Parent_ID, Node_Type, Text, Value, AF_Text, Gate_Type, "Values" FROM technical_tree WHERE Node_ID like '{TAT_id}_Node%'""")
        TAT_rows = []
        tree_nodes = get_instances(TechnicalAttackTree, {'tree_id':TAT_id, 'is_deleted':False})
        print(tree_nodes)
        ta_tree_nodes = []
        if tree_nodes:
            tat_json_tree = build_ta_tree_json(tree_nodes)
            print(tat_json_tree)
            tat_list_tree = flatten_node_tree(tat_json_tree, TAT_id)
            print("------------------------------------technical attack tree list--------------------------------")
            print(tat_list_tree)
            
            for node in tat_list_tree:
                node_data = [node['node_id'], node['parent_id'], node['node_type'], node['node_Text'], node['af_value'], node['af_level'], node['gate'], node['values']]
                ta_tree_nodes.append(tuple(node_data))
            print(ta_tree_nodes)
            TAT_rows.extend(ta_tree_nodes)
        # print(TAT_rows)
        if TAT_rows:
            attack_trees = Generate_tree_dictionary(TAT_id, TAT_rows) 
            print(attack_trees)
            generate_word_report(TAT_id, TAT_map[TAT_id], 'output1.docx', document)

def Generate_tree_dictionary(TAT_id, tree_rows):
    # Function to extract the number at the end of each node
    def extract_number(node):
        match = re.search(r"_(\d+)$", node)
        return int(match.group(1)) if match else float('inf')

    # Sorting node_data based on the numeric suffix in node_id (first column)
    sorted_node_data = sorted(tree_rows, key=lambda x: extract_number(x[0]))

    available_nodes = []
    for (node_id, parent_id, node_type, name, AF_Value, AF_Text, gate, values) in sorted_node_data:
        available_nodes.append(node_id)
    
    tree_dictionary = {}
    for (node_id, parent_id, node_type, name, AF_Value, AF_Text, gate, values) in sorted_node_data:
        if node_type != 'head' and parent_id not in available_nodes:
            return {}
        if node_type == 'head':
            tree_dictionary[node_id] = {'node_id': node_id,
                                        'parent_id': parent_id,
                                        'node_type': node_type,
                                        'name': name, 
                                        'AF_Value': AF_Value,
                                        'AF_Text': AF_Text,
                                        'gate': gate,
                                        'values': values,
                                        'children': []
                                       }
        elif parent_id in available_nodes and node_type in ['intermediate', 'leaf']:
            tree_dictionary[node_id] = {'node_id': node_id,
                                        'parent_id': parent_id,
                                        'node_type': node_type,
                                        'name': name, 
                                        'AF_Value': AF_Value,
                                        'AF_Text': AF_Text,
                                        'gate': gate,
                                        'values': values,
                                        'children': []
                                       }
            tree_dictionary[parent_id]['children'].append(node_id)

    return tree_dictionary

def generate_word_report(TAT_id, TAT_name, output_path, Document):
    # tree_rows = DB.execute_db(f"""SELECT Node_ID, Parent_ID, Node_Type, Text, Value, AF_Text, Gate_Type, "Values" FROM technical_tree WHERE Node_ID like '{TAT_id}_Node%'""")
    tree_rows = []
    tree_nodes = get_instances(TechnicalAttackTree, {'tree_id':TAT_id, 'is_deleted':False})
    print(tree_nodes)
    if not tree_nodes:
        print(f"No data found for TAT ID: {TAT_id}")
        return
    ta_tree_nodes = []
    if tree_nodes:
        tat_json_tree = build_ta_tree_json(tree_nodes)
        print(tat_json_tree)
        tat_list_tree = flatten_node_tree(tat_json_tree, TAT_id)
        print("------------------------------------technical attack tree list--------------------------------")
        print(tat_list_tree)
        
        for node in tat_list_tree:
            node_data = [node['node_id'], node['parent_id'], node['node_type'], node['node_Text'], node['af_value'], node['af_level'], node['gate'], node['values']]
            ta_tree_nodes.append(tuple(node_data))
        print(ta_tree_nodes)
        tree_rows.extend(ta_tree_nodes)
    tree_dictionary = Generate_tree_dictionary(TAT_id, tree_rows)
    if not tree_dictionary:
        print(f"Failed to generate tree dictionary for TAT ID: {TAT_id}")
        return

    document = Document
    document.add_heading(f'Technical Attack Tree for TAT ID: {TAT_id}', level=1)

    def set_cell_border(cell, **kwargs):
        
        tc = cell._element
        tcPr = tc.get_or_add_tcPr()
        tcBorders = tcPr.first_child_found_in("w:tcBorders")
        if tcBorders is None:
            tcBorders = OxmlElement("w:tcBorders")
            tcPr.append(tcBorders)
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            edge_data = kwargs.get(edge)
            if edge_data:
                tag = "w:{}".format(edge)
                element = tcBorders.find(qn(tag))
                if element is None:
                    element = OxmlElement(tag)
                    tcBorders.append(element)
                for key in ["sz", "val", "color", "space"]:
                    if key in edge_data:
                        element.set(qn("w:{}".format(key)), str(edge_data[key]))


    def add_node_to_document(node, level=1, row_idx=3):
        parent_row_index = row_idx
        child_row_index = row_idx+1
        p_col_idx = level
        parent_column_index = p_col_idx
        child_column_index = parent_column_index + 2

        for i, child_id in enumerate(node['children']):
            child_node = tree_dictionary[child_id]
            # row_idx = parent_row_index +1 + child_row_index

            # Ensure enough rows exist
            while len(table.rows) <= child_row_index:
                table.add_row()
            
            # Ensure the column index does not exceed table limits
            num_columns = len(table.rows[0].cells)  # Get total columns in the first row
            column_idx = min(20, num_columns - 1)   # Prevent out-of-range errors

            # Ensure enough column exist
            while len(table.rows[0].cells) <= child_column_index:
                table.add_column()

            # Determine the background color based on node type
            node_color = 'FFFFFF'
            if child_node['node_type'] == 'intermediate':
                node_color = tree_style.intermediatenode_sidebar_color
            elif child_node['node_type'] == 'riskcontrol head':
                node_color = tree_style.controlnode_sidebar_color
            elif child_node['node_type'] == 'technical head':
                node_color = tree_style.technicalnode_sidebar_color
            elif child_node['node_type'] == 'leaf':
                node_color = tree_style.leafnode_sidebar_color


            if child_node['node_type'] in ['head', 'intermediate']:
                column_num = len(table.rows[0].cells)
                # Merge table cells for hierarchical structure
                a = table.cell(child_row_index, child_column_index)
                b = table.cell(child_row_index, column_num-1)
                a.merge(b)
                table.cell(child_row_index, child_column_index).text = f"{child_node['name']}"

                # Apply background color
                tcPr = table.cell(child_row_index, child_column_index)._element.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:fill'), node_color)
                tcPr.append(shd)

                gate_row_idx = child_row_index + 1  # Gate should appear below the node name
                
                while len(table.rows) <= gate_row_idx:
                    table.add_row()  # Ensure a row exists for the gate
                
                # Display the gate type (AND/OR)
                gate_text = 'AND' if child_node['gate'] == 'and_gate' else 'OR'
                table.cell(gate_row_idx, child_column_index).text = gate_text

                set_cell_border(table.cell(gate_row_idx, child_column_index), 
                                top={"sz": 12, "val": "single", "color": 'black'},
                                bottom={"sz": 12, "val": "single", "color": 'black'},
                                left={"sz": 12, "val": "single", "color": 'black'},
                                right={"sz": 12, "val": "single", "color": 'black'})
               
               
                set_cell_border(table.cell(gate_row_idx - 1,child_column_index), left={"sz": 12, "val": "single", "color": 'black'})
                set_cell_border(table.cell(gate_row_idx, child_column_index), left={"sz": 12, "val": "single", "color": 'black'})
                child_row_index = gate_row_idx 

            # If leaf node, add additional details
            elif child_node['node_type'] == 'leaf':
                cleaned_values = get_values_from_db(child_node["values"])  # Convert from DB
                formatted_values = format_values(cleaned_values)
                column_num = len(table.rows[0].cells)
                # Merge table cells for hierarchical structure
                a = table.cell(child_row_index, child_column_index)
                b = table.cell(child_row_index, column_num-1)
                a.merge(b)
                table.cell(child_row_index, child_column_index).text = f"{child_node['name']}\n{child_node['AF_Value']}             {formatted_values}              {child_node['AF_Text']}"

                # Apply background color
                tcPr = table.cell(child_row_index, child_column_index)._element.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:fill'), node_color)
                tcPr.append(shd)
            
            row_idx_num = 0
            row_idx_num = child_row_index if node['node_type'] == 'head' else child_row_index+1
            for index in range(parent_row_index, child_row_index):
                set_cell_border(
                    table.cell(index, p_col_idx),
                    left={"sz": 12, "val": "single", "color": 'black'}
                )

            # child_row_index = row_idx
            while len(table.rows) <= (child_row_index):
                table.add_row()

            for col_idx in range(p_col_idx, child_column_index):
                set_cell_border(
                    table.cell(child_row_index if node['node_type'] == 'leaf' else child_row_index-1 , col_idx),
                    bottom={"sz": 12, "val": "single", "color": 'black'}
                )

            # Recursively add this child's children
            next_row_idx = add_node_to_document(child_node, child_column_index, child_row_index-1 if node['node_type'] == 'leaf' else child_row_index)

            # Ensure the next sibling starts at the correct row
            child_row_index = next_row_idx

        return child_row_index  # Return updated row index so the next sibling starts correctly


    for node_id, node in tree_dictionary.items():
        if node['node_type'] == 'head':
            # document.add_heading(f'TAT ID: {TAT_id} - Name: {node["name"]}', level=level)
            
            table = document.add_table(rows=20, cols=21)
            for row in table.rows:
                row.height = Pt(0)  # Ensures minimal row height
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        paragraph.paragraph_format.space_after = Pt(0)
                        paragraph.paragraph_format.space_before = Pt(0)  # Ensure no extra space on top
                        paragraph.paragraph_format.line_spacing = Pt(1)  # Minimal spacing

            
            # Initially set all cell borders to white
            for row in table.rows:
                for cell in row.cells:
                    set_cell_border(cell, top={"sz": 12, "val": "single", "color": "FFFFFF"},
                                         left={"sz": 12, "val": "single", "color": "FFFFFF"},
                                         bottom={"sz": 12, "val": "single", "color": "FFFFFF"},
                                         right={"sz": 12, "val": "single", "color": "FFFFFF"})
            
            # Merge all cells in the first row
            a = table.cell(0, 0)
            b = table.cell(0, 20)
            a.merge(b)
            head_text = f'{TAT_id}: {TAT_name}\n'

            # Add initial AFR only if at least one field is not empty
            if node["AF_Value"] or node["AF_Text"]:
                head_text += f'AFR: {node["AF_Value"]}    {node["AF_Text"]}'

            table.cell(0, 0).text = head_text
            
            # Change background color to green for cell (1, 0)
            tcPr = table.cell(0, 0)._element.get_or_add_tcPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:fill'), tree_style.headnode_sidebar_color)  # Hex code for green
            tcPr.append(shd)
            
            table.cell(1, 0).text = 'AND' if node["gate"] == 'and_gate' else 'OR'
            table.cell(1, 0).width = Cm(2.0)

            set_cell_border(table.cell(1, 0), left={"sz": 12, "val": "single", "color": 'black'})
            set_cell_border(table.cell(1, 0), bottom={"sz": 12, "val": "single", "color": 'black'})
            set_cell_border(table.cell(1, 0), right={"sz": 12, "val": "single", "color": 'black'})
            set_cell_border(table.cell(1, 0), top={"sz": 12, "val": "single", "color": 'black'})
            
            add_node_to_document(node, row_idx=2, level=0)
            # add_node_to_document(document, node, tree_dictionary)


    # document.save(output_path)
    print(f"Word document generated at {output_path}")

def get_values_from_db(raw_value):
    try:
        # Convert string list (e.g., "['0', '3', '7', '1', '4']") to a real list
        value_list = ast.literal_eval(raw_value)  
        if isinstance(value_list, list):
            return [int(v) for v in value_list]  # Convert elements to integers
    except (ValueError, SyntaxError):
        return raw_value     

def format_values(values):
    if isinstance(values, list) and len(values) == 5:
        return f"T={values[0]} Ex={values[1]} K={values[2]} A={values[3]} Eq={values[4]}"
    return str(values)  # Default fallback

