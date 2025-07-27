

from controllers.database_tables.attack_paths_tables import AttackLeafNodes, AttackTree, RiskControlTree, TechnicalAttackTree
from controllers.schema_manager import create_instance, get_first_instance, get_instances_like, update_instance
from PyQt5.QtWidgets import QLineEdit, QMessageBox
import controllers.DatabaseCreator as DB
import sqlite3
from Attack_Paths.controllers.riskcontrol_tree_AFR_update import RiskControlTree_Update
from Attack_Paths.controllers.Update_Connected_Modules import update_threat_table, update_attacktree_table, update_risktreatment_table
from Attack_Paths.controllers.attack_tree_AFR_update import AttackTree_AFR_Update
from Attack_Paths.controllers.technical_tree_AFR_update import TechnicalTree_Update
from Attack_Paths.controllers.Refresh_AllTree_Leaf_Data import Update_AllTree_Leaf

# save Attack Leaves data into the database
def AttackLeaves_Submit_Changes(self): 
    try:
        self.update_button_states()
        self.value_updated_leafs_list = []
        self.name_updated_leafs_list = []

        # 1. Insert/Update all leaves from the table UI
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(1, self.table.columnCount()):
                if col in [3, 4, 5, 6, 7]:
                    combo_box = self.table.cellWidget(row, col)
                    row_data.append(combo_box.currentText() if combo_box else "")
                elif col == 8:
                    line_edit = self.table.cellWidget(row, col)
                    row_data.append(line_edit.text() if isinstance(line_edit, QLineEdit) else "")
                else:
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else '')

            leaf_id = row_data[0]
            existing_leaf = get_first_instance(AttackLeafNodes, {'id': leaf_id, 'is_deleted': False})
            if existing_leaf:
                value_diff = (
                    existing_leaf.time != row_data[2] or
                    existing_leaf.expertise != row_data[3] or
                    existing_leaf.knowledge != row_data[4] or
                    existing_leaf.access != row_data[5] or
                    existing_leaf.equipment != row_data[6]
                )
                if value_diff and leaf_id not in self.value_updated_leafs_list:
                    self.value_updated_leafs_list.append(leaf_id)
                if existing_leaf.name != row_data[1] and leaf_id not in self.name_updated_leafs_list:
                    self.name_updated_leafs_list.append(leaf_id)
                update_instance(
                    AttackLeafNodes, {'id': leaf_id}, {
                        'name': row_data[1],
                        'time': row_data[2],
                        'expertise': row_data[3],
                        'knowledge': row_data[4],
                        'access': row_data[5],
                        'equipment': row_data[6],
                        'afr_level': row_data[7],
                        'reasoning': row_data[8],
                        'comments': row_data[9]
                    }
                )
            else:
                create_instance(AttackLeafNodes(
                    id=row_data[0],
                    name=row_data[1],
                    time=row_data[2],
                    expertise=row_data[3],
                    knowledge=row_data[4],
                    access=row_data[5],
                    equipment=row_data[6],
                    afr_level=row_data[7],
                    reasoning=row_data[8],
                    comments=row_data[9],
                    created_by="system",
                    updated_by="system",
                    version="3",
                    is_latest=True,
                    is_deleted=False
                ))

        # 2. Sync all trees for any updated leaves (LIKE logic using helper)
        if self.value_updated_leafs_list:
            # LIKE pattern for ORM via get_instances_like (MUST be implemented in schema_manager)
            for leaf_id in self.value_updated_leafs_list:
                like_pattern = f"{leaf_id} %"

                # TechnicalTree sync (only for node_type="leaf")
                tech_nodes = get_instances_like(
                    TechnicalAttackTree,
                    column_name="node_id",
                    like_pattern=like_pattern,
                    extra_filters={"node_type": "leaf"}
                )
                tech_ids = set(node.node_id.split('_')[0] for node in tech_nodes)
                for tech_id in tech_ids:
                    TechnicalTree_Update(tech_id)

                # RiskControlTree sync (node_type in ["leaf", "technical leaf"])
                rc_nodes = get_instances_like(
                    RiskControlTree,
                    column_name="node_id",
                    like_pattern=like_pattern,
                    extra_filters={"node_type": ["leaf", "technical leaf"]}
                )
                rc_ids = set(node.node_id.split('_')[0] for node in rc_nodes)
                for rc_id in rc_ids:
                    RiskControlTree_Update(rc_id)

                # AttackTree sync (node_type in allowed list)
                at_nodes = get_instances_like(
                    AttackTree,
                    column_name="node_id",
                    like_pattern=like_pattern,
                    extra_filters={
                        "node_type": [
                            "leaf", "riskcontrol leaf",
                            "technical leaf", "riskcontrol technical leaf"
                        ]
                    }
                )
                threat_ids = set(node.node_id.split('_')[0] for node in at_nodes)
                for threat_id in threat_ids:
                    AttackTree_AFR_Update(threat_id)

        # 3. Call all sync/update functions (these must be defined elsewhere)
        Update_AllTree_Leaf(
            value_updated_leafs_list=self.value_updated_leafs_list,
            name_updated_leafs_list=self.name_updated_leafs_list
        )
        update_threat_table()
        update_attacktree_table()
        update_risktreatment_table()

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error saving data: {e}")