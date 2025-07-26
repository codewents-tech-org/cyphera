from PyQt5.QtWidgets import QMessageBox
import sqlite3
import controllers.DatabaseCreator as DB

from Attack_Paths.controllers.technical_tree_AFR_update import TechnicalTree_Update
from Attack_Paths.controllers.riskcontrol_tree_AFR_update import RiskControlTree_Update
from Attack_Paths.controllers.attack_tree_AFR_update import AttackTree_AFR_Update
from Attack_Paths.controllers.Update_Connected_Modules import Update_Threat_Table, Update_AttackTree_Table, Update_RiskTreatment_Table
from controllers.database_tables.attack_paths_tables import AttackLeafNodes, TechnicalAttackTree, RiskControlTree, AttackTree

from sqlalchemy import or_
from controllers.schema_manager import get_instances, delete_all_instance, delete_instance, bulk_delete_with_like_and_types

def attack_leaves_delete_entry(self):
    try:
        print("[UI] Delete entry: Opening confirmation dialog")
        replay = QMessageBox.warning(
            None, "Warning", "Delete selected row.",
            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok
        )
        if replay == QMessageBox.Ok:
            print("[UI] User confirmed delete.")
            selected_row = self.table.currentRow()
            if selected_row < 0:
                print("[UI] No row selected, aborting delete.")
                QMessageBox.warning(None, "Warning", "Please select a row to delete.")
                return
            id_item = self.table.item(selected_row, 1).text()
            print(f"[DELETE] Attempting to delete AttackLeafNodes row with id={id_item}")

            # Delete from attack_leaf_home using ORM
            result = delete_instance(AttackLeafNodes, {"id": id_item})
            print(f"[DELETE] ORM delete_instance for AttackLeafNodes id={id_item} returned {result}")

            # Optionally insert into trash table here...

            self.table.removeRow(selected_row)
            row_count = self.table.rowCount()
            print(f"[UI] Row removed from table. Rows left: {row_count}")
            if row_count > 0:
                next_row = min(selected_row, row_count - 1)
                self.table.selectRow(next_row)
                print(f"[UI] Selected next row: {next_row}")

            print(f"[SYNC] Now syncing removal from all trees for leaf_id={id_item}")
            sync_removed_leaf_from_tree(id_item)
            print("[COMPLETE] attack_leaves_delete_entry finished.")
        else:
            print("[UI] User cancelled delete.")

    except Exception as e:
        print(f"[ERROR] Exception in attack_leaves_delete_entry: {e}")
        QMessageBox.critical(None, "Database Error", f"Error deleting row: {e}")

from controllers.database import get_engine_and_session

def sync_removed_leaf_from_tree(leaf_id):
    print(f"[SYNC] Removing leaf {leaf_id} from Technical, RiskControl, and Attack Trees.")

    engine, session_cls = get_engine_and_session()
    session = session_cls()

    try:
        # 1. TechnicalAttackTree
        bulk_delete_with_like_and_types(
            session,
            TechnicalAttackTree,
            like_field="node_id",
            like_value=f"{leaf_id} %",
            node_types=["leaf"]
        )
        print(f"[SYNC][TechnicalTree] Deleted leaf nodes for leaf_id={leaf_id}")

        # 2. RiskControlTree
        bulk_delete_with_like_and_types(
            session,
            RiskControlTree,
            like_field="node_id",
            like_value=f"{leaf_id} %",
            node_types=["leaf", "technical leaf"]
        )
        print(f"[SYNC][RiskControlTree] Deleted leaf/control nodes for leaf_id={leaf_id}")

        # 3. AttackTree
        bulk_delete_with_like_and_types(
            session,
            AttackTree,
            like_field="node_id",
            like_value=f"{leaf_id} %",
            node_types=["leaf", "riskcontrol leaf", "technical leaf", "riskcontrol technical leaf"]
        )
        print(f"[SYNC][AttackTree] Deleted attack nodes for leaf_id={leaf_id}")

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"[ERROR][sync_removed_leaf_from_tree] {e}")
    finally:
        session.close()

    Update_Threat_Table()
    Update_AttackTree_Table()
    Update_RiskTreatment_Table()
    print("[SYNC] sync_removed_leaf_from_tree complete.")

