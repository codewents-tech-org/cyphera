import uuid
import logging
from Attack_Paths.controllers.Refresh_AllTree_Leaf_Data import Update_AllTree_Leaf
from Attack_Paths.controllers.Update_Connected_Modules import update_attacktree_table, update_risktreatment_table, update_threat_table
from controllers.database_tables.attack_paths_tables import (
    AttackLeafNodes, TechnicalAttackTree, RiskControlTree, AttackTree
)
from controllers.schema_manager import (
    create_instance, get_instances, update_instance, delete_instance,
    get_first_instance, get_max_numeric_suffix, bulk_update_instances,
    get_instances_like
)
from PyQt5.QtWidgets import QTableWidgetItem, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.table_row_indicator as TRI

logger = logging.getLogger(__name__)

ATTACK_LEAF_CACHE = {}
last_leaf_number = None

# ========================== CRUD MANAGER ==========================

def load_all_attack_leaves():
    global ATTACK_LEAF_CACHE
    ATTACK_LEAF_CACHE.clear()
    leaves = get_instances(AttackLeafNodes, {'is_deleted': False})
    for leaf in leaves:
        ATTACK_LEAF_CACHE[leaf.uuid] = {
            'record': leaf,
            'changed': False,
            'deleted': False
        }
    return [entry['record'] for entry in ATTACK_LEAF_CACHE.values()]

def create_attack_leaf(leaf_id, name):
    leaf = AttackLeafNodes(
        uuid=str(uuid.uuid4()),
        id=leaf_id,
        name=name,
        time="0",
        expertise="0",
        knowledge="0",
        access="0",
        equipment="0",
        afr_level="High",
        reasoning='',
        comments='',
        created_by="system",
        updated_by="system",
        version="3",
        is_latest=True,
        is_deleted=False
    )
    leaf = create_instance(leaf)
    if not leaf:
        logger.error(f"[❌] Failed to create Attack Leaf with ID: {leaf_id}")
        return None
    ATTACK_LEAF_CACHE[leaf.uuid] = {
        'record': leaf,
        'changed': False,
        'deleted': False
    }
    return leaf

def update_attack_leaf(uuid, updates: dict):
    if uuid in ATTACK_LEAF_CACHE:
        obj = ATTACK_LEAF_CACHE[uuid]['record']
        changed = False
        for k, v in updates.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                setattr(obj, k, v)
                changed = True
        if changed:
            ATTACK_LEAF_CACHE[uuid]['changed'] = True
        return changed
    return False

def delete_attack_leaf(uuid):
    if uuid in ATTACK_LEAF_CACHE:
        ATTACK_LEAF_CACHE[uuid]['deleted'] = True
        ATTACK_LEAF_CACHE[uuid]['changed'] = True
        return True
    return False

def persist_attack_leaf_changes(sync=True):
    updates = []
    deleted_ids = []

    for uuid, entry in ATTACK_LEAF_CACHE.items():
        if not entry['changed']:
            continue

        obj = entry['record']
        if entry['deleted']:
            updates.append({'uuid': uuid, 'is_deleted': True})
            deleted_ids.append(obj.id)
        else:
            updates.append({
                'uuid': uuid,
                'id': obj.id,
                'name': obj.name,
                'time': obj.time,
                'expertise': obj.expertise,
                'knowledge': obj.knowledge,
                'access': obj.access,
                'equipment': obj.equipment,
                'afr_level': obj.afr_level,
                'reasoning': obj.reasoning,
                'comments': obj.comments,
                'updated_by': obj.updated_by,
                'is_deleted': False
            })
        entry['changed'] = False

    if updates:
        bulk_update_instances(AttackLeafNodes, updates)

    if sync and (updates or deleted_ids):
        sync_all_attack_leafs([x['id'] for x in updates if not x.get('is_deleted', False)], deleted_ids)

def generate_new_attack_leaf_id(self):
    # Find max used in DB
    max_id_num = get_max_numeric_suffix(AttackLeafNodes, "id", prefix="Lf")
    # Find all current (including unsaved) max in the table
    max_ui_id = max_id_num
    for row in range(self.table.rowCount()):
        item = self.table.item(row, 1)
        if item:
            text = item.text()
            if text.startswith("Lf"):
                try:
                    n = int(text[2:])
                    max_ui_id = max(max_ui_id, n)
                except Exception:
                    pass
    return f"Lf{max_ui_id + 1}"



# ========================== SYNC / BUSINESS LOGIC ==========================

def sync_all_attack_leafs(updated_leaf_ids, deleted_leaf_ids):
    if updated_leaf_ids:
        # Update_AllTree_Leaf(value_u0d_leafs_list=updated_leaf_ids, name_updated_leafs_list=[])
        update_threat_table()
        # update_attacktree_table()
        # update_risktreatment_table()
    if deleted_leaf_ids:
        for leaf_id in deleted_leaf_ids:
            remove_leaf_from_trees(leaf_id)

def remove_leaf_from_trees(leaf_id):
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
        try:
            from Attack_Paths.controllers.Update_Connected_Modules import TechnicalTree_Update
            TechnicalTree_Update(tech_id)
        except ImportError:
            pass  # If function isn't ported/available

    # RISK CONTROL TREE
    rc_nodes = []
    for nt in ["leaf", "technical leaf"]:
        rc_nodes += get_instances_like(
            RiskControlTree,
            column_name="node_id",
            like_pattern=like_pattern,
            extra_filters={"node_type": nt}
        )
    rc_ids = set(node.node_id.split('_')[0] for node in rc_nodes)
    for node in rc_nodes:
        delete_instance(RiskControlTree, {'uuid': node.uuid})
    for rc_id in rc_ids:
        try:
            from Attack_Paths.controllers.Update_Connected_Modules import RiskControlTree_Update
            RiskControlTree_Update(rc_id)
        except ImportError:
            pass

    # ATTACK TREE
    at_nodes = []
    for nt in ["leaf", "riskcontrol leaf", "technical leaf", "riskcontrol technical leaf"]:
        at_nodes += get_instances_like(
            AttackTree,
            column_name="node_id",
            like_pattern=like_pattern,
            extra_filters={"node_type": nt}
        )
    threat_ids = set(node.node_id.split('_')[0] for node in at_nodes)
    for node in at_nodes:
        delete_instance(AttackTree, {'uuid': node.uuid})
    for threat_id in threat_ids:
        try:
            from Attack_Paths.controllers.Update_Connected_Modules import AttackTree_AFR_Update
            AttackTree_AFR_Update(threat_id)
        except ImportError:
            pass

    # Final updates
    update_threat_table()
    update_attacktree_table()
    update_risktreatment_table()

# ========================== UI HOOKS (Use These in Your QWidget) ==========================

def attack_leaves_load_data(self):
    try:
        self.table.setRowCount(0)
        self.existing_entries.clear()
        rows = load_all_attack_leaves()
        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row.id)
            sidebar = TRI.SidebarWidget()
            self.table.setCellWidget(row_idx, 0, sidebar)
            id_item = QTableWidgetItem(row.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 1, id_item)
            name_item = QTableWidgetItem(row.name)
            self.table.setItem(row_idx, 2, name_item)
            # -- ComboBoxes
            for i, (val, col_idx) in enumerate(zip(
                [row.time, row.expertise, row.knowledge, row.access, row.equipment], [3,4,5,6,7])):
                combo = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[i])
                combo.set_text(str(val) if val is not None else "0")
                combo.currentTextChanged.connect(self.set_unsaved_changes)
                combo.currentIndexChanged.connect(lambda: self.Update_AFR_Level(combo))
                self.table.setCellWidget(row_idx, col_idx, combo)
            afr_item = QLineEdit(row.afr_level if row.afr_level else '')
            afr_item.setReadOnly(True)
            helper.Apply_AFR_Level_Color(afr_item, row.afr_level)
            self.table.setCellWidget(row_idx, 8, afr_item)
            reasoning_item = QTableWidgetItem(row.reasoning or '')
            self.table.setItem(row_idx, 9, reasoning_item)
            comment_item = QTableWidgetItem(row.comments or '')
            self.table.setItem(row_idx, 10, comment_item)
        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 1)
    except Exception as e:
        logger.exception("Error loading attack leaves")
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")

def create_attack_leaf_and_insert_row(self):
    leaf_id = generate_new_attack_leaf_id()
    leaf_name = f"Leaf {leaf_id.split('-')[-1]}"
    leaf = create_attack_leaf(leaf_id, leaf_name)
    if leaf is None:
        QMessageBox.critical(None, "Error", f"Attack Leaf with ID '{leaf_id}' already exists. Please try again.")
        return
    row_index = self.table.rowCount()
    self.table.insertRow(row_index)
    self.table.setRowHeight(row_index, 40)
    sidebar = TRI.SidebarWidget()
    self.table.setCellWidget(row_index, 0, sidebar)
    id_item = QTableWidgetItem(leaf.id)
    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
    self.table.setItem(row_index, 1, id_item)
    name_item = QTableWidgetItem(leaf.name)
    self.table.setItem(row_index, 2, name_item)
    self.table.setCurrentCell(row_index, 2)
    for i, (value, col_idx) in enumerate(zip(
        [leaf.time, leaf.expertise, leaf.knowledge, leaf.access, leaf.equipment], [3, 4, 5, 6, 7]
    )):
        combo = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[i])
        combo.set_text(str(value) if value is not None else "0")
        combo.currentTextChanged.connect(self.set_unsaved_changes)
        combo.currentIndexChanged.connect(lambda: self.Update_AFR_Level(combo))
        self.table.setCellWidget(row_index, col_idx, combo)
    afr_item = QLineEdit(leaf.afr_level if leaf.afr_level else 'High')
    afr_item.setReadOnly(True)
    helper.Apply_AFR_Level_Color(afr_item, leaf.afr_level or 'High')
    self.table.setCellWidget(row_index, 8, afr_item)
    reasoning_item = QTableWidgetItem(leaf.reasoning or '')
    self.table.setItem(row_index, 9, reasoning_item)
    comment_item = QTableWidgetItem(leaf.comments or '')
    self.table.setItem(row_index, 10, comment_item)
    if hasattr(self, "row_uuid_map"):
        self.row_uuid_map[row_index] = leaf.uuid
    self.delete_button.setEnabled(True)
    self.submit_button.setEnabled(True)
    self.table.selectRow(row_index)
