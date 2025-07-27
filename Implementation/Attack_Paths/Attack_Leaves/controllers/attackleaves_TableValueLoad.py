

from controllers.database_tables.attack_paths_tables import AttackLeafNodes
from controllers.schema_manager import get_instances
from PyQt5.QtWidgets import QTableWidgetItem, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
import sqlite3
import controllers.DatabaseCreator as DB
import models.helper as helper
import components.table.multioption_selector as MOS
import components.table.table_row_indicator as TRI
import logging

logger = logging.getLogger(__name__)
# Load Attack Leaves data from the database
def AttackLeaves_Load_data(self):
    try:
        self.table.setRowCount(0)
        self.existing_entries.clear()

        # ORM fetch instead of raw SQL
        rows = get_instances(AttackLeafNodes, {'is_deleted': False})
        if not rows:
            return

        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 40)
            self.existing_entries.add(row.id)

            # 0: sidebar widget
            sidebar = TRI.SidebarWidget()
            self.table.setCellWidget(row_idx, 0, sidebar)

            # 1: id (not editable)
            id_item = QTableWidgetItem(row.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 1, id_item)

            # 2: name (editable)
            name_item = QTableWidgetItem(row.name)
            self.table.setItem(row_idx, 2, name_item)

            # 3: time
            item_time = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[0])
            item_time.set_text(str(row.time) if row.time is not None else "0")
            item_time.currentTextChanged.connect(self.set_unsaved_changes)
            item_time.currentIndexChanged.connect(lambda: self.Update_AFR_Level(item_time))
            self.table.setCellWidget(row_idx, 3, item_time)

            # 4: expertise
            item_expertise = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[1])
            item_expertise.set_text(str(row.expertise) if row.expertise is not None else "0")
            item_expertise.currentTextChanged.connect(self.set_unsaved_changes)
            item_expertise.currentIndexChanged.connect(lambda: self.Update_AFR_Level(item_expertise))
            self.table.setCellWidget(row_idx, 4, item_expertise)

            # 5: knowledge
            item_knowledge = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[2])
            item_knowledge.set_text(str(row.knowledge) if row.knowledge is not None else "0")
            item_knowledge.currentTextChanged.connect(self.set_unsaved_changes)
            item_knowledge.currentIndexChanged.connect(lambda: self.Update_AFR_Level(item_knowledge))
            self.table.setCellWidget(row_idx, 5, item_knowledge)

            # 6: access
            item_access = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[3])
            item_access.set_text(str(row.access) if row.access is not None else "0")
            item_access.currentTextChanged.connect(self.set_unsaved_changes)
            item_access.currentIndexChanged.connect(lambda: self.Update_AFR_Level(item_access))
            self.table.setCellWidget(row_idx, 6, item_access)

            # 7: equipment
            item_equipment = MOS.CustomComboBoxLeave(helper.attackpath_leaf_values_menu[4])
            item_equipment.set_text(str(row.equipment) if row.equipment is not None else "0")
            item_equipment.currentTextChanged.connect(self.set_unsaved_changes)
            item_equipment.currentIndexChanged.connect(lambda: self.Update_AFR_Level(item_equipment))
            self.table.setCellWidget(row_idx, 7, item_equipment)

            # 8: afr_level (readonly, colored)
            afr_item = QLineEdit(row.afr_level if row.afr_level else '')
            afr_item.setReadOnly(True)
            helper.Apply_AFR_Level_Color(afr_item, row.afr_level)
            self.table.setCellWidget(row_idx, 8, afr_item)

            # 9: reasoning (editable)
            reasoning_item = QTableWidgetItem(row.reasoning or '')
            self.table.setItem(row_idx, 9, reasoning_item)

            # 10: comments (editable)
            comment_item = QTableWidgetItem(row.comments or '')
            self.table.setItem(row_idx, 10, comment_item)

        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 1)

    except Exception as e:
        logger.exception("Error loading attack leaves")
        QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")