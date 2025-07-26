
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import controllers.DatabaseCreator as DB

from Attack_Paths.RiskControl_Tree.controllers.RiskControl_TechnicanTree_Update import riskcontrol_TechnicalTree_Update
from Attack_Paths.Attack_Tree.controllers.Attack_TechnicanTree_Update import AttackTechnicalTreeUpdater
from Attack_Paths.controllers.Update_Connected_Modules import Update_Threat_Table, Update_AttackTree_Table, Update_RiskTreatment_Table
from controllers.schema_manager import get_instances, get_first_instance, create_instance, delete_instance, delete_instances_like
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome 
import logging
logger = logging.getLogger(__name__)


def technical_delete_entry(self):
    logger.info("Delete selected row.")
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

            # Delete from technical_tree_home using ORM

            delete_instance(TechnicalTreeHome, {"id": id_item})

            # Insert to tat_trash table using ORM
            # trash_entry = TatTrash(id=id_item)
            # create_instance(trash_entry)

            self.table.removeRow(selected_row)
            row_count = self.table.rowCount()
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                self.table.selectRow(next_row)

            logger.info("Row deleted.")
            sync_removed_technicaltree_from_tree(id_item)

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error deleting row: {e}")


def sync_removed_technicaltree_from_tree(tree_id):
    logger.info("Sync removed technical tree from riskcontrol and attack tree.")

    # 1. Delete all technical_tree where node_id LIKE '{tree_id}_node%'
    delete_instances_like(
        TechnicalTreeHome,
        field_name="node_id",
        like_pattern=f"{tree_id}_node%"
    )

    logger.info("Technical tree removed from Risk Control Tree.")

    # 2. Remove from riskcontrol_tree where Node_Type='technical head' AND Text LIKE '{tree_id} %'
    risk_rows = get_instances(
        RiskControlTree, {"node_type": "technical head"}
    )
    for row in risk_rows:
        if row.text and row.text.startswith(f"{tree_id} "):
            # Delete all with Node_ID LIKE tree_node
            delete_instances_like(
                RiskControlTree,
                field_name="node_id",
                like_pattern=row.node_id  # This matches the old code: LIKE {tree_node}
            )
            cir_tree = row.node_id.split('_')[0]
            riskcontrol_TechnicalTree_Update(cir_tree)

    logger.info("Technical tree removed from attack tree.")

    # 3. Remove from attack_tree where Node_Type in (...) AND Text LIKE '{tree_id} %'
    attack_rows = get_instances(AttackTree)
    for row in attack_rows:
        if (
            row.node_type in ("technical head", "riskcontrol technical head")
            and row.text and row.text.startswith(f"{tree_id} ")
        ):
            delete_instances_like(
                AttackTree,
                field_name="node_id",
                like_pattern=row.node_id
            )
            att_tree = row.node_id.split('_')[0]
            # Attack_TechnicalTree_Update(att_tree)

    logger.info("Update threat, attack tree table and risk treatment.")
    Update_Threat_Table()
    Update_AttackTree_Table()
    Update_RiskTreatment_Table()


