
from PyQt5.QtWidgets import QMessageBox
#from DatabaseCreator import execute_db
import models.helper as helper

import controllers.DatabaseCreator as DB
#from Attack_Paths.Attack_Tree.controllers.Attack_RiskControlTree_Update import Attack_RiskControlTree_Update 
from PyQt5.QtWidgets import QMessageBox
#from DatabaseCreator import execute_db
import models.helper as helper

import controllers.DatabaseCreator as DB
#from Attack_Paths.Attack_Tree.controllers.Attack_RiskControlTree_Update import Attack_RiskControlTree_Update
from Attack_Paths.controllers.Update_Connected_Modules import Update_Threat_Table, Update_TechnicalTree_Table, Update_RiskControlTree_Table, Update_AttackTree_Table, Update_RiskTreatment_Table
import re
import logging
from controllers.schema_manager import (
    get_instances, create_instance, update_instance, delete_instance, get_max_numeric_suffix
)
#from controllers.tablemodel import TOEConfigurationInManagementSummary,AssumptionsInManagementSummary
#from controllers.tablemodel import SecurityControls as SCModel, MS_SecurityControl
import re
from controllers.tablemodel import SecurityGoals, SecurityControls

from controllers.database_tables.target_of_evaluation_tables import Assumptions,Misusecases,TOEConfiguration
from controllers.database_tables.analysis_tables import Assets,DamageScenarios,Threats,ThreatScenarios
from controllers.database_tables.security_measurment_tables import SecurityClaims, SecurityGoals,SecurityControls
from controllers.database_tables.catalog_tables import ThreatCatalog
from controllers.database_tables.attack_paths_tables import RiskControlTreeHome,RiskControlTree,AttackTreeHome,AttackTree
from controllers.database_tables.risk_assessment_tables import RiskData

logger = logging.getLogger(__name__)

def generate_name(asset_id, property):
    try:
        logger.info(f"Generating name for asset_id: {asset_id}, property: {property}")

        # ✅ Step 1: Use schema_manager to fetch the asset by ID
        assets = get_instances(Assets, {'asset_id': asset_id})

        if not assets:
            return f"Unknown asset for ID {asset_id}"

        asset = assets[0]
        asset_name = asset.name.strip() if asset.name else f"Unnamed asset for ID {asset_id}"

        # ✅ Step 2: Generate threat name based on the security property
        mapping = {
            "Availability":      f"Blocking {asset_name}",
            "Confidentiality":   f"Extraction of {asset_name}",
            "Integrity":         f"Manipulation of {asset_name}",
            "Authenticity":      f"Forgery of {asset_name}",
            "Correctness":       f"Invalidation of {asset_name}",
            "Freshness":         f"Replay of {asset_name}",
            "Authorization":     f"Unauthorized access to {asset_name}",
            "Non-repudiation":   f"Repudiation of {asset_name}"
        }

        return mapping.get(property, f"Unknown impact on {asset_name}")

    except Exception as e:
        logger.exception("Error generating threat name")
        return f"Error generating name: {e}"


def sync_threats_with_assets():
    logger.info("Updated Threats from Assets")

    # ✅ Fetch assets
    asset_rows = get_instances(Assets, {})
    existing_assets_ids = [a.asset_id for a in asset_rows]
    existing_assets_datas = {}
    asset_name_map = {}

    for asset in asset_rows:
        sp_list = [s.strip() for s in (asset.security_properties or "").split(',') if s.strip()]
        if sp_list:
            existing_assets_datas[asset.asset_id] = sp_list
        asset_name_map[asset.asset_id] = asset.name

    # ✅ Fetch threats
    threat_rows = get_instances(Threats, {})
    existing_threat_maps = {
        t.threat_id: t for t in threat_rows
    }

    # ✅ Identify outdated or orphaned threats
    remove_threat_list = []
    for threat_id, threat in existing_threat_maps.items():
        asset_id = threat.asset_id
        sp_in_threat = threat.security_properties
        threat_name = threat.name

        match = re.match(r"^\[(\d+(\.\d+)?)\]", threat_name or "")
        if match:
            continue  # Skip those with [X] pattern

        if asset_id not in existing_assets_ids or sp_in_threat not in existing_assets_datas.get(asset_id, []):
            remove_threat_list.append(threat_id)
        else:
            expected_name = generate_name(asset_id, sp_in_threat)
            if threat.name != expected_name:
                update_instance(Threats, {'threat_id': threat_id}, {'name': expected_name})

    # ✅ Filter out threats present in ThreatCatalog
    catalog_entries = get_instances(ThreatCatalog, {})
    catalog_threat_names = {entry.Threat for entry in catalog_entries if entry.Threat}
    final_remove_list = [
        tid for tid in remove_threat_list
        if existing_threat_maps[tid].name not in catalog_threat_names
    ]

    # ✅ Move to trash + delete from Threats
    for threat_id in final_remove_list:
        # insert into `threat_trash` (if that model/table is defined — otherwise, log)
        logger.info(f"Soft-deleting threat {threat_id}")
        delete_instance(Threats, {'threat_id': threat_id})

    # ✅ Insert new threats based on Assets
    for asset_id, sp_list in existing_assets_datas.items():
        for sp in sp_list:
            exists = any(
                t.asset_id == asset_id and t.security_properties == sp
                for t in existing_threat_maps.values()
            )
            if not exists:
                new_threat_id = threat_generate_id()
                new_name = generate_name(asset_id, sp)

                new_threat = Threats(
                    threat_id=new_threat_id,
                    name=new_name,
                    ds_id="",
                    toe_configuration_id="",
                    misuse_cases_id="",
                    initia_afr="",
                    resid_afr="",
                    asset_id=asset_id,
                    security_properties=sp,
                    reasoning="",
                    comments="",
                    created_by="system",
                    updated_by="system",
                    is_deleted=False
                )
                create_instance(new_threat)

    # ✅ Resync dependent structures
    sync_attack_tree_with_threats()
    update_threatscenario_from_threat()


def update_threatscenario_from_threat():
    logger.info("Updated threat scenarios from Assets")

    # ✅ Step 1: Fetch damage scenarios
    damage_scenarios = get_instances(DamageScenarios, {})
    damage_scenario_map = {ds.ds_id: ds.name for ds in damage_scenarios}

    # ✅ Step 2: Fetch threats
    threats = get_instances(Threats, {})
    threat_damage_map = {}     # {threat_id: [damage_scenarios]}
    threat_name_map = {}       # {threat_id: name}
    threat_toe_config_map = {} # {threat_id: toe_configuration_id}

    for t in threats:
        ds_ids = [ds.strip() for ds in (t.ds_id or "").split(',') if ds.strip()]
        threat_damage_map[t.threat_id] = ds_ids
        threat_name_map[t.threat_id] = t.name
        threat_toe_config_map[t.threat_id] = t.toe_configuration_id or ""

    # ✅ Step 3: Fetch existing ThreatScenarios
    ts_rows = get_instances(ThreatScenarios, {})
    existing_ts_map = {}   # {ts_id: (threat_id, ds_id)}
    existing_threat_ds_map = {}

    for ts in ts_rows:
        ts_id = ts.ts_id
        threat_id = (ts.threat_id or "").strip()
        ds_id = (ts.ds_id or "").split("::")[0].strip() if ts.ds_id else ""
        toe_cfg = ts.toe_configuration_id or ""

        existing_ts_map[ts_id] = (threat_id, ds_id, toe_cfg)

        if threat_id not in existing_threat_ds_map:
            existing_threat_ds_map[threat_id] = []
        if ds_id and ds_id not in existing_threat_ds_map[threat_id]:
            existing_threat_ds_map[threat_id].append(ds_id)

    # ✅ Step 4: Identify and remove invalid TS entries
    for ts_id, (threat_id, ds_id, _) in existing_ts_map.items():
        if threat_id not in threat_damage_map or ds_id not in threat_damage_map[threat_id]:
            delete_instance(ThreatScenarios, {'ts_id': ts_id})
            logger.info(f"🗑️ Removed invalid TS: {ts_id}")

    # ✅ Step 5: Call the sync_threat_scenarios function to handle insertions and updates
    sync_threat_scenarios(
        threat_damage_map=threat_damage_map,
        threat_name_map=threat_name_map,
        threat_toe_config_map=threat_toe_config_map,
        damage_scenario_map=damage_scenario_map,
        existing_threat_ds_map=existing_threat_ds_map
    )


    # Function to generate a unique threat scenario ID
    def generate_unique_ts_id():
        try:
            # Get max suffix from both threat_scenarios and trash (optional if trash is modeled)
            max_suffix = get_max_numeric_suffix(ThreatScenarios, 'ts_id', prefix="TS")
            return f"TS-{max_suffix + 1}"
        except Exception as e:
            logger.exception("Error generating unique TS ID")
            return ""

    def sync_threat_scenarios(threat_damage_map, threat_name_map, threat_toe_config_map, damage_scenario_map, existing_threat_ds_map):
        # ✅ Step 1: Fetch existing ThreatScenarios for update or match
        existing_ts = get_instances(ThreatScenarios, {})
        existing_pairs = {
            (ts.threat_id, (ts.ds_id or '').split("::")[0]): ts
            for ts in existing_ts
            if ts.threat_id and ts.ds_id
        }

        for threat_id, damage_scenarios in threat_damage_map.items():
            threat_name = threat_name_map.get(threat_id, "")
            toe_cfg = threat_toe_config_map.get(threat_id, "")

            for damage_scenario in damage_scenarios:
                damage_scenario = damage_scenario.strip()
                ds_full = f"{damage_scenario}::{damage_scenario_map.get(damage_scenario, '')}"
                threat_display = f"{threat_id} - {threat_name}"

                key = (threat_id, damage_scenario)
                if key in existing_pairs:
                    # ✅ Update existing row
                    ts = existing_pairs[key]
                    update_instance(
                        ThreatScenarios,
                        {'ts_id': ts.ts_id},
                        {
                            'threat_id': threat_id,
                            'ds_id': ds_full,
                            'toe_configuration_id': toe_cfg,
                            'reasoning': ts.reasoning or '',
                            'comments': ts.comments or '',
                            'updated_by': 'system'
                        }
                    )
                    logger.info(f"🔁 Updated ThreatScenario: {ts.ts_id} for {threat_id} / {damage_scenario}")
                else:
                    # ✅ Create new TS row
                    new_ts = ThreatScenarios(
                        ts_id=generate_unique_ts_id(),
                        threat_id=threat_id,
                        ds_id=ds_full,
                        toe_configuration_id=toe_cfg,
                        reasoning='',
                        comments='',
                        created_by='system',
                        updated_by='system',
                        is_deleted=False
                    )
                    create_instance(new_ts)
                    logger.info(f"➕ Inserted new ThreatScenario for {threat_id} / {damage_scenario}")
    


def sync_attack_tree_with_threats():
    logger.info("Syncing Attack Tree with Threats via schema_manager")

    # ✅ Fetch all threats from the database
    threat_rows = get_instances(Threats, {'is_deleted': False})
    threat_ids = {t.threat_id for t in threat_rows}

    # ✅ Fetch all attack tree home rows
    attack_tree_rows = get_instances(AttackTreeHome, {})
    attack_tree_map = {row.ath_id: row for row in attack_tree_rows}

    # ✅ Sync/update or insert each Threat into AttackTreeHome
    for threat in threat_rows:
        ath_id = threat.threat_id
        if ath_id in attack_tree_map:
            # Update existing row if values differ
            update_instance(
                AttackTreeHome,
                {'ath_id': ath_id},
                {
                    'name': threat.name,
                    'initial_afr': threat.initia_afr,
                    'resid_afr': threat.resid_afr,
                    'toe_configuration_id': threat.toe_configuration_id or ''
                }
            )
            logger.info(f"🔁 Updated attack_tree_home row for threat_id: {ath_id}")
        else:
            # Insert new row
            new_row = AttackTreeHome(
                ath_id=ath_id,
                name=threat.name,
                initial_afr=threat.initia_afr,
                resid_afr=threat.resid_afr,
                toe_configuration_id=threat.toe_configuration_id or '',
                comments='',
                created_by='system',
                updated_by='system',
                is_deleted=False
            )
            create_instance(new_row)
            logger.info(f"➕ Inserted attack_tree_home row for threat_id: {ath_id}")

    # ✅ Remove attack_tree_home entries that no longer exist in the threats table
    for ath_id in attack_tree_map:
        if ath_id not in threat_ids:
            delete_instance(AttackTreeHome, {'ath_id': ath_id})
            logger.info(f"🗑️ Deleted orphaned attack_tree_home row for threat_id: {ath_id}")


def threat_generate_id():
    logger.info("Generating new Threat ID")
    try:
        # Get max suffix from both threat and threat_trash tables
        max_in_threat = get_max_numeric_suffix(Threats, 'threat_id', prefix="TH")
        #max_in_trash = get_max_numeric_suffix(ThreatTrash, 'threat_id', prefix="TH")

        max_suffix = max(max_in_threat)
        new_id = f"TH-{max_suffix + 1}"
        return new_id

    except Exception as e:
        logger.exception("Error generating Threat ID")
        return ""

def sync_assumptions_with_securityClaims():
    logger.info("🔄 Syncing assumptions with SecurityClaims and RiskControlTreeHome")

    # ✅ Step 1: Fetch all valid assumptions
    assumptions = get_instances(Assumptions, {})
    valid_assumption_ids = {a.assumption_id for a in assumptions if a.assumption_id}

    # ✅ Step 2: Sync with SecurityClaims
    security_claims = get_instances(SecurityClaims, {})
    for sc in security_claims:
        if sc.assumptions:
            assumption_list = [a.strip() for a in sc.assumptions.split(',') if a.strip()]
            updated_list = [a for a in assumption_list if a in valid_assumption_ids]

            if assumption_list != updated_list:
                new_value = ', '.join(updated_list)
                logger.info(f"🔁 Updating SecurityClaims {sc.scc_id}: removed non-existent assumptions")
                update_instance(SecurityClaims, {'id': sc.scc_id}, {'assumptions': new_value})

    # ✅ Step 3: Sync with RiskControlTreeHome
    risk_controls = get_instances(RiskControlTreeHome, {})
    for rc in risk_controls:
        if rc.assumptions:
            assumption_list = [a.strip() for a in rc.assumptions.split(',') if a.strip()]
            updated_list = [a for a in assumption_list if a in valid_assumption_ids]

            if assumption_list != updated_list:
                new_value = ', '.join(updated_list)
                logger.info(f"🔁 Updating RiskControlTreeHome {rc.id}: removed non-existent assumptions")
                update_instance(RiskControlTreeHome, {'id': rc.id}, {'assumptions': new_value})
    
def sync_toe_configuration():
    logger.info("🔄 Syncing TOE Configuration across modules")

    # ✅ Step 1: Get all valid TOE Configuration IDs
    toe_configs = get_instances(TOEConfiguration, {})
    valid_toe_ids = {t.toe_configuration_id for t in toe_configs if t.toe_configuration_id}

    # ----------------------------
    # Step 2: Sync with SecurityClaims
    # ----------------------------
    sc_rows = get_instances(SecurityClaims, {})
    for sc in sc_rows:
        if sc.toe_configuration:
            original = [t.strip() for t in sc.toe_configuration.split(',') if t.strip()]
            filtered = [t for t in original if t in valid_toe_ids]
            if original != filtered:
                new_val = ', '.join(filtered)
                update_instance(SecurityClaims, {'id': sc.scc_id}, {'toe_configuration': new_val})
                logger.info(f"✅ Updated SecurityClaims {sc.scc_id}")

    # ----------------------------
    # Step 3: Sync with SecurityGoals
    # ----------------------------
    sg_rows = get_instances(SecurityGoals, {})
    for sg in sg_rows:
        if sg.toe_configuration:
            original = [t.strip() for t in sg.toe_configuration.split(',') if t.strip()]
            filtered = [t for t in original if t in valid_toe_ids]
            if original != filtered:
                new_val = ', '.join(filtered)
                update_instance(SecurityGoals, {'id': sg.id}, {'toe_configuration': new_val})
                logger.info(f"✅ Updated SecurityGoals {sg.id}")

    # ----------------------------
    # Step 4: Sync with Threats
    # ----------------------------
    threat_rows = get_instances(Threats, {})
    for threat in threat_rows:
        if threat.toe_configuration_id:
            original = [t.strip() for t in threat.toe_configuration_id.split(',') if t.strip()]
            filtered = [t for t in original if t in valid_toe_ids]
            if original != filtered:
                new_val = ', '.join(filtered)
                update_instance(Threats, {'threat_id': threat.threat_id}, {'toe_configuration_id': new_val})
                logger.info(f"✅ Updated Threat {threat.threat_id}")

    # ----------------------------
    # Step 5: Sync with ThreatScenarios
    # ----------------------------
    ts_rows = get_instances(ThreatScenarios, {})
    for ts in ts_rows:
        if ts.toe_configuration_id:
            original = [t.strip() for t in ts.toe_configuration_id.split(',') if t.strip()]
            filtered = [t for t in original if t in valid_toe_ids]
            if original != filtered:
                new_val = ', '.join(filtered)
                update_instance(ThreatScenarios, {'ts_id': ts.ts_id}, {'toe_configuration_id': new_val})
                logger.info(f"✅ Updated ThreatScenario {ts.ts_id}")

    # ----------------------------
    # Step 6: Sync with RiskData
    # ----------------------------
    rd_rows = get_instances(RiskData, {})
    for rd in rd_rows:
        if rd.toe_configuration:
            original = [t.strip() for t in rd.toe_configuration.split(',') if t.strip()]
            filtered = [t for t in original if t in valid_toe_ids]
            if original != filtered:
                new_val = ', '.join(filtered)
                update_instance(RiskData, {'id': rd.id}, {'toe_configuration': new_val})
                logger.info(f"✅ Updated RiskData {rd.id}")

    # ----------------------------
    # Step 7: Sync with AttackTreeHome
    # ----------------------------
    ath_rows = get_instances(AttackTreeHome, {})
    for ath in ath_rows:
        if ath.toe_configuration_id:
            original = [t.strip() for t in ath.toe_configuration_id.split(',') if t.strip()]
            filtered = [t for t in original if t in valid_toe_ids]
            if original != filtered:
                new_val = ', '.join(filtered)
                update_instance(AttackTreeHome, {'ath_id': ath.ath_id}, {'toe_configuration_id': new_val})
                logger.info(f"✅ Updated AttackTreeHome {ath.ath_id}")

    # ----------------------------
    # Step 8: Repopulate TOEConfigurationInManagementSummary
    # ----------------------------
    """ delete_instance(TOEConfigurationInManagementSummary, {})  # Clear table

    for toe in toe_configs:
        item_text = f"{toe.toe_configuration_id}: {toe.toe_configuration_name}"
        summary_entry = TOEConfigurationInManagementSummary(
            toe_configuration=item_text
        )
        create_instance(summary_entry)

    logger.info("✅ Finished syncing TOE Configuration across all modules") """


def sync_misuse_cases_with_threats():
    logger.info("🔄 Syncing misuse_cases references in threats")

    # ✅ Step 1: Get all valid misuse_case IDs
    existing_mc = get_instances(Misusecases, {})
    valid_mc_ids = {mc.misuse_cases_id for mc in existing_mc if mc.misuse_cases_id}

    # ✅ Step 2: Fetch all threats
    threats = get_instances(Threats, {})
    for threat in threats:
        if threat.misuse_cases_id:
            original_mc_list = [mc.strip() for mc in threat.misuse_cases_id.split(',') if mc.strip()]
            filtered_mc_list = [mc for mc in original_mc_list if mc in valid_mc_ids]

            if original_mc_list != filtered_mc_list:
                updated_value = ', '.join(filtered_mc_list)
                update_instance(Threats, {'threat_id': threat.threat_id}, {'misuse_cases_id': updated_value})
                logger.info(f"✅ Updated Threat {threat.threat_id}: removed invalid misuse_case references")                                                                                       

def sync_securityGoals_from_securityControl():
    logger.info("🔄 Syncing SecurityControls → SecurityGoals references")

    # ✅ Step 1: Get all valid security goals
    valid_goals = get_instances(SecurityGoals, {})
    valid_goal_map = {goal.sg_id: goal.name for goal in valid_goals if goal.sg_id}

    # ✅ Step 2: Get all security controls
    security_controls = get_instances(SecurityControls, {})
    for sc in security_controls:
        if sc.security_goal_id:
            properties_list = [p.strip() for p in sc.security_goal_idc.split(',') if p.strip()]
            properties_id_list = [p.split('::')[0] for p in properties_list if '::' in p]

            updated_properties_list = []
            for sg_id in properties_id_list:
                if sg_id in valid_goal_map:
                    updated_properties_list.append(f"{sg_id}::{valid_goal_map[sg_id]}")

            # Compare full string representations for actual update
            if properties_list != updated_properties_list:
                updated_value = ', '.join(updated_properties_list)
                update_instance(SecurityControls, {'id': sc.scc_id}, {'properties': updated_value})
                logger.info(f"✅ Updated SecurityControl {sc.scc_id}: removed invalid security goal references")

            # Optional debug logs
            print("test1", properties_list)
            print("test2", properties_id_list)
            print("test3", updated_properties_list)

def update_riskData_from_securityClaims():
    logger.info("🔄 Updating RiskData from SecurityClaims")

    # ✅ Step 1: Fetch all valid SecurityClaim IDs
    security_claims = get_instances(SecurityClaims, {})
    valid_claim_ids = {sc.sc_id for sc in security_claims if sc.sc_id}

    # ✅ Step 2: Fetch all RiskData rows
    risk_rows = get_instances(RiskData, {})
    for risk in risk_rows:
        if risk.security_claims:
            original_list = [c.strip() for c in risk.security_claims.split(',') if c.strip()]
            filtered_list = [c for c in original_list if c in valid_claim_ids]

            if original_list != filtered_list:
                updated_claims = ', '.join(filtered_list)
                update_instance(RiskData, {'id': risk.id}, {'security_claims': updated_claims})
                logger.info(f"✅ Updated RiskData {risk.id}: removed invalid security claim references")


# def update_threatscenario_from_threat():
#     # Fetch all damage scenarios
#     damage_scenario_rows = DB.execute_db("SELECT ds_id, name FROM damage_scenarios")
#     damage_scenario_map = {row[0]: row[1] for row in damage_scenario_rows}

#     # Fetch all threats with their damage scenarios
#     existing_threat_rows = DB.execute_db("SELECT threat_id, name, damage_scenarios FROM threat")
#     threat_damage_map = {}
#     for threat_row in existing_threat_rows:
#         threat_id = threat_row[0]
#         threat_name = threat_row[1]
#         threat_damage_scenarios = threat_row[2].strip().split(', ') if threat_row[2] else []
#         threat_damage_map[threat_id] = [threat_name, [ds.strip() for ds in threat_damage_scenarios if ds.strip()]]

#     # Fetch all rows from the threat_scenarios table
#     existing_ts_rows = DB.execute_db("SELECT ts_id, threat, damage_scenarios, toe_configuration, reasoning, comments FROM threat_scenarios")
#     existing_ts_map = {}
#     existing_threat_ds_map = {}
#     for ts_row in existing_ts_rows:
#         ts_id = ts_row[0]
#         threat_id = ts_row[1].strip().split(' ')[0]
#         damage_scenario = ts_row[2].split('::')[0] if ts_row[2] else ""
#         if ts_id not in existing_ts_map:  # Initialize the list for this ts_id
#             existing_ts_map[ts_id] = []
#         existing_ts_map[ts_id].append((threat_id, damage_scenario))
#         if threat_id not in existing_threat_ds_map:
#             existing_threat_ds_map[threat_id] = []
#         if damage_scenario and damage_scenario not in existing_threat_ds_map[threat_id]:
#             existing_threat_ds_map[threat_id].append(damage_scenario)

#     # Identify rows to remove from 'threat_scenarios'
#     remove_ts_list = []
#     for ts_id, threats in existing_ts_map.items():
#         for threat_id, damage_scenario in threats:
#             if threat_id not in threat_damage_map.keys() or damage_scenario not in threat_damage_map[threat_id][1]:
#                 remove_ts_list.append(ts_id)
#                 break  # Exit inner loop if a match is found

#     # Delete invalid threat scenarios
#     for ts_id in set(remove_ts_list):  # Use set to avoid duplicates
#         DB.update_db("DELETE FROM threat_scenarios WHERE ts_id = ?", (ts_id,))

#     # Function to generate a unique threat scenario ID
#     def generate_unique_ts_id():
#         try:
#             # Query to get the maximum ID from both the 'threat_scenarios' and 'ts_trash' tables
#             result = DB.execute_db(""" 
#                 SELECT MAX(CAST(SUBSTR(ts_id, 4) AS INTEGER)) FROM (
#                     SELECT ts_id FROM threat_scenarios WHERE ts_id LIKE 'TS-%'
#                     UNION 
#                     SELECT ts_id FROM ts_trash WHERE ts_id LIKE 'TS-%'
#                 )
#             """)
#             print(result)
#             if result:

#                 max_existing_id = result[0][0] if result[0][0] else 0
#                 new_ts_id = f"TS-{max_existing_id + 1}"
#                 return new_ts_id
#             else:
#                 new_ts_id =  "TS-1"
#                 return new_ts_id
#         except sqlite3.Error as e:
#             QMessageBox.critical(None, "Database Error", f"Error generating ID: {e}")
#             return ""

#     # Add missing scenarios in the 'threat_scenarios' table
#     for threat_id, (threat_name, damage_scenarios) in threat_damage_map.items():
#         # Retrieve the toe_configuration for the current threat_id
#         toe_configuration_list = DB.execute_db_query("SELECT toe_configuration FROM threat WHERE threat_id = ?", (threat_id,))
#         if toe_configuration_list:
#             toe_configuration = toe_configuration_list[0][0]  # Extract the value
#         else:
#             toe_configuration = ''  # Default empty value if not found
        
#         if threat_id not in existing_threat_ds_map.keys():
#             new_ts_id = generate_unique_ts_id()
#             threat = f"{threat_id} - {threat_name}"
#             for damage_scenario in damage_scenarios:
#                 damage_scenario = damage_scenario.strip()  # Trim whitespace
#                 if damage_scenario and damage_scenario in damage_scenario_map:
#                     ds = f"{damage_scenario}::{damage_scenario_map[damage_scenario]}"
#                     DB.update_db("""
#                         INSERT INTO threat_scenarios (ts_id, threat, damage_scenarios, toe_configuration, reasoning, comments)
#                         VALUES (?, ?, ?, ?, ?, ?)
#                     """, (new_ts_id, threat, ds, toe_configuration, '', ''))
#                 else:
#                     print(f"Warning: Damage scenario '{damage_scenario}' is invalid. Skipping.")
#         else:
#             # Loop through each damage scenario for the current threat
#             for damage_scenario in damage_scenarios:
#                 damage_scenario = damage_scenario.strip()  # Trim whitespace
#                 if damage_scenario and damage_scenario in existing_threat_ds_map[threat_id]:
#                     for ts,[(threat , ds)] in existing_ts_map.items():
#                          if threat == threat_id and ds == damage_scenario: existing_ts_id = ts
#                     DB.update_db("""
#                     UPDATE threat_scenarios
#                     SET threat = ?, damage_scenarios = ?, toe_configuration=? 
#                     WHERE ts_id = ?
#                 """, (f"{threat_id} - {threat_name}", f"{damage_scenario}::{damage_scenario_map[damage_scenario]}", toe_configuration, existing_ts_id))
#                     print(existing_ts_id)
#                     # print("Hello",existing_ts_map)
            
#                 elif damage_scenario and damage_scenario in damage_scenario_map:
#                     new_ts_id = generate_unique_ts_id()
#                     threat = f"{threat_id} - {threat_name}"
#                     ds = f"{damage_scenario}::{damage_scenario_map[damage_scenario]}"
#                     DB.update_db("""
#                         INSERT INTO threat_scenarios (ts_id, threat, damage_scenarios, toe_configuration, reasoning, comments)
#                         VALUES (?, ?, ?, ?, ?, ?)
#                     """, (new_ts_id, threat, ds, toe_configuration, '', ''))
#                     print(f"Inserted new row with TS ID: {new_ts_id}, toe_configuration: {toe_configuration}")
#                 else:
#                     print(f"Warning: Damage scenario '{damage_scenario}' is invalid. Skipping.")

def remove_securityGoal_from_riskData():
    logger.info("🔄 Removing invalid Security Goals from RiskData")

    # ✅ Step 1: Fetch all valid SecurityGoal IDs
    security_goals = get_instances(SecurityGoals, {})
    valid_goal_ids = {sg.sg_id for sg in security_goals if sg.sg_id}

    # ✅ Step 2: Fetch all RiskData records
    risk_rows = get_instances(RiskData, {})
    for risk in risk_rows:
        if risk.security_goals:
            original_list = [g.strip() for g in risk.security_goals.split(',') if g.strip()]
            filtered_list = [g for g in original_list if g in valid_goal_ids]

            if original_list != filtered_list:
                updated_value = ', '.join(filtered_list)
                update_instance(RiskData, {'id': risk.id}, {'security_goals': updated_value})
                logger.info(f"✅ Updated RiskData {risk.id}: removed invalid security goal references")

def update_threat_TS_from_DS():
    logger.info("🔄 Updating Threats and ThreatScenarios from Damage Scenarios")

    # ✅ Step 1: Fetch all Damage Scenarios
    ds_rows = get_instances(DamageScenarios, {})
    existing_ds_ids = [ds.ds_id for ds in ds_rows if ds.ds_id]
    existing_ds_map = {ds.ds_id: ds.name for ds in ds_rows if ds.ds_id and ds.name}

    # ✅ Step 2: Update Threats' damage_scenarios
    threat_rows = get_instances(Threats, {})
    for threat in threat_rows:
        if threat.ds_id:
            ds_list = [ds.strip() for ds in threat.ds_id.split(',') if ds.strip()]
            filtered_ds_list = [ds_id for ds_id in ds_list if ds_id in existing_ds_ids]

            updated_ds = ', '.join(filtered_ds_list)

            if ds_list != filtered_ds_list:
                update_instance(Threats, {'threat_id': threat.threat_id}, {'ds_id': updated_ds})
                logger.info(f"✅ Updated Threat {threat.threat_id}: cleaned invalid DS refs")

    # ✅ Step 3: Update or delete ThreatScenarios
    ts_rows = get_instances(ThreatScenarios, {})
    for ts in ts_rows:
        if ts.ds_id:
            ds_id = ts.ds_id.strip().split('::')[0]

            if ds_id in existing_ds_ids:
                updated_ds = f"{ds_id}::{existing_ds_map[ds_id]}"
                update_instance(ThreatScenarios, {'ts_id': ts.ts_id}, {'ds_id': updated_ds})
                logger.info(f"✅ Updated ThreatScenario {ts.ts_id}")
            else:
                delete_instance(ThreatScenarios, {'ts_id': ts.ts_id})
                logger.info(f"🗑️ Deleted ThreatScenario {ts.ts_id}: invalid DS ID")

def sync_security_controls_with_riskcontrol():
    logger.info("🔄 Syncing SecurityControls → RiskControlTreeHome & RiskControlTree")

    # ✅ Step 1: Fetch security_controls and existing riskcontrol_tree_home
    sc_rows = get_instances(SecurityControls, {})
    rc_home_rows = get_instances(RiskControlTreeHome, {})
    rc_home_ids = {rc.id for rc in rc_home_rows if rc.id}

    # ✅ Step 2: Sync into riskcontrol_tree_home
    for sc in sc_rows:
        rc_name = f"Risk_Control - {sc.name}"
        if sc.scc_id not in rc_home_ids:
            new_rc = RiskControlTreeHome(
                id=sc.scc_id,
                name=rc_name,
                mitigates="",
                assumption_id="",
                comment="",
                created_by="system",
                updated_by="system",
                is_deleted=False
            )
            create_instance(new_rc)
            logger.info(f"➕ Inserted new RiskControlTreeHome for SC {sc.scc_id}")
        else:
            update_instance(RiskControlTreeHome, {'id': sc.scc_id}, {'name': rc_name})
            logger.info(f"🔁 Updated RiskControlTreeHome name for SC {sc.scc_id}")

    # ✅ Step 3: Fetch RiskControlTree Texts
    rc_tree_rows = get_instances(RiskControlTree, {})
    rc_text_map = {row.node_id: row.text for row in rc_tree_rows if row.node_id and row.text}
    rc_ids_from_text = {
        node_id: text.split(' ')[0]
        for node_id, text in rc_text_map.items()
    }

    # ✅ Step 4: Sync into riskcontrol_tree
    for sc in sc_rows:
        rc_text_label = f"{sc.scc_id} Risk_Control - {sc.name}"
        for node_id, first_token in rc_ids_from_text.items():
            if first_token == sc.scc_clsid:
                update_instance(RiskControlTree, {'node_id': node_id}, {'text': rc_text_label})
                logger.info(f"🔁 Updated RiskControlTree text for SC {sc.scc_id}")


def sync_security_controls_with_attack():
    logger.info("🔄 Syncing SecurityControls with AttackTree riskcontrol heads")

    # ✅ Step 1: Fetch Security Controls
    sc_rows = get_instances(SecurityControls, {})

    # ✅ Step 2: Fetch riskcontrol head nodes from AttackTree
    attack_tree_nodes = get_instances(AttackTree, {})
    rc_head_nodes = [
        node for node in attack_tree_nodes
        if node.node_type and node.node_type.lower() == 'riskcontrol head' and node.text
    ]

    # ✅ Step 3: Build mapping from control_id prefix to Node_ID
    control_node_map = {}
    for node in rc_head_nodes:
        parts = node.text.strip().split(' ', 1)
        if parts:
            control_id = parts[0]
            control_node_map[control_id] = node.node_id

    # ✅ Step 4: Update node text for matched Security Control entries
    for sc in sc_rows:
        rc_label = f"{sc.scc_id} Risk_Control - {sc.name}"
        if sc.scc_id in control_node_map:
            update_instance(AttackTree, {'node_id': control_node_map[sc.scc_id]}, {'text': rc_label})
            logger.info(f"🔁 Updated AttackTree node {control_node_map[sc.scc_id]} for SC {sc.scc_id}")

""" def sync_security_controls_with_MS_SecurityControl():
    logger.info("🔄 Syncing SecurityControls into MS_SecurityControl table")

    # ✅ Step 1: Fetch existing security controls (id + name)
    sc_rows = get_instances(SCModel, {})
    formatted_controls = [f"{sc.scc_id}:{sc.name}" for sc in sc_rows if sc.scc_id and sc.name]

    # ✅ Step 2: Clear MS_SecurityControl table
    delete_instance(MS_SecurityControl, {})  # Deletes all rows

    # ✅ Step 3: Insert each formatted control
    for control_text in formatted_controls:
        entry = MS_SecurityControl(security_controls=control_text)
        create_instance(entry)
        logger.info(f"➕ Inserted into MS_SecurityControl: {control_text}")
        

def sync_security_controls_with_MS_Assumptions():
    logger.info("🔄 Syncing Assumptions into AssumptionsInManagementSummary")

    # ✅ Step 1: Fetch all assumptions (id + name)
    assumption_rows = get_instances(Assumptions, {})
    formatted_assumptions = [
        f"{a.id}:{a.name}" for a in assumption_rows if a.id and a.name
    ]

    # ✅ Step 2: Clear AssumptionsInManagementSummary table
    delete_instance(AssumptionsInManagementSummary, {})  # Deletes all rows

    # ✅ Step 3: Insert formatted assumptions
    for entry in formatted_assumptions:
        summary_entry = AssumptionsInManagementSummary(assumptions=entry)
        create_instance(summary_entry)
        logger.info(f"➕ Inserted into AssumptionsInManagementSummary: {entry}") """
            

def remove_from_riskcontrol_on_security_control_delete():

    logger.info("🗑️ Removing orphaned risk control entries from riskcontrol_tree_home and riskcontrol_tree")

    # ✅ Step 1: Fetch all current security control IDs
    sc_rows = get_instances(SecurityControls, {})
    sc_ids = {sc.scc_id for sc in sc_rows if sc.scc_id}
    logger.debug(f"[Security Control IDs] {sc_ids}")

    # ✅ Step 2: Delete orphaned riskcontrol_tree_home rows
    rc_home_rows = get_instances(RiskControlTreeHome, {})
    for rc in rc_home_rows:
        if rc.id not in sc_ids:
            logger.info(f"🗑️ Deleting RiskControlTreeHome {rc.id} (orphaned)")
            delete_instance(RiskControlTreeHome, {'id': rc.id})

    # ✅ Step 3: Delete orphaned riskcontrol_tree 'head' nodes
    rc_tree_rows = get_instances(RiskControlTree, {})
    for rc in rc_tree_rows:
        if rc.node_type == 'head' and rc.node_id:
            control_id = rc.node_id.split('_')[0]
            if control_id not in sc_ids:
                logger.info(f"🗑️ Deleting RiskControlTree nodes for control ID {control_id}")
                delete_instance(RiskControlTree, {'node_id': rc.node_id})

def remove_orphaned_attack_tree_rows():
    logger.info("🔄 Removing orphaned attack_tree rows not linked to any existing threat")

    # ✅ Step 1: Get all valid threat IDs
    threat_rows = get_instances(Threats, {})
    valid_threat_ids = {t.threat_id for t in threat_rows if t.threat_id}

    # ✅ Step 2: Get all attack_tree 'head' nodes
    attack_tree_rows = get_instances(AttackTree, {})
    head_nodes = [node for node in attack_tree_rows if node.node_type == 'head' and node.node_id]

    # ✅ Step 3: Delete orphaned attack_tree nodes
    for node in head_nodes:
        threat_id = node.node_id.split('_')[0]
        if threat_id not in valid_threat_ids:
            logger.info(f"🗑️ Deleting AttackTree node: {node.node_id} (orphaned)")
            delete_instance(AttackTree, {'node_id': node.node_id})

    # ✅ Step 4: Call tree table updates (assumes these are defined elsewhere)
    Update_RiskControlTree_Table()
    Update_TechnicalTree_Table()

def update_attack_tree_text():
    logger.info("🔄 Updating attack_tree.text values based on Threat names")

    # ✅ Step 1: Fetch all threat IDs and names
    threat_rows = get_instances(Threats, {})
    threat_map = {t.threat_id: t.name for t in threat_rows if t.threat_id and t.name}

    # ✅ Step 2: Fetch all attack_tree rows where Node_Type = 'head'
    attack_tree_rows = get_instances(AttackTree, {})
    head_nodes = [row for row in attack_tree_rows if row.node_type == 'head' and row.node_id]

    # ✅ Step 3: Update attack_tree.text where threat_id matches
    for node in head_nodes:
        threat_id = node.node_id.strip().split('_')[0]
        if threat_id in threat_map:
            new_text = f"{threat_id} {threat_map[threat_id]}"
            if node.text != new_text:
                update_instance(AttackTree, {'node_id': node.node_id}, {'text': new_text})
                logger.info(f"✅ Updated AttackTree node {node.node_id} with new text: {new_text}")

def remove_claims_from_risk_data():
    logger.info("🔄 Removing non-existent security claim references from RiskData")

    # ✅ Step 1: Fetch valid SecurityClaim IDs
    valid_claims = get_instances(SecurityClaims, {})
    valid_claim_ids = {sc.sc_id for sc in valid_claims if sc.sc_id}

    # ✅ Step 2: Fetch all RiskData entries
    risk_rows = get_instances(RiskData, {})
    for risk in risk_rows:
        if risk.security_claims:
            original_list = [claim.strip() for claim in risk.security_claims.split(',') if claim.strip()]
            filtered_list = [claim for claim in original_list if claim in valid_claim_ids]

            if original_list != filtered_list:
                updated_value = ', '.join(filtered_list)
                update_instance(RiskData, {'id': risk.id}, {'security_claims': updated_value})
                logger.info(f"✅ Updated RiskData {risk.id}: removed invalid security claim references")
                
def remove_toe_configurations_from_risk_data():
    logger.info("🔄 Removing non-existent TOE configuration references from RiskData")

    # ✅ Step 1: Fetch valid TOE configuration IDs
    valid_toe_configs = get_instances(TOEConfiguration, {})
    valid_toe_ids = {toe.toe_configuration_id for toe in valid_toe_configs if toe.toe_configuration_id}

    # ✅ Step 2: Fetch all RiskData entries
    risk_rows = get_instances(RiskData, {})
    for risk in risk_rows:
        if risk.toe_configuration:
            original_list = [config.strip() for config in risk.toe_configuration.split(',') if config.strip()]
            filtered_list = [config for config in original_list if config in valid_toe_ids]

            if original_list != filtered_list:
                updated_value = ', '.join(filtered_list)
                update_instance(RiskData, {'id': risk.id}, {'toe_configuration': updated_value})
                logger.info(f"✅ Updated RiskData {risk.id}: removed invalid TOE configuration references")

def remove_SC_from_risk_data():
    logger.info("🔄 Removing non-existent SecurityControl references from RiskData.mitigated_by")

    # ✅ Step 1: Fetch valid SecurityControl IDs
    valid_controls = get_instances(SecurityControls, {})
    valid_control_ids = {sc.scc_id for sc in valid_controls if sc.scc_id}

    # ✅ Step 2: Fetch all RiskData entries
    risk_rows = get_instances(RiskData, {})
    for risk in risk_rows:
        if risk.mitigated_by:
            original_list = [entry.strip() for entry in risk.mitigated_by.split(',') if entry.strip()]
            filtered_list = [entry for entry in original_list if entry in valid_control_ids]

            if original_list != filtered_list:
                updated_value = ', '.join(filtered_list)
                update_instance(RiskData, {'id': risk.id}, {'mitigated_by': updated_value})
                logger.info(f"✅ Updated RiskData {risk.id}: removed invalid mitigated_by entries")


def remove_threats_from_mitigation():
    logger.info("🔄 Removing non-existent threats from RiskControlTreeHome.mitigates")

    # ✅ Step 1: Fetch all valid threat IDs
    threat_rows = get_instances(Threats, {})
    valid_threat_ids = {t.threat_id for t in threat_rows if t.threat_id}

    # ✅ Step 2: Fetch all RiskControlTreeHome rows
    rc_rows = get_instances(RiskControlTreeHome, {})
    for rc in rc_rows:
        if rc.mitigates:
            original_list = [tid.strip() for tid in rc.mitigates.split(',') if tid.strip()]
            filtered_list = [tid for tid in original_list if tid in valid_threat_ids]

            if original_list != filtered_list:
                updated_value = ', '.join(filtered_list)
                update_instance(RiskControlTreeHome, {'id': rc.id}, {'mitigates': updated_value})
                logger.info(f"✅ Updated RiskControlTreeHome {rc.id}: removed invalid threat IDs")

def update_risktreatement_data():
    logger.info("Updating Risk Treatment via ORM")

    try:
        damage_rows = get_instances(DamageScenarios, {})
        threat_rows = get_instances(ThreatScenarios, {})
        threat_map = {t.ts_id: t for t in threat_rows}

        # Prepare lookups
        ds_map = {ds.ds_id: ds.name for ds in damage_rows}
        impact_map = {ds.ds_id: ds.impact for ds in damage_rows}
        threat_scenarios_by_ds = {}
        for ts in threat_rows:
            threat_scenarios_by_ds.setdefault(ts.ds_id, []).append(ts)

        goal_map = {g.sg_id: g.name for g in get_instances(SecurityGoals, {})}
        claim_map = {c.sc_id: c.name for c in get_instances(SecurityClaims, {})}
        threat_afr_map = {
            t.threat_id: (t.initia_afr, t.resid_afr) for t in get_instances(Threats, {})
        }
        threat_name_map = {t.threat_id: t.name for t in get_instances(Threats, {})}
        toe_config_map = {
            ts.threat_id: ts.toe_configuration_id for ts in threat_rows
        }

        existing_riskdata = get_instances(RiskData, {})
        existing_map = {
            rd.rd_id: rd for rd in existing_riskdata
        }

        preserve_fields = {
            rd.rd_id: (
                rd.risk_treatment, rd.security_claims_id, rd.security_goal_id, rd.mitigated_by
            ) for rd in existing_riskdata
        }

        # risk_id = ts_id, assumed
        for ds in damage_rows:
            related_ts = threat_scenarios_by_ds.get(ds.ds_id, [])
            for ts in related_ts:
                rd_id = ts.ts_id
                tid = ts.threat_id

                # Compose fields
                damage = f"{ds.ds_id} - {ds.name}"
                impact = ds.impact
                afr_init, afr_resid = threat_afr_map.get(tid, ("", ""))
                afr_init_val = str(helper.risk_map.get((impact, afr_init))) if afr_init else ""
                afr_resid_val = str(helper.risk_map.get((impact, afr_resid))) if afr_resid else ""
                toe_id = toe_config_map.get(tid, "")

                prev_rt, prev_sc, prev_sg, prev_mb = preserve_fields.get(rd_id, ('', '', '', ''))

                payload = {
                    'rd_id': rd_id,
                    'ds_id': ds.ds_id,
                    'damage': damage,
                    'impact': impact,
                    'threat_id': tid,
                    'init_afr_level': afr_init,
                    'init_afr_value': afr_init_val,
                    'resid_afr_level': afr_resid,
                    'resid_afr_value': afr_resid_val,
                    'toe_configuration_id': toe_id,
                    'risk_treatment': prev_rt,
                    'security_claims_id': prev_sc,
                    'security_goal_id': prev_sg,
                    'mitigated_by': prev_mb
                }

                if rd_id in existing_map:
                    update_instance(RiskData, {'rd_id': rd_id}, payload)
                    logger.info(f"🔄 Updated RiskData: {rd_id}")
                else:
                    create_instance(RiskData(**payload))
                    logger.info(f"➕ Inserted new RiskData: {rd_id}")

        # Cleanup orphaned RiskData rows
        valid_ts_ids = {ts.ts_id for ts in threat_rows}
        for rd in existing_riskdata:
            if rd.rd_id not in valid_ts_ids:
                delete_instance(RiskData, {'rd_id': rd.rd_id})
                logger.info(f"🗑️ Deleted orphan RiskData: {rd.rd_id}")

        Update_RiskTreatment_Table()

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error updating risk treatment: {e}")
        logger.exception("❌ Failed to update risk treatment")

def remove_riskcontrol_from_attack_tree_rows(control_id):
    logger.info(f"🗑️ Removing attack_tree riskcontrol head nodes for control ID: {control_id}")

    # ✅ Step 1: Fetch relevant AttackTree rows
    attack_nodes = get_instances(AttackTree, {})
    target_nodes = [
        node for node in attack_nodes
        if node.node_type == 'riskcontrol head' and node.text and node.text.startswith(f"{control_id} ")
    ]

    # ✅ Step 2: Collect associated threat IDs and delete matched rows
    threat_ids = {node.node_id.split('_')[0] for node in target_nodes}

    for node in target_nodes:
        delete_instance(AttackTree, {'node_id': node.node_id})
        logger.info(f"🗑️ Deleted AttackTree node: {node.node_id} (riskcontrol head)")

    #for threat_id in threat_ids:
        #Attack_RiskControlTree_Update(threat_id)

    # ✅ Step 3: Refresh relevant trees
    Update_Threat_Table()
    Update_AttackTree_Table()
    Update_RiskControlTree_Table()
    Update_RiskTreatment_Table()
    Update_TechnicalTree_Table()

def remove_nonexistent_threat_scenarios_from_Risk_data():
    logger.info("🔄 Removing RiskData rows where ts_id does not exist in ThreatScenarios")

    # ✅ Step 1: Fetch valid ts_ids from ThreatScenarios
    existing_ts = get_instances(ThreatScenarios, {})
    valid_ts_ids = {ts.ts_id for ts in existing_ts if ts.ts_id}

    # ✅ Step 2: Fetch all Risk... (1 KB left)