
import json
from sqlalchemy.orm import Session
from controllers.database_tables.attack_paths_tables import ReferenceTrees
from Attack_Paths.Technical_Attack_Tree.controllers.tat_to_database import update_technical_tree
from Attack_Paths.RiskControl_Tree.controllers.rct_to_database import update_riskcontrol_tree
from Attack_Paths.Attack_Tree.controllers.at_to_database import update_attack_tree
from controllers.schema_manager import get_first_instance, create_instance

def save_tree_in_database(tree_id: str, root_data: dict, tree_type: str):

    ref_tree = get_first_instance(ReferenceTrees, {"id": tree_id, "is_deleted": False})

    if ref_tree is None:
        ref_tree = ReferenceTrees(id=tree_id, created_by="system")
        create_instance(ref_tree)

    # ref_tree = session.query(ReferenceTrees.uuid).filter_by(id=tree_id).first()
    ref_tree = get_first_instance(ReferenceTrees, {"id": tree_id, "is_deleted": False})
    ref_uuid = ref_tree.uuid if ref_tree else None  # ✅ UNPACK THE TUPLE
    print(f"Reference UUID for {tree_id}: {ref_uuid}")

    if ref_uuid:
        active_nodes: set[tuple[str | None, str]] = set()
        match tree_type:
            case "technical_tree":
                update_technical_tree(tree_id=tree_id, root_data=root_data, tree_ref_uuid=ref_uuid, active_nodes=active_nodes)
                print(f"✅ Tree '{tree_id}' updated successfully.")

            case "risk_control_tree":
                update_riskcontrol_tree(tree_id=tree_id, root_data=root_data, tree_ref_uuid=ref_uuid, active_nodes=active_nodes)
                print(f"✅ Tree '{tree_id}' updated successfully.")
                
            case "attack_tree":
                update_attack_tree(tree_id=tree_id, root_data=root_data, tree_ref_uuid=ref_uuid, active_nodes=active_nodes)
                print(f"✅ Tree '{tree_id}' updated successfully.")

