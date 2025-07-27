
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalAttackTree
from controllers.schema_manager import delete_instance, get_instances_like
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import controllers.DatabaseCreator as DB

from Attack_Paths.controllers.technical_tree_AFR_update import TechnicalTree_Update
from Attack_Paths.controllers.riskcontrol_tree_AFR_update import RiskControlTree_Update
from Attack_Paths.controllers.attack_tree_AFR_update import AttackTree_AFR_Update
from Attack_Paths.controllers.Update_Connected_Modules import update_threat_table, update_attacktree_table, update_risktreatment_table

def attack_leaves_delete_entry(self):
    try:
        replay = QMessageBox.warning(
            None, "Warning", "Delete selected row.",
            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok
        )
        if replay == QMessageBox.Ok:
            selected_row = self.table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(None, "Warning", "Please select a row to delete.")
                return

            id_item = self.table.item(selected_row, 1).text()

            # Hard delete the leaf node
            delete_instance(AttackLeafNodes, {'id': id_item})

            # Add to trash (optional, if trash table is present)
            try:
                create_instance(LeafNodeTrash(id=id_item))
            except Exception as e:
                print(f"[WARNING] Could not insert to trash: {e}")

            self.table.removeRow(selected_row)
            row_count = self.table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                self.table.selectRow(next_row)

            sync_removed_leaf_from_tree(id_item)
    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")

def sync_removed_leaf_from_tree(leaf_id):
    like_pattern = f"{leaf_id} %"

    # TECHNICAL TREE
    tech_nodes = get_instances_like(
        TechnicalAttackTree,
        column_name="node_id",
        like_pattern=like_pattern,
        extra_filters={"node_type": "leaf"}
    )
    tech_ids = set(node.node_id.split('_')[0] for node in tech_nodes)
    for node in tech_nodes:
        delete_instance(TechnicalAttackTree, {'uuid': node.uuid})
    for tech_id in tech_ids:
        TechnicalTree_Update(tech_id)

    # RISK CONTROL TREE
    rc_nodes = get_instances_like(
        RiskControlTree,
        column_name="node_id",
        like_pattern=like_pattern,
        extra_filters={"node_type": ["leaf", "technical leaf"]}
    )
    rc_ids = set(node.node_id.split('_')[0] for node in rc_nodes)
    for node in rc_nodes:
        delete_instance(RiskControlTree, {'uuid': node.uuid})
    for rc_id in rc_ids:
        RiskControlTree_Update(rc_id)

    # ATTACK TREE
    at_nodes = get_instances_like(
        AttackTree,
        column_name="node_id",
        like_pattern=like_pattern,
        extra_filters={
            "node_type": [
                "leaf", "riskcontrol leaf", "technical leaf", "riskcontrol technical leaf"
            ]
        }
    )
    threat_ids = set(node.node_id.split('_')[0] for node in at_nodes)
    for node in at_nodes:
        delete_instance(AttackTree, {'uuid': node.uuid})
    for threat_id in threat_ids:
        AttackTree_AFR_Update(threat_id)

    # Call parent update flows (unchanged)
    update_threat_table()
    update_attacktree_table()
    update_risktreatment_table()