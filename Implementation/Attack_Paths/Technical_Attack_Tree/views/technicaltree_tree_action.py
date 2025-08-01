"""
Module: Technical Attack Tree UI Panel      \n 
File: technicaltree_tree_action.py      \n
Layer: UI / View Layer      \n
Component ID:          \n
Requirement IDs:       \n
Author: Vijaya karagi  \n
Created On: 2025-07-08     \n
Updated By:   \n
Updated On:   \n
Version: V 3.0      \n

Purpose:
--------
Provides the UI logic for creating and displaying a Technical Attack Tree tab using PyQt5.
It sets up the graphics view, loads data from the database, and interfaces with the 
TechnicalTreeScene and its node/arrow layout system.

Description:
------------
This module defines the `TechnicalATClass`, a QWidget subclass that represents a
dynamic, graphical, and interactive Technical Attack Tree editor. It embeds a 
custom QGraphicsView and scene, connects user actions to the internal data model, 
and renders hierarchical risk assessment trees from saved or new data.

Responsibilities
----------------
- Create and manage technical tree tabs dynamically inside a tab widget.
- Setup QGraphicsScene and QGraphicsView with dotted background and smooth rendering.
- Load tree data from database and initialize scene with hierarchy.
- Persist tree state and track unsaved changes.
- Interface with database, layout manager, and shared interfaces.

Dependencies:
-------------
- PyQt5 (QtCore, QtGui, QtWidgets)
- Attack_Paths.components.customgraphics_view
- Attack_Paths.Technical_Attack_Tree.controllers.technicaltree_scene
- styles.tree_panel_style
- models.ScrollBarStyle
- controllers.DatabaseCreator
- utils.interface_utils

Limitations
-----------
- Currently loads only sample structure from in-memory dict, not DB records.
- No visual undo/redo or tree diff features.
- Tree layout spacing is static.
- Assumes only one tree per tab and loads only root-level hierarchy.

Improvements
------------
- Implement live sync with DB records via ORM layer.
- Integrate undo/redo tracking.
- Add visual feedback for AFR calculation errors.
- Improve dynamic zoom and drag performance.
- Enable tab rename and tree export/import.

Change History:
---------------
+----------------+----------------------+----------------------------------------+----------------------+
| Version        | Date                 | Change                                 | Author               |
+================+======================+========================================+======================+
| V 3.0          | 2025-07-08           | Initial version created                | Vijaya Karagi        |
+----------------+----------------------+----------------------------------------+----------------------+
|                |                      |                                        |                      |
+----------------+----------------------+----------------------------------------+----------------------+

"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QMessageBox
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt
import controllers.DatabaseCreator as DB
import models.ScrollBarStyle as SBS
import styles.tree_panel_style as tree_panel_style
import utils.interface_utils as interfaces
from Attack_Paths.components.customgraphics_view import CustomGraphicsView
from Attack_Paths.Technical_Attack_Tree.controllers.technicaltree_scene import TechnicalTreeScene
from components.threading_decorator import run_in_thread
from controllers.schema_manager import get_instances, create_instance, get_max_numeric_suffix
from Attack_Paths.Technical_Attack_Tree.controllers.database_to_tat import build_ta_tree_json
from controllers.database_tables.attack_paths_tables import NodeType, RiskControlTreeHome, TechnicalAttackTree, AttackIntermediateNodes, AttackLeafNodes

import logging
logger = logging.getLogger(__name__)

class TechnicalATClass(QWidget):
    """
    Widget class that encapsulates a Technical Attack Tree editor tab.

    This class handles the graphical view and scene setup, data loading,
    and tree initialization for a specific technical tree ID.
    """
    def __init__(self, parent=None):
        """
        Initializes the technical attack tree editor.

        Args:
            parent (QWidget): Optional parent widget.
        """
        super().__init__(parent)
        logger.info("Technical Tree Class")
        self.parent = parent 

    # Create a tree tab for Technical tree action
    def Create_TechnicalTree_Tab(self, technical_id, technical_name):
        """
        Creates a new tab (or reuses an existing one) for the technical tree.

        Args:
            technical_id (str): Unique ID of the technical attack tree.
            technical_name (str): Display name or description.
        """
        logger.info(f"Create Technical Tree {technical_id} Tab")
        self.technical_id = technical_id
        self.technical_name = technical_name
        for index in range(self.parent.inner_tab_widget.count()):
            if self.parent.inner_tab_widget.tabText(index) == f"{technical_id}":
                self.parent.inner_tab_widget.setCurrentIndex(index)
                self.Load_TechnicalTree()
                return

        # Create Action tab and its layout
        self.action_tab = QWidget()
        self.action_tab_layout = QVBoxLayout(self.action_tab)
        self.action_tab_layout.setContentsMargins(2,0,2,2)
        self.action_tab.setStyleSheet(tree_panel_style.action_panel_style)

        self.Setup_GraphicsScene()
        
        # Add the action tab to the tab widget
        self.parent.inner_tab_widget.addTab(self.action_tab, f"{self.technical_id}")
        self.parent.inner_tab_widget.setCurrentWidget(self.action_tab)

    # Create a canvas for the Technical tree
    def Setup_GraphicsScene(self):
        """
        Initializes the QGraphicsScene and attaches it to a custom graphics view.
        Applies dotted background pattern and smooth rendering styles.
        """
        # Create a QGraphicsScene
        self.scene = TechnicalTreeScene(self.technical_id)

        # Use the CustomGraphicsView instead of QGraphicsView
        self.graphics_view = CustomGraphicsView(self.scene, self)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphics_view.setEnabled(True)
        self.graphics_view.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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
    
    # Save Technical tree
    def Save_Tree(self): 
        """
        Persists the current technical tree structure to internal state or disk.
        Flags unsaved_changes = False after saving.
        """
        logger.info("Save Technical Tree")
        self.scene.save_tree()
        interfaces.previous_tree = self
        interfaces.unsaved_changes = False
    
    # Refresh Technical tree
    def Load_TechnicalTree(self):
        """
        Loads a technical tree from the database or fallback template.
        Updates the QGraphicsScene with the deserialized structure.
        If no data found, initializes a default head node.
        """
        logger.info("Load Technical Tree")
        try:
            self.scene.last_intermediate_node_id = get_max_numeric_suffix(AttackIntermediateNodes, 'id','Nd')
            self.scene.last_leaf_node_id = get_max_numeric_suffix(AttackLeafNodes, 'id','Lf')
            tat_nodes = get_instances(TechnicalAttackTree, {'tree_id':self.technical_id, 'is_deleted':False})
            
            if tat_nodes:
                tat_json_tree = build_ta_tree_json(tat_nodes)
                self.scene.load_tree(tat_json_tree)
            else: 
                self.scene.initialize_parameters()
                self.scene.add_head_node(f"{self.technical_id}_node_0", self.technical_id, self.technical_name, 0, 0, "0", "High", "AND")
                
            interfaces.previous_tree = self
            interfaces.unsaved_changes = True

        except Exception as e:
            self.scene.initialize_parameters()
            self.scene.add_head_node(f"{self.technical_id}_node_0", self.technical_id, self.technical_name, 0, 0, "0", "High", "AND")
            interfaces.previous_tree = self
            interfaces.unsaved_changes = True
            QMessageBox.critical(None, "Load Error", f"Failed to load the tree: {e}")
