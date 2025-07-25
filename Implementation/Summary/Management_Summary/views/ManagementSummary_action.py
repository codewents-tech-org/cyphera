from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QToolBar, QToolButton, QSizePolicy, QScrollArea, QMessageBox, QLineEdit,
    QSplitter,QFrame
)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSize
import sqlite3
import models.helper as helper
import controllers.DatabaseCreator as DB
import models.ToolbarStyle as TBS
import models.Parameters as P
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib.colors as mcolors

import Summary.Management_Summary.views.TOE_managementSummary as TOE_managementSummary
import models.ScrollBarStyle as SBS
from PyQt5.QtWidgets import QHeaderView
import styles.table_style as styles 
from PyQt5.QtWidgets import QSpacerItem
import utils.interface_utils as interfaces
from components.loading_dialog import RoundLoader
import logging
logger = logging.getLogger(__name__)





from Summary.Management_Summary.views.managementsummary_toolbar_panel import create_toolbar


class ManagementSummary_module(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.panel1_layout = None
        self.panel2_layout = None
        self.panel3_layout = None
        
    def setup_toolbar(self, layout):
        # Add the toolbar and table to the left panel layout
        create_toolbar(self)
        self.main_layout.addWidget(self.toolbar)


    def toggle_table_visibility(self, table_widget, button):
        logger.info(f"Toggling visibility for table: {table_widget}")

        if table_widget.isVisible():
            table_widget.hide()
            button.setIcon(QIcon(P.rightarrow_icon))  # Set to right arrow (collapsed)
            button.setIconSize(QSize(12, 12))
        else:
            table_widget.show()
            button.setIcon(QIcon(P.downarrow_icon))  # Set to down arrow (expanded)
            button.setIconSize(QSize(12, 12))
         
    def setup_panel1(self, layout):
        def adjust_table_height(table_widget, max_height=None):
            """
            Adjust the height of the table dynamically based on its content.
            If max_height is provided, it limits the table height to that value.
            """
            table_widget.resizeRowsToContents()  # Resize rows to fit contents
            row_count = table_widget.rowCount()
            total_height = sum(table_widget.rowHeight(row) for row in range(row_count)) + table_widget.horizontalHeader().height()
            if max_height and total_height > max_height:
                total_height = max_height
                table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            else:
                table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            table_widget.setFixedHeight(total_height)

        def add_spacing(layout, space=30):
            """
            Add consistent spacing between sections.
            Space is set to 40 (double the previous value).
            """
            spacer = QSpacerItem(0, space, QSizePolicy.Minimum, QSizePolicy.Expanding)
            layout.addSpacerItem(spacer)

        ### High-Level Risks Section
        high_risk_title_layout = QHBoxLayout()

        # Add the expand/collapse button BEFORE the title_label
        high_risk_toggle_btn = QToolButton()
        high_risk_toggle_btn.setIcon(QIcon(P.downarrow_icon))  # Down arrow for expanded
        high_risk_toggle_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        high_risk_toggle_btn.setIconSize(QSize(12, 12))
        high_risk_title_layout.addWidget(high_risk_toggle_btn)

        title_label = QLabel("High-Level Risks")
        title_label.setFont(QFont("Roboto", 18, QFont.Bold))
        title_label.setStyleSheet("color: black;")  # Set the text color to black
        high_risk_title_layout.addWidget(title_label)

        layout.addLayout(high_risk_title_layout)

        self.high_risk_table = QTableWidget()
        self.high_risk_table.setStyleSheet(styles.table_style)

        self.high_risk_table.horizontalHeader().setVisible(True)
        self.high_risk_table.verticalHeader().setVisible(False)
        self.high_risk_table.setColumnCount(3)  # Initial column count
        self.high_risk_table.setHorizontalHeaderLabels(["Impact Category", "Init. AFR Risk", "Resid. AFR Risk"])

        # Set dynamic column resizing
        self.high_risk_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.customize_table_headers(self.high_risk_table)
        self.load_data_into_table(self.high_risk_table)

        layout.addWidget(self.high_risk_table)
        add_spacing(layout)
        high_risk_toggle_btn.clicked.connect(lambda: self.toggle_table_visibility(self.high_risk_table, high_risk_toggle_btn))

        adjust_table_height(self.high_risk_table, max_height=300)  # Adjust height dynamically with max limit
        add_spacing(layout)

        ### Security Controls Section
        sec_control_title_layout = QHBoxLayout()

        sec_controls_toggle_btn = QToolButton()
        sec_controls_toggle_btn.setIcon(QIcon(P.downarrow_icon))  # Down arrow for expanded
        sec_controls_toggle_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        sec_controls_toggle_btn.setIconSize(QSize(12, 12))
        sec_control_title_layout.addWidget(sec_controls_toggle_btn)

        sec_controls_label = QLabel("Security Controls")
        sec_controls_label.setFont(QFont("Roboto", 18, QFont.Bold))
        sec_controls_label.setStyleSheet("color: black;")
        sec_control_title_layout.addWidget(sec_controls_label)

        layout.addLayout(sec_control_title_layout)

        self.sec_controls_table = QTableWidget()
        self.sec_controls_table.setStyleSheet(styles.table_style)
        self.sec_controls_table.setColumnCount(1)
        self.sec_controls_table.verticalHeader().setVisible(False)
        self.sec_controls_table.horizontalHeader().setVisible(False)

        self.load_security_controls_table()
        layout.addWidget(self.sec_controls_table)
        add_spacing(layout)
        sec_controls_toggle_btn.clicked.connect(lambda: self.toggle_table_visibility(self.sec_controls_table, sec_controls_toggle_btn))

        adjust_table_height(self.sec_controls_table, max_height=300)  # Adjust height dynamically with max limit
        add_spacing(layout)

        ### TOE Configuration Section
        toe_configuration_title_layout = QHBoxLayout()

        toe_configuration_toggle_btn = QToolButton()
        toe_configuration_toggle_btn.setIcon(QIcon(P.downarrow_icon))  # Down arrow for expanded
        toe_configuration_toggle_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        toe_configuration_toggle_btn.setIconSize(QSize(12, 12))
        toe_configuration_title_layout.addWidget(toe_configuration_toggle_btn)

        toe_configuration_label = QLabel("TOE Configuration")
        toe_configuration_label.setFont(QFont("Roboto", 18, QFont.Bold))
        toe_configuration_label.setStyleSheet("color: black;")
        toe_configuration_title_layout.addWidget(toe_configuration_label)

        layout.addLayout(toe_configuration_title_layout)

        self.toe_configuration_table = QTableWidget()
        self.toe_configuration_table.setStyleSheet(styles.table_style)
        self.toe_configuration_table.setColumnCount(1)
        self.toe_configuration_table.verticalHeader().setVisible(False)
        self.toe_configuration_table.horizontalHeader().setVisible(False)
        self.load_toe_configuration_table()
        layout.addWidget(self.toe_configuration_table)
        add_spacing(layout)
        toe_configuration_toggle_btn.clicked.connect(lambda: self.toggle_table_visibility(self.toe_configuration_table, toe_configuration_toggle_btn))

        adjust_table_height(self.toe_configuration_table, max_height=300)
        add_spacing(layout)

        ### Assumptions Section
        assumptions_title_layout = QHBoxLayout()

        assumptions_toggle_btn = QToolButton()
        assumptions_toggle_btn.setIcon(QIcon(P.downarrow_icon))  # Down arrow for expanded
        assumptions_toggle_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        assumptions_toggle_btn.setIconSize(QSize(12, 12))
        assumptions_title_layout.addWidget(assumptions_toggle_btn)

        assumptions_label = QLabel("Assumptions")
        assumptions_label.setFont(QFont("Roboto", 18, QFont.Bold))
        assumptions_label.setStyleSheet("color: black;")
        assumptions_title_layout.addWidget(assumptions_label)

        layout.addLayout(assumptions_title_layout)

        self.assumptions_table = QTableWidget()
        self.assumptions_table.setStyleSheet(styles.table_style)
        self.assumptions_table.setColumnCount(1)
        self.assumptions_table.verticalHeader().setVisible(False)
        self.assumptions_table.horizontalHeader().setVisible(False)
        self.load_assumptions_table()
        layout.addWidget(self.assumptions_table)
        add_spacing(layout)
        assumptions_toggle_btn.clicked.connect(lambda: self.toggle_table_visibility(self.assumptions_table, assumptions_toggle_btn))

        adjust_table_height(self.assumptions_table, max_height=300)
        add_spacing(layout)

    def setup_panel2(self, layout):
        # TOE Description Section
        toe_description_label = QLabel("Summary Description")
        toe_description_label.setFont(QFont("Roboto", 18, QFont.Bold))
        toe_description_label.setStyleSheet("color: black;")  # Set the text color to black
        layout.addWidget(toe_description_label)

    def setup_panel3(self, layout):
        # Create a horizontal layout for the canvases and their headings
        canvas_layout = QHBoxLayout()

        # Create a vertical layout for the left matrix and its heading
        left_matrix_layout = QVBoxLayout()
        left_matrix_label = QLabel("Risk Matrices")  # Heading for the left matrix
        left_matrix_label.setFont(QFont("Roboto", 18, QFont.Bold))
        left_matrix_label.setStyleSheet("color: black;")
        left_matrix_label.setAlignment(Qt.AlignLeft)  # Align left for consistency
        left_matrix_layout.addWidget(left_matrix_label)

        # Adjust spacing between the label and the TARA label
        left_matrix_layout.addSpacing(2)  # Reduced spacing to decrease the gap

        # Add the TARA label
        tara_label = QLabel("Threat and Risk Analysis")
        tara_label.setFont(QFont("Roboto", 16, QFont.Bold))
        tara_label.setStyleSheet("color: black;")
        tara_label.setAlignment(Qt.AlignCenter)  # Center the label
        left_matrix_layout.addWidget(tara_label)

        # Add the left matrix plot
        self.canvas1 = FigureCanvas(plt.figure(figsize=(7, 6)))
        self.plot_matrix_one()  # Plot the left matrix
        left_matrix_layout.addWidget(self.canvas1)

        # Create a vertical layout for the right matrix and its heading
        right_matrix_layout = QVBoxLayout()

        # Add spacing between the label and the ARA label
        right_matrix_layout.addSpacing(5)  # Reduced spacing to decrease the gap

        # Add the ARA label
        ara_label = QLabel("Residual Risk Analysis")
        ara_label.setFont(QFont("Roboto", 16, QFont.Bold))
        ara_label.setStyleSheet("color: black;")
        ara_label.setAlignment(Qt.AlignCenter)  # Center the label
        right_matrix_layout.addWidget(ara_label)

        # Add the right matrix plot
        self.canvas2 = FigureCanvas(plt.figure(figsize=(7, 6)))
        self.plot_matrix_two()  # Plot the right matrix
        right_matrix_layout.addWidget(self.canvas2)

        # Add both the left and right layouts to the horizontal layout
        canvas_layout.addLayout(left_matrix_layout)
        canvas_layout.addLayout(right_matrix_layout)

        # Add the horizontal layout to the main layout
        layout.addLayout(canvas_layout)

        # Add some spacing after the matrices
        layout.addSpacing(20)

        # Add the table below the matrices
        self.matrix_data_table = QTableWidget()
        self.matrix_data_table.verticalHeader().setVisible(False)  # Hide row numbers
        self.matrix_data_table.setColumnCount(6)  # Adjusted column count to 6
        self.matrix_data_table.setHorizontalHeaderLabels([
            "Risk", "Init. AFR Value", "Resid. AFR Value",
            "Damage Scenario", "Threat", "Impact", "Mitigated By"
        ])

        # Configure the table properties
        self.matrix_data_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.matrix_data_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.matrix_data_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.matrix_data_table.setStyleSheet(styles.table_style)
        self.matrix_data_table.horizontalHeader().setVisible(True)
        self.matrix_data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matrix_data_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Customize the headers of the table
        self.customize_last_table_headers()

        # Add the table to the main layout
        layout.addWidget(self.matrix_data_table)

    def customize_table_headers(self, table_widget):
        # Define colors for headers
        header_colors = ['black']  # Set header text color

        # Define font properties for headers
        header_font = QFont("Poppins")  # Use "Poppins" font family
        header_font.setUnderline(False)  # Disable underline
        header_font.setPointSize(16)  # Set font size to 16 for better visibility
        header_font.setBold(True)  # Make font bold

        # Define headers without icons
        headers = [
            "Impact Category",
            "Init. AFR Value",
            "Resid. AFR Value"
        ]

        # Loop through each header to set or modify in the table widget
        for i, header_text in enumerate(headers):
            existing_item = table_widget.horizontalHeaderItem(i)

            if existing_item:
                # Modify existing header item
                existing_item.setText(f" {header_text}")  # Set header text
                existing_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align left and vertically center
                existing_item.setForeground(QColor(header_colors[i % len(header_colors)]))  # Set text color
                existing_item.setFont(header_font)  # Apply font
                table_widget.setHorizontalHeaderItem(i, existing_item)  # Update the table widget
            else:
                # Create a new header item with text
                new_item = QTableWidgetItem()
                new_item.setText(f" {header_text}")  # Set header text
                new_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align left and vertically center
                new_item.setForeground(QColor(header_colors[i % len(header_colors)]))  # Set text color
                new_item.setFont(header_font)  # Apply font
                table_widget.setHorizontalHeaderItem(i, new_item)  # Set in the table widget

        # Apply consistent header style
        table_widget.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #E7E9EE;  /* Light grey background */
                font-family: Poppins;  /* Poppins font family */
                font-size: 16px;  /* Font size */
                font-weight: bold;  /* Bold font weight */
                color: black;  /* Black text color */
                border: 0px solid transparent;  /* No border */
            }
        """)

        # Resize columns to fit content
        table_widget.resizeColumnsToContents()
        table_widget.resizeRowsToContents()

    def customize_last_table_headers(self):
        # Define font properties for headers
        header_font = QFont("Poppins", 16, QFont.Bold)  # Poppins font, bold, size 16

        # Define the headers with text
        headers = [
            "Risk", "Init. AFR Risk", "Resid. AFR Risk",
            "Damage Scenario", "Threat", "Impact", "Mitigated By"
        ]

        # Define the column widths for better alignment
        column_widths = [80, 200, 200, 400, 400, 200, 300]

        # Loop through each header to apply settings
        for i, header_text in enumerate(headers):
            existing_item = self.matrix_data_table.horizontalHeaderItem(i)

            if existing_item:
                # Modify existing header item
                existing_item.setText(f" {header_text}")  # Add text with spacing
                existing_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align left and vertically center
                existing_item.setFont(header_font)  # Apply the font
                existing_item.setForeground(QColor("black"))  # Set text color to black
                self.matrix_data_table.setHorizontalHeaderItem(i, existing_item)  # Update header item
            else:
                # Create a new header item
                header_item = QTableWidgetItem()
                header_item.setText(f" {header_text}")  # Add text with spacing
                header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align left and vertically center
                header_item.setFont(header_font)  # Apply the font
                header_item.setForeground(QColor("black"))  # Set text color to black
                self.matrix_data_table.setHorizontalHeaderItem(i, header_item)  # Add the header item

        # Apply consistent styling to the headers
        self.matrix_data_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #E7E9EE;  /* Light grey background */
                font-family: Poppins;  /* Use Poppins font */
                font-size: 16px;  /* Font size 16 */
                font-weight: bold;  /* Bold font weight */
                color: black;  /* Black text color */
                border: 0px solid transparent;  /* No border */
            }
        """)

        # Apply specific column widths for better alignment
        for i, width in enumerate(column_widths):
            self.matrix_data_table.setColumnWidth(i, width)

        # Adjust the header to resize columns and rows to fit content
        self.matrix_data_table.resizeColumnsToContents()
        self.matrix_data_table.resizeRowsToContents()


    def load_data_into_table(self, table_widget):
        logger.info("Loading data into High-Level Risk Table")
        try:
            # Clear the table before repopulating
            table_widget.clearContents()

            # Fetch Impact_category data from management.db
            impact_categories = DB.execute_db("SELECT ds_id, name, impact_category FROM damage_scenarios")
            risk_data = DB.execute_db("SELECT damage, init_AFR_value, resid_AFR_value FROM RiskData")

            # Mapping damage_scenarios ID, name, and impact category
            ds_impactcatogory_map = {}
            Operational_ds_list = []
            Financial_ds_list = []
            Safety_ds_list = []
            Privacy_ds_list = []
            NotApplicable_ds_list = []

            for (id, name, ic_data) in impact_categories:
                ic_list = ic_data.strip().split(', ')
                for ic in ic_list:
                    if ic == 'Operational': Operational_ds_list.append(f"{id} - {name}")
                    elif ic == 'Financial': Financial_ds_list.append(f"{id} - {name}")
                    elif ic == 'Safety': Safety_ds_list.append(f"{id} - {name}")
                    elif ic == 'Privacy': Privacy_ds_list.append(f"{id} - {name}")
                    elif ic == '': NotApplicable_ds_list.append(f"{id} - {name}")

            RL_impactcatagory_menu = []
            for ic in helper.DS_impactcatagory_menu:
                RL_impactcatagory_menu.append(ic)
            RL_impactcatagory_menu.append('Not Applicable')

            for ic in RL_impactcatagory_menu:
                if ic == 'Operational': ds_impactcatogory_map[ic] = Operational_ds_list
                elif ic == 'Financial': ds_impactcatogory_map[ic] = Financial_ds_list
                elif ic == 'Safety': ds_impactcatogory_map[ic] = Safety_ds_list
                elif ic == 'Privacy': ds_impactcatogory_map[ic] = Privacy_ds_list
                elif ic == 'Not Applicable': ds_impactcatogory_map[ic] = NotApplicable_ds_list

            # Create a risk map for each impact category
            risk_map = {}
            for impact in RL_impactcatagory_menu:
                IAFR_list = []
                RAFR_list = []
                IAFR_max_value = ''
                RAFR_max_value = ''
                for (damage, IAFR, RAFR) in risk_data:
                    if impact in ds_impactcatogory_map.keys():
                        if damage in ds_impactcatogory_map[impact]:
                            if IAFR != '': IAFR_list.append(int(IAFR))
                            if RAFR != '': RAFR_list.append(int(RAFR))
                IAFR_max_value = str(max(IAFR_list)) if IAFR_list else ''
                RAFR_max_value = str(max(RAFR_list)) if RAFR_list else ''
                risk_map[impact] = [IAFR_max_value, RAFR_max_value]
                DB.update_db("""
                    INSERT OR REPLACE INTO HighLevelRisk (Impact_Category, InitAFRValue, ResidAFRValue)
                    VALUES  ( ?, ?, ?)
                    """, (impact, IAFR_max_value, RAFR_max_value))

            # Set the number of rows and columns
            table_widget.setRowCount(5)  # Set row count for 4 Impact categories
            table_widget.setColumnCount(3)

            # Define the color mapping for AFR values
            color_mapping = {
                '5': "#a80000",
                '4': "#ff3131",
                '3': "#ff914d",
                '2': "#ffde59",
                '1': "#7ed957"
            }

            # Insert data for Impact Category, Initial AFR, Residual AFR
            for row_index, impact in enumerate(RL_impactcatagory_menu):
                # Create QTableWidgetItem for Impact Category and align left
                impact_item = QTableWidgetItem(impact)
                impact_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make non-editable
                impact_item.setTextAlignment(Qt.AlignLeft)
                table_widget.setItem(row_index, 0, impact_item)

                # Create non-editable QLineEdit for AFR values
                init_afr_value = risk_map[impact][0]
                resid_afr_value = risk_map[impact][1]

                init_afr_item = QLineEdit()
                init_afr_item.setText(init_afr_value)
                init_afr_item.setAlignment(Qt.AlignCenter)
                init_afr_item.setReadOnly(True)  # Make read-only
                if init_afr_value in color_mapping:
                    init_afr_item.setStyleSheet(f"background-color:{color_mapping[init_afr_value]}")

                resid_afr_item = QLineEdit()
                resid_afr_item.setText(resid_afr_value)
                resid_afr_item.setAlignment(Qt.AlignCenter)
                resid_afr_item.setReadOnly(True)  # Make read-only
                if resid_afr_value in color_mapping:
                    resid_afr_item.setStyleSheet(f"background-color:{color_mapping[resid_afr_value]}")

                # Set the items in the table
                table_widget.setCellWidget(row_index, 1, init_afr_item)
                table_widget.setCellWidget(row_index, 2, resid_afr_item)

            # Resize columns to fit the content
            table_widget.resizeColumnsToContents()

        except sqlite3.Error as e:
            # Show error message if there's an issue with the database
            QMessageBox.critical(None, "Database Error", f"Error fetching data: {e}")


    def load_security_controls_table(self):
        self.loader = RoundLoader(self, label_text="Loading Security Controls Table...")
        self.loader.show()
        QApplication.processEvents()  # Ensure UI updates before loading starts

        logger.info("Loading Security Controls Table")
        try:
            DB.update_db_db("DELETE FROM SecurityControls")
            # Fetch security controls data from the database
            security_controls = DB.execute_db("SELECT id, name FROM security_controls")

            # Clear any existing content in the table
            self.sec_controls_table.clearContents()

            # Set the number of rows and columns based on the data
            self.sec_controls_table.setRowCount(len(security_controls))
            self.sec_controls_table.setColumnCount(2)  # Two columns: ID and Name

            # Configure table properties
            self.sec_controls_table.setHorizontalHeaderLabels(["Security Control ID", "Security Control Name"])  # Set headers
            self.sec_controls_table.verticalHeader().setVisible(False)  # Hide vertical header
            self.sec_controls_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns
            self.sec_controls_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table non-editable
            self.sec_controls_table.setSelectionMode(QTableWidget.NoSelection)  # Disable selection
            self.sec_controls_table.setStyleSheet(styles.table_style)  # Apply consistent styles

            # Populate the table with security controls data
            for row_index, (sec_id, sec_name) in enumerate(security_controls):
                # First column: Security Control ID
                item_id = QTableWidgetItem(str(sec_id))
                item_id.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item_id.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Non-editable
                self.sec_controls_table.setItem(row_index, 0, item_id)

                # Second column: Security Control Name
                item_name = QTableWidgetItem(sec_name)
                item_name.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Non-editable
                self.sec_controls_table.setItem(row_index, 1, item_name)

                item_text = f"{sec_id}::{sec_name}"
                DB.update_db("""INSERT INTO SecurityControls (Security_Controls) VALUES (?)""", (item_text,))
            # Adjust table rows and columns to fit content
            self.adjust_table_columns(self.sec_controls_table)  # Use the common adjust table function

        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error loading security controls data: {e}")
        finally:
            # Hide the loader after loading completes
            self.loader.close()    

    def adjust_table_columns(self, table_widget):
        """
        Adjust the size of table columns and rows dynamically for better alignment.
        """
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns
        table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # First column resizes to content
        table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Second column stretches
        table_widget.horizontalHeader().setStretchLastSection(True)  # Ensure grid lines extend fully
        table_widget.resizeRowsToContents()

    def load_toe_configuration_table(self):
        try:
            DB.update_db_db("DELETE FROM TOEConfigurationInManagementSummary")

            # Fetch TOE configuration data from the database
            toe_configuration_data = DB.execute_db("SELECT toe_configuration_id, toe_configuration_name FROM toe_configuration")

            # Clear any existing content in the table
            self.toe_configuration_table.clearContents()

            # Set the number of rows and columns based on the data
            self.toe_configuration_table.setRowCount(len(toe_configuration_data))
            self.toe_configuration_table.setColumnCount(2)  # Two columns: ID and Name

            # Configure table properties
            self.toe_configuration_table.setHorizontalHeaderLabels(["Configuration ID", "Configuration Name"])  # Set headers
            self.toe_configuration_table.verticalHeader().setVisible(False)  # Hide vertical header
            self.toe_configuration_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch to fit width
            self.toe_configuration_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table non-editable
            self.toe_configuration_table.setSelectionMode(QTableWidget.NoSelection)  # Disable selection
            self.toe_configuration_table.setStyleSheet(styles.table_style)  # Apply styles

            # Populate the table with TOE configuration data
            for row_index, (toe_configuration_id, toe_configuration_name) in enumerate(toe_configuration_data):
                # Add the first column data
                item_id = QTableWidgetItem(str(toe_configuration_id))
                item_id.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align left and vertically center
                item_id.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Non-editable
                self.toe_configuration_table.setItem(row_index, 0, item_id)

                # Add the second column data
                item_name = QTableWidgetItem(toe_configuration_name)
                item_name.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align left and vertically center
                item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Non-editable
                self.toe_configuration_table.setItem(row_index, 1, item_name)

                item_text = f"{toe_configuration_id}::{toe_configuration_name}"
                DB.update_db("""INSERT INTO TOEConfigurationInManagementSummary (TOE_Configuration) VALUES  ( ?)""", (item_text,))


            # Dynamically adjust the table column sizes
            self.adjust_table_columns(self.toe_configuration_table)

        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error loading TOE configuration data: {e}")


    def adjust_table_height(self, table_widget, max_height=None):
        """
        Adjust the height of the table dynamically based on its content.
        If max_height is provided, it limits the table height to that value.
        """
        table_widget.resizeRowsToContents()  # Resize rows to fit contents
        row_count = table_widget.rowCount()
        total_height = sum(table_widget.rowHeight(row) for row in range(row_count)) + table_widget.horizontalHeader().height()

        if max_height and total_height > max_height:
            total_height = max_height
            table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        table_widget.setFixedHeight(total_height)
            



    def load_assumptions_table(self):
        try:
            DB.update_db_db("DELETE FROM AssumptionsInManagementSummary")

            # Fetch assumptions data from the database
            assumptions_data = DB.execute_db("SELECT assumption_id, assumptions FROM assumptions")

            # Clear any existing content in the table
            self.assumptions_table.clearContents()

            # Set the number of rows and columns based on the data
            self.assumptions_table.setRowCount(len(assumptions_data))
            self.assumptions_table.setColumnCount(2)  # Two columns: ID and Assumptions

            # Configure table properties
            self.assumptions_table.setHorizontalHeaderLabels(["Assumption ID", "Assumption Text"])  # Set headers
            self.assumptions_table.verticalHeader().setVisible(False)  # Hide vertical header
            self.assumptions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns
            self.assumptions_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table non-editable
            self.assumptions_table.setSelectionMode(QTableWidget.NoSelection)  # Disable selection
            self.assumptions_table.setStyleSheet(styles.table_style)  # Apply consistent styles

            # Populate the table with assumptions data
            for row_index, (assumption_id, assumption_text) in enumerate(assumptions_data):
                # First column: Assumption ID
                item_id = QTableWidgetItem(str(assumption_id))
                item_id.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item_id.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Non-editable
                self.assumptions_table.setItem(row_index, 0, item_id)

                # Second column: Assumption Text
                item_text = QTableWidgetItem(assumption_text)
                item_text.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item_text.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Non-editable
                self.assumptions_table.setItem(row_index, 1, item_text)

                item_text = f"{assumption_id}::{assumption_text}"
                DB.update_db("""INSERT INTO AssumptionsInManagementSummary (Assumptions) VALUES  ( ?)""", (item_text,))

            # Adjust table rows and columns to fit content
            self.adjust_table_columns(self.assumptions_table)  # Use the common adjust table function

        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error loading assumptions data: {e}")


    def plot_matrix_one(self):
        logger.info("Plotting Initial AFR Risk Matrix")
        try:
            # Fetch the risk data from the database
            risk_data = DB.execute_db("SELECT id, impact, init_AFR_level, init_AFR_value, resid_AFR_level, resid_AFR_value, damage, threat, impact, mitigated_by FROM RiskData")

            # Define the mapping between labels and matrix indices
            row_labels = ["High", "Medium", "Low", "Very Low"]
            col_labels = ["Negligible", "Moderate", "Major", "Severe"]

            # Initialize the matrix data and color matrix
            matrix_data = np.zeros((len(row_labels), len(col_labels)), dtype=int)
            color_matrix = np.zeros((len(row_labels), len(col_labels)), dtype=int)

            # Define the color mapping for the matrix
            matrix_color_mapping = {
                ('High', 'Negligible'): 0,
                ('High', 'Moderate'): 1,
                ('High', 'Major'): 2,
                ('High', 'Severe'): 3,
                ('Medium', 'Negligible'): 4,
                ('Medium', 'Moderate'): 5,
                ('Medium', 'Major'): 6,
                ('Medium', 'Severe'): 7,
                ('Low', 'Negligible'): 8,
                ('Low', 'Moderate'): 9,
                ('Low', 'Major'): 10,
                ('Low', 'Severe'): 11,
                ('Very Low', 'Negligible'): 12,
                ('Very Low', 'Moderate'): 13,
                ('Very Low', 'Major'): 14,
                ('Very Low', 'Severe'): 15
            }

            # Define the color mapping for AFR values (for use in the last table columns)
            color_mapping = {
                '5': "#a80000",  # Dark Red
                '4': "#ff3131",  # Red
                '3': "#ff914d",  # Orange
                '2': "#ffde59",  # Yellow
                '1': "#7ed957"   # Green
            }

            # Store all records for each combination of row and column
            risk_map = {}
            for risk_id, impact, afl, afr_value, resid_afl, resid_afr_value, damage, threat, impact_category, mitigated_by in risk_data:
                row_label = afl.strip().title()  # Normalize the labels
                col_label = impact.strip().title()

                if row_label in row_labels and col_label in col_labels:
                    row_idx = row_labels.index(row_label)
                    col_idx = col_labels.index(col_label)
                    matrix_data[row_idx, col_idx] += 1

                    if (row_idx, col_idx) not in risk_map:
                        risk_map[(row_idx, col_idx)] = []

                    # Append the current record to the list for this point
                    risk_map[(row_idx, col_idx)].append({
                        "Risk": risk_id,
                        "Init. AFR Value": afr_value,
                        "Resid. AFR Value": resid_afr_value,
                        "Damage scenario": damage,
                        "Threat": threat,
                        "Impact category": impact_category,
                        "Mitigated by": mitigated_by
                    })
            
            # Apply color mapping to the matrix
            for i in range(len(row_labels)):
                for j in range(len(col_labels)):
                    if color_matrix[i, j] == 0:
                        color_matrix[i, j] = matrix_color_mapping[(row_labels[i], col_labels[j])]

            # Create a custom colormap for the matrix
            cmap = mcolors.ListedColormap([
                 '#7ed957', '#ff914d', '#ff3131', '#8B0000',
                '#7ed957', '#ffde59', '#ff914d', '#ff3131',
                '#7ed957', '#ffde59', '#ffde59', '#ff914d',
                '#7ed957', '#7ed957', '#7ed957', '#ffde59'
            ])
            bounds = np.arange(0, 17)
            norm = mcolors.BoundaryNorm(bounds, cmap.N)

            # Plot the matrix with color coding
            fig, ax = plt.subplots()
            cax = ax.imshow(color_matrix, cmap=cmap, norm=norm)

            # Set labels for the matrix
            ax.set_xticks(np.arange(len(col_labels)))
            ax.set_yticks(np.arange(len(row_labels)))
            ax.set_xticklabels(col_labels)
            ax.set_yticklabels(row_labels)

            # Rotate x-axis labels to horizontal
            plt.xticks(rotation=0)

            # Add axis labels
            ax.set_xlabel('Impact')
            ax.set_ylabel('Init. AFR' ,labelpad=20)

            # Annotate each cell with the count
            for i in range(len(row_labels)):
                for j in range(len(col_labels)):
                    if matrix_data[i, j] != 0:
                        ax.text(j, i, int(matrix_data[i, j]), ha="center", va="center", color="black")
            
            # Connect click event to the plot
            def on_click(event):
                if event.inaxes == ax:
                    x = int(round(event.xdata))
                    y = int(round(event.ydata))
                    if matrix_data[y, x] == 0:  # No data in the clicked cell
                        self.matrix_data_table.setRowCount(0)  # Clear the table
                        return
                    if (y, x) in risk_map:
                        risk_info_list = risk_map[(y, x)]
                        logger.info(f"Found {len(risk_info_list)} risk records for (x={x}, y={y})")


                        # Set row count based on the number of records for the clicked point
                        self.matrix_data_table.setRowCount(len(risk_info_list))

                        # Populate the table with all the records for the clicked point
                        for row_idx, risk_info in enumerate(risk_info_list):
                            self.matrix_data_table.setItem(row_idx, 0, QTableWidgetItem(str(risk_info['Risk'])))

                            # Init. AFR Value with color coding
                            init_afr_value = risk_info['Init. AFR Value']
                            init_afr_item = QLineEdit()
                            init_afr_item.setText(str(init_afr_value))
                            init_afr_item.setReadOnly(True)
                            init_afr_item.setAlignment(Qt.AlignCenter)
                            if str(init_afr_value) in color_mapping:
                                init_afr_item.setStyleSheet(f"background-color:{color_mapping[str(init_afr_value)]}")
                            self.matrix_data_table.setCellWidget(row_idx, 1, init_afr_item)

                                        # Resid. AFR Value with color coding
                            resid_afr_value = risk_info['Resid. AFR Value']
                            resid_afr_item = QLineEdit()
                            resid_afr_item.setText(str(resid_afr_value))
                            resid_afr_item.setAlignment(Qt.AlignCenter)
                            resid_afr_item.setReadOnly(True)

                            # Apply background color based on AFR value
                            if str(resid_afr_value) in color_mapping:
                                resid_afr_item.setStyleSheet(f"background-color:{color_mapping[str(resid_afr_value)]}")

                            self.matrix_data_table.setCellWidget(row_idx, 2, resid_afr_item)

                            # Function to wrap text for tooltips
                            def wrap_tooltip_text(text, width=50):
                                return '\n'.join(text[i:i+width] for i in range(0, len(text), width))

                            # Populate other columns without color coding
                            damage_item = QTableWidgetItem(risk_info['Damage scenario'])
                            damage_tooltip_text = wrap_tooltip_text(risk_info['Damage scenario'])  # Wrap text
                            damage_item.setToolTip(damage_tooltip_text)  # Apply tooltip
                            damage_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                            self.matrix_data_table.setItem(row_idx, 3, damage_item)

                            threat_item = QTableWidgetItem(risk_info['Threat'])
                            threat_tooltip_text = wrap_tooltip_text(risk_info['Threat'])  # Wrap text
                            threat_item.setToolTip(threat_tooltip_text)  # Apply tooltip
                            threat_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                            self.matrix_data_table.setItem(row_idx, 4, threat_item)

                            self.matrix_data_table.setItem(row_idx, 5, QTableWidgetItem(risk_info['Impact category']))
                            self.matrix_data_table.setItem(row_idx, 6, QTableWidgetItem(risk_info['Mitigated by']))



            # Connect click event to update the last table
            fig.canvas.mpl_connect('button_press_event', on_click)

            # Draw the plot on the canvas
            self.canvas1.figure = fig
            self.canvas1.draw()

            print('matrix_data: ', matrix_data)
            risk_data_map = {}
            risk_level = ['High', 'Medium', 'Low', 'Very Low']
            for i, risk in enumerate(matrix_data):    risk_data_map[risk_level[i]] = risk
            for risk, data in risk_data_map.items():
                DB.update_db("""
                    INSERT OR REPLACE INTO initialriskmatriks (risk, Negligible, Moderate, Major, Severe)
                    VALUES  ( ?, ?, ?, ?, ?)
                    """, (risk, str(data[0]) if int(data[0])>0 else '', str(data[1]) if int(data[1])>0 else '', str(data[2]) if int(data[2])>0 else '', str(data[3]) if int(data[3])>0 else ''))
            DB.update_db("""
                INSERT OR REPLACE INTO initialriskmatriks (risk, Negligible, Moderate, Major, Severe)
                VALUES  ( ?, ?, ?, ?, ?)
                """, ('', 'Negligible', 'Moderate', 'Major', 'Severe'))
        

        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error fetching data: {e}")

    def plot_matrix_two(self):
        logger.info("Plotting Residual AFR Risk Matrix")
        try:
            # Fetch the risk data from the database
            risk_data = DB.execute_db("SELECT id, impact, resid_AFR_level, resid_AFR_value, init_AFR_level, init_AFR_value, damage, threat, impact, mitigated_by FROM RiskData")

            # Define the mapping between labels and matrix indices
            row_labels = ["High", "Medium", "Low", "Very Low"]
            col_labels = ["Negligible", "Moderate", "Major", "Severe"]

            # Initialize the matrix data and color matrix
            matrix_data = np.zeros((len(row_labels), len(col_labels)), dtype=int)
            color_matrix = np.zeros((len(row_labels), len(col_labels)), dtype=int)

            # Define the color mapping for the matrix
            matrix_color_mapping = {
                ('High', 'Negligible'): 0,
                ('High', 'Moderate'): 1,
                ('High', 'Major'): 2,
                ('High', 'Severe'): 3,
                ('Medium', 'Negligible'): 4,
                ('Medium', 'Moderate'): 5,
                ('Medium', 'Major'): 6,
                ('Medium', 'Severe'): 7,
                ('Low', 'Negligible'): 8,
                ('Low', 'Moderate'): 9,
                ('Low', 'Major'): 10,
                ('Low', 'Severe'): 11,
                ('Very Low', 'Negligible'): 12,
                ('Very Low', 'Moderate'): 13,
                ('Very Low', 'Major'): 14,
                ('Very Low', 'Severe'): 15
            }

            # Define the color mapping for AFR values (for use in the last table columns)
            color_mapping = {
                '5': "#a80000",  # Dark Red
                '4': "#ff3131",  # Red
                '3': "#ff914d",  # Orange
                '2': "#ffde59",  # Yellow
                '1': "#7ed957"   # Green
            }

            # Store all records for each combination of row and column
            risk_map = {}
            for risk_id, impact, resid_afl, resid_afr_value, init_afl, init_afr_value, damage, threat, impact_category, mitigated_by in risk_data:
                row_label = resid_afl.strip().title()  # Normalize the labels
                col_label = impact.strip().title()

                if row_label in row_labels and col_label in col_labels:
                    row_idx = row_labels.index(row_label)
                    col_idx = col_labels.index(col_label)
                    matrix_data[row_idx, col_idx] += 1

                    if (row_idx, col_idx) not in risk_map:
                        risk_map[(row_idx, col_idx)] = []

                    # Append the current record to the list for this point
                    risk_map[(row_idx, col_idx)].append({
                        "Risk": risk_id,
                        "Init. AFR Value": init_afr_value,
                        "Resid. AFR Value": resid_afr_value,
                        "Damage scenario": damage,
                        "Threat": threat,
                        "Impact category": impact_category,
                        "Mitigated by": mitigated_by
                    })

            # Apply color mapping to the matrix
            for i in range(len(row_labels)):
                for j in range(len(col_labels)):
                    if color_matrix[i, j] == 0:
                        color_matrix[i, j] = matrix_color_mapping[(row_labels[i], col_labels[j])]

            # Create a custom colormap for the matrix
            cmap = mcolors.ListedColormap([
                '#7ed957', '#ff914d', '#ff3131', '#8B0000',
                '#7ed957', '#ffde59', '#ff914d', '#ff3131',
                '#7ed957', '#ffde59', '#ffde59', '#ff914d',
                '#7ed957', '#7ed957', '#7ed957', '#ffde59'
            ])
            bounds = np.arange(0, 17)
            norm = mcolors.BoundaryNorm(bounds, cmap.N)

            # Plot the matrix with color coding
            fig, ax = plt.subplots()
            cax = ax.imshow(color_matrix, cmap=cmap, norm=norm)

            # Set labels for the matrix
            ax.set_xticks(np.arange(len(col_labels)))
            ax.set_yticks(np.arange(len(row_labels)))
            ax.set_xticklabels(col_labels)
            ax.set_yticklabels(row_labels)

            # Rotate x-axis labels to horizontal
            plt.xticks(rotation=0)

            # Add axis labels
            ax.set_xlabel('Impact')
            ax.set_ylabel('Resid. AFR' , labelpad=20)

            # Annotate each cell with the count
            for i in range(len(row_labels)):
                for j in range(len(col_labels)):
                    if matrix_data[i, j] != 0:
                        ax.text(j, i, int(matrix_data[i, j]), ha="center", va="center", color="black")

            # Connect click event to the plot
            def on_click(event):
                if event.inaxes == ax:
                    x = int(round(event.xdata))
                    y = int(round(event.ydata))
                    if matrix_data[y, x] == 0:  # No data in the clicked cell
                        self.matrix_data_table.setRowCount(0)  # Clear the table
                        return
                    if (y, x) in risk_map:
                        risk_info_list = risk_map[(y, x)]
                        logger.info(f"Found {len(risk_info_list)} risk records for (x={x}, y={y})")


                        # Set row count based on the number of records for the clicked point
                        self.matrix_data_table.setRowCount(len(risk_info_list))

                        # Populate the table with all the records for the clicked point
                        for row_idx, risk_info in enumerate(risk_info_list):
                            self.matrix_data_table.setItem(row_idx, 0, QTableWidgetItem(str(risk_info['Risk'])))

                            # Init. AFR Value with color coding
                            init_afr_value = risk_info['Init. AFR Value']
                            init_afr_item = QLineEdit()
                            init_afr_item.setText(str(init_afr_value))
                            init_afr_item.setAlignment(Qt.AlignCenter)
                            if str(init_afr_value) in color_mapping:
                                init_afr_item.setStyleSheet(f"background-color:{color_mapping[str(init_afr_value)]}")
                            self.matrix_data_table.setCellWidget(row_idx, 1, init_afr_item)

                            # Resid. AFR Value with color coding
                            resid_afr_value = risk_info['Resid. AFR Value']
                            resid_afr_item = QLineEdit()
                            resid_afr_item.setText(str(resid_afr_value))
                            resid_afr_item.setAlignment(Qt.AlignCenter)
                            resid_afr_item.setReadOnly(True)

                            # Apply background color based on AFR value
                            if str(resid_afr_value) in color_mapping:
                                resid_afr_item.setStyleSheet(f"background-color:{color_mapping[str(resid_afr_value)]}")

                            self.matrix_data_table.setCellWidget(row_idx, 2, resid_afr_item)

                            # Function to wrap text for tooltips
                            def wrap_tooltip_text(text, width=50):
                                return '\n'.join(text[i:i+width] for i in range(0, len(text), width))

                            # Populate other columns without color coding
                            damage_item = QTableWidgetItem(risk_info['Damage scenario'])
                            damage_tooltip_text = wrap_tooltip_text(risk_info['Damage scenario'])  # Wrap text
                            damage_item.setToolTip(damage_tooltip_text)  # Apply tooltip
                            damage_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                            self.matrix_data_table.setItem(row_idx, 3, damage_item)

                            threat_item = QTableWidgetItem(risk_info['Threat'])
                            threat_tooltip_text = wrap_tooltip_text(risk_info['Threat'])  # Wrap text
                            threat_item.setToolTip(threat_tooltip_text)  # Apply tooltip
                            threat_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                            self.matrix_data_table.setItem(row_idx, 4, threat_item)

                            self.matrix_data_table.setItem(row_idx, 5, QTableWidgetItem(risk_info['Impact category']))
                            self.matrix_data_table.setItem(row_idx, 6, QTableWidgetItem(risk_info['Mitigated by']))

            # Connect click event to update the last table
            fig.canvas.mpl_connect('button_press_event', on_click)

            # Draw the plot on the canvas
            self.canvas2.figure = fig
            self.canvas2.draw()

            print('matrix_data: ', matrix_data)
            risk_data_map = {}
            risk_level = ['High', 'Medium', 'Low', 'Very Low']
            for i, risk in enumerate(matrix_data):    risk_data_map[risk_level[i]] = risk
            for risk, data in risk_data_map.items():
                DB.update_db("""
                    INSERT OR REPLACE INTO residriskmatriks (risk, Negligible, Moderate, Major, Severe)
                    VALUES  ( ?, ?, ?, ?, ?)
                    """, (risk, str(data[0]) if int(data[0])>0 else '', str(data[1]) if int(data[1])>0 else '', str(data[2]) if int(data[2])>0 else '', str(data[3]) if int(data[3])>0 else ''))
            DB.update_db("""
                INSERT OR REPLACE INTO residriskmatriks (risk, Negligible, Moderate, Major, Severe)
                VALUES  ( ?, ?, ?, ?, ?)
                """, ('', 'Negligible', 'Moderate', 'Major', 'Severe'))
        

        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error fetching data: {e}")

    def load_data(self):
        layout = self.main_layout
        if layout is not None:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
        layout = self.panel1_layout
        if layout is not None:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
        layout = self.panel2_layout
        if layout is not None:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
        layout = self.panel3_layout
        if layout is not None:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

        # Create the main content widget
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(0)  # Set minimal spacing between elements
        self.content_layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        content_widget.setStyleSheet("background-color: #ffffff; border: none;")

        scrollArea =QScrollArea()
        scrollArea.setWidgetResizable(False)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollArea.setStyleSheet(SBS.Scrollbar_ScrollBar_style)
        scrollArea.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff;  /* Background color of the Scroll Area */
                border: none;  /* Remove border if not needed */
            }

            /* Vertical Scrollbar */
            QScrollBar:vertical {
                background: #e0e0e0;  /* Light grey background for the scrollbar */
                width: 12px;  /* Adjust the width of the scrollbar */
                border-radius: 6px;  /* Rounded scrollbar edges */
            }

            QScrollBar::handle:vertical {
                background: #a0a0a0;  /* Grey color for the scrollbar handle */
                border-radius: 6px;  /* Rounded handle */
                min-height: 20px;  /* Minimum height for the handle */
            }

            QScrollBar::handle:vertical:hover {
                background: #888888;  /* Darker grey when hovered */
            }

            QScrollBar::handle:vertical:pressed {
                background: #666666;  /* Darker grey when pressed */
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;  /* Remove add-line and sub-line buttons */
                background: none;
            }

            QScrollBar::add-page:vertical, 
            QScrollBar::sub-page:vertical {
                background: none;  /* No background for the page sections */
            }
        """)


        scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Splitter to split three panels vertically
        splitter = QSplitter(Qt.Vertical)  # Change to Qt.Vertical for vertical layout

        # Panel 1: High-Level Risks, Security Controls, and Assumptions
        panel1 = QWidget()
        self.panel1_layout = QVBoxLayout()
        panel1.setLayout(self.panel1_layout)
        self.setup_panel1(self.panel1_layout)
        panel1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        # panel1.setMinimumSize(800, 600)

        # Panel 2: TOE Description
        panel2 = QWidget()
        self.panel2_layout = QVBoxLayout()
        panel2.setLayout(self.panel2_layout)
        self.setup_panel2(self.panel2_layout)
        # panel2.setMinimumHeight(300)
        frame=TOE_managementSummary.TOEDescription()
        interfaces.previous_module = frame
        self.panel2_layout.addWidget(frame)
        panel2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Panel 3: Other modules (Risk Matrices, etc.)
        panel3 = QWidget()
        self.panel3_layout = QVBoxLayout()
        panel3.setLayout(self.panel3_layout)
        self.setup_panel3(self.panel3_layout)
        # panel3.setMinimumHeight(300)
        panel3.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Add panels to the splitter
        splitter.addWidget(panel1)
        splitter.addWidget(panel2)
        splitter.addWidget(panel3)

        splitter.setStretchFactor(0, 2)  
        splitter.setStretchFactor(1, 1) 
        splitter.setStretchFactor(2, 3) 

        self.content_layout.addWidget(splitter)
        

        # Main layout for the window
        self.setup_toolbar(self.main_layout)
        scrollArea.setWidget(content_widget)
        self.main_layout.addWidget(scrollArea)