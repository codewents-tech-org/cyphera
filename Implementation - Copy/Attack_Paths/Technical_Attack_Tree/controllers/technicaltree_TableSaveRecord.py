

from PyQt5.QtWidgets import QMessageBox
import controllers.DatabaseCreator as DB
import components.table.multioption_selector as MOS
import sqlite3
from controllers.schema_manager import get_instances, get_first_instance, create_instance, update_instance, delete_instances_like
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome 
import logging
logger = logging.getLogger(__name__)
# save Technical tree data into the database
def technical_Submit_Changes(self):
    logger.info("Saving technical tree data to the database")
    try:
        self.update_button_states()

        for row in range(self.table.rowCount()):
            # Collect data for ORM object, mapping columns appropriately
            # Assumes first column is an index or sidebar widget, so skip col=0
            record = {}
            col_names = [c.name for c in TechnicalTreeHome.__table__.columns]
            col_count = min(len(col_names), self.table.columnCount()-1)
            for i in range(col_count):
                col = i + 1  # skip the first column (sidebar)
                item = self.table.item(row, col)
                if item is not None:
                    value = item.text()
                else:
                    widget = self.table.cellWidget(row, col)
                    if widget is not None and hasattr(widget, 'selected_items'):
                        selected = widget.selected_items()
                        value = ", ".join(selected) if isinstance(selected, list) else str(selected)
                    else:
                        value = ""
                record[col_names[i]] = value

            # INSERT OR REPLACE by primary key (id)
            existing = get_first_instance(TechnicalTreeHome, {"id": record.get("id")})
            if existing:
                update_instance(TechnicalTreeHome, {"id": record.get("id")}, record)
            else:
                new_entry = TechnicalTreeHome(**record)
                create_instance(new_entry)

        Sync_TechnicalTree_name()

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error saving data: {e}")

def Sync_TechnicalTree_name():

    # Map {id: name} for all technical_tree_home rows
    tech_entries = get_instances(TechnicalTreeHome)
    technicaltree_map = {entry.id: entry.name for entry in tech_entries}

    # Fetch all heads from other trees
    available_tech_tree = get_instances(TechnicalTreeHome, {"node_type": "head"})
    available_cir_tech_tree = get_instances(RiskControlTree, {"node_type": "technical head"})
    available_att_tech_tree = get_instances(AttackTree, {"node_type": "technical head"})
    available_att_cir_tech_tree = get_instances(AttackTree, {"node_type": "riskcontrol technical head"})

    # Sync names across all related tables
    for tech_id, tech_name in technicaltree_map.items():
        for row in available_tech_tree:
            if row.text and row.text.startswith(f"{tech_id} "):
                update_instance(TechnicalTreeHome, {"node_id": row.node_id}, {"text": f"{tech_id} {tech_name}"})

        for row in available_cir_tech_tree:
            if row.text and row.text.startswith(f"{tech_id} "):
                update_instance(RiskControlTree, {"node_id": row.node_id}, {"text": f"{tech_id} {tech_name}"})

        for row in available_att_tech_tree:
            if row.text and row.text.startswith(f"{tech_id} "):
                update_instance(AttackTree, {"node_id": row.node_id}, {"text": f"{tech_id} {tech_name}"})

        for row in available_att_cir_tech_tree:
            if row.text and row.text.startswith(f"{tech_id} "):
                update_instance(AttackTree, {"node_id": row.node_id}, {"text": f"{tech_id} {tech_name}"})
