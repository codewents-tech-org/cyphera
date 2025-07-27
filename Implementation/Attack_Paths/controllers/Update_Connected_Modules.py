
import sys
from controllers.database_tables.analysis_tables import Threats
from controllers.database_tables.risk_assessment_tables import RiskData
from controllers.database_tables.security_measurment_tables import SecurityControls
from  controllers.database_tables.attack_paths_tables import AttackTree, AttackTreeHome, NodeType, RiskControlTree, RiskControlTreeHome, TechnicalTreeHome
from  controllers.schema_manager import get_first_instance, get_instances, get_instances_like, update_instance
import controllers.DatabaseCreator as DB
import models.helper as helper

import logging
logger = logging.getLogger(__name__)
def update_threat_table():
    # 1. Get all Threat records
    threats = get_instances(Threats)
    for threat in threats:
        threat_id = threat.threat_id

        # 2. Find AttackTree HEAD node for this threat
        attacktree_head = get_first_instance(
            AttackTree,
            filters={
                "node_id": f"{threat_id}_node_0",
                "node_type": NodeType.HEAD
            }
        )

        # 3. Get AF and RF values, or set blank if not found
        if attacktree_head:
            initial_afr = attacktree_head.af_value
            resid_afr = attacktree_head.rf_value
        else:
            initial_afr = ""
            resid_afr = ""

        # 4. Update threat table with these values
        update_instance(
            Threats,
            {"threat_id": threat_id},
            {
                "InitialAFR": initial_afr,
                "ResidAFR": resid_afr
            }
        )


def update_attacktree_table():
    # Get all attack_tree_home records
    attack_tree_homes = get_instances(AttackTreeHome)
    for home in attack_tree_homes:
        threat_id = home.id

        # Find AttackTree node where node_id = '{threat_id}_node_0' and node_type == NodeType.HEAD
        attacktree_head = get_first_instance(
            AttackTree,
            filters={
                "node_id": f"{threat_id}_node_0",
                "node_type": NodeType.HEAD
            }
        )

        update_data = {
            "initial_afr": attacktree_head.af_value if attacktree_head else "",
            "resid_afr": attacktree_head.rf_value if attacktree_head else ""
        }

        update_instance(
            AttackTreeHome,
            {"id": threat_id},
            update_data
        )


def update_riskcontroltree_table():
    # Step 1: Get all controls and build control_map: {scc_id: name}
    controls = get_instances(SecurityControls)
    control_map = {control.scc_id: control.name for control in controls}
    control_list = list(control_map.keys())
    
    # Step 2: For each control, build the mitigates string based on matching AttackTree node_id
    for control_id in control_list:
        # Your new text-matching logic is node_id startswith control_id (no "Text" column anymore)
        related_attacktree_nodes = [
            node for node in get_instances(AttackTree)
            if node.node_id.startswith(f"{control_id}_node")
        ]

        # Build mitigates string (unique prefix up to first underscore)
        mitigates_set = set()
        for node in related_attacktree_nodes:
            node_id_prefix = node.node_id.strip().split('_')[0] if '_' in node.node_id else node.node_id.strip()
            mitigates_set.add(node_id_prefix)
        mitigates_str = ', '.join(sorted(mitigates_set))

        # Update RiskControlTreeHome.mitigates for this control
        update_instance(
            RiskControlTreeHome,
            {"id": control_id},
            {"mitigates": mitigates_str}
        )

def update_technicaltree_table():
    # Step 1: Build technical_map: {id: name}
    technical_rows = get_instances(TechnicalTreeHome)
    technical_map = {row.id: row.name if row.name else row.id for row in technical_rows}
    technical_list = list(technical_map.keys())

    for technical_id in technical_list:
        text = f"{technical_id} {technical_map[technical_id]}"

        # (A) Find AttackTree nodes whose node_id starts with the technical id
        attacktree_nodes = [
            node for node in get_instances(AttackTree)
            if node.node_id.startswith(f"{technical_id}_node")
        ]
        attacktree_technical_map = set()
        for node in attacktree_nodes:
            node_id_prefix = node.node_id.strip().split('_')[0] if '_' in node.node_id else node.node_id.strip()
            attacktree_technical_map.add(node_id_prefix)
        attacktree_technical_map_str = ', '.join(sorted(attacktree_technical_map))

        # (B) Find RiskControlTree nodes whose node_id starts with the technical id
        riskcontroltree_nodes = [
            node for node in get_instances(RiskControlTree)
            if node.node_id.startswith(f"{technical_id}_node")
        ]
        riskcontroltree_technical_map = set()
        for node in riskcontroltree_nodes:
            node_id_prefix = node.node_id.strip().split('_')[0] if '_' in node.node_id else node.node_id.strip()
            riskcontroltree_technical_map.add(node_id_prefix)
        riskcontroltree_technical_map_str = ', '.join(sorted(riskcontroltree_technical_map))

        # (C) Update TechnicalTreeHome.used_in_threat and used_in_riskcontrol
        update_instance(
            TechnicalTreeHome,
            {"id": technical_id},
            {
                "used_in_threat": attacktree_technical_map_str,
                "used_in_riskcontrol": riskcontroltree_technical_map_str
            }
        )


def update_risktreatment_table():
    # 1. Fetch all AttackTree nodes with node_type = "riskcontrol head"
    attacktree_nodes = get_instances(
        AttackTree,
        filters={"node_type": NodeType.RCT_HEAD}
    )

    # 2. Build control <-> threat mappings
    attacktree_linked_controls_CT = {}  # Control to Threat(s)
    attacktree_linked_controls_RT = {}  # Threat to Control(s)

    for node in attacktree_nodes:
        node_id = node.node_id               # e.g. Ctrl-3_node_0
        threat = node_id.split('_')[0]       # e.g. Ctrl-3
        control = threat                     # in your old code, control came from Text, now node_id prefix

        # CT: control → threat(s)
        if control not in attacktree_linked_controls_CT:
            attacktree_linked_controls_CT[control] = threat
        else:
            attacktree_linked_controls_CT[control] += f", {threat}"

        # RT: threat → control(s)
        if threat not in attacktree_linked_controls_RT:
            attacktree_linked_controls_RT[threat] = control
        else:
            attacktree_linked_controls_RT[threat] += f", {control}"

    # 3. Update all RiskData rows
    risks = get_instances(RiskData)
    for risk in risks:
        # Map: risk.threat_id (in new model) == threat_id ('TH-21', etc)
        threat_id_key = risk.threat_id
        mitigated_by = attacktree_linked_controls_RT.get(threat_id_key, "")

        # Get AFR levels from AttackTreeHome
        afr_home = get_first_instance(AttackTreeHome, filters={"id": threat_id_key})
        if afr_home:
            init_afr_level = afr_home.initial_afr
            resid_afr_level = afr_home.resid_afr

            init_afr_value = (
                helper.risk_map.get((risk.impact, init_afr_level))
                if (hasattr(helper, "risk_map") and hasattr(helper, "AFR_Levels") and hasattr(helper, "DS_impact_menu")
                    and init_afr_level in helper.AFR_Levels and risk.impact in helper.DS_impact_menu)
                else ""
            )
            resid_afr_value = (
                helper.risk_map.get((risk.impact, resid_afr_level))
                if (hasattr(helper, "risk_map") and hasattr(helper, "AFR_Levels") and hasattr(helper, "DS_impact_menu")
                    and resid_afr_level in helper.AFR_Levels and risk.impact in helper.DS_impact_menu)
                else ""
            )
        else:
            init_afr_level = ""
            resid_afr_level = ""
            init_afr_value = ""
            resid_afr_value = ""

        update_instance(
            RiskData,
            {"uuid": risk.uuid},  # or {"rd_id": risk.rd_id} if that's your unique app-level ID
            {
                "init_afr_level": init_afr_level,
                "init_afr_value": init_afr_value,
                "resid_afr_level": resid_afr_level,
                "resid_afr_value": resid_afr_value,
                "mitigated_by": mitigated_by,
            }
        )