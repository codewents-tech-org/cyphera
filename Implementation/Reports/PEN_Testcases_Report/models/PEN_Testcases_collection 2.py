
import controllers.DatabaseCreator as DB
import re
from controllers.schema_manager import get_instances
from controllers.tablemodel import AttackTree, RiskControlTree, Threats, SecurityControls

from Target_Of_Evaluation.Scope.Scope_MindMap.tree_id_converter import rename_attacktree_node_ids_flat


Penetration_Severity_Levels = {

	"High":
    {
        "Severity_Level" : "Critical",
        "Description" : "Vulnerabilities that pose an immediate and significant risk, potentially leading to full system compromise, data breach, or severe financial and reputational damage.",
        "Action" : "Address immediately."
    },
    "Medium":
    {
        "Severity_Level" : "High",
        "Description" : "Vulnerabilities that could lead to significant damage or unauthorized access but may require additional steps or specific conditions to exploit.",
        "Action" : "Fix as soon as possible."
    },
    "Low":
    {
        "Severity_Level" : "Medium",
        "Description" : "Vulnerabilities that may allow unauthorized actions or impact system integrity but are harder to exploit or have limited scope of impact.",
        "Action" : "Address in the next development cycle."
    },
    "Very low":
    {
        "Severity_Level" : "Low",
        "Description" : "Minor issues that have a limited impact on security and may require a combination of other vulnerabilities to cause harm.",
        "Action" : "Address as part of routine updates."
    }
}


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
            "af_level": n.get("af_level"),
            "rf_level": n.get("rf_level")
        }

        flat_nodes.append(flat_node)

        # Recurse into children
        for child in n.get("childrens", []):
            _walk(child, node_id)

    _walk(node, parent_id=None)
    return flat_nodes

def Update_PEN_Testcases():
    # Fetch data from the attack_tree table
    
    # threats = DB.execute_db("SELECT threat_id, security_properties FROM threat")
    print("-----------------------------------threats--------------------------------")
    threats = []
    threat_data = get_instances(Threats, {'is_deleted':'False'})
    if threat_data:
        for instance in threat_data:
            threats.append(tuple([instance.threat_id, instance.security_properties]))
    print(threats)
    
    # security_controls = DB.execute_db("SELECT id, properties FROM security_controls")
    print("-----------------------------------security controls--------------------------------")
    security_controls = []
    sc_data = get_instances(SecurityControls, {'is_deleted':'False'})
    if sc_data:
        for instance in sc_data:
            security_controls.append(tuple([instance.scc_id, instance.security_goal_id]))
    print(security_controls)

    # nodes = DB.execute_db("SELECT Node_ID, Text, AF_Text, RF_Text, Node_Type FROM attack_tree")
    print("-----------------------------------attack tree--------------------------------")
    nodes = []
    for threat_id, security_property in threats: 
        print(threat_id)
        tree_nodes = get_instances(AttackTree, {'tree_id':threat_id, 'is_deleted':False})
        print(tree_nodes)
        attack_tree_nodes = []
        if tree_nodes:
            at_json_tree = build_at_tree_json(tree_nodes)
            print(at_json_tree)
            at_list_tree = flatten_node_tree(at_json_tree, threat_id)
            print("------------------------------------attack tree list--------------------------------")
            print(at_list_tree)
            
            for node in at_list_tree:
                node_data = [node['node_id'], node['node_Text'], node['af_level'], node['rf_level'], node['node_type']]
                attack_tree_nodes.append(tuple(node_data))
            print(attack_tree_nodes)
        nodes.extend(attack_tree_nodes)
    print("------------------------------------final attack tree--------------------------------")
    print(nodes)

    def group_nodes_by_threat_id(nodes):
        grouped_nodes = {}
        for node_id, text, af_value, rf_value, node_type in nodes:
            match = re.search(r"(TH-\d+)", node_id)
            if match:
                threat_id = match.group(1)
                if threat_id not in grouped_nodes:
                    grouped_nodes[threat_id] = []
                grouped_nodes[threat_id].append((node_id, text, af_value, rf_value, node_type))
        return grouped_nodes

    grouped_nodes = group_nodes_by_threat_id(nodes)

    # Severity levels mapping
    penetration_severity_levels = {"High": "Critical", "Medium": "High", "Low": "Medium", "Very Low": "Low"}
    keywords = ["Extraction", "Manipulation", "Block", "Forged", "Get Unauthorized Access", 
                "Repudiated", "Invalidated", "Replayed"]
    keywords_suffix = [
        "Extraction of", "Manipulation of", "Blocking", "Forgery of", "Invalidation of",
        "Replay of", "Unauthorized access to", "Repudiation of"
    ]

    security_property_mapping = {
        "Confidentiality": "Unauthorized disclosure",
        "Integrity": "Unauthorized Modification",
        "Availability": "Service Disruption",
        "Authenticity": "Unaunthenticated Use",
        "Authorization": "Unauthorized Access",
        "Non - Repudiation": "Untraceable Actions",
        "Correctness": "Invalid Operations",
        "Freshness": "Reused Information"
    }
    
    security_property_mapping2 = {
        "Confidentiality": "Information Disclosure",
        "Integrity": "Tampering",
        "Availability": "Denial of Service",
        "Authenticity": "Spoofing",
        "Authorization": "Elevation of Privilege",
        "Non - Repudiation": "Repudiation",
        "Correctness": "Invalid Outputs",
        "Freshness": "Duplicate Requests"
    }

    security_property_mapping3 ={
        "Confidentiality": "Extracted",
        "Integrity": "Manipulated",
        "Availability": "Blocked",
        "Authenticity": "Forged",
        "Authorization": "Get Unauthorized Access",
        "Non - Repudiation": "Repudiated",
        "Correctness": "Invalidated",
        "Freshness": "Replayed"
    }

    security_property_mapping4 ={
        "Confidentiality": "Exposed",
        "Integrity": "Altered",
        "Availability": "Unavailable",
        "Authenticity": "Impersonated",
        "Authorization": "Exploited",
        "Non - Repudiation": "Denied",
        "Correctness": "Invalid",
        "Freshness": "Duplicated"
    }

    security_property_mapping5 ={
        "Confidentiality": "Unauthorized disclosure",
        "Integrity": "Unauthorized Modification",
        "Availability": "Service Disruption",
        "Authenticity": "Unaunthenticated Use",
        "Authorization": "Unauthorized Access",
        "Non - Repudiation": "Untraceable Actions",
        "Correctness": "Invalid Operations",
        "Freshness": "Reused Information"
    }

    # Initialize counters and dictionaries
    testcase_number = 1
    penetration_testcases = {}
    penetration_all_testcases = {}

    def extract_suffix(text, keywords_suffix):
        for keyword in keywords_suffix:
            if keyword.lower() in text.lower():
                # Find the position of the keyword and extract the suffix
                keyword_pos = text.lower().find(keyword.lower())
                suffix_start = keyword_pos + len(keyword)
                suffix = text[suffix_start:].strip()  # Get everything after the keyword
                return suffix
        return "object"  # Default if no keywords match

    for threat_id, threat_nodes in grouped_nodes.items():
        print(f"Processing threat_id: {threat_id}")

        # Initialize Test Scenarios for the current threat_id
        # threat_testcases = {}

    # for threat_id, threat_nodes in grouped_nodes.items():
        # Filter nodes by type
        head_nodes = [n for n in threat_nodes if n[4] == "head"]
        riskcontrol_head_nodes = [n for n in threat_nodes if n[4] == "riskcontrol head"]
        riskcontrol_leaf_nodes = [n for n in threat_nodes if n[4] in ["riskcontrol leaf", "riskcontrol technical leaf"]]
        leaf_nodes = [n for n in threat_nodes if n[4] in ["leaf", "technical leaf"]]

        print("---------", head_nodes)
    # Process head nodes (first level)
        for node_id, text, af_value, rf_value, node_type in head_nodes:
            severity = penetration_severity_levels.get(af_value, "")
            suffix = extract_suffix(text, keywords_suffix)
            # Extract matching keywords for the description
            vulnerabilities = [kw for kw in keywords if kw.lower() in text.lower()]
            vulnerabilities_str = ", ".join(vulnerabilities) if vulnerabilities else "general vulnerabilities"
            testcase_id = f"TS_{testcase_number}"
            testcase_number += 1
            penetration_testcases[testcase_id] = {}
            penetration_testcases[testcase_id]["Object Type"] = "Threat Test Scenario"
            penetration_testcases[testcase_id]["Test Scenario Name"] =  text
            penetration_testcases[testcase_id]["Test Scenario Description"] = f"The {suffix} will be vulnerable to attacks due to {vulnerabilities_str}"
            penetration_testcases[testcase_id]["Test Goal"] = " "
                # "Severity": penetration_severity_levels.get(af_value, "Unknown"),
            penetration_testcases[testcase_id]["Severity"] = severity
            penetration_testcases[testcase_id]["Vulnerability Description"] = " "
            penetration_testcases[testcase_id]["Business Impacts"] = " "
            # penetration_testcases[testcase_id]["Recommendations"] =" "
        
            penetration_all_testcases[testcase_id] = penetration_testcases[testcase_id]
            

            # Process riskcontrol head nodes (sub-level)
            for c_node_id, c_text, c_af_value, c_rf_value, c_node_type in riskcontrol_head_nodes:
                # if c_node_id.startswith(node_id):  # Check if it's under the current head
                    clean_c_text = c_text.replace("Risk_Control -", "").strip()
                    match = re.search(r"Ctrl-\d+\s*(.*)", clean_c_text)  # This captures everything after "Ctrl-<number>"
        
                    if match:
                        clean_c_suffix = match.group(1).strip()  # This gives us everything after "Ctrl-<number>"
                    else:
                        clean_c_suffix = " "  # Default value if no match is found
                    parent_suffix = suffix

                    # Extract the "Ctrl-" and number part
                    ctrl_match = re.search(r"(Ctrl-\d+)", clean_c_text)  # This captures "Ctrl-" followed by a number

                    if ctrl_match:
                        ctrl_number = ctrl_match.group(1)  # This gives us the "Ctrl-" followed by the number (e.g., "Ctrl-1")
                    else:
                        ctrl_number = "" 

                    # # Extract all conditions from security_controls
                    # conditions = []
                    # for control in security_controls:
                    #     properties = control[0]
                    #     if properties:
                    #         # Split the properties by comma
                    #         individual_properties = properties.split(",")
                    #         # Process each property to extract the condition
                    #         for prop in individual_properties:
                    #             if "::" in prop:
                    #                 condition = prop.split("::")[1].strip()  # Get the part after '::'
                    #                 conditions.append(condition)  # Add to the list of conditions

                    # # Combine all conditions into a single string, if needed
                    # combined_conditions = ", ".join(conditions) if conditions else "No conditions found"

                    # Extract conditions from security_controls based on ctrl_number
                    conditions = []
                    for control in security_controls:
                        # Assuming control[0] contains the id and control[1] contains properties
                        control_id = control[0]  # The 'id' in the security_controls table
                        if control_id == ctrl_number:  # Only take the data where the id matches the ctrl_number
                            properties = control[1]  # Get the properties from the matching row
                            if properties:
                                individual_properties = properties.split(",")
                                for prop in individual_properties:
                                    if "::" in prop:
                                        condition = prop.split("::")[1].strip()  # Get the part after '::'
                                        conditions.append(condition)  # Add to the list of conditions

                    combined_conditions = ", ".join(conditions) if conditions else ""

                    sub_testcase_id = f"TS_{testcase_number}"
                    testcase_number += 1
                    penetration_testcases[testcase_id][sub_testcase_id] = {}
                    penetration_testcases[testcase_id][sub_testcase_id] = {}
                    penetration_testcases[testcase_id][sub_testcase_id]["Object Type"]= "Control Test Scenario"
                    penetration_testcases[testcase_id][sub_testcase_id]["Test Scenario Name"] =  clean_c_text
                    penetration_testcases[testcase_id][sub_testcase_id]["Test Scenario Description"] = f"The Test Scenario checks if the {clean_c_suffix} meets the level of security in {parent_suffix}."
                    penetration_testcases[testcase_id][sub_testcase_id]["Test Goal"] = f"The Test Scenario should ensure that the condition {combined_conditions} is satisfied"
                        # "Severity": penetration_severity_levels.get(af_value, "Unknown"),
                    penetration_testcases[testcase_id][sub_testcase_id]["Severity"] = "Critical"
                    penetration_testcases[testcase_id][sub_testcase_id]["Vulnerability Description"] = " "
                    penetration_testcases[testcase_id][sub_testcase_id]["Business Impacts"] = " "
                    # penetration_testcases[testcase_id][sub_testcase_id]["Recommendations"] = " "
                    
                    penetration_all_testcases[sub_testcase_id] = penetration_testcases[testcase_id][sub_testcase_id]

                    # Process riskcontrol leaf nodes (sub-sub level)
                    for cl_node_id, cl_text, cl_af_value, cl_rf_value, cl_node_type in riskcontrol_leaf_nodes:
                        # if cl_node_id.startswith(c_node_id):  # Check if it's under the current riskcontrol head
                            severity2 = penetration_severity_levels.get(cl_rf_value, "")
                            match1 = re.search(r"Lf-\d+\s*(.*)", cl_text)  # This captures everything after "Ctrl-<number>"
        
                            if match1:
                                clean_cl_suffix = match1.group(1).strip()  # This gives us everything after "Ctrl-<number>"
                            else:
                                clean_cl_suffix = " "  # Default value if no match is found

                            sub_sub_testcase_id = f"TS_{testcase_number}"
                            testcase_number += 1
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id] = {}
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id] = {}
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id] = {}
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id]["Object Type"] = "Leaf Sub Test Scenario"
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id]["Test Scenario Name"] = cl_text
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id]["Test Scenario Description"] = f"This Test Scenario checks if {clean_cl_suffix} is protected from any malicious action, Otherwise attacker can misuse the service"
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id]["Test Goal"] = " "
                                # "Severity": penetration_severity_levels.get(af_value, "Unknown"),
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id]["Severity"] = severity2
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id]["Vulnerability Description"] = f"The {clean_c_suffix} will be vulnerable due to exploit in the {clean_cl_suffix}"
                            penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id]["Business Impacts"] = f"If the system is attacked , the system features will be compromised and lead to unintended activities"
                            # penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id]["Recommendations"] = f"It is recommended to protect {clean_cl_suffix} from any malicious action"
                            
                            penetration_all_testcases[sub_sub_testcase_id] = penetration_testcases[testcase_id][sub_testcase_id][sub_sub_testcase_id]


            def get_security_property_from_threat_id(threat_id):
                #Fetch the security property for a given threat_id.
                for threat in threats:
                    if threat[0] == threat_id:
                        return threat[1]
                return None  # Return None if no matching threat_id is found

            # Process leaf nodes (sub-level under the head)
            for l_node_id, l_text, l_af_value, l_rf_value, l_node_type in leaf_nodes:
                    # severity3 = penetration_severity_levels.get(l_rf_value, "Unknown")
                    match2 = re.search(r"(TH-\d+)", l_node_id)
                    if match2:
                        threat_id = match2.group(0).strip()  # Extract the threat_id
                        security_property = get_security_property_from_threat_id(threat_id)
                        security_description = security_property_mapping.get(security_property, "Unknown Security Property")
                        security_description2 = security_property_mapping2.get(security_property, "Unknown Security Property")
                        security_description3 = security_property_mapping3.get(security_property, "Unknown Security Property")
                        security_description4 = security_property_mapping4.get(security_property, "Unknown Security Property")
                        security_description5 = security_property_mapping5.get(security_property, "Unknown Security Property")
                        
                        if security_property:
                            # Extract first security property, if available
                            properties = security_property.split(",")
                            security_property = properties[0].strip() if properties else "Unknown Security Property"
                        else:
                            security_property = "Unknown Security Property"
                        # Print the fetched security property
                        print(f"Threat ID: {threat_id}")
                        print(f"Security Properties: {security_property}")

                    else:
                        security_property = "Unknown Threat ID"
                        print(f"Threat ID: Unknown")
                        print(f"Security Properties: {security_property}")

                    match3 = re.search(r"Lf-\d+\s*(.*)", l_text)  # This captures everything after "Ctrl-<number>"
        
                    if match3:
                        clean_l_suffix = match3.group(1).strip()  # This gives us everything after "Ctrl-<number>"
                    else:
                        clean_l_suffix = " "    
                # if l_node_id.startswith(node_id):  # Check if it's under the current head
                    severity3 = penetration_severity_levels.get(l_rf_value, "")
                    sub_testcase_id = f"TS_{testcase_number}"
                    testcase_number += 1
                    penetration_testcases[testcase_id][sub_testcase_id] = {}
                    penetration_testcases[testcase_id][sub_testcase_id]["Object Type"] = "Leaf Test Scenario"
                    penetration_testcases[testcase_id][sub_testcase_id]["Test Scenario Name"] = l_text
                    penetration_testcases[testcase_id][sub_testcase_id]["Test Scenario Description"] = f"This Test Scenario checks if the {clean_l_suffix} is protected from {security_description}, Otherwise attacker can create a {security_description2} using the service  "
                    penetration_testcases[testcase_id][sub_testcase_id]["Test Goal"] = " "
                                # "Severity": penetration_severity_levels.get(af_value, "Unknown"),
                    penetration_testcases[testcase_id][sub_testcase_id]["Severity"] = severity3
                    penetration_testcases[testcase_id][sub_testcase_id]["Vulnerability Description"] = f"The {suffix} will be {security_description3} and vulnerable to attacks due to {clean_l_suffix}"
                    penetration_testcases[testcase_id][sub_testcase_id]["Business Impacts"] = f"If the system is attacked, the system features will be {security_description4}"
                    # penetration_testcases[testcase_id][sub_testcase_id]["Recommendations"] = f"It is recommended to protect {clean_l_suffix} from any {security_description5}"
                    
                    penetration_all_testcases[sub_testcase_id] = penetration_testcases[testcase_id][sub_testcase_id]

    print("----------",penetration_all_testcases)
    return penetration_testcases, penetration_all_testcases
