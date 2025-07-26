import uuid
import pandas as pd
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox, QTreeWidget, QTreeWidgetItem, QStyledItemDelegate
)
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import Qt

from components import action_panel
from controllers.database_tables.catalog_tables import ThreatCatalog
from controllers.tablemodel import Threats, SecurityControls
from controllers.schema_manager import get_instances, create_instance, delete_instance, get_max_numeric_suffix
from Catalog.Threat_Catalog.views.threatcatalog_toolbar_panel import create_toolbar
 # if not already imported as components.action_panel
import Analysis.models.analysis_synchronization as AS

logger = logging.getLogger(__name__)

def normalize_checkbox(text):
    """Remove common prefixes and strip whitespace."""
    if text.startswith("Attack or Vulnerability: "):
        return text[len("Attack or Vulnerability: "):].strip()
    if text.startswith("Mitigation: "):
        return text[len("Mitigation: "):].strip()
    return text.strip()

def threat_generate_id():
    try:
        max_suffix = get_max_numeric_suffix(Threats, 'threat_id', prefix="TH")
        return f"TH-{max_suffix + 1}"
    except Exception:
        logger.exception("Error generating Threat ID")
        return ""

def securitycontrols_generate_id():
    try:
        max_suffix = get_max_numeric_suffix(SecurityControls, 'scc_id', prefix="Ctrl")
        return f"Ctrl-{max_suffix + 1}"
    except Exception:
        logger.exception("Error generating Security Controls ID")
        return ""

class AutoResizeDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        text = index.data(Qt.DisplayRole)
        doc = QTextDocument()
        doc.setPlainText(text)
        doc.setTextWidth(900)
        return doc.size().toSize()

class ThreatCatalog_Module(QWidget):
    def __init__(self, parent=None):
        logger.info("Threat Catalog class")
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        create_toolbar(self)
        main_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)
        self.action_panel_layout.setContentsMargins(10,10,10,10)
        self.content_panel = QWidget(self)
        self.content_panel.setStyleSheet("background-color: #FFFFFF; border: 2px solid #E3E5EC; border-radius: 8px;")
        self.content_panel_layout = QVBoxLayout(self.content_panel)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderLabels([""])
        self.tree_widget.setFocusPolicy(Qt.NoFocus)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setStyleSheet("font-size:14px;")
        self.tree_widget.setWordWrap(True)
        self.content_panel_layout.addWidget(self.tree_widget)
        self.action_panel_layout.addWidget(self.content_panel)  
        main_layout.addWidget(self.action_panel)
        self.submit_button.clicked.connect(self.on_generate_button_clicked)

    def load_data(self):
        logger.info("Loading data (single-table)")
        # --- Load DB selections ---
        catalog_rows = get_instances(ThreatCatalog, {})
        selected_attack_items = {
            normalize_checkbox(row.attack_or_vulnerability_checkbox)
            for row in catalog_rows if row.attack_or_vulnerability_checkbox
        }
        self.checked_mitigations = {
            (normalize_checkbox(row.mitigation_checkbox), normalize_checkbox(row.attack_or_vulnerability_checkbox))
            for row in catalog_rows if row.mitigation_checkbox and row.attack_or_vulnerability_checkbox
        }
        try:
            self.tree_widget.itemChanged.disconnect(self.on_item_changed)
        except TypeError:
            pass
        self.tree_widget.clear()
        # --- Load Excel ---
        excel_file = "utils/templates/Threat_Catalog_templete.xlsx"
        data = pd.read_excel(excel_file, skiprows=1)
        data = data.applymap(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)
        data.ffill(inplace=True)
        # --- Build tree data ---
        tree_data = {}
        for _, row in data.iterrows():
            high_level = str(row[0]).strip()
            sub_sub_level1 = f"[{str(row[1]).strip()}] {str(row[2]).strip()}"
            sub_sub_level2 = f"Attack or Vulnerability: [{str(row[3]).strip()}] {str(row[4]).strip()}"
            sub_sub_level3 = f"Mitigation: [{str(row[5]).strip()}] {str(row[6]).strip()}"
            tree_data.setdefault(high_level, {}) \
                     .setdefault(sub_sub_level1, {}) \
                     .setdefault(sub_sub_level2, {}) \
                     .setdefault(sub_sub_level3, {})
        # --- Populate tree ---
        for level1, level2_dict in tree_data.items():
            high_level_item = QTreeWidgetItem([f"High Level Threat: {level1}"])
            self.tree_widget.addTopLevelItem(high_level_item)
            for level2, level3_dict in level2_dict.items():
                sub_level_item = QTreeWidgetItem([f"Sub Level Threat: {level2}"])
                high_level_item.addChild(sub_level_item)
                for level3, level4_dict in level3_dict.items():
                    attack_item = QTreeWidgetItem([level3])
                    attack_item.setFlags(attack_item.flags() | Qt.ItemIsUserCheckable)
                    is_checked = Qt.Checked if normalize_checkbox(level3) in selected_attack_items else Qt.Unchecked
                    attack_item.setCheckState(0, is_checked)
                    sub_level_item.addChild(attack_item)
                    for level4 in level4_dict.keys():
                        mitigation_item = QTreeWidgetItem([level4])
                        mitigation_item.setFlags(mitigation_item.flags() | Qt.ItemIsUserCheckable)
                        pair = (normalize_checkbox(level4), normalize_checkbox(level3))
                        is_mit_checked = Qt.Checked if pair in self.checked_mitigations else Qt.Unchecked
                        mitigation_item.setCheckState(0, is_mit_checked)
                        attack_item.addChild(mitigation_item)
        self.tree_widget.itemChanged.connect(self.on_item_changed)

    def get_checked_items(self):
        checked_attacks = set()
        checked_mitigations = set()
        for i in range(self.tree_widget.topLevelItemCount()):
            top_item = self.tree_widget.topLevelItem(i)
            for j in range(top_item.childCount()):
                child_item = top_item.child(j)
                for k in range(child_item.childCount()):
                    attack_item = child_item.child(k)
                    if attack_item.checkState(0) == Qt.Checked:
                        checked_attacks.add(normalize_checkbox(attack_item.text(0)))
                    for l in range(attack_item.childCount()):
                        mitigation_item = attack_item.child(l)
                        if mitigation_item.checkState(0) == Qt.Checked:
                            checked_mitigations.add((
                                normalize_checkbox(mitigation_item.text(0)),
                                normalize_checkbox(attack_item.text(0))
                            ))
        return checked_attacks, checked_mitigations

    def on_item_changed(self, item, column):
        if item.checkState(column) == Qt.Checked:
            parent = item.parent()
            # If this is a mitigation and parent (attack/vuln) is not checked, auto-check parent
            if parent and "Attack or Vulnerability:" in parent.text(0):
                if parent.checkState(0) == Qt.Unchecked:
                    # Block recursive signals while changing parent
                    self.tree_widget.blockSignals(True)
                    parent.setCheckState(0, Qt.Checked)
                    self.tree_widget.blockSignals(False)
        elif item.checkState(column) == Qt.Unchecked:
            # If this is an attack/vulnerability and is being unchecked, uncheck all mitigations
            if "Attack or Vulnerability:" in item.text(0):
                for i in range(item.childCount()):
                    child = item.child(i)
                    if child.checkState(0) != Qt.Unchecked:
                        self.tree_widget.blockSignals(True)
                        child.setCheckState(0, Qt.Unchecked)
                        self.tree_widget.blockSignals(False)


    def on_generate_button_clicked(self):
        logger.info("generate button clicked")
        checked_attacks, checked_mitigations = self.get_checked_items()
        catalog_rows = get_instances(ThreatCatalog, {})
        db_attacks = {normalize_checkbox(row.attack_or_vulnerability_checkbox)
                      for row in catalog_rows if row.attack_or_vulnerability_checkbox}
        db_mitigations = {(normalize_checkbox(row.mitigation_checkbox),
                           normalize_checkbox(row.attack_or_vulnerability_checkbox))
                          for row in catalog_rows if row.mitigation_checkbox and row.attack_or_vulnerability_checkbox}
        # Compute changes
        attacks_to_add = checked_attacks - db_attacks
        attacks_to_remove = db_attacks - checked_attacks
        mitig_to_add = checked_mitigations - db_mitigations
        mitig_to_remove = db_mitigations - checked_mitigations
        # Save/Remove threats
        self.save_to_threat_table(attacks_to_add)
        self.remove_deselected_threat_data(attacks_to_remove)
        # Save/Remove mitigations
        self.save_to_security_controls_table(mitig_to_add)
        self.remove_deselected_mitigates_data(mitig_to_remove)
        # Optionally sync with other modules
        reply = QMessageBox.warning(None, 'Confirm', 'Sync Attack Tree & Security Controls with other modules?', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            pass
            # AS.sync_attack_tree_with_threats()
            # AS.sync_security_controls_with_riskcontrol()
            # AS.remove_from_riskcontrol_on_security_control_delete()

    def save_to_threat_table(self, to_add):
        logger.info("Save to ThreatCatalog table")
        for name in to_add:
            entry = ThreatCatalog(
                uuid=str(uuid.uuid4()),
                attack_or_vulnerability_checkbox=name,
                mitigation_checkbox="",
                security_controls="",
                threat_id="",
                created_by="system",
                updated_by="system"
            )
            create_instance(entry)
            logger.info(f"✅ Inserted attack '{name}' into ThreatCatalog.")

    def remove_deselected_threat_data(self, to_remove):
        logger.info("Remove Deselected Threat Data")
        for name in to_remove:
            deleted = delete_instance(
                ThreatCatalog, {'attack_or_vulnerability_checkbox': name}
            )
            if deleted:
                logger.info(f"✅ Deleted threat '{name}' from ThreatCatalog.")
            else:
                logger.info(f"⚠️ No matching threat entry found for '{name}'")

    def save_to_security_controls_table(self, to_add):
        logger.info("Save mitigations to ThreatCatalog and SecurityControls")
        existing_controls = get_instances(SecurityControls, {})
        existing_control_names = {c.name.strip() for c in existing_controls if c.name}
        for mitig, parent in to_add:
            # Add mitigation to SecurityControls if not present
            if mitig not in existing_control_names:
                new_id = securitycontrols_generate_id()
                entry = SecurityControls(
                    scc_id=new_id,
                    name=mitig,
                    description="",
                    comments="",
                    created_by="system",
                    updated_by="system",
                    is_deleted=False
                )
                create_instance(entry)
                logger.info(f"✅ Added mitigation '{mitig}' to SecurityControls")
            # Add mitigation link to ThreatCatalog
            entry = ThreatCatalog(
                uuid=str(uuid.uuid4()),
                attack_or_vulnerability_checkbox=parent,
                mitigation_checkbox=mitig,
                security_controls=mitig,
                threat_id="",
                created_by="system",
                updated_by="system"
            )
            create_instance(entry)
            logger.info(f"✅ Linked mitigation '{mitig}' to threat '{parent}' in ThreatCatalog.")

    def remove_deselected_mitigates_data(self, to_remove):
        logger.info("Remove Deselected Security Controls")
        all_catalog = get_instances(ThreatCatalog, {})
        mitigation_counts = {}
        for row in all_catalog:
            if row.mitigation_checkbox:
                name = normalize_checkbox(row.mitigation_checkbox)
                mitigation_counts[name] = mitigation_counts.get(name, 0) + 1
        for mitig, parent in to_remove:
            deleted = delete_instance(
                ThreatCatalog,
                {'mitigation_checkbox': mitig, 'attack_or_vulnerability_checkbox': parent}
            )
            if deleted:
                mitigation_counts[mitig] -= 1
                if mitigation_counts[mitig] <= 0:
                    delete_instance(SecurityControls, {'name': mitig})
                    logger.info(f"✅ Deleted mitigation '{mitig}' from SecurityControls")
            else:
                logger.info(f"⚠️ No matching mitigation pair ({mitig}, {parent}) found for deletion")

