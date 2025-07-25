
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy,
                             QMessageBox, QTabWidget, QTableWidget, QToolBar, QToolButton, 
                             QTableWidgetItem
                            )   
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
import models.Parameters as P
import models.helper as helper
from PyQt5.QtWidgets import QApplication

import sqlite3 
import Attack_Paths.RiskControl_Tree.views.RiskControlTree_Control_action as RCTCA
from Attack_Paths.RiskControl_Tree.views.riskcontrol_table_toolbar_panel import create_toolbar
from Attack_Paths.RiskControl_Tree.views.riskcontrol_tree_toolbar_panel import create_tree_toolbar
from Attack_Paths.views.attackpaths_table_panel import create_table_panel
from Attack_Paths.RiskControl_Tree.views.riskcontroltree_column_setup import Setup_Tabel_ColumnHeading
import models.TableStyle as TS
import models.ToolbarStyle as TBS
import controllers.DatabaseCreator as DB
import components.table.tree_row_indicator as TRI2
import components.table.multioption_selector as MOS
import controllers.TableValueHighlight as TVH
import controllers.CreateTabAction as CTA

import components.action_panel as action_panel
import styles.tree_panel_style as tree_panel_style
import styles.action_panel_style as action_panel_style
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
import utils.interface_utils as interfaces
import logging
from controllers.schema_manager import get_instances, bulk_insert_instances, delete_all_instance
from controllers.database_tables.attack_paths_tables import AttackTree, RiskControlTree, TechnicalTreeHome, AttackLeafNodes, RiskControlTreeHome

logger = logging.getLogger(__name__)


class RiskControl_Tree(QWidget):
    def __init__(self):
        super().__init__()
        logger.info("[RiskControl_Tree] __init__ called")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.Init_UI()

    def Init_UI(self):
        logger.info("[RiskControl_Tree] Init_UI called")
        self.tab_container = QTabWidget()
        self.tab_container.setContentsMargins(0,0,0,0)
        self.tab_container.setTabsClosable(False)
        self.tab_container.tabBar().setVisible(False)
        self.layout.addWidget(self.tab_container)

        self.home_panel = QWidget()
        self.home_panel_layout = QVBoxLayout()
        self.home_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.home_panel_layout.setSpacing(0)
        self.home_panel.setLayout(self.home_panel_layout)

        create_toolbar(self)
        self.home_panel_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)
        create_table_panel(self)
        self.index = None
        self.table.clicked.connect(self.get_index)
        self.action_panel_layout.addLayout(self.table_layout)
        self.home_panel_layout.addWidget(self.action_panel)
        Setup_Tabel_ColumnHeading(self)

        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.Submit_Changes)

        self.table_data_changed = False
        self.table.itemChanged.connect(self.table_data_changed_set_flag)
        self.table.itemChanged.connect(self.set_unsaved_changes)
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()

        self.child_panel = QWidget()
        self.child_panel_layout = QVBoxLayout()
        self.child_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.child_panel_layout.setSpacing(0)
        self.child_panel.setLayout(self.child_panel_layout)

        self.active_control_ct_class = None
        self.tab_control_instances = {}
        create_tree_toolbar(self)
        self.child_panel_layout.addWidget(self.toolbar)
        action_panel.create_action_panel(self)
        self.tree_submit_button.clicked.connect(self.on_save_button_click)

        self.action_tabwidget_panel = QWidget()
        self.action_tabwidget_panel_layout = QHBoxLayout()
        self.action_tabwidget_panel.setLayout(self.action_tabwidget_panel_layout)
        self.action_tabwidget_panel_layout.setContentsMargins(0,0,0,0)
        self.action_tabwidget_panel_layout.setSpacing(0)
        self.action_tabwidget_panel.setStyleSheet(tree_panel_style.action_panel_style)

        self.inner_tab_widget = QTabWidget()
        self.inner_tab_widget.setTabsClosable(True)
        self.inner_tab_widget.setStyleSheet(action_panel_style.action_panel_style)
        self.inner_tab_widget.tabCloseRequested.connect(self.Close_Tab)
        self.inner_tab_widget.currentChanged.connect(self.update_toolbar_tree_label)
        self.action_tabwidget_panel_layout.addWidget(self.inner_tab_widget)
        self.action_panel_layout.addWidget(self.action_tabwidget_panel)
        self.action_panel_layout.setContentsMargins(10,10,10,10)
        self.child_panel_layout.addWidget(self.action_panel)

        self.tab_container.addTab(self.home_panel, "Home")
        self.tab_container.addTab(self.child_panel, "Child Panel")
        self.previous_text = None
        logger.info("[RiskControl_Tree] Init_UI finished")

    def load_data(self):
        logger.info("[RiskControl_Tree] load_data called")
        self.tab_container.setCurrentIndex(0)
        self.loader = RoundLoader(self, label_text="Loading Risk Control Data...")
        self.loader.show()
        QApplication.processEvents()
        self.tab_container.setCurrentIndex(0)
        try:
            self.table.setRowCount(0)
            logger.info("[RiskControl_Tree] Fetching RiskControlTreeHome records")
            rows = get_instances(RiskControlTreeHome)
            logger.debug(f"[RiskControl_Tree] ORM get_instances returned {len(rows) if rows else 0} rows")
            if not rows:
                logger.info("[RiskControl_Tree] No RiskControlTreeHome rows found")
                return
            for row_idx, row in enumerate(rows):
                logger.debug(f"[RiskControl_Tree] Adding row {row_idx}: id={row.id} name={row.name}")
                self.table.insertRow(row_idx)
                self.table.setRowHeight(row_idx, 40)
                sidebar = TRI2.SidebarWidget(parent=self, index=row_idx)
                self.table.setCellWidget(row_idx, 0, sidebar)
                id_item = QTableWidgetItem(row.id)
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 1, id_item)
                name_item = QTableWidgetItem(row.name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 2, name_item)
                mitigates_item = QTableWidgetItem(row.mitigates)
                mitigates_item.setFlags(mitigates_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 3, mitigates_item)
                comments_item = QTableWidgetItem(row.comment)
                comments_item.setFlags(comments_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, 5, comments_item)
            if self.table.rowCount() > 0:
                self.table.setCurrentCell(0, 1)
            self.table_data_changed = False
            interfaces.unsaved_changes = False
            logger.info("[RiskControl_Tree] Table data loaded, now syncing tabs")
            all_rows = get_instances(RiskControlTreeHome)
            available_ids = [r.id for r in all_rows]
            for i in reversed(range(self.inner_tab_widget.count())):
                if self.inner_tab_widget.tabText(i) not in available_ids:
                    logger.debug(f"[RiskControl_Tree] Removing orphaned tab: {self.inner_tab_widget.tabText(i)}")
                    self.inner_tab_widget.removeTab(i)
            if not available_ids:
                for i in reversed(range(self.inner_tab_widget.count())):
                    self.inner_tab_widget.removeTab(i)
            logger.info("[RiskControl_Tree] load_data finished successfully")
        except Exception as e:
            logger.error(f"[RiskControl_Tree] Error loading data: {e}")
            QMessageBox.critical(None, "Database Error", f"Error loading data: {e}")
        finally:
            self.loader.close()

    def on_row_selection_changed(self):
        logger.info("[RiskControl_Tree] on_row_selection_changed called")
        temp = interfaces.unsaved_changes
        TVH.on_row_selection_changed2(self.table)
        interfaces.unsaved_changes = temp

    def get_index(self, index):
        logger.info(f"[RiskControl_Tree] get_index called: {index}")
        self.index = index
        print("index: ", index)

    def open_tree(self):
        logger.info("[RiskControl_Tree] open_tree called")
        sender = self.sender()
        if sender:
            sidebar_widget = sender.parent()
            for row in range(self.table.rowCount()):
                if self.table.cellWidget(row, 0) == sidebar_widget:
                    logger.debug(f"[RiskControl_Tree] Sidebar row selected: {row}")
                    self.table.selectRow(row)
                    self.index = self.table.model().index(row, 0)
                    TVH.on_row_selection_changed2(self.table)
                    break

        if self.index is None or not self.index.isValid():
            logger.warning("[RiskControl_Tree] Invalid selection index in open_tree")
            QMessageBox.warning(None, "Selection Error", "Unable to determine the selected row.")
            if self.round_loader:
                self.round_loader.accept()
                self.round_loader = None
            self.setEnabled(True)
            return

        open_tree_enable = True
        if self.table_data_changed:
            logger.info("[RiskControl_Tree] Table data changed, checking autosave before switch")
            if not interfaces.autosave_enabled:
                message_reply = QMessageBox.warning(None, "Warning", "Please save the changes before switching to the edit page.", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if message_reply == QMessageBox.Ok:
                    self.Submit_Changes()
            else:
                self.Submit_Changes()

        row = self.index.row()
        item_id = self.table.itemFromIndex(self.index.siblingAtColumn(1)).text()
        item_name = self.table.itemFromIndex(self.index.siblingAtColumn(2)).text()
        logger.info(f"[RiskControl_Tree] Editor Opened for id={item_id} name={item_name}")

        self.setEnabled(False)
        if not hasattr(self, "round_loader") or self.round_loader is None:
            self.round_loader = RoundLoader(self, label_text='Loading...')
            self.round_loader.show()
            QApplication.processEvents()

        try:
            tab_index = self.is_tab_available(item_id)
            if tab_index != -1:
                logger.info(f"[RiskControl_Tree] Tab already exists for {item_id}, switching to index {tab_index}")
                self.inner_tab_widget.setCurrentIndex(tab_index)
                self.active_control_ct_class = self.tab_control_instances[f'{self.inner_tab_widget.tabText(tab_index)}']
                self.active_control_ct_class.Load_RiskControlTree()
            else:
                logger.info(f"[RiskControl_Tree] Creating new tab for {item_id}")
                tab_header = CTA.TabHeader(title=item_id, close_callback=lambda: self.Close_Tab(self.inner_tab_widget.indexOf(tab_header)))
                control_ct_class = RCTCA.ControlCTClass(self)
                if item_id not in self.tab_control_instances:
                    self.tab_control_instances[item_id] = control_ct_class
                control_ct_class.Create_RiskControlTree_Tab(item_id, item_name)
                self.active_control_ct_class = self.tab_control_instances[item_id]
                self.tree_toolbar_label.setText(item_name)
            if open_tree_enable:
                self.tab_container.setCurrentIndex(1)
        except Exception as e:
            logger.error(f"[RiskControl_Tree] Error opening Risk Control Tree: {e}")
            QMessageBox.critical(None, "Error", f"An error occurred: {e}")
        finally:
            self.setEnabled(True)
            if self.round_loader:
                self.round_loader.accept()
                self.round_loader = None

    def update_button_states(self):
        logger.debug("[RiskControl_Tree] update_button_states called")
        row_count = self.table.rowCount()
        has_selection = bool(self.table.selectionModel().selectedRows())
        self.submit_button.setEnabled(row_count > 0)

    def Submit_Changes(self):
        logger.info("[RiskControl_Tree] Submit_Changes called")
        self.table.setFocus()
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()
        orm_objects = []
        logger.info("[RiskControl_Tree] Deleting all existing RiskControlTreeHome rows")
        delete_all_instance(RiskControlTreeHome, {})  # Deletes all
        for row in range(row_count):
            row_data = {}
            for col in range(col_count):
                header = self.table.horizontalHeaderItem(col).text().lower()
                if col == 4:  # Assumptions column (multi-select combo box)
                    combo_box = self.table.cellWidget(row, col)
                    if combo_box is not None:
                        selected_items = combo_box.selected_items()
                        assumption_ids = [item.split("::")[0] for item in selected_items]
                        row_data['assumptions'] = ", ".join(assumption_ids)
                    else:
                        row_data['assumptions'] = ""
                else:
                    item = self.table.item(row, col)
                    row_data[header] = item.text() if item is not None else ""
            orm_obj = RiskControlTreeHome(
                id=row_data.get('id', ""),
                name=row_data.get('name', ""),
                mitigates=row_data.get('mitigates', ""),
                assumptions=row_data.get('assumptions', ""),
                comment=row_data.get('comment', "")
            )
            orm_objects.append(orm_obj)
        logger.info(f"[RiskControl_Tree] Prepared {len(orm_objects)} ORM objects for bulk insert")
        self.update_button_states()
        bulk_insert_instances(orm_objects)
        logger.info("[RiskControl_Tree] Data Saved Successfully")
        self.table_data_changed = False
        interfaces.unsaved_changes = False

    def update_toolbar_tree_label(self, index):
        logger.info(f"[RiskControl_Tree] update_toolbar_tree_label called for tab index {index}")
        from controllers.schema_manager import get_instance
        from models.risk_control import RiskControlTreeHome  # Adjust the import to match your project
        tab_id = self.inner_tab_widget.tabText(index)
        if (
            self.inner_tab_widget.currentIndex() == index and
            self.active_control_ct_class == self.tab_control_instances.get(tab_id)
        ):
            logger.info("[RiskControl_Tree] Same tab selected, skipping update")
            return
        interfaces.previous_module = None
        if interfaces.autosave_enabled and interfaces.previous_tree and interfaces.unsaved_changes:
            logger.info("[RiskControl_Tree] Autosave enabled, saving previous tree")
            interfaces.previous_tree.Save_Tree()
        elif not interfaces.autosave_enabled and interfaces.previous_tree and interfaces.unsaved_changes:
            reply = QMessageBox.question(
                None, 'Unsaved Changes',
                "You have unsaved changes. Do you want to save them before switching?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                logger.info("[RiskControl_Tree] User chose to save previous tree")
                interfaces.previous_tree.Save_Tree()
            elif reply == QMessageBox.No:
                logger.info("[RiskControl_Tree] User chose to discard changes")
                interfaces.unsaved_changes = False

        if not hasattr(self, "round_loader") or self.round_loader is None:
            self.round_loader = RoundLoader(self, label_text='Loading Tab...')
            self.round_loader.show()
            QApplication.processEvents()
        try:
            rc_tree_home = get_instance(RiskControlTreeHome, {"rc_id": tab_id})
            if rc_tree_home:
                logger.info(f"[RiskControl_Tree] Set toolbar label to {rc_tree_home.name}")
                self.tree_toolbar_label.setText(rc_tree_home.name)
                self.active_control_ct_class = self.tab_control_instances[tab_id]
                interfaces.previous_tree = self.active_control_ct_class
                if not interfaces.tool_reset_enable:
                    self.active_control_ct_class.Load_RiskControlTree()
                interfaces.tree_tab_panel['RiskControlTree'] = (self.inner_tab_widget, self.tab_control_instances)
        except Exception as e:
            logger.error(f"[RiskControl_Tree] Error updating toolbar tree label: {e}")
            QMessageBox.critical(None, "Database Error", f"Error loading tree label: {e}")
        finally:
            if hasattr(self, "round_loader") and self.round_loader:
                self.round_loader.close()
                self.round_loader = None

    def on_save_button_click(self):
        logger.info("[RiskControl_Tree] on_save_button_click called")
        self.round_loader = RoundLoader(self, label_text='Saving...')
        self.round_loader.show()
        QApplication.processEvents()
        try:
            if self.active_control_ct_class:
                logger.info("[RiskControl_Tree] Calling Save_Tree on active_control_ct_class")
                self.active_control_ct_class.Save_Tree()
                self.round_loader.accept()
                logger.info("[RiskControl_Tree] Save completed successfully")
        except Exception as e:
            self.round_loader.accept()
            logger.error(f"[RiskControl_Tree] Error saving tree: {e}")
            QMessageBox.critical(None, "Error", f"Error saving Risk Control Tree: {str(e)}")

    def Close_Tab(self, index):
        logger.info(f"[RiskControl_Tree] Close_Tab called for tab index {index}")
        if self.inner_tab_widget.tabText(index):
            self.tab_control_instances.pop(f'{self.inner_tab_widget.tabText(index)}', None)
            interfaces.tree_tab_panel['RiskControlTree'] = (self.inner_tab_widget, self.tab_control_instances)
        self.inner_tab_widget.removeTab(index)
        tab_count = self.inner_tab_widget.count()
        if tab_count == 0:
            self.tab_container.setCurrentIndex(0)
            interfaces.previous_tree = None
            if interfaces.tool_reset_enable != True:
                interfaces.previous_module = self
                self.load_data()

    def table_data_changed_set_flag(self):
        logger.debug("[RiskControl_Tree] table_data_changed_set_flag called")
        self.table_data_changed = True
        self.update_button_states()

    def set_unsaved_changes(self):
        logger.debug("[RiskControl_Tree] set_unsaved_changes called")
        interfaces.unsaved_changes = True

    def is_tab_available(self, item_id):
        logger.debug(f"[RiskControl_Tree] is_tab_available called for item_id={item_id}")
        for index in range(self.inner_tab_widget.count()):
            if self.inner_tab_widget.tabText(index) == f"{item_id}":
                logger.debug(f"[RiskControl_Tree] Tab found at index {index}")
                return index
        logger.debug("[RiskControl_Tree] Tab not found")
        return -1
