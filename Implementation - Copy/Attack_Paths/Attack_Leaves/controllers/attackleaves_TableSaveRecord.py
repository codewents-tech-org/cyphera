from PyQt5.QtWidgets import QLineEdit, QMessageBox
from controllers.schema_manager import get_first_instance, get_instances, create_instance, update_instance
from Attack_Paths.controllers.riskcontrol_tree_AFR_update import RiskControlTree_Update
from Attack_Paths.controllers.Update_Connected_Modules import Update_Threat_Table, Update_AttackTree_Table, Update_RiskTreatment_Table
from Attack_Paths.controllers.attack_tree_AFR_update import AttackTree_AFR_Update
from Attack_Paths.controllers.technical_tree_AFR_update import TechnicalTree_Update
from Attack_Paths.controllers.Refresh_AllTree_Leaf_Data import Update_AllTree_Leaf
from controllers.database_tables.attack_paths_tables import AttackLeafNodes, TechnicalAttackTree, RiskControlTree, AttackTree, NodeType
import datetime

def AttackLeaves_Submit_Changes(self):
    try:
        print("[UI] Button state update...")
        self.update_button_states()
        self.value_updated_leafs_list = []
        self.name_updated_leafs_list = []
        print("[START] Processing attack leaf nodes table rows...")

        for row in range(self.table.rowCount()):
            print(f"  [ROW {row}] Reading cell values...")
            row_data = []
            for col in range(1, self.table.columnCount()):
                if col in [3, 4, 5, 6, 7]:
                    combo_box = self.table.cellWidget(row, col)
                    value = combo_box.currentText() if combo_box is not None else ""
                elif col == 8:
                    line_edit = self.table.cellWidget(row, col)
                    value = line_edit.text() if isinstance(line_edit, QLineEdit) else ""
                else:
                    item = self.table.item(row, col)
                    value = item.text() if item is not None else ''
                row_data.append(value)
            print(878787, row_data)
            leaf_id = row_data[0]
            new_name = row_data[1]
            new_time = row_data[2]
            new_expertise = row_data[3]
            new_knowledge = row_data[4]
            new_access = row_data[5]
            new_equipment = row_data[6]
            new_afr_level = row_data[7]
            new_description = row_data[8]
            new_comments = row_data[9]

            print(f"    [DEBUG] Fetched data for leaf_id={leaf_id} - name={new_name}")

            # Fetch existing leaf (ORM)
            leaf_obj = get_first_instance(AttackLeafNodes, filters={'id': leaf_id, 'is_deleted': False})
            print(f"    [SCHEMA_MANAGER] get_first_instance for id={leaf_id} returned: {leaf_obj}")

            if leaf_obj:
                if (getattr(leaf_obj, "time", "") != new_time or
                    getattr(leaf_obj, "expertise", "") != new_expertise or
                    getattr(leaf_obj, "knowledge", "") != new_knowledge or
                    getattr(leaf_obj, "access", "") != new_access or
                    getattr(leaf_obj, "reasoning", "") != new_description or
                    getattr(leaf_obj, "comments", "") != new_comments or
                    getattr(leaf_obj, "afr_level", "") != new_afr_level or
                    getattr(leaf_obj, "equipment", "") != new_equipment):
                    print(f"    [TRACK] Value change detected for leaf {leaf_id}")
                    if leaf_id not in self.value_updated_leafs_list:
                        self.value_updated_leafs_list.append(leaf_id)
                if getattr(leaf_obj, "name", "") != new_name:
                    print(f"    [TRACK] Name change detected for leaf {leaf_id}")
                    if leaf_id not in self.name_updated_leafs_list:
                        self.name_updated_leafs_list.append(leaf_id)

                update_fields = {
                    "name": new_name,
                    "time": new_time,
                    "expertise": new_expertise,
                    "knowledge": new_knowledge,
                    "access": new_access,
                    "equipment": new_equipment,
                    "updated_on": datetime.datetime.utcnow(),
                    "reasoning": new_description,
                    "comments": new_comments,
                    "afr_level": new_afr_level
                }
                print(f"    [SCHEMA_MANAGER] update_instance called for id={leaf_id} with fields={update_fields}")
                update_instance(AttackLeafNodes, {"id": leaf_id}, update_fields)
            else:
                print(f"    [SCHEMA_MANAGER] Creating new instance for leaf_id={leaf_id}")
                instance = AttackLeafNodes(
                    id=leaf_id,
                    name=new_name,
                    time=new_time,
                    expertise=new_expertise,
                    knowledge=new_knowledge,
                    access=new_access,
                    afr_level=new_afr_level,
                    equipment=new_equipment,
                    created_by="system",      # or fetch actual user
                    created_on=datetime.datetime.utcnow(),
                    is_latest=True,
                    is_deleted=False
                )
                create_instance(instance)

        print("[REFRESH] Calling Update_AllTree_Leaf...")
        Update_AllTree_Leaf(
            value_updated_leafs_list=self.value_updated_leafs_list,
            name_updated_leafs_list=self.name_updated_leafs_list
        )
        print(f"[AFTER REFRESH] value_updated_leafs_list={self.value_updated_leafs_list}, name_updated_leafs_list={self.name_updated_leafs_list}")

        # --- Refresh/Trigger downstream trees via ORM ---
        if self.value_updated_leafs_list:
            print("[TREE UPDATE] Collecting affected TechnicalAttackTree nodes...")
            tech_nodes = get_instances(
                TechnicalAttackTree,
                filters={"node_type": NodeType.LEAF}
            )
            print(f"[SCHEMA_MANAGER] get_instances TechnicalAttackTree (LEAF) returned {len(tech_nodes)} nodes.")
            tech_ids = {
                n.tree_id.split("_")[0]
                for n in tech_nodes if n.node_id in self.value_updated_leafs_list
            }
            print(f"[TREE UPDATE] Will update {len(tech_ids)} TechnicalTree: {list(tech_ids)}")
            for tech_id in tech_ids:
                print(f"    [CALL] TechnicalTree_Update({tech_id})")
                TechnicalTree_Update(tech_id)

            print("[TREE UPDATE] Collecting affected RiskControlTree nodes...")
            rc_nodes = get_instances(
                RiskControlTree,
                filters={"node_type": NodeType.LEAF}
            )
            print(f"[SCHEMA_MANAGER] get_instances RiskControlTree (LEAF) returned {len(rc_nodes)} nodes.")
            rc_ids = {
                n.tree_id.split("_")[0]
                for n in rc_nodes if n.node_id in self.value_updated_leafs_list
            }
            print(f"[TREE UPDATE] Will update {len(rc_ids)} RiskControlTree: {list(rc_ids)}")
            for rc_id in rc_ids:
                print(f"    [CALL] RiskControlTree_Update({rc_id})")
                RiskControlTree_Update(rc_id)

            print("[TREE UPDATE] Collecting affected AttackTree nodes...")
            atk_nodes = get_instances(
                AttackTree,
                filters={"node_type": NodeType.LEAF}
            )
            print(f"[SCHEMA_MANAGER] get_instances AttackTree (LEAF) returned {len(atk_nodes)} nodes.")
            atk_ids = {
                n.tree_id.split("_")[0]
                for n in atk_nodes if n.node_id in self.value_updated_leafs_list
            }
            print(f"[TREE UPDATE] Will update {len(atk_ids)} AttackTree: {list(atk_ids)}")
            for atk_id in atk_ids:
                print(f"    [CALL] AttackTree_AFR_Update({atk_id})")
                AttackTree_AFR_Update(atk_id)

            print("[TABLE SYNC] Calling summary table update functions...")
            print("[CALL] Update_Threat_Table()")
            Update_Threat_Table()
            print("[CALL] Update_AttackTree_Table()")
            Update_AttackTree_Table()
            print("[CALL] Update_RiskTreatment_Table()")
            Update_RiskTreatment_Table()

        print("[COMPLETE] AttackLeaves_Submit_Changes finished OK.")

    except Exception as e:
        print(f"[ERROR] {e}")
        QMessageBox.critical(None, "Database Error", f"Error saving data: {e}")
