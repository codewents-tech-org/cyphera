import json
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QMessageBox
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt
import Target_Of_Evaluation.Scope.Scope_MindMap.Mindmap_home as MindmapHome
import Target_Of_Evaluation.Scope.Scope_MindMap.TreeBuilder as TB
import controllers.DatabaseCreator as DB
import Target_Of_Evaluation.Scope.controllers.customgraphics as CG
import Target_Of_Evaluation.Scope.controllers.scope_synchronization as Sync
import Target_Of_Evaluation.Scope.controllers.scope_attack_tree_generator as SATG
import Target_Of_Evaluation.Scope.controllers.scope_synchronization as TSS
from Target_Of_Evaluation.Scope.controllers.mindmap_manager import update_mindmap_tree
from Target_Of_Evaluation.Scope.Scope_MindMap.tree_id_converter import rename_mindmap_node_ids_flat
from controllers.schema_manager import get_instances
from controllers.tablemodel import ScopeHomeMindmap, ScopeMindmaps, MindmapNodeType
import Target_Of_Evaluation.Scope.controllers.scope_synchronizations as Synch
import Target_Of_Evaluation.Scope.Scope_MindMap.mindmap_at_generator as MindmapATGen

import models.ScrollBarStyle as SBS
import styles.action_panel_style as action_panel_style
import styles.tree_panel_style as tree_panel_style
import utils.interface_utils as interfaces
import logging

logger = logging.getLogger(__name__)

class MindMapClass(QWidget):
    def __init__(self, parent=None):
        logger.info("Mindmap Class")
        super().__init__(parent)
        self.parent = parent 
        
    # Create a control tab for mindmap tree action
    def Create_MindMap_Tab(self, scope_id, scope_name):
        logger.info("Mindmap tab Creation")
        self.scope_id = scope_id
        self.scope_name = scope_name
        for index in range(self.parent.inner_tab_widget.count()):
            if self.parent.inner_tab_widget.tabText(index) == f"{scope_id}":
                self.parent.inner_tab_widget.setCurrentIndex(index)
                return

        # Create Action tab and its layout
        self.action_tab = QWidget()
        self.action_tab_layout = QVBoxLayout(self.action_tab)
        self.action_tab_layout.setContentsMargins(2,0,2,2)
        self.action_tab.setStyleSheet(tree_panel_style.action_panel_style)

        self.Setup_GraphicsScene()
        
        # Add the action tab to the tab widget
        self.parent.inner_tab_widget.addTab(self.action_tab, f"{self.scope_id}")
        self.parent.inner_tab_widget.setCurrentWidget(self.action_tab)

        self.Load_MindMap()

    # Create a canvas for the mindmap tree
    def Setup_GraphicsScene(self):
        logger.info("Setting Up Graphics Scene")
        # Create a QGraphicsScene
        #self.scene = QGraphicsScene()
        self.scene = MindmapHome.MMScene()
        # Use the CustomGraphicsView instead of QGraphicsView
        self.graphics_view = CG.CustomGraphicsView(self.scene, self)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphics_view.setEnabled(True)
        self.graphics_view.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        #self.graphics_view.setAlignment(Qt.AlignHCenter)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.graphics_view.setStyleSheet(action_panel_style.action_panel_style)
        self.graphics_view.setStyleSheet(SBS.GraphicsView_ScrollBar_style)
        self.graphics_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.graphics_view.setStyleSheet(tree_panel_style.tree_style)

        # Set background as a dotted design
        dot_pattern = QPixmap(20, 20)  # Create a 20x20 dot pattern
        dot_pattern.fill(Qt.transparent)  # Make the background transparent

        # Draw dots on the pattern
        painter = QPainter(dot_pattern)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#EAEAEA")))  # Dots color
        painter.drawEllipse(10, 10, 4, 4)  # Dot size and position
        painter.end()

        # Apply the dot pattern as the background brush
        self.graphics_view.setBackgroundBrush(QBrush(dot_pattern))

        # Add the QScrollArea to the action tab layout
        self.action_tab_layout.addWidget(self.graphics_view)

    def Save_Tree(self):
        logger.info("Submit button clicked. Saving Mindmap")
        data = self.scene.getPostionData()
        update_mindmap_tree(self.scope_id, data)

        # Display confirmation dialog
        if self.scope_id:
            Synch.synch_mindmap_changes(self.scope_id, data['node_text'])
            # Synch.sync_linked_modules()
        interfaces.unsaved_changes = False

    # Refresh mindmap tree
    def Load_MindMap(self):
        logger.info("Mindmapp Loading")
        sc_mind_map_nodes = get_instances(ScopeMindmaps, {'scope_id':self.scope_id})
        sc_mind_map_nodes = rename_mindmap_node_ids_flat(sc_mind_map_nodes)
        if len(sc_mind_map_nodes) > 0:
            tree_builder = TB.TreeBuilder(sc_mind_map_nodes)
            json_mm_data  = tree_builder.build()
            resultJsonString =  json.dumps(json_mm_data)   
            resultJsonObjObj = json.loads(resultJsonString)
             
            self.scene.load_existing_data=resultJsonObjObj[0]
            self.scene.loadData(self.scene.load_existing_data)
            self.scene.scope_id = self.scope_id
            self.scene.scope_name = self.scope_name
            self.graphics_view.show()
            
        else: 
            #print("Load_MindMap else part")   
            self.scene.scope_id = self.scope_id
            self.scene.scope_name = self.scope_name
            self.scene.add_root_node()
            self.graphics_view.show()
        interfaces.unsaved_changes = False

