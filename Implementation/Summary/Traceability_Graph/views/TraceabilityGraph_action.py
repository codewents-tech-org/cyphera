# Analysis_action.py
                             
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QLabel, QFrame, QGridLayout, QScrollArea, QSpacerItem
from PyQt5.QtGui import QPainter, QFont, QPen, QPainterPath, QColor, QPixmap, QBrush
from PyQt5.QtCore import Qt, QPointF, QEvent
import sqlite3
from controllers.schema_manager import get_instances
import models.Parameters as P
import models.helper as helper
import controllers.DatabaseCreator as DB
import Summary.Traceability_Graph.controllers.Traceability_customgraphics as TC

from Summary.Traceability_Graph.views.traceabilitygraph_toolbar_panel import create_toolbar
import styles.traceabilitygraph_panel_style as tree_panel_style
import styles.action_panel_style as action_panel_style
import logging
logger = logging.getLogger(__name__)


class TraceabilityGraph_Module(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)        
        self.scroll_area = None
        self.header_layout = None
        self.header_scroll_area = None  # Add this line
        self.selected_box = None
        self.initUI()
        self.installEventFilter(self)

    def initUI(self):
        # Main widget and layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout) 

        # Add the toolbar and table to the left panel layout
        create_toolbar(self)
        self.action_panel = QWidget()
        self.action_panel_layout = QVBoxLayout()
        self.action_panel.setLayout(self.action_panel_layout)
        self.action_panel.setContentsMargins(0,0,0,0)
        self.action_panel_layout.setContentsMargins(10,10,10,10)
        self.action_panel_layout.setSpacing(0)
        self.action_panel.setStyleSheet(action_panel_style.action_panel_style)
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.action_panel)

    def load_data(self):
        # Remove the old scroll area from the layout
        if self.scroll_area is not None:
            self.main_layout.removeWidget(self.scroll_area)
            self.header_scroll_area.deleteLater()
            self.scroll_area.deleteLater()  # Clean up the old widget

        # Create a new scroll area for dynamic content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setContentsMargins(10, 10, 10, 10)
        self.scroll_area.setStyleSheet(tree_panel_style.trace_panel_style)

        # Create a grid layout to organize the threat and damage scenario boxes
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setVerticalSpacing(30)
        self.grid_layout.setHorizontalSpacing(0)

        # Set fixed widths for specific columns
        self.grid_layout.setColumnMinimumWidth(1, 200)
        self.grid_layout.setColumnMinimumWidth(3, 200)
        self.grid_layout.setColumnMinimumWidth(5, 200)
        self.grid_layout.setColumnMinimumWidth(7, 200)

        self.grid_layout.setColumnStretch(1, 0)
        self.grid_layout.setColumnStretch(3, 0)
        self.grid_layout.setColumnStretch(5, 0)
        self.grid_layout.setColumnStretch(7, 0)

        # Create a layout for the header labels
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(0)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setStyleSheet(tree_panel_style.trace_panel_style)

        # Add Heading_label_list label
        for index, label_text in enumerate(helper.TraceabilityGraph_header):
            item_label = QLabel(label_text)
            item_label.setFont(tree_panel_style.traceabilitygraph_label_font)
            item_label.setFixedSize(300, 60)
            item_label.setWordWrap(True)
            item_label.setAlignment(Qt.AlignCenter)
            item_label.setStyleSheet("border: none;")
            self.header_layout.addWidget(item_label, alignment=Qt.AlignTop)

        # Create a new scroll area for the header
        self.header_scroll_area = QScrollArea()
        self.header_scroll_area.setWidgetResizable(True)
        self.header_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide the scrollbar
        self.header_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.header_scroll_area.setStyleSheet(tree_panel_style.trace_header_panel_style)
        self.header_scroll_area.setFixedHeight(60)

        # Create a widget to hold the header layout
        header_widget = QWidget()
        header_widget.setLayout(self.header_layout)
        header_widget.setStyleSheet("border: none;")
        self.header_scroll_area.setWidget(header_widget)

        # Add the header scroll area to the main layout
        # self.main_layout.addWidget(self.header_scroll_area)
        self.action_panel_layout.addWidget(self.header_scroll_area)

        # Initialize scroll_content_widget as an instance of CustomScrollContent
        self.scroll_content_widget = TC.CustomScrollContent()

        # Create a vertical layout for the content inside the scroll area
        self.dynamic_content_layout = QVBoxLayout(self.scroll_content_widget)

        # Set expanding policy to allow horizontal expansion
        self.scroll_content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the scrollable content to the scroll area
        self.scroll_area.setWidget(self.scroll_content_widget)

        # self.main_layout.addWidget(self.scroll_area)
        self.action_panel_layout.addWidget(self.scroll_area)

        # Connect the horizontal scroll bars of the header and content scroll areas
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.header_scroll_area.horizontalScrollBar().setValue)

        # Fetch and display data
        self.fetch_data()
        self.display_data()

    from controllers.schema_manager import get_instances

    def fetch_data(self):
        logger.info("Fetching Data for Traceability graph")
        try:
            # ORM fetches instead of direct SQL
            threat_rows = get_instances(Threat)
            damage_scenario_rows = get_instances(DamageScenario)
            security_goals_rows = get_instances(SecurityGoal)
            security_claims_rows = get_instances(SecurityClaim)
            security_controls_rows = get_instances(SecurityControl)
            risk_rows = get_instances(RiskData)
            risk_data_rows = get_instances(RiskData)

            self.damage_scenarios_list = {row.ds_id: row.name for row in damage_scenario_rows}
            self.threats_list = {row.threat_id: row.name for row in threat_rows}
            self.risk_list = {}

            for risk in risk_rows:
                # adjust attributes according to your model
                threat_id = risk.threat.strip().split(" - ")[0]
                threat_name = risk.threat.strip().split(" - ")[1]
                damage_id = risk.damage.strip().split(" - ")[0]
                damage_name = risk.damage.strip().split(" - ")[1]
                self.risk_list[f"{threat_id} {damage_id}"] = (damage_name, threat_name)

            self.security_goals_list = {row.id: row.name for row in security_goals_rows}
            self.security_claims_list = {row.id: row.name for row in security_claims_rows}
            self.security_controls_list = {row.id: row.name for row in security_controls_rows}

            # You may need to do a double-loop or dict comprehension for these advanced joins
            self.security_goals_control_list = {}
            for sg in security_goals_rows:
                control_lists = []
                for sc in security_controls_rows:
                    sg_data = getattr(sc, "properties", "")  # or correct field name
                    sg_list = sg_data.strip().split(', ')
                    sg_id_list = [sg_text.split('::')[0] for sg_text in sg_list]
                    if sg.id in sg_id_list and sc.id not in control_lists:
                        control_lists.append(sc.id)
                self.security_goals_control_list[sg.id] = control_lists

            self.traceability_link = {}
            path_count = 0
            for risk in risk_data_rows:
                damage_id = risk.damage.strip().split(' - ')[0]
                threat_id = risk.threat.strip().split(' - ')[0]
                claims_list = risk.security_claims.strip().split(', ') if risk.security_claims else []
                goals_list = risk.security_goals.strip().split(', ') if risk.security_goals else []
                controls_list = risk.mitigated_by.strip().split(', ') if risk.mitigated_by else []

                for goal, control_list in self.security_goals_control_list.items():
                    if goal in goals_list:
                        if len(control_list) > 0:
                            for control in control_list:
                                self.traceability_link[f'path_{path_count}'] = {
                                    'damage': damage_id,
                                    'threat': threat_id,
                                    'risk': f"{threat_id} {damage_id}",
                                    'goal': goal,
                                    'claim': '',
                                    'control': control
                                }
                                path_count += 1
                        else:
                            self.traceability_link[f'path_{path_count}'] = {
                                'damage': damage_id,
                                'threat': threat_id,
                                'risk': f"{threat_id} {damage_id}",
                                'goal': goal,
                                'claim': '',
                                'control': ''
                            }
                            path_count += 1
                    else:
                        if len(control_list) > 0:
                            for control in control_list:
                                self.traceability_link[f'path_{path_count}'] = {
                                    'damage': '',
                                    'threat': '',
                                    'risk': '',
                                    'goal': goal,
                                    'claim': '',
                                    'control': control
                                }
                                path_count += 1
                        else:
                            self.traceability_link[f'path_{path_count}'] = {
                                'damage': '',
                                'threat': '',
                                'risk': '',
                                'goal': goal,
                                'claim': '',
                                'control': ''
                            }
                            path_count += 1

                for sc_id in claims_list:
                    if len(controls_list) > 0:
                        for control in controls_list:
                            self.traceability_link[f'path_{path_count}'] = {
                                'damage': damage_id,
                                'threat': threat_id,
                                'risk': f"{threat_id} {damage_id}",
                                'goal': '',
                                'claim': sc_id,
                                'control': ''
                            }
                            path_count += 1
                    else:
                        self.traceability_link[f'path_{path_count}'] = {
                            'damage': damage_id,
                            'threat': threat_id,
                            'risk': f"{threat_id} {damage_id}",
                            'goal': '',
                            'claim': sc_id,
                            'control': ''
                        }
                        path_count += 1

        except Exception as e:
            logger.error(f"Error: {e}")

    def create_Custom_Box(self, box_id='', text=''):
        # Create the outer frame for the custom box
        custom_box = QFrame()
        custom_box.setFrameShape(QFrame.Box)
        custom_box.setFrameShadow(QFrame.Plain)
        custom_box.setFixedWidth(400)
        
        custom_box.setStyleSheet(tree_panel_style.traceabilitygraph_box_style)
        
        # Set up the layout for the custom box
        custom_box_layout = QVBoxLayout()
        custom_box_layout.setContentsMargins(1, 1, 5, 1)
        
        spacer_above_id = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        custom_box_layout.addItem(spacer_above_id)
        # Create the ID label
        custom_id_label = QLabel(f"{box_id}")
        custom_id_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_id_label.setFixedHeight(25)
        custom_id_label.setAlignment(Qt.AlignLeft)
        custom_id_label.setStyleSheet("border: none; padding-left: 10px; font-weight: bold; font-size: 18px;")  # Customize ID label style
        custom_box_layout.addWidget(custom_id_label)

        spacer = QSpacerItem( 0, QSizePolicy.Fixed)  
        custom_box_layout.addItem(spacer)
        
        # Create the Name label
        custom_name_label = QLabel(f"{text}")
        custom_name_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_name_label.setAlignment(Qt.AlignLeft)
        custom_name_label.setWordWrap(True)  # Enable word wrapping for long names
        custom_name_label.setStyleSheet("border: none; padding-left: 10px;")  # Customize Name label style
        custom_name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    
        custom_box_layout.addWidget(custom_name_label)
        

            
        # Set the layout and return the box
        custom_box.setLayout(custom_box_layout)
        custom_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        custom_box.setMaximumHeight(custom_name_label.sizeHint().height() + 50)  # Dynamic height based on text
        
        # Optional: Attach a click event handler
        custom_box.mousePressEvent = lambda event, box=custom_box: self.on_box_clicked(event, box)
        
        return custom_box

    def create_Custom_Box_multivalue(self, box_id='', ds_text='', th_text=''):
        # Create the outer frame for the custom box
        custom_box = QFrame()
        custom_box.setFrameShape(QFrame.Box)
        custom_box.setFrameShadow(QFrame.Plain)
        custom_box.setFixedWidth(400)
        custom_box.setStyleSheet(tree_panel_style.traceabilitygraph_box_style)
        
        # Set up the layout for the custom box
        custom_box_layout = QVBoxLayout()
        custom_box_layout.setContentsMargins(1, 1, 5, 1)
        
        spacer_above_id = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        custom_box_layout.addItem(spacer_above_id)

        custom_ts_label = QLabel(f"{box_id}")
        custom_box_layout.addWidget(custom_ts_label)
        custom_ts_label.setVisible(False)

        ds_id = box_id.split(' ')[0]
        th_id = box_id.split(' ')[1]
        # Create the ID label
        custom_ds_label = QLabel("Damage Scenario")
        custom_ds_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_ds_label.setFixedHeight(25)
        custom_ds_label.setAlignment(Qt.AlignLeft)
        custom_ds_label.setStyleSheet("border: none; padding-left: 10px; font-weight: bold; font-size: 18px; text-decoration: underline;")  # Customize ID label style
        custom_box_layout.addWidget(custom_ds_label)

        spacer = QSpacerItem( 0, QSizePolicy.Fixed)  
        custom_box_layout.addItem(spacer)

        # Create the ID label
        custom_ds_id_label = QLabel(f"{ds_id}")
        custom_ds_id_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_ds_id_label.setFixedHeight(25)
        custom_ds_id_label.setAlignment(Qt.AlignLeft)
        custom_ds_id_label.setStyleSheet("border: none; padding-left: 10px; font-weight: bold; font-size: 18px;")  # Customize ID label style
        custom_box_layout.addWidget(custom_ds_id_label)

        spacer = QSpacerItem( 0, QSizePolicy.Fixed)  
        custom_box_layout.addItem(spacer)
        
        # Create the Name label
        custom_ds_name_label = QLabel(f"{ds_text}")
        custom_ds_name_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_ds_name_label.setAlignment(Qt.AlignLeft)
        custom_ds_name_label.setWordWrap(True)  # Enable word wrapping for long names
        custom_ds_name_label.setStyleSheet("border: none; padding-left: 10px;")  # Customize Name label style
        custom_box_layout.addWidget(custom_ds_name_label)

        spacer = QSpacerItem( 0, QSizePolicy.Fixed)  
        custom_box_layout.addItem(spacer)
        
        # Create the ID label
        custom_th_label = QLabel("Threat")
        custom_th_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_th_label.setFixedHeight(25)
        custom_th_label.setAlignment(Qt.AlignLeft)
        custom_th_label.setStyleSheet("border: none; padding-left: 10px; font-weight: bold; font-size: 18px; text-decoration: underline;")  # Customize ID label style
        custom_box_layout.addWidget(custom_th_label)

        spacer = QSpacerItem( 0, QSizePolicy.Fixed)  
        custom_box_layout.addItem(spacer)

        # Create the ID label
        custom_th_id_label = QLabel(f"{th_id}")
        custom_th_id_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_th_id_label.setFixedHeight(25)
        custom_th_id_label.setAlignment(Qt.AlignLeft)
        custom_th_id_label.setStyleSheet("border: none; padding-left: 10px; font-weight: bold; font-size: 18px;")  # Customize ID label style
        custom_box_layout.addWidget(custom_th_id_label)

        spacer = QSpacerItem( 0, QSizePolicy.Fixed)  
        custom_box_layout.addItem(spacer)
        
        # Create the Name label
        custom_th_name_label = QLabel(f"{th_text}")
        custom_th_name_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_th_name_label.setAlignment(Qt.AlignLeft)
        custom_th_name_label.setWordWrap(True)  # Enable word wrapping for long names
        custom_th_name_label.setStyleSheet("border: none; padding-left: 10px;")  # Customize Name label style
        custom_box_layout.addWidget(custom_th_name_label)
            
        # Set the layout and return the box
        custom_box.setLayout(custom_box_layout)
        custom_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        custom_box.adjustSize()
        
        # Optional: Attach a click event handler
        custom_box.mousePressEvent = lambda event, box=custom_box: self.on_box_clicked(event, box)
        
        return custom_box
    
    def create_NO_Data_Custom_Box(self, box_id='', text=''):
        # Create the outer frame for the custom box
        custom_box = QFrame()
        custom_box.setFixedWidth(400)

        # Apply transparent background and remove borders
        custom_box.setStyleSheet("background: transparent; border: none;")

        # Set up the layout for the custom box
        custom_box_layout = QVBoxLayout()
        custom_box_layout.setContentsMargins(1, 1, 5, 1)
        custom_box_layout.setAlignment(Qt.AlignCenter)  # Align the content to the center

        spacer_above_id = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        custom_box_layout.addItem(spacer_above_id)

        # Create the ID label
        custom_id_label = QLabel(f"{box_id}")
        custom_id_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_id_label.setFixedHeight(25)
        custom_id_label.setAlignment(Qt.AlignLeft)
        custom_id_label.setStyleSheet("border: none; padding-left: 10px; font-weight: bold; font-size: 18px;")
        custom_box_layout.addWidget(custom_id_label)

        spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        custom_box_layout.addItem(spacer)

        # Create the placeholder label when there is no data
        if not text.strip():
            custom_name_label = QLabel("No data")
            custom_name_label.setAlignment(Qt.AlignCenter)
            custom_name_label.setStyleSheet("border: none; font-size: 16px; color: gray;")
        else:
            custom_name_label = QLabel(f"{text}")

        custom_name_label.setFont(tree_panel_style.traceabilitygraph_box_font)
        custom_name_label.setWordWrap(True)
        custom_box_layout.addWidget(custom_name_label, alignment=Qt.AlignCenter)  # Center the label

        # Set the layout and return the box
        custom_box.setLayout(custom_box_layout)
        custom_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        custom_box.adjustSize()

        return custom_box



    def display_data(self):
        logger.info("Displaying Data in graph")
        self.threat_boxes = []
        self.damage_boxes = []
        self.risk_boxes = []
        self.goals_boxes = []
        self.claims_boxes = []
        self.controls_boxes = []
        self.seen_data = {}
        self.damage_seen = {}
        self.threat_seen = {}
        self.risk_seen = {}
        self.goals_seen = {}
        self.claims_seen = {}
        self.controls_seen = {}
        damage_row = 1
        threat_row = 1
        risk_row = 1
        security_row = 1
        control_row = 1

        # add all damage scenarios
        for ds_id, damage in self.damage_scenarios_list.items():
            if ds_id not in self.damage_seen:
                damage_box = self.create_Custom_Box(ds_id, damage) if damage else self.create_NO_Data_Custom_Box(ds_id, "")
                self.grid_layout.addWidget(damage_box, damage_row, 0)
                self.damage_boxes.append(damage_box)
                self.damage_seen[ds_id] = damage_box
                self.seen_data[ds_id] = damage_box
                damage_row += 1
        if not self.damage_scenarios_list:
            empty_damage_box = self.create_NO_Data_Custom_Box("", "")
            self.grid_layout.addWidget(empty_damage_box, 1, 0)        
        
        # add all threats
        for threat_id, threat in self.threats_list.items():
            if threat_id not in self.threat_seen:
                threat_box = self.create_Custom_Box(threat_id, threat) if threat else self.create_NO_Data_Custom_Box(threat_id, "")
                self.grid_layout.addWidget(threat_box, threat_row, 2)
                self.threat_boxes.append(threat_box)
                self.threat_seen[threat_id] = threat_box
                self.seen_data[threat_id] = threat_box
                threat_row += 1
        if not self.threats_list:
            empty_threat_box = self.create_NO_Data_Custom_Box("", "")
            self.grid_layout.addWidget(empty_threat_box, 1, 2)        

        # add all risks
        for risk_id, (ds_risk, th_risk) in self.risk_list.items():
            if risk_id not in self.risk_seen:
                risk_box = self.create_Custom_Box_multivalue(risk_id, ds_risk, th_risk) if ds_risk or th_risk else self.create_NO_Data_Custom_Box(risk_id, "")
                self.grid_layout.addWidget(risk_box, risk_row, 4)
                self.risk_boxes.append(risk_box)
                self.risk_seen[risk_id] = risk_box
                self.seen_data[risk_id] = risk_box
                risk_row += 1
        if not self.risk_list:
            empty_risk_box = self.create_NO_Data_Custom_Box("", "")
            self.grid_layout.addWidget(empty_risk_box, 1, 4)        

        # add all security goals
        for sg_id, goal in self.security_goals_list.items():
            if sg_id not in self.goals_seen:
                goal_box = self.create_Custom_Box(sg_id, goal) if goal else self.create_NO_Data_Custom_Box(sg_id, "")
                self.grid_layout.addWidget(goal_box, security_row, 6)
                self.goals_boxes.append(goal_box)
                self.goals_seen[sg_id] = goal_box
                self.seen_data[sg_id] = goal_box
                security_row += 1

        if not self.security_goals_list:
            empty_goal_box = self.create_NO_Data_Custom_Box("", "")
            self.grid_layout.addWidget(empty_goal_box, 1, 6)        

        # add all security claims
        for sc_id, claim in self.security_claims_list.items():
            if sc_id not in self.claims_seen:
                claim_box = self.create_Custom_Box(sc_id, claim)
                self.grid_layout.addWidget(claim_box, security_row, 6)
                self.claims_boxes.append(claim_box)
                self.claims_seen[sc_id] = claim_box
                self.seen_data[sc_id] = claim_box
                security_row += 1

        # add all security controls
        for scc_id, control in self.security_controls_list.items():
            if scc_id not in self.controls_seen:
                control_box = self.create_Custom_Box(scc_id, control) if control else self.create_NO_Data_Custom_Box(scc_id, "")
                self.grid_layout.addWidget(control_box, control_row, 8)
                self.controls_boxes.append(control_box)
                self.controls_seen[scc_id] = control_box
                self.seen_data[scc_id] = control_box
                control_row += 1

        if not self.security_controls_list:
                empty_control_box = self.create_NO_Data_Custom_Box("", "")
                self.grid_layout.addWidget(empty_control_box, 1, 8)    

        for details  in self.traceability_link.values():
            if details['damage'] != '' and details['threat'] != '':
                if details['damage'] in self.damage_seen.keys() and details['threat'] in self.threat_seen.keys():
                    self.scroll_content_widget.add_line(self.damage_seen[details['damage']], self.threat_seen[details['threat']])
                    self.scroll_content_widget.line_seen[f"{details['damage']} 2 {details['threat']}"] = {'start_box': self.damage_seen[details['damage']], 'end_box': self.threat_seen[details['threat']], 'color': QColor(P.LightGray)}
            if details['risk'] != '' and details['threat'] != '':
                if details['threat'] in self.threat_seen.keys() and details['risk'] in self.risk_seen.keys():
                    self.scroll_content_widget.add_line(self.threat_seen[details['threat']], self.risk_seen[details['risk']])
                    self.scroll_content_widget.line_seen[f"{details['threat']} 2 {details['risk']}"] = {'start_box': self.threat_seen[details['threat']], 'end_box': self.risk_seen[details['risk']], 'color': QColor(P.LightGray)}
            if details['goal'] != '' and details['risk'] != '': 
                if details['goal'] in self.goals_seen.keys() and details['risk'] in self.risk_seen.keys():
                    self.scroll_content_widget.add_line(self.risk_seen[details['risk']], self.goals_seen[details['goal']])
                    self.scroll_content_widget.line_seen[f"{details['risk']} 2 {details['goal']}"] = {'start_box': self.risk_seen[details['risk']], 'end_box': self.goals_seen[details['goal']], 'color': QColor(P.LightGray)}
            if details['claim'] != '' and details['risk'] != '': 
                if details['claim'] in self.claims_seen.keys() and details['risk'] in self.risk_seen.keys():
                    self.scroll_content_widget.add_line(self.risk_seen[details['risk']], self.claims_seen[details['claim']])
                    self.scroll_content_widget.line_seen[f"{details['risk']} 2 {details['claim']}"] = {'start_box': self.risk_seen[details['risk']], 'end_box': self.claims_seen[details['claim']], 'color': QColor(P.LightGray)}
            if details['control'] != '': 
                if details['goal'] != '': 
                    if details['goal'] in self.goals_seen.keys() and details['control'] in self.controls_seen.keys():
                        self.scroll_content_widget.add_line(self.goals_seen[details['goal']], self.controls_seen[details['control']])
                        self.scroll_content_widget.line_seen[f"{details['goal']} 2 {details['control']}"] = {'start_box': self.goals_seen[details['goal']], 'end_box': self.controls_seen[details['control']], 'color': QColor(P.LightGray)}
                if details['claim'] != '': 
                    if details['claim'] in self.claims_seen.keys() and details['control'] in self.controls_seen.keys():
                        self.scroll_content_widget.add_line(self.claims_seen[details['claim']], self.controls_seen[details['control']])
                        self.scroll_content_widget.line_seen[f"{details['claim']} 2 {details['control']}"] = {'start_box': self.claims_seen[details['claim']], 'end_box': self.controls_seen[details['control']], 'color': QColor(P.LightGray)}

        # Add the grid layout to the dynamic content layout
        self.dynamic_content_layout.addLayout(self.grid_layout)

        # Trigger a repaint to draw lines
        self.scroll_content_widget.update()

    def on_box_clicked(self, event, box):
        self.selected_box = box
        label = box.findChild(QLabel)
        box_id = label.text()
        
        selected_path_items = []
        selected_path_lines = [] 
        for index, details  in self.traceability_link.items():
            if details['damage'] == box_id or  details['threat'] == box_id or  details['risk'] == box_id or  details['goal'] == box_id or  details['claim'] == box_id or  details['control'] == box_id:
                if details['damage'] not in selected_path_items: selected_path_items.append(details['damage'])
                if details['threat'] not in selected_path_items: selected_path_items.append(details['threat'])
                if details['risk'] not in selected_path_items: selected_path_items.append(details['risk'])
                if details['goal'] not in selected_path_items and  details['goal'] != '': selected_path_items.append(details['goal'])
                if details['claim'] not in selected_path_items and  details['claim'] != '': selected_path_items.append(details['claim'])
                if details['control'] not in selected_path_items and  details['control'] != '': selected_path_items.append(details['control'])
                if f"{details['damage']} 2 {details['threat']}" not in selected_path_lines: selected_path_lines.append(f"{details['damage']} 2 {details['threat']}")
                if f"{details['threat']} 2 {details['risk']}" not in selected_path_lines: selected_path_lines.append(f"{details['threat']} 2 {details['risk']}")
                if f"{details['risk']} 2 {details['goal']}" not in selected_path_lines and  details['goal'] != '' and  details['control'] != '': selected_path_lines.append(f"{details['risk']} 2 {details['goal']}")
                if f"{details['risk']} 2 {details['claim']}" not in selected_path_lines and details['claim'] != '': selected_path_lines.append(f"{details['risk']} 2 {details['claim']}")

                if f"{details['goal']} 2 {details['control']}" not in selected_path_lines and  details['goal'] != '' and  details['control'] != '': selected_path_lines.append(f"{details['goal']} 2 {details['control']}")
                if f"{details['claim']} 2 {details['control']}" not in selected_path_lines and  details['claim'] != '' and  details['control'] != '': selected_path_lines.append(f"{details['claim']} 2 {details['control']}")
                
        for box_name, custom_box in self.seen_data.items():
            if box_name in selected_path_items:
                custom_box.setStyleSheet(tree_panel_style.traceabilitygraph_selected_box_style)  # Change to your desired color
            else:
                custom_box.setStyleSheet(tree_panel_style.traceabilitygraph_box_style)  # Reset to original color
        self.selected_box.setStyleSheet(tree_panel_style.traceabilitygraph_selected_box_style)
        # Update line colors for all lines connected to the clicked box
        for line_key, line_info in self.scroll_content_widget.line_seen.items():
            if line_key in selected_path_lines:
                line_info['color'] = QColor('#17CFCE')
            else:
                line_info['color'] = QColor('#CCD2E3')

        # Trigger a repaint to reflect the color change
        self.scroll_content_widget.update()

    def reset_data(self):
        # Logic to reset data goes here
        for box_name, custom_box in self.seen_data.items():
            custom_box.setStyleSheet(tree_panel_style.traceabilitygraph_box_style)  # Reset to original color
        
        # Update line colors for all lines connected to the clicked box
        for line_key, line_info in self.scroll_content_widget.line_seen.items():
            line_info['color'] = QColor('#CCD2E3')

        # Trigger a repaint to reflect the color change
        self.scroll_content_widget.update()

    def eventFilter(self, obj, event):
        # Capture click events and check if they are outside a custom box
        if event.type() == QEvent.MouseButtonPress:
            if self.selected_box is not None and obj != self.selected_box:
                # Click happened outside the selected box, trigger reset
                self.reset_data()
                self.selected_box = None
        return super().eventFilter(obj, event)