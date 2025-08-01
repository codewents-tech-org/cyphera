#Updated report generation 18.10.24
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QMessageBox, QMenuBar, QAction, QHeaderView, QTabWidget, QMenu,QMainWindow,QSizePolicy,
    QLineEdit, QLabel, QSplitter, QFrame, QToolTip, QGraphicsDropShadowEffect, QStyledItemDelegate, QToolBar,
    QGridLayout, QFileDialog, QStackedWidget, QButtonGroup, QSpacerItem, QTextEdit, QToolButton, QStyle,
    QFontComboBox,QWidgetAction, QColorDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QDialog,
    QSpinBox,QInputDialog, QScrollArea, QTextBrowser, QCheckBox
)
from PyQt5.QtGui import (
    QIcon, QPainter, QCursor, QFont, QColor, QBrush, QStandardItemModel, QStandardItem, 
    QTextCharFormat, QTextCursor, QTextListFormat, QTextImageFormat, QPainter, QTextTableFormat,QImage, 
    QTextLength, QPen, QPixmap, QWheelEvent
)
from PyQt5.QtCore import QTimer, Qt, QSize, QRect, QRectF, pyqtSlot, QPoint, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage
from components.loading_dialog import RoundLoader
import sqlite3
import shutil
import sys
import os
import docx
from docx2pdf import convert
import models.Parameters as P
import models.helper as helper
import controllers.DatabaseCreator as DB
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib.colors as mcolorsfrom
from docx.shared import Inches, Pt
from reportlab.lib.pagesizes import letter
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import RGBColor, Pt
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from bs4 import BeautifulSoup
from docx import Document
from html2docx import html2docx
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx import Document
from bs4 import BeautifulSoup
import base64
import os
from io import BytesIO
from PIL import Image
import win32com.client
from Reports.Generate_Reports.models.attacktree_collection import Update_AttackTree_Dictionary
from Reports.Generate_Reports.models.technical_attacktree_collection import Update_TechnicalAttackTree_Dictionary
from Reports.Generate_Reports.models.riskcontrol_tree_collection import Update_RiskControlTree_Dictionary
from Settings.views.controller import Report_input_submit as Report_Input_Submit
import Summary.Management_Summary.views.ManagementSummary_action as MSA
from Reports.Generate_Reports.views.generatereport_toolbar_panel import create_toolbar
from Reports.Generate_Reports.views.selection_panel import create_selection_panel
import components.action_panel as action_panel
import styles.property_panel_style as property_style
import styles.action_panel_style as actionpanel_style
import utils.interface_utils as interfaces
from controllers.schema_manager import get_instances, get_first_instance
from controllers.tablemodel import (
            SystemDescription, ScopeDescription, ScopeHomeMindmap, Assumptions, Misusecases, TOEConfiguration,
            Assets, DamageScenarios, Threats, ThreatScenarios,
            SecurityClaims, SecurityGoals, SecurityControls,
            AttackTreeHome, AttackTree, RiskControlTreeHome, RiskControlTree, TechnicalTreeHome, TechnicalAttackTree, AttackLeafNodes,
            RiskData, HighLevelRisk, InitialRiskMatriks, ResidRiskMatriks, MSDescription
        )
import logging

logger = logging.getLogger(__name__)


MAX_WIDTH = 6.5  # Maximum width allowed in inches
MAX_HEIGHT = 9.0  # Maximum height allowed in inches

def process_image(img_src, doc):
        """Handles both base64 and file path images, ensuring only resized images are centered."""
        try:
            if img_src.startswith('data:image/'):
                # Extract base64 data and decode
                base64_str = img_src.split('base64,')[1]
                img_data = base64.b64decode(base64_str)
                img = Image.open(BytesIO(img_data))
            else:
                # Load image from file path
                img = Image.open(img_src)

            img_width, img_height = img.size
            aspect_ratio = img_width / img_height

            # Convert pixels to inches (assuming 96 DPI for Word documents)
            width_inches = img_width / 96
            height_inches = img_height / 96

            # Determine if resizing is required
            needs_resizing = width_inches > MAX_WIDTH or height_inches > MAX_HEIGHT

            if needs_resizing:
                # Resize while maintaining aspect ratio
                if width_inches > MAX_WIDTH:
                    new_width = MAX_WIDTH
                    new_height = new_width / aspect_ratio
                if new_height > MAX_HEIGHT:
                    new_height = MAX_HEIGHT
                    new_width = new_height * aspect_ratio

                img = img.resize((int(new_width * 96), int(new_height * 96)))  # Use 96 DPI
            else:
                new_width, new_height = width_inches, height_inches  # Keep original size

            # Save temporary image file (to ensure proper rendering in PDFs)
            temp_img_path = "temp_image.png"
            img.save(temp_img_path)

            # Insert Image into Word document
            doc.add_picture(temp_img_path, width=Inches(new_width), height=Inches(new_height))

            # **Center alignment only for resized images**
            if needs_resizing:
                last_paragraph = doc.paragraphs[-1]
                last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER  # Center only resized images

            # Clean up the temporary file
            os.remove(temp_img_path)

        except Exception as e:
            print(f"Failed to process image: {img_src}. Error: {e}")


class GenerateReport_module(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_path = P.Report_footer_Logo
        self.logo1_path = P.Report_Logo
        self.logo2_path = P.Report_footer_Logo
        self.table_display_order = {
        "Target of Evaluation": {

            "System Description": "system_description",
            "Scope": "scope_description",
            "Assumptions": "assumptions",
            "Misuse Cases": "misuse_cases",
            "TOE Configuration": "toe_configuration",
        },
        "Analysis": {
           
            "Assets": "assets",
            "Damage Scenarios": "damage_scenarios",
            "Threats": "threat",
            "Threat Scenarios": "threat_scenarios"
        },
        "Security Measurement": {
           
            "Security Claims": "security_claims",
            "Security Goals": "security_goals",
            "Security Controls": "security_controls",
            
        },
         "Attack Paths": {
           
           "Attack Tree": "attack_tree_home",
            "Risk Control Tree": "riskcontrol_tree_home",
            "Technical Attack Tree": "technical_tree_home",
            "Attack Leaves": "attack_leaf_nodes"
        },
        "Risk Assessment": {

            "Risk Treatment": "risk_data",
        },
        "Summary": {
            
            "Management Summary": "management_summary"
        }
    }
        self.checkboxes = {}
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        create_toolbar(self)
        main_layout.addWidget(self.toolbar)

        action_panel.create_action_panel(self)

        create_selection_panel(self)

        self.download_button.setEnabled(False)
        self.generate_button.clicked.connect(self.generateReport)
        self.download_button.clicked.connect(self.downloadReport)

        for group_name, items in self.table_display_order.items():
            # Add group label (e.g., "System Info", "Configuration")
            group_label = QLabel(group_name)
            group_label.setStyleSheet(property_style.property_label_style)
            self.selection_layout.addWidget(group_label)

            # Add a spacer between the label and the group items
            spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.selection_layout.addItem(spacer)

            # Add checkboxes for each item in the group
            for display_name, internal_name in items.items():
                # Create a horizontal layout to add left padding
                checkbox_layout = QHBoxLayout()
                checkbox_layout.setContentsMargins(20, 0, 0, 0)  # Set left padding (20px)
                checkbox_layout.setSpacing(0)  # Remove internal spacing

                checkbox = QCheckBox(display_name)
                checkbox.setChecked(True)  # Optionally set to True or False
                
                # Add the checkbox to the horizontal layout
                checkbox_layout.addWidget(checkbox)
                
                # Add the horizontal layout with padding to the selection layout
                self.selection_layout.addLayout(checkbox_layout)
                self.checkboxes[internal_name] = checkbox
            
            # Add space before the line
            space_before_line = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.selection_layout.addItem(space_before_line)
            
            # Optionally, add a divider line after each group
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setFixedHeight(2)  # Ensure it's thick enough to be visible
            line.setStyleSheet(property_style.property_line_style)  # Ensure the line color is visible
            self.selection_layout.addWidget(line)
            
            # Add space before the line
            space_before_line = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.selection_layout.addItem(space_before_line)
        
        # Add the selection panel layout to the main layout
        #main_layout.addLayout(self.selection_layout)

       # Create a layout to hold the web view (QVBoxLayout or QHBoxLayout, based on preference)
        self.web_view_layout = QVBoxLayout()
        self.web_view_layout.setContentsMargins(10, 10, 10, 10)  # Left, Top, Right, Bottom margins

        # Create the CustomWebEngineView instance
        self.web_view = CustomWebEngineView(self)
        self.web_view.setStyleSheet(actionpanel_style.web_view_style)
        self.web_view.setZoomFactor(1.0)  # Optional: Set zoom level
        interfaces.report_panel_view = self.web_view

        # Enable settings for PDF rendering
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)

        # Add the web view to the layout
        self.web_view_layout.addWidget(self.web_view)

        # Add the web view layout to the action panel layout
        self.action_panel_layout.addLayout(self.web_view_layout)

        # Add the other panels after the web view
        self.action_panel_layout.addWidget(self.switch_selection_panel)
        self.action_panel_layout.addWidget(self.selection_panel)

        # Add the action panel to the main layout
        main_layout.addWidget(self.action_panel)

    def load_data(self): pass

    def generateReport(self):
        logger.info("Generating Report as PDF")
        self.loader = RoundLoader(self, label_text='Generating...')  # Use the same loader
        self.loader.show()  # Show loader first
        QApplication.processEvents()  # Allow UI to update immediately

        MSA.ManagementSummary_module().load_data()
        
        self.GenerateReport_table_list = [internal_name for internal_name, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        self.GenerateReport_tables = [checkbox.text() for internal_name, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        doc_path = 'report/generated_report.docx'
        doc_path = P.GenerateReport_path

        doc = docx.Document()

        doc.add_paragraph()
        doc.add_paragraph()
        paragraph = doc.add_paragraph("CYPHERA REPORT", style='Heading 1')
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        doc.paragraphs[-1].runs[0].font.color.rgb = RGBColor(136, 171, 142)

        run = paragraph.runs[0]
        run.font.size = Pt(50)

        doc.add_paragraph()
        paragraph = doc.add_paragraph()

        footer_db = Report_Input_Submit.FooterDatabase()
        heading_image_path = footer_db.fetch_heading_image_path()

        # Add heading image to first page
        if heading_image_path:
            heading_paragraph = doc.add_paragraph()
            heading_run = heading_paragraph.add_run()
            heading_run.add_picture(heading_image_path, width=Inches(3))  # Adjust width as needed
            
            # Align to center
            heading_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        footer_db.close_connection()

        doc.add_paragraph()
        doc.add_paragraph()

        footer_paragraph = doc.add_paragraph()
        current_date = datetime.now().strftime("%d.%m.%Y")
        footer_paragraph.add_run("\nDate of Submission: ").bold = True
        footer_paragraph.add_run(current_date).font.size = Pt(12)
        footer_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

        self.addHeaderFooter(doc)

        doc.add_page_break()
        # project_paragraph = doc.add_paragraph(f"\n\n\n\t\tProject Name : {P.Project_name}\n", style='Heading 2')
        # project_paragraph = doc.add_paragraph(f"\t\tAuthor : {P.Author_name}\n", style='Heading 2')
        # project_paragraph = doc.add_paragraph(f"\t\tClient : {P.Client_name}\n", style='Heading 2')
        # project_paragraph = doc.add_paragraph(f"\t\tSupplier : {P.Supplier_name}\n", style='Heading 2')
        # project_paragraph = doc.add_paragraph(f"\t\tMethodology : {P.selected_methedology}\n", style='Heading 2')
        # project_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

        # project_heading = doc.add_paragraph(P.Project_name, style='Heading 1')
        doc.add_paragraph()
        doc.add_heading(f'{P.Project_name}', level=1).runs[0].font.size = Pt(30)
        doc.paragraphs[-1].runs[0].font.color.rgb = RGBColor(136, 171, 142)
        doc.add_paragraph()
        # Create a 4-row, 2-column table for the remaining metadata
        table = doc.add_table(rows=4, cols=2)
        table.style = 'Table Grid'  # You can change this to 'Light Grid', 'Plain Table', etc.

        def remove_table_borders(table):
            tbl = table._tbl
            tblPr = tbl.tblPr
            borders = OxmlElement('w:tblBorders')

            for border_name in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'nil')  # 'nil' disables the border
                borders.append(border)

            tblPr.append(borders)

        remove_table_borders(table)
        # Fill table with data
        entries = [
            ("Author\n", P.Author_name),
            ("Client\n", P.Client_name),
            ("Supplier\n", P.Supplier_name),
            ("Methodology\n", P.selected_methedology)
        ]

        for row, (label, value) in zip(table.rows, entries):
            row.cells[0].text = label
            row.cells[1].text = value

        # Optional: Set alignment for table cells
        for row in table.rows:
            for i, cell in enumerate(row.cells):
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    for run in paragraph.runs:
                        run.font.size = Pt(18)
                
                # Set first-column text color to blue
                if i == 0:
                    run.font.color.rgb = RGBColor(0, 0, 255)
                    row.cells[0].width = Inches(2.0)

        doc.add_page_break()
        doc.add_heading('Contents', level=1).runs[0].font.size = Pt(30)
        doc.paragraphs[-1].runs[0].font.color.rgb = RGBColor(136, 171, 142)
        self.table_name_mapping = {}
        self.heading_mapping = {}
        contents = self.create_contents()

        numbering_main = 1
        for content in contents:
            if "subcontents" in content:
                paragraph = doc.add_paragraph()
                paragraph.add_run(f"{numbering_main}. {content['title']}\t").bold = True
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

                numbering_sub = 1
                for subcontent in content['subcontents']:
                    paragraph = doc.add_paragraph(f"\t{numbering_main}.{numbering_sub} {subcontent['title']}")
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    numbering_sub += 1

                numbering_main += 1
            else:
                paragraph = doc.add_paragraph(f"{numbering_main}. {content['title']}")
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                numbering_main += 1

        table_column_names = {
        "assets": ["ID", "Name", "Security Properties", "Description", "Comments"],
        "damage_scenarios": ["ID", "Name", "Impact", "Impact Category", "Description", "Comments"],
        "risk_data": ["Damage", "Impact", "Threat Values", "Initial AFR", "Initial Risk", "Resd AFR", "Resd Risk", "TOE Configuration", "Resd Decision", "Security Claims", "Security Goals", "Mitigated By", "Risk ID"],
        "security_claims" : ["ID", "Name", "Assumptions", "Responsible", "TOE Configuration", "Description", "Comments"],
        "security_controls" : ["ID", " Name", "Security Goal", "Description", "Comments"],
        "security_goals" : ["ID", " Name", "Responsible", "TOE Configuration", "Description", "Comments"],
        "attack_leaf_nodes" : ["ID", "Name", "Time", "Expertise", "knowledge", "Access", "Equipment", "AFR_Level", "Reasoning", "comments"],
        "threat" : ["Threat ID", "Name", "Damage Scenarios", "TOE Configuration", "Misuse Cases", "Initial AFR", "Resid AFR", "Asset", "Security Properties","Reasoning", "Comment"],
        "riskcontrol_tree_home" :["ID", "Name", "Mitigates", "Assumptions", "Comment"],
        "technical_tree_home" : ["ID", "Name", "Used In Threats", "Used In Security Controls", "TOE Configuration", "Assumptions", "Comments"],
        "assumptions" : ["Assumption ID", "Assumptions", "Comments"],
        "attack_tree_home" : ["ID" ,"Name", "Initial AFR", "Resid AFR", "TOE Configuration", "Comments"],
        "threat_scenarios" : ["ID", "Threat", "Damage Scenarios", "TOE Configuration", "Reasoning", "Comment"],
        "high_level_risk" : ["Impact Category", "Initial AFR Level", "Resid AFR Level"],
        "SecurityControls" : ["Security Controls"],
        "AssumptionsInManagementSummary" : ["Assumptions"],
        "TOEConfigurationInManagementSummary" : ["TOE Configuration"],
        "misuse_cases" : ["ID", "Name", "Comments"],
        "toe_configuration" : ["ID", "Name", "Description", "Comments"],
        "initialriskmatriks" : ["risk", "Negligible", "Moderate", "Major", "Severe"],
        "residriskmatriks" : ["risk", "Negligible", "Moderate", "Major", "Severe"],
        }

        try:
            # tables = DB.execute_db("SELECT name FROM sqlite_master WHERE type='table' ;")
            doc.add_page_break()
            doc.add_heading('1.Introduction', level=1).runs[0].font.size = Pt(30)
            doc.paragraphs[-1].runs[0].font.color.rgb = RGBColor(136, 171, 142)
            doc.add_paragraph()
            doc.add_paragraph()
            introduction_text = (
                "Threat Analysis and Risk Assessment is a vital tool in Cybersecurity that helps "
                "organizations identify, assess, and prioritize potential threats and risks. "
                "By systematically evaluating the security landscape, TARA provides insights "
                "into vulnerabilities and threats, enabling organizations to implement effective "
                "measures to mitigate risks. The TARA process involves identifying assets, "
                "determining threats, assessing vulnerabilities, and evaluating the potential "
                "impact of these threats. This comprehensive approach ensures that security "
                "strategies are well-informed and aligned with the organization's overall risk management goals."
            )
            p = doc.add_paragraph(introduction_text)
            p.alignment = 3
            doc.add_page_break()

            excluded_tables = {'trash', 'threat_trash', 'ts_trash', 'asset_trash', 'ds_trash', 'assum_trash', 'attack_scenarios', 'sqlite_sequence', 'notes','ManagementSummary', 'riskcontrol_tree', 'security_controls_trash',  'SClaims_trash', 'SGoals_trash', 'attack_tree'}

            heading_number = 2
            for heading_name, table_list in self.heading_mapping.items():
                doc.add_heading(f" {heading_number}. {heading_name}", level=1).runs[0].font.size = Pt(30)
                doc.paragraphs[-1].runs[0].font.color.rgb = RGBColor(136, 171, 142)
                heading_number += 1
                print(table_list)
                for table_name in table_list:
                    if table_name == 'system_description':
                       if table_name == 'system_description':
                            print("................................system_description.......................................")
                            project_paragraph = doc.add_paragraph(f"{self.table_name_mapping['system_description']}", style='Heading 2')
                            project_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                            run = project_paragraph.runs[0]
                            run.font.size = Pt(30)
                            run.font.bold = True
                            run.font.color.rgb = RGBColor(136, 171, 142)
                            
                            # **Add extra padding before inserting images or content**
                            doc.add_paragraph("\n\n")  # Adds two blank lines for spacing

                            self.save_to_word_document(doc) 
                    
                    elif table_name == 'scope_description':
                        print("................................scope.......................................")
                        project_paragraph = doc.add_paragraph(f"{self.table_name_mapping['scope_description']}", style='Heading 2')
                        project_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                        run = project_paragraph.runs[0]
                        run.font.size = Pt(30)
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(136, 171, 142)
                        self.save_to_word_document2(doc)
                    
                    elif table_name == 'MS_Description':
                        print("................................MS_description.......................................")
                        project_paragraph = doc.add_paragraph(f"{self.table_name_mapping['MS_Description']}", style='Heading 2')
                        project_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                        run = project_paragraph.runs[0]
                        run.font.size = Pt(30)
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(136, 171, 142)
                        self.save_to_word_document3(doc)
                    
                    elif table_name == 'misuse_cases':  
                        print("................................mC.......................................")
                        display_name = self.table_name_mapping.get(table_name, table_name)
                        doc.add_heading(f" {display_name}", level=2).runs[0].font.size = Pt(30)
                        doc.paragraphs[-1].runs[0].font.color.rgb = RGBColor(136, 171, 142)
                        doc.add_paragraph()
                        if table_name in table_column_names:
                            column_names = table_column_names[table_name]
                            doc_table = doc.add_table(rows=1, cols=len(column_names))
                            header_cells = doc_table.rows[0].cells
                            for i, col_name in enumerate(column_names):
                                paragraph = header_cells[i].paragraphs[0]
                                run = paragraph.add_run(col_name)
                                run.font.color.rgb = RGBColor(0, 0, 0)
                                run.font.bold = True
                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                header_cells[i]._element.get_or_add_tcPr().append(
                                    parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                )
                            # Fetch data from the database
                            # rows = DB.execute_db("SELECT misuse_cases_id, misuse_cases_name, misuse_cases_comments FROM misuse_cases;")
                            table_data = get_instances(Misusecases, {'is_deleted':'False'})
                            for instance in table_data:
                                row_cells = doc_table.add_row().cells
                                row = [instance.misuse_cases_id, instance.misuse_cases_name, instance.misuse_cases_comments]
                                for i, value in enumerate(row):
                                    row_cells[i].text = str(value)
                                    paragraph = row_cells[i].paragraphs[0]
                                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            doc.add_paragraph() 
                    
                    elif table_name == 'toe_configuration':  
                        print("................................TOE Configure.......................................")
                        display_name = self.table_name_mapping.get(table_name, table_name)
                        doc.add_heading(f" {display_name}", level=2).runs[0].font.size = Pt(30)
                        doc.paragraphs[-1].runs[0].font.color.rgb = RGBColor(136, 171, 142)
                        doc.add_paragraph()
                        if table_name in table_column_names:
                            column_names = table_column_names[table_name]
                            doc_table = doc.add_table(rows=1, cols=len(column_names))
                            header_cells = doc_table.rows[0].cells
                            for i, col_name in enumerate(column_names):
                                paragraph = header_cells[i].paragraphs[0]
                                run = paragraph.add_run(col_name)
                                run.font.color.rgb = RGBColor(0, 0, 0)
                                run.font.bold = True
                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                header_cells[i]._element.get_or_add_tcPr().append(
                                    parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                )
                            # Fetch data from the database
                            # rows = DB.execute_db("SELECT toe_configuration_id, toe_configuration_name, toe_configuration_description, toe_configuration_comments FROM toe_configuration;")
                            table_data = get_instances(TOEConfiguration, {'is_deleted':'False'})
                            for instance in table_data:
                                row_cells = doc_table.add_row().cells
                                row = [instance.toe_configuration_id, instance.toe_configuration_name, instance.toe_configuration_description, instance.toe_configuration_comments]
                                for i, value in enumerate(row):
                                    row_cells[i].text = str(value)
                                    paragraph = row_cells[i].paragraphs[0]
                                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            doc.add_paragraph()               
    
                    else:
                        if table_name not in table_column_names:
                            continue
                        if table_name.lower() in excluded_tables:
                            continue
                        display_name = self.table_name_mapping.get(table_name, table_name)
                        doc.add_heading(f" {display_name}", level=2).runs[0].font.size = Pt(30)
                        doc.paragraphs[-1].runs[0].font.color.rgb = RGBColor(136, 171, 142)

                        doc.add_paragraph()

                        impact_color_map = {
                            "Major": RGBColor(199, 91, 122),
                            "Moderate": RGBColor(217, 171, 171),
                            "Negligible": RGBColor(244, 217, 208),
                            "Severe": RGBColor(146,26,64)
                        }
                        afr_level_color_map = {
                            "High": "0097b2",
                            "Medium": "0cc0df",
                            "Low": "5ce1e6",
                            "Very Low": "cefdff"
                        }
                        afr_value_color_map = {
                            "5": "a80000",
                            "4": "ff3131",
                            "3": "ff914d",
                            "2": "ffde59",
                            "1": "7ed957"
                        }

                        if table_name == "risk_data":
                            column_names_1 = ["Damage Scenario", "Impact", "Initial Risk", "Resid. Risk"]
                            doc_table = doc.add_table(rows=1, cols=len(column_names_1))
                            header_cells = doc_table.rows[0].cells
                            for i, col_name in enumerate(column_names_1):
                                paragraph = header_cells[i].paragraphs[0]
                                run = paragraph.add_run(col_name)
                                run.font.color.rgb = RGBColor(0, 0, 0)
                                run.font.bold = True
                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                header_cells[i]._element.get_or_add_tcPr().append(
                                    parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                )
                            
                            # rows = DB.execute_db("""
                            #     SELECT damage, impact, [init_AFR_value], [resid_AFR_value] 
                            #     FROM RiskData;
                            # """)
                            rows = get_instances(RiskData)
                            for instance in rows:
                                row_cells = doc_table.add_row().cells
                                row = [instance.ds_id, instance.impact, instance.init_afr_value, instance.resid_afr_value]
                                for i, value in enumerate(row):
                                    row_cells[i].text = str(value)
                                    paragraph = row_cells[i].paragraphs[0]
                                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                                    if column_names_1[i] == "Impact":
                                        impact_text = str(value)
                                        if impact_text in impact_color_map:
                                            color_code = impact_color_map[impact_text]
                                            row_cells[i]._element.get_or_add_tcPr().append(
                                                parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                            )

                                    if column_names_1[i] == "Initial Risk":
                                        init_AFR_value_text = str(value)
                                        if init_AFR_value_text in afr_value_color_map:
                                            color_code = afr_value_color_map[init_AFR_value_text]
                                            row_cells[i]._element.get_or_add_tcPr().append(
                                                parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                            )
                                    
                                    if column_names_1[i] == "Resid. Risk":
                                        resid_AFR_value_text = str(value)
                                        if resid_AFR_value_text in afr_value_color_map:
                                            color_code = afr_value_color_map[resid_AFR_value_text]
                                            row_cells[i]._element.get_or_add_tcPr().append(
                                                parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                            )

                            doc.add_paragraph()

                            # damage_scenarios = DB.execute_db("SELECT DISTINCT damage FROM RiskData;")
                            damage_scenarios = []
                            rows = get_instances(RiskData)
                            for row in rows:
                                if row.ds_id not in damage_scenarios: damage_scenarios.append(row.ds_id)
                            for damage in damage_scenarios:
                                doc.add_heading(f"Damage Scenario: {damage}", level=3).runs[0].font.size = Pt(24)
                                doc.paragraphs[-1].runs[0].font.color.rgb = RGBColor(136, 171, 142)
                                doc.add_paragraph()

                                column_names_2 = ["ID", "Threat ", "Impact", "Initial AFR", "Initial Risk", "Resid. AFR", "Resid. Risk"]
                                doc_table = doc.add_table(rows=1, cols=len(column_names_2))
                                header_cells = doc_table.rows[0].cells
                                for i, col_name in enumerate(column_names_2):
                                    paragraph = header_cells[i].paragraphs[0]
                                    run = paragraph.add_run(col_name)
                                    run.font.color.rgb = RGBColor(0, 0, 0)
                                    run.font.bold = True
                                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                    header_cells[i]._element.get_or_add_tcPr().append(
                                        parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                    )

                                # DB.cursor.execute("""
                                #     SELECT [id], [threat], impact, [init_AFR_level], [init_AFR_value], [resid_AFR_level], [resid_AFR_value]
                                #     FROM RiskData WHERE damage = ?""", (damage,))
                                # rows = DB.cursor.fetchall()
                                rows = get_instances(RiskData, {'ds_id':damage})
                                for instance in rows:
                                    row_cells = doc_table.add_row().cells
                                    row = [instance.rd_id, instance.threat_id, instance.impact, instance.init_afr_level, instance.init_afr_value, instance.resid_afr_level, instance.resid_afr_value]
                                    for i, value in enumerate(row):
                                        row_cells[i].text = str(value)
                                        paragraph = row_cells[i].paragraphs[0]
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                                        if column_names_2[i] == "Impact":
                                            impact_text = str(value)
                                            if impact_text in impact_color_map:
                                                color_code = impact_color_map[impact_text]
                                                row_cells[i]._element.get_or_add_tcPr().append(
                                                    parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                                )

                                        if column_names_2[i] == "Initial AFR":
                                            init_AFR_level_text = str(value)
                                            if init_AFR_level_text in afr_level_color_map:
                                                color_code = afr_level_color_map[init_AFR_level_text]
                                                row_cells[i]._element.get_or_add_tcPr().append(
                                                    parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                                )
                                        
                                        if column_names_2[i] == "Resid. AFR":
                                            resid_AFR_level_text = str(value)
                                            if resid_AFR_level_text in afr_level_color_map:
                                                color_code = afr_level_color_map[resid_AFR_level_text]
                                                row_cells[i]._element.get_or_add_tcPr().append(
                                                    parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                                )

                                        if column_names_2[i] == "Initial Risk":
                                            init_AFR_value_text = str(value)
                                            if init_AFR_value_text in afr_value_color_map:
                                                color_code = afr_value_color_map[init_AFR_value_text]
                                                row_cells[i]._element.get_or_add_tcPr().append(
                                                    parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                                )
                                        
                                        if column_names_2[i] == "Resid. Risk":
                                            resid_AFR_value_text = str(value)
                                            if resid_AFR_value_text in afr_value_color_map:
                                                color_code = afr_value_color_map[resid_AFR_value_text]
                                                row_cells[i]._element.get_or_add_tcPr().append(
                                                    parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                                )
                                for row in doc_table.rows:
                                    for cell in row.cells:
                                        for paragraph in cell.paragraphs:
                                            paragraph.paragraph_format.keep_with_next = True        

                                doc.add_paragraph()
                                column_names_3 = ["ID", "TOE Configuration", "Risk Decision", "Security Claims", "Security Goals", "Mitigated By"]
                                doc_table = doc.add_table(rows=1, cols=len(column_names_3))
                                header_cells = doc_table.rows[0].cells
                                for i, col_name in enumerate(column_names_3):
                                    paragraph = header_cells[i].paragraphs[0]
                                    run = paragraph.add_run(col_name)
                                    run.font.color.rgb = RGBColor(0, 0, 0)
                                    run.font.bold = True
                                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                    header_cells[i]._element.get_or_add_tcPr().append(
                                        parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                    )

                                # DB.cursor.execute("""
                                #     SELECT [id], [toe_configuration], [risk_treatment], [security_claims], [security_goals], [mitigated_by] 
                                #     FROM RiskData 
                                #     WHERE damage = ?;
                                # """, (damage,))
                                # rows = DB.cursor.fetchall()
                                rows = get_instances(RiskData, {'ds_id':damage})
                                for instance in rows:
                                    row_cells = doc_table.add_row().cells
                                    row = [instance.rd_id, instance.toe_configuration_id, instance.risk_treatment, instance.security_claims_id, instance.security_goal_id, instance.mitigated_by]
                                    for i, value in enumerate(row):
                                        row_cells[i].text = str(value)
                                        paragraph = row_cells[i].paragraphs[0]
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                for row in doc_table.rows:
                                    for cell in row.cells:
                                        for paragraph in cell.paragraphs:
                                            paragraph.paragraph_format.keep_with_next = True        

                                doc.add_paragraph()

                        elif table_name == 'attack_leaf_nodes':
                            display_name = self.table_name_mapping.get(table_name, table_name)


                            # Fetch the attack leaves from the database with additional attributes
                            # rows = DB.execute_db("SELECT id, name, time, expertise, knowledge, access, equipment, AFR_Level, reasoning, comments  FROM attack_leaf_home;")
                            rows = get_instances(AttackLeafNodes, {'is_deleted':False})
                            # Iterate through each attack leaf and format the output
                            for instance in rows:
                                row = [instance.id, instance.name, instance.time, instance.expertise, instance.knowledge, instance.access, instance.equipment, instance.afr_level, instance.reasoning, instance.comments]
                                attack_id, attack_name, time, expertise, knowledge, access, equipment, afr_level, reasoning, description = row

                                # Add a sub-heading for each attack leaf (ID & Name)
                                sub_heading = doc.add_heading(f"{attack_id}: {attack_name}", level=3)
                                sub_heading.runs[0].font.size = Pt(12)
                                sub_heading.runs[0].font.color.rgb = RGBColor(0, 0, 0)

                                # Create a two-column table for additional details
                                doc_table = doc.add_table(rows=4, cols=2)
                                tbl = doc_table._element
                                tblBorders = tbl.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblBorders")
                                if tblBorders is not None:
                                    tbl.remove(tblBorders)

                                # Define attribute names and corresponding values
                                attack_potential = f"T= {time}  Ex= {expertise}  K= {knowledge}  A= {access}  Eq= {equipment}"
                                attributes = [
                                    ("Attack Potential", attack_potential),
                                    ("AFR", afr_level),
                                    ("Reasoning", reasoning),
                                    ("Description", description)
                                ]

                                # Populate the table
                                for i, (attr_name, attr_value) in enumerate(attributes):
                                    row_cells = doc_table.rows[i].cells
                                    row_cells[0].text = attr_name  # Left column → Attribute name
                                    row_cells[1].text = str(attr_value)  # Right column → Corresponding value

                                    for j, cell in enumerate(row_cells):
                                        paragraph = cell.paragraphs[0]
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        run = paragraph.runs[0]
                                        if j == 0:  # Only bold the first column (attribute names)
                                            run.font.bold = False
                                        else:  # Ensure the second column (values) is not bold
                                            run.font.bold = False

                                    row_cells[0].width = Inches(2)  # First column (Attribute name)
                                    row_cells[1].width = Inches(2.4)        

                                    if attr_name == "AFR":
                                        afr_color = afr_level_color_map.get(attr_value, "FFFFFF")
                                        row_cells[1]._element.get_or_add_tcPr().append(
                                            parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), afr_color))
                                        ) 
                            
                                doc.add_paragraph()  # Add spacing between attack leaves


                        elif table_name == 'technical_tree_home':
                            print("................................technical attack tree.......................................")
                            if table_name in table_column_names:
                                column_names = table_column_names[table_name]
                                doc_table = doc.add_table(rows=1, cols=len(column_names))
                                header_cells = doc_table.rows[0].cells

                                # Set table headers
                                for i, col_name in enumerate(column_names):
                                    paragraph = header_cells[i].paragraphs[0]
                                    run = paragraph.add_run(col_name)
                                    run.font.color.rgb = RGBColor(0, 0, 0)
                                    run.font.bold = True
                                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                    header_cells[i]._element.get_or_add_tcPr().append(
                                        parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                    )

                                # Fetch data from the database
                                # rows = DB.execute_db("SELECT id, name, used_in_threat, used_in_riskcontrol, toe_configuration, assumptions, comment FROM technical_tree_home;")
                                rows = get_instances(TechnicalTreeHome, {'is_deleted':False})
                                for instance in rows:
                                    row_cells = doc_table.add_row().cells
                                    row = [instance.id, instance.name, instance.used_in_threat, instance.used_in_riskcontrol, instance.toe_configuartion_id, instance.assumption_id, instance.comment]
                                    for i, value in enumerate(row):
                                        row_cells[i].text = str(value)
                                        paragraph = row_cells[i].paragraphs[0]
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                            doc.add_paragraph()  # Space before the Technical Attack Tree

                            # Now, add the Technical Attack Tree below the table
                            Update_TechnicalAttackTree_Dictionary(doc)                    

                        elif table_name == 'riskcontrol_tree_home':
                            print("................................risk control tree.......................................")
                            if table_name in table_column_names:
                                column_names = table_column_names[table_name]
                                doc_table = doc.add_table(rows=1, cols=len(column_names))
                                header_cells = doc_table.rows[0].cells

                                # Set table headers
                                for i, col_name in enumerate(column_names):
                                    paragraph = header_cells[i].paragraphs[0]
                                    run = paragraph.add_run(col_name)
                                    run.font.color.rgb = RGBColor(0, 0, 0)
                                    run.font.bold = True
                                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                    header_cells[i]._element.get_or_add_tcPr().append(
                                        parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                    )

                                # Fetch data from the database
                                # rows = DB.execute_db("SELECT id, name, mitigates, assumptions, comment FROM riskcontrol_tree_home;")
                                rows = get_instances(RiskControlTreeHome, {'is_deleted':False})
                                for instance in rows:
                                    row_cells = doc_table.add_row().cells
                                    row = [instance.id, instance.name, instance.mitigates, instance.assumption_id, instance.comment]
                                    for i, value in enumerate(row):
                                        row_cells[i].text = str(value)
                                        paragraph = row_cells[i].paragraphs[0]
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                            # doc.add_paragraph()  # Space before the risk control tree

                            # Now, add the Risk Control Tree below the table
                            Update_RiskControlTree_Dictionary(doc)

                        elif table_name == 'attack_tree_home':
                            print("................................attack tree.......................................")
                            # Set column names
                            column_names = ["ID", "Name", "Initial AFR", "Resid AFR", "TOE Configuration", "Comments"]
                            doc_table = doc.add_table(rows=1, cols=len(column_names))
                            header_cells = doc_table.rows[0].cells
                            
                            # Set header
                            for i, col_name in enumerate(column_names):
                                paragraph = header_cells[i].paragraphs[0]
                                run = paragraph.add_run(col_name)
                                run.font.color.rgb = RGBColor(0, 0, 0)
                                run.font.bold = True
                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                header_cells[i]._element.get_or_add_tcPr().append(
                                    parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                )
                            
                            # Fetch rows from database
                            # rows = DB.execute_db(f"SELECT id, name, InitialAFR, ResidAFR, toe_configuration, comments FROM attack_tree_home;")
                            rows = get_instances(AttackTreeHome, {'is_deleted':False})
                            # Populate the table and apply color based on AFR level
                            for instance in rows:
                                row_cells = doc_table.add_row().cells
                                row = [instance.id, instance.name, instance.initial_afr, instance.resid_afr, instance.toe_configuration_id, instance.comments]
                                for i, value in enumerate(row):
                                    row_cells[i].text = str(value)
                                    paragraph = row_cells[i].paragraphs[0]
                                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                    
                                    # Apply background color for "Initial AFR" based on the afr_level_color_map
                                    if column_names[i] == "Initial AFR":
                                        init_AFR_level_text = str(value)
                                        if init_AFR_level_text in afr_level_color_map:
                                            color_code = afr_level_color_map[init_AFR_level_text]
                                            row_cells[i]._element.get_or_add_tcPr().append(
                                                parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                            )

                                    # Apply background color for "Resid AFR" based on the afr_level_color_map
                                    if column_names[i] == "Resid AFR":
                                        resid_AFR_level_text = str(value)
                                        if resid_AFR_level_text in afr_level_color_map:
                                            color_code = afr_level_color_map[resid_AFR_level_text]
                                            row_cells[i]._element.get_or_add_tcPr().append(
                                                parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                            )
                            Update_AttackTree_Dictionary(doc)  
            
                        else:
                            if table_name == 'threat':
                                print("................................threat.......................................")
                                # Regular table handling
                                if table_name in table_column_names:
                                    column_names = table_column_names[table_name]
                                    doc_table = doc.add_table(rows=1, cols=len(column_names))
                                    header_cells = doc_table.rows[0].cells
                                    for i, col_name in enumerate(column_names):
                                        paragraph = header_cells[i].paragraphs[0]
                                        run = paragraph.add_run(col_name)
                                        run.font.color.rgb = RGBColor(0, 0, 0)
                                        run.font.bold = True
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        header_cells[i]._element.get_or_add_tcPr().append(
                                            parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                        )

                                    # rows = DB.execute_db(f"SELECT threat_id, name, damage_scenarios, toe_configuration, misuse_cases, InitialAFR, ResidAFR, asset, security_properties, reasoning, comments FROM threat")
                                    rows = get_instances(Threats, {'is_deleted':'False'})
                                    for instance in rows:
                                        row_cells = doc_table.add_row().cells
                                        row = [instance.threat_id, instance.name, instance.ds_id, instance.toe_configuration_id, instance.misuse_cases_id, instance.initia_afr, instance.resid_afr, instance.asset_id, instance.security_properties, instance.reasoning, instance.comments]
                                        for i, value in enumerate(row):
                                            row_cells[i].text = str(value)
                                            paragraph = row_cells[i].paragraphs[0]
                                            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        
                                            # Apply background color for "Initial AFR" based on the afr_level_color_map
                                            if column_names[i] == "Initial AFR":
                                                init_AFR_level_text = str(value)
                                                if init_AFR_level_text in afr_level_color_map:
                                                    color_code = afr_level_color_map[init_AFR_level_text]
                                                    row_cells[i]._element.get_or_add_tcPr().append(
                                                        parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                                    )

                                            # Apply background color for "Resid AFR" based on the afr_level_color_map
                                            if column_names[i] == "Resid AFR":
                                                resid_AFR_level_text = str(value)
                                                if resid_AFR_level_text in afr_level_color_map:
                                                    color_code = afr_level_color_map[resid_AFR_level_text]
                                                    row_cells[i]._element.get_or_add_tcPr().append(
                                                        parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                                    )

                            elif table_name == 'high_level_risk':
                                # Set column names
                                column_names = table_column_names['high_level_risk']
                                doc_table = doc.add_table(rows=1, cols=len(column_names))
                                header_cells = doc_table.rows[0].cells
                                
                                # Set header
                                for i, col_name in enumerate(column_names):
                                    paragraph = header_cells[i].paragraphs[0]
                                    run = paragraph.add_run(col_name)
                                    run.font.color.rgb = RGBColor(0, 0, 0)
                                    run.font.bold = True
                                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                    header_cells[i]._element.get_or_add_tcPr().append(
                                        parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                    )
                                
                                # Fetch rows from database
                                # rows = DB.execute_db(f"SELECT Impact_Category, InitAFRValue, ResidAFRValue FROM HighLevelRisk;")
                                rows = get_instances(HighLevelRisk)
                                # Populate the table and apply color based on AFR level
                                for instance in rows:
                                    row_cells = doc_table.add_row().cells
                                    row = [instance.impact_category, instance.init_afr_value, instance.resid_afr_value]
                                    for i, value in enumerate(row):
                                        row_cells[i].text = str(value)
                                        paragraph = row_cells[i].paragraphs[0]
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        
                                        # Apply background color for "Initial AFR" based on the afr_level_color_map
                                        if column_names[i] == "Initial AFR Level":
                                            init_AFR_level_text = str(value)
                                            if init_AFR_level_text in afr_value_color_map:
                                                color_code = afr_value_color_map[init_AFR_level_text]
                                                row_cells[i]._element.get_or_add_tcPr().append(
                                                    parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                                )

                                        # Apply background color for "Resid AFR" based on the afr_level_color_map
                                        if column_names[i] == "Resid AFR Level":
                                            resid_AFR_level_text = str(value)
                                            if resid_AFR_level_text in afr_value_color_map:
                                                color_code = afr_value_color_map[resid_AFR_level_text]
                                                row_cells[i]._element.get_or_add_tcPr().append(
                                                    parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_code))
                                                )
                                            
                            elif table_name == 'initialriskmatriks' or table_name == 'residriskmatriks':
                                    # Create a table with no header row
                                doc_table = doc.add_table(rows=0, cols=8)  # Adjust the number of columns as needed

                                # Retrieve data from the database
                                # rows = DB.execute_db(f"SELECT risk, Negligible, Moderate, Major, Severe FROM {table_name}")
                                table_name_select = InitialRiskMatriks if table_name == 'initialriskmatriks' else ResidRiskMatriks
                                rows = get_instances(table_name_select)
                                # Add data rows to the table
                                for row_index, instance in enumerate(rows):
                                    row_cells = doc_table.add_row().cells
                                    row = [instance.risk, instance.negligible, instance.moderate, instance.major, instance.severe]
                                    for col_index, value in enumerate(row):
                                        row_cells[col_index].text = str(value)
                                        paragraph = row_cells[col_index].paragraphs[0]
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        
                                        hex_color = None  # Initialize as None
            
                                        if col_index == 1 and row_index in [0, 1, 2, 3]:  # 2nd column (index 1), rows 1 to 4 (indexes 0 to 3)
                                            hex_color = '#90EE90'
                                        elif col_index == 2 and row_index in [3]:  # 2nd column (index 1), rows 1 to 4 (indexes 0 to 3)
                                            hex_color = '#90EE90'
                                        elif col_index == 2 and row_index in [0]:  # 2nd column (index 1), rows 1 to 4 (indexes 0 to 3)
                                            hex_color = '#ff9100'
                                        elif col_index == 3 and row_index in [1]:  # 2nd column (index 1), rows 1 to 4 (indexes 0 to 3)
                                            hex_color = '#ff9100' 
                                        elif col_index == 4 and row_index in [2]:  # 2nd column (index 1), rows 1 to 4 (indexes 0 to 3)
                                            hex_color = '#ff9100'
                                        elif col_index == 3 and row_index in [0]:  # 2nd column (index 1), rows 1 to 4 (indexes 0 to 3)
                                            hex_color = '#FF6347'
                                        elif col_index == 4 and row_index in [1]:  # 2nd column (index 1), rows 1 to 4 (indexes 0 to 3)
                                            hex_color = '#FF6347'                        
                                        elif col_index == 2 and row_index in [1, 2]:  # 3rd column (index 2), rows 2 and 3 (indexes 1, 2)
                                            hex_color = '#FFD700'
                                        elif col_index == 3 and row_index in [2, 3]:  # 4th column (index 3), rows 3 and 4 (indexes 2, 3)
                                            hex_color = '#FFD700'
                                        elif col_index == 4 and row_index == 3:  # 5th column (index 4), 4th row (index 3)
                                            hex_color = '#FFD700'
                                        elif col_index == 4 and row_index == 0:  # 5th column (index 4), 4th row (index 3)
                                            hex_color = '#8B0000'    
                                        
                                        # Apply the background color to the cell if a color is set
                                        if hex_color:
                                            row_cells[col_index]._element.get_or_add_tcPr().append(
                                                parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), hex_color[1:]))
                                            )
                            
                            elif table_name == 'security_controls':
                                print("................................security control.......................................")
                                # Regular table handling
                                if table_name in table_column_names:
                                    column_names = table_column_names[table_name]
                                    doc_table = doc.add_table(rows=1, cols=len(column_names))
                                    header_cells = doc_table.rows[0].cells
                                    for i, col_name in enumerate(column_names):
                                        paragraph = header_cells[i].paragraphs[0]
                                        run = paragraph.add_run(col_name)
                                        run.font.color.rgb = RGBColor(0, 0, 0)
                                        run.font.bold = True
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        header_cells[i]._element.get_or_add_tcPr().append(
                                            parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                        )

                                    # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                    rows = get_instances(SecurityControls, {'is_deleted':'False'})
                                    for instance in rows:
                                        row_cells = doc_table.add_row().cells
                                        row = [instance.scc_id, instance.name, instance.security_goal_id, instance.description, instance.comments]
                                        print(row)
                                        for i, value in enumerate(row):
                                            print(i, " : ", value)
                                            row_cells[i].text = str(value)
                                            paragraph = row_cells[i].paragraphs[0]
                                            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        print("am out.....")
                            
                            elif table_name == 'SecurityControls':
                                # Regular table handling
                                if table_name in table_column_names:
                                    column_names = table_column_names[table_name]
                                    doc_table = doc.add_table(rows=1, cols=len(column_names))
                                    header_cells = doc_table.rows[0].cells
                                    for i, col_name in enumerate(column_names):
                                        paragraph = header_cells[i].paragraphs[0]
                                        run = paragraph.add_run(col_name)
                                        run.font.color.rgb = RGBColor(0, 0, 0)
                                        run.font.bold = True
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        header_cells[i]._element.get_or_add_tcPr().append(
                                            parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                        )

                                    # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                    rows = get_instances(SecurityControls, {'is_deleted':'False'})
                                    for instance in rows:
                                        row_cells = doc_table.add_row().cells
                                        row = [f"{instance.scc_id}::{instance.name}"]
                                        for i, value in enumerate(row):
                                            row_cells[i].text = str(value)
                                            paragraph = row_cells[i].paragraphs[0]
                                            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            
                            elif table_name == 'AssumptionsInManagementSummary':
                                # Regular table handling
                                if table_name in table_column_names:
                                    column_names = table_column_names[table_name]
                                    doc_table = doc.add_table(rows=1, cols=len(column_names))
                                    header_cells = doc_table.rows[0].cells
                                    for i, col_name in enumerate(column_names):
                                        paragraph = header_cells[i].paragraphs[0]
                                        run = paragraph.add_run(col_name)
                                        run.font.color.rgb = RGBColor(0, 0, 0)
                                        run.font.bold = True
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        header_cells[i]._element.get_or_add_tcPr().append(
                                            parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                        )

                                    # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                    rows = get_instances(Assumptions, {'is_deleted':'False'})
                                    for instance in rows:
                                        row_cells = doc_table.add_row().cells
                                        row = [f"{instance.assumption_id}::{instance.assumptions}"]
                                        for i, value in enumerate(row):
                                            row_cells[i].text = str(value)
                                            paragraph = row_cells[i].paragraphs[0]
                                            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            
                            elif table_name == 'TOEConfigurationInManagementSummary':
                                # Regular table handling
                                if table_name in table_column_names:
                                    column_names = table_column_names[table_name]
                                    doc_table = doc.add_table(rows=1, cols=len(column_names))
                                    header_cells = doc_table.rows[0].cells
                                    for i, col_name in enumerate(column_names):
                                        paragraph = header_cells[i].paragraphs[0]
                                        run = paragraph.add_run(col_name)
                                        run.font.color.rgb = RGBColor(0, 0, 0)
                                        run.font.bold = True
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        header_cells[i]._element.get_or_add_tcPr().append(
                                            parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                        )

                                    # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                    rows = get_instances(TOEConfiguration, {'is_deleted':'False'})
                                    for instance in rows:
                                        row_cells = doc_table.add_row().cells
                                        row = [f"{instance.toe_configuration_id}::{instance.toe_configuration_name}"]
                                        for i, value in enumerate(row):
                                            row_cells[i].text = str(value)
                                            paragraph = row_cells[i].paragraphs[0]
                                            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            
                            else:
                                print("................................table name : ", table_name)
                                # Regular table handling
                                if table_name in table_column_names:
                                    column_names = table_column_names[table_name]
                                    doc_table = doc.add_table(rows=1, cols=len(column_names))
                                    header_cells = doc_table.rows[0].cells
                                    for i, col_name in enumerate(column_names):
                                        paragraph = header_cells[i].paragraphs[0]
                                        run = paragraph.add_run(col_name)
                                        run.font.color.rgb = RGBColor(0, 0, 0)
                                        run.font.bold = True
                                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                        header_cells[i]._element.get_or_add_tcPr().append(
                                            parse_xml(r'<w:shd {} w:fill="D3D3D3"/>'.format(nsdecls('w')))
                                        )

                                    if table_name == 'assets':
                                        print("................................assets.......................................")
                                        # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                        rows = get_instances(Assets, {'is_deleted':'False'})
                                        for instance in rows:
                                            row_cells = doc_table.add_row().cells
                                            row = [instance.asset_id, instance.name, instance.security_properties, instance.description, instance.comments]
                                            for i, value in enumerate(row):
                                                row_cells[i].text = str(value)
                                                paragraph = row_cells[i].paragraphs[0]
                                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                                    elif table_name == 'damage_scenarios':
                                        print("................................damege .......................................")
                                        # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                        rows = get_instances(DamageScenarios, {'is_deleted':'False'})
                                        for instance in rows:
                                            row_cells = doc_table.add_row().cells
                                            row = [instance.ds_id, instance.name, instance.impact, instance.impact_category, instance.description, instance.comments]
                                            for i, value in enumerate(row):
                                                row_cells[i].text = str(value)
                                                paragraph = row_cells[i].paragraphs[0]
                                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                                    elif table_name == 'threat_scenarios':
                                        print("................................threat scenarios.......................................")
                                        # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                        rows = get_instances(ThreatScenarios, {'is_deleted':'False'})
                                        for instance in rows:
                                            row_cells = doc_table.add_row().cells
                                            row = [instance.ts_id, instance.threat_id, instance.ds_id, instance.toe_configuration_id, instance.reasoning, instance.comments]
                                            for i, value in enumerate(row):
                                                row_cells[i].text = str(value)
                                                paragraph = row_cells[i].paragraphs[0]
                                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                                    elif table_name == 'security_claims':
                                        print("................................security claims.......................................")
                                        # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                        rows = get_instances(SecurityClaims, {'is_deleted':'False'})
                                        for instance in rows:
                                            row_cells = doc_table.add_row().cells
                                            row = [instance.sc_id, instance.name, instance.assumption_id, instance.responsible, instance.toe_configuration_id, instance.description, instance.comments]
                                            for i, value in enumerate(row):
                                                row_cells[i].text = str(value)
                                                paragraph = row_cells[i].paragraphs[0]
                                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                                    elif table_name == 'security_goals':
                                        print("................................security goals.......................................")
                                        # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                        rows = get_instances(SecurityGoals, {'is_deleted':'False'})
                                        for instance in rows:
                                            row_cells = doc_table.add_row().cells
                                            row = [instance.sg_id, instance.name, instance.responsible, instance.toe_configuration_id, instance.description, instance.comments]
                                            for i, value in enumerate(row):
                                                row_cells[i].text = str(value)
                                                paragraph = row_cells[i].paragraphs[0]
                                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

                                    elif table_name == 'assumptions':
                                        print("................................assumptions.......................................")
                                        # rows = DB.execute_db(f"SELECT * FROM {table_name};")
                                        rows = get_instances(Assumptions, {'is_deleted':'False'})
                                        for instance in rows:
                                            row_cells = doc_table.add_row().cells
                                            row = [instance.assumption_id, instance.assumptions, instance.comments]
                                            for i, value in enumerate(row):
                                                row_cells[i].text = str(value)
                                                paragraph = row_cells[i].paragraphs[0]
                                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                    
                                    else: pass

                    if table_name:
                        doc.add_page_break()
                
        except sqlite3.Error as e:
            #self.report_editor.setText(f"Database error: {e}")
            QMessageBox.warning(None, "SQL Error", f"Database: {e}")
            if self.loader: self.loader.close()
            return
        except Exception as e:
            #self.report_editor.setText(f"An error occurred: {e}")
            print(e)
            QMessageBox.warning(None, "Error", f"Error saving or opening the document: {e}")
            if self.loader: self.loader.close()
            return

        try:
            doc.save(doc_path)
        except Exception as e:
            #self.report_editor.setText(f"Error saving or opening the document: {e}")
            QMessageBox.warning(None, "Error", f"Error saving or opening the document1: {e}")
        try:
            doc.save(doc_path)
            
            print(f"Converting DOCX to PDF: {doc_path} -> {P.GeneratePdfReport_path}")
            self.convert_docx_to_pdf(docx_path=doc_path, pdf_path=P.GeneratePdfReport_path)
            
            print(f"Displaying generated PDF: {P.GeneratePdfReport_path}")
            self.display_pdf(P.GeneratePdfReport_path)
        except Exception as e:
            logger.error(f"Error in saving or opening document: {e}")
            print(f"Error in saving or opening document: {e}")
            QMessageBox.warning(None, "Error", f"Error saving or opening the document2: {e}")
        
        finally:
            if self.loader: self.loader.close()   

    def display_pdf(self, pdf_file_path):
        logger.info("Displaying the Generated PDF")
        try:
            # Ensure the PDF file path is absolute
            pdf_file_path = os.path.abspath(pdf_file_path)
            # Check if the file exists
            if not os.path.exists(pdf_file_path):
                raise FileNotFoundError(f"PDF file does not exist: {pdf_file_path}")
            # Generate file URL
            pdf_url = QUrl.fromLocalFile(pdf_file_path)
            #print(f"Generated PDF URL: {pdf_url.toString()}")
            # Configure the QWebEngineView
            settings = self.web_view.settings()
            settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
            settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
    
            # Load the PDF into the viewer
            self.web_view.load(pdf_url)

            self.web_view.repaint()  # Ensure the widget updates

            print(f"PDF successfully loaded: {pdf_file_path}")
            
        except Exception as e:
            print(f"Error displaying PDF: {e}")
            QMessageBox.critical(None, "Error", f"Failed to display PDF: {e}")
            
    def convert_docx_to_pdf(self, docx_path, pdf_path):
        try:
            # Ensure absolute paths for both DOCX and PDF
            docx_path = os.path.abspath(docx_path)
            pdf_path = os.path.abspath(pdf_path)
            
            # Debug: Print paths
            print(f"Attempting to convert DOCX to PDF. DOCX Path: {docx_path}, PDF Path: {pdf_path}")
            
            if not os.path.exists(docx_path):
                raise FileNotFoundError(f"The specified DOCX file does not exist: {docx_path}")
            
            # Initialize Word application using COM
            word = win32com.client.Dispatch("Word.Application")
            
            print(f"Opening DOCX file: {docx_path}")
            doc = word.Documents.Open(docx_path)
            
            # Save as PDF
            print(f"Saving DOCX as PDF at: {pdf_path}")
            doc.SaveAs(pdf_path, FileFormat=17)
            
            # Close the document and quit Word application
            doc.Close()
            word.Quit()
            
            # Set paths to class variables
            P.GenerateReport_path = docx_path
            P.GeneratePdfReport_path = pdf_path
            
            # Debug: Confirm that the PDF has been saved
            print(f"PDF saved successfully at: {pdf_path}")
            
            # Show success message and enable download button
            QMessageBox.information(None, "Success", f"Report generated successfully at: {pdf_path}")
            self.download_button.setEnabled(True)
            
            # Optional: Remove the DOCX file after conversion
            if os.path.exists(pdf_path):
                print(f"Removing original DOCX file: {docx_path}")
                os.remove(docx_path)
            
            # Verify if the PDF file exists
            if os.path.exists(pdf_path):
                print(f"PDF successfully generated and exists: {pdf_path}")
            else:
                print(f"Error: PDF file does not exist at: {pdf_path}")

        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
        except Exception as e:
            print(f"Error converting DOCX to PDF: {e}")
            # Ensure Word quits even in case of an error
            if 'word' in locals():
                word.Quit()
        
        finally:
            if self.loader: self.loader.close()       

    def downloadReport(self):        
        logger.info("Downloading the Generated PDF")  
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Report As", 
            os.path.join(P.project_path, "report.pdf"),  
            "PDF Files (*.pdf);;All Files (*)"
        )

        if file_name:
            try:
                if not os.path.exists(P.GeneratePdfReport_path):
                    raise FileNotFoundError(f"The generated PDF report does not exist: {P.GeneratePdfReport_path}")

                if not file_name.endswith('.pdf'):
                    file_name += '.pdf'

                shutil.copyfile(P.GeneratePdfReport_path, file_name)
                QMessageBox.information(None, "Success", "Report successfully downloaded!")

            except FileNotFoundError as fnfe:
                QMessageBox.warning(None, "File Not Found", str(fnfe))
                logger.error("File Not Found", str(fnfe))
            except Exception as e:
                logger.error(f"Failed to download the report:{e}")
                QMessageBox.warning(None, "Error", f"Failed to download the report: {e}")
    
    def addHeaderFooter(self, doc):
        # Add header
        section = doc.sections[0]
        header = section.header

        # Add a paragraph to hold both text and logo
        header_paragraph = header.add_paragraph()
        
        # Set tab stop to position the logo after the text
        header_paragraph.paragraph_format.tab_stops.add_tab_stop(Inches(6.3), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)

        # Add text (left aligned)
        run_text = header_paragraph.add_run("CYPHERA REPORT")
        run_text.font.bold = True
        run_text.font.size = Pt(8)

        # Insert a tab to align the logo to the right
        header_paragraph.add_run("\t")

        footer_db = Report_Input_Submit.FooterDatabase()
        header_logo_path = footer_db.fetch_header_logo_path()

        # Add header logo in header or wherever needed
        if header_logo_path:
            header_logo_run = header_paragraph.add_run()
            header_logo_run.add_picture(header_logo_path, width=Inches(1))  # Adjust width as needed

        footer_db.close_connection()


        # Adjust header margins
        section.top_margin = Inches(0)  # Reduce space above the header

        footer_db = Report_Input_Submit.FooterDatabase()
        footer_text = footer_db.fetch_footer_text()
        footer_db.close_connection()

        if footer_text:
            copyright_text = footer_text
        else:
            # Fallback if no DB entry
            current_year = datetime.now().year
            next_year_short = str(current_year + 1)[-2:]
            copyright_text = f" © Copyright {current_year}-{next_year_short} | Your Organisation name | All Rights Reserved"


        # Add footer
        footer = section.footer
        footer_db = Report_Input_Submit.FooterDatabase()
        footer_logo_path = footer_db.fetch_logo_path()

        # Add logo and text to the footer (left aligned)
        footer_paragraph = footer.add_paragraph()
        footer_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        run_footer_logo = footer_paragraph.add_run()
        if footer_logo_path:
            run_footer_logo.add_picture(footer_logo_path, width=Inches(0.3))  # Adjust width as needed
        footer_db.close_connection()
        run_footer_logo.add_text(copyright_text)

        # Add page number to the footer (right aligned)
        page_number_paragraph = footer.add_paragraph()
        page_number_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        page_number_run = page_number_paragraph.add_run("Page No: ")

        # Add the page number field
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')

        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = "PAGE"

        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')

        page_number_run._r.append(fldChar1)
        page_number_run._r.append(instrText)
        page_number_run._r.append(fldChar2)

        # Style adjustments for the footer text
        page_number_run.font.bold = True
        page_number_run.font.size = Pt(10)

        # Adjust footer margins
        section.bottom_margin = Inches(0)  # Reduce space below the footer

    def create_contents(self):
        contents = [
            {"title": "Introduction", "level": 1},
            {"title": "Target of Evaluation", "level": 1, "subcontents": []},
            {"title": "Analysis", "level": 1, "subcontents": []},
            {"title": "Security Measurement", "level": 1, "subcontents": []},
            {"title": "Attack Paths", "level": 1, "subcontents": []},
            {"title": "Risk Assessment", "level": 1, "subcontents": []},
            {"title": "Management Summary", "level": 1, "subcontents": []},
        ]

        subcontent_data = {
            "Target of Evaluation": [
                {"title": "System Description", "level": 2},
                {"title": "Scope", "level": 2},
                {"title": "Assumptions", "level": 2},
                {"title": "Misuse Cases", "level": 2},
                {"title": "TOE Configuration", "level": 2}
                
            ],
            "Analysis": [
                {"title": "Assets", "level": 2},
                {"title": "Damage Scenarios", "level": 2},
                {"title": "Threats", "level": 2},
                {"title": "Threat Scenarios", "level": 2}
            ],
            "Security Measurement": [
                {"title": "Security Claims", "level": 2},
                {"title": "Security Goals", "level": 2},
                {"title": "Security Controls", "level": 2}
            ],
            "Attack Paths": [
                {"title": "Attack Tree", "level": 2},
                {"title": "Risk Control Tree", "level": 2},
                {"title": "Technical Attack Tree", "level": 2},
                {"title": "Attack Leaves", "level": 2}
            ],
            "Risk Assessment": [
                {"title": "Risk Treatment", "level": 2}
            ],
            "Management Summary": [
                {"title": "High Level Risks", "level": 2},
                {"title": "Security Controls", "level": 2},
                {"title": "TOE Configuration", "level": 2},
                {"title": "Assumptions", "level": 2},
                {"title": "Management Summary description", "level": 2},
                {"title": "Init. Risk Matrix", "level": 2},
                {"title": "Resid. Risk Matrix", "level": 2}
            ]
        }

        h1_index = 2
        for section in contents:
            h2_index = 1
            section_name = section["title"].strip()
            if section_name in subcontent_data:
                level2_list = []
                if section_name != 'Management Summary':
                    for susection in subcontent_data[section_name]:
                        susection_name = susection["title"].strip()
                        # Find the internal name by iterating through the nested structure
                        internal_name = None
                        for group_items in self.table_display_order.values():
                            if susection_name in group_items:
                                internal_name = group_items[susection_name]
                                break
                        
                        if internal_name and susection_name in self.GenerateReport_tables:
                            self.table_name_mapping[internal_name] = f"{h1_index}.{h2_index} {susection_name}"
                            section["subcontents"].append({"title": f"{susection_name}", "level": 2})
                            h2_index += 1
                            level2_list.append(internal_name)
                
                # Only update h1_index and heading_mapping if subcontents are present
                if len(section["subcontents"]) > 0:
                    h1_index += 1
                    self.heading_mapping[section_name] = level2_list
            if section_name == 'Management Summary':
                if section_name in self.GenerateReport_tables:
                    level2_list = []    
                    table_list = ["HighLevelRisk", "SecurityControls", "TOEConfigurationInManagementSummary", "AssumptionsInManagementSummary", "MS_Description", "initialriskmatriks", "residriskmatriks"]
                    for index, susection in enumerate(subcontent_data[section_name]):
                        susection_name = susection["title"].strip()
                        self.table_name_mapping[table_list[index]] = f"{h1_index}.{h2_index} {susection_name}"
                        section["subcontents"].append({"title": f"{susection_name}", "level": 2})
                        h2_index += 1
                        level2_list.append(table_list[index])
                    if len(section["subcontents"]) > 0:
                        h1_index += 1
                        self.heading_mapping[section_name] = level2_list
            print(self.table_name_mapping)
        for section in contents:
            if "subcontents" in section.keys() and len(section["subcontents"]) == 0:
                contents.remove(section)

        return contents
    

    def save_to_word_document(self, doc=None):
        """
        Extracts HTML content from the database, cleans it, and saves it into a Word document.
        Handles text, tables, and images, including base64 and file-based images.
        """
        # Retrieve HTML content from the database
        html_content = self.retrieve_text_from_db()

        if not html_content:
            print("No TOE_Description found in the database.")
            return

        # Clean the HTML content by removing unnecessary headers and styles
        cleaned_html = html_content[0]

        # Remove unnecessary HTML tags and styling
        cleaned_html = cleaned_html.replace('HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd"', '')
        cleaned_html = cleaned_html.replace('p, li { white-space: pre-wrap; }', '')
        cleaned_html = cleaned_html.replace('<html>', '').replace('</html>', '')
        cleaned_html = cleaned_html.replace('<head>', '').replace('</head>', '')
        cleaned_html = cleaned_html.replace('<body>', '').replace('</body>', '')

        # Parse the cleaned HTML using BeautifulSoup
        soup = BeautifulSoup(cleaned_html, 'html.parser')

        # Remove any heading or paragraph before a table (assumed to be table name)
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
            if tag.find_next_sibling() and tag.find_next_sibling().name == 'table':
                tag.decompose()

        # Create a new Word document if none is provided
        if doc is None:
            doc = Document()

        # Handle text, tables, and images
        for element in soup.descendants:
            if isinstance(element, str):
                text = element.strip()
                if text:
                    doc.add_paragraph(text)

            elif element.name == 'br':  # Handle line breaks
                doc.add_paragraph()

            elif element.name == 'img':  # Handle images
                img_src = element.get('src')
                if img_src:
                    try:
                        process_image(img_src, doc)  # Use the process_image function
                    except Exception as e:
                        print(f"Failed to process image: {img_src}. Error: {e}")

            elif element.name == 'table':  # Handle tables
                rows = element.find_all('tr')
                if rows:
                    num_cols = len(rows[0].find_all(['td', 'th']))
                    table = doc.add_table(rows=1, cols=num_cols)

                    # Process table headers
                    hdr_cells = table.rows[0].cells
                    for i, cell in enumerate(rows[0].find_all(['td', 'th'])):
                        hdr_cells[i].text = cell.get_text(strip=True)

                    # Process table rows
                    for row in rows[1:]:
                        row_cells = table.add_row().cells
                        for i, cell in enumerate(row.find_all('td')):
                            row_cells[i].text = cell.get_text(strip=True)

        # Save the document
        doc.save('generated_report.docx')
        print("Content saved to 'generated_report.docx'")


    def retrieve_text_from_db(self):
        # Query to retrieve content from the TOE_Description table
        # result = DB.execute_db('SELECT content FROM TOE_Description')
        result = get_first_instance(SystemDescription, {'toe_id':1})
        
        # Return the HTML content if available, else return None
        return result.content if result else None
    
    def retrieve_text_from_db2(self):
        # Query to retrieve content from the Scope table
        # result = DB.execute_db('SELECT scope_content FROM scope_description')
        result = get_first_instance(ScopeDescription, {'scope_id':1})
        
        # Return the HTML content if available, else return None
        return result.scope_content if result else None
    
    def retrieve_text_from_db3(self):
        # Query to retrieve content from the Scope table
        # result = DB.execute_db('SELECT content FROM MS_Description')
        result = get_first_instance(MSDescription, {'ms_id':1})
        
        # Return the HTML content if available, else return None
        return result.content if result else None

    def save_to_word_document2(self, doc=None):
        print('save_to_word_document2')
        # Retrieve HTML content from the database
        html_content = self.retrieve_text_from_db2()

        if not html_content:
            print("No TOE_Description found in the database.")
            return

        # Clean the HTML content by removing unnecessary headers and styles
        cleaned_html = html_content[0]

        # Remove specific parts like DOCTYPE, HTML header, and style blocks
        # Remove the DOCTYPE declaration
        cleaned_html = cleaned_html.replace('HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd"', '')
        # Remove CSS styling for elements like <p>, <li>, and others
        cleaned_html = cleaned_html.replace('p, li { white-space: pre-wrap; }', '')

        # You can also remove the <html>, <head>, and <body> tags if present
        cleaned_html = cleaned_html.replace('<html>', '').replace('</html>', '')
        cleaned_html = cleaned_html.replace('<head>', '').replace('</head>', '')
        cleaned_html = cleaned_html.replace('<body>', '').replace('</body>', '')

        # Parse the cleaned HTML using BeautifulSoup
        soup = BeautifulSoup(cleaned_html, 'html.parser')

        # Remove any heading or paragraph right before the table (assuming table name is here)
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
            if tag.find_next_sibling() and tag.find_next_sibling().name == 'table':
                tag.decompose()

        # Create a new Word document if none is provided
        if doc is None:
            doc = Document()

        # Handle text, tables, and images as before
        for element in soup.descendants:
            if isinstance(element, str):
                text = element.strip()
                if text:
                    doc.add_paragraph(text)
            elif element.name == 'br':  # Line breaks
                doc.add_paragraph()
            elif element.name == 'img':  # Handle images
                img_src = element.get('src')
                if img_src:
                    try:
                        process_image(img_src, doc)  # Use the process_image function
                    except Exception as e:
                        print(f"Failed to process image: {img_src}. Error: {e}")


            elif element.name == 'table':  # Handle tables
                rows = element.find_all('tr')
                if rows:
                    num_cols = len(rows[0].find_all(['td', 'th']))
                    table = doc.add_table(rows=1, cols=num_cols)

                    # Process table header
                    hdr_cells = table.rows[0].cells
                    for i, cell in enumerate(rows[0].find_all(['td', 'th'])):
                        hdr_cells[i].text = cell.get_text(strip=True)

                    # Process table rows
                    for row in rows[1:]:
                        row_cells = table.add_row().cells
                        for i, cell in enumerate(row.find_all('td')):
                            row_cells[i].text = cell.get_text(strip=True)
                            
        # Save the document
        doc.save('generated_report.docx')
        print("Content saved to 'generated_report.docx'")

    def save_to_word_document3(self, doc=None):
        print('save_to_word_document2')

        # Retrieve HTML content from the database
        html_content = self.retrieve_text_from_db3()

        if not html_content:
            print("No TOE_Description found in the database.")
            return

        # Clean the HTML content by removing unnecessary headers and styles
        cleaned_html = html_content[0]

        # Remove specific parts like DOCTYPE, HTML header, and style blocks
        # Remove the DOCTYPE declaration
        cleaned_html = cleaned_html.replace('HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd"', '')
        # Remove CSS styling for elements like <p>, <li>, and others
        cleaned_html = cleaned_html.replace('p, li { white-space: pre-wrap; }', '')

        # You can also remove the <html>, <head>, and <body> tags if present
        cleaned_html = cleaned_html.replace('<html>', '').replace('</html>', '')
        cleaned_html = cleaned_html.replace('<head>', '').replace('</head>', '')
        cleaned_html = cleaned_html.replace('<body>', '').replace('</body>', '')

        # Parse the cleaned HTML using BeautifulSoup
        soup = BeautifulSoup(cleaned_html, 'html.parser')

        # Remove any heading or paragraph right before the table (assuming table name is here)
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
            if tag.find_next_sibling() and tag.find_next_sibling().name == 'table':
                tag.decompose()

        # Create a new Word document if none is provided
        if doc is None:
            doc = Document()

        # Handle text, tables, and images as before
        for element in soup.descendants:
            if isinstance(element, str):
                text = element.strip()
                if text:
                    doc.add_paragraph(text)
            elif element.name == 'br':  # Line breaks
                doc.add_paragraph()
            elif element.name == 'img':  # Handle images
                img_src = element.get('src')
                if img_src:
                    try:
                        process_image(img_src, doc)  # Use the process_image function
                    except Exception as e:
                        print(f"Failed to process image: {img_src}. Error: {e}")


            elif element.name == 'table':  # Handle tables
                rows = element.find_all('tr')
                if rows:
                    num_cols = len(rows[0].find_all(['td', 'th']))
                    table = doc.add_table(rows=1, cols=num_cols)

                    # Process table header
                    hdr_cells = table.rows[0].cells
                    for i, cell in enumerate(rows[0].find_all(['td', 'th'])):
                        hdr_cells[i].text = cell.get_text(strip=True)

                    # Process table rows
                    for row in rows[1:]:
                        row_cells = table.add_row().cells
                        for i, cell in enumerate(row.find_all('td')):
                            row_cells[i].text = cell.get_text(strip=True)
        
        # Save the document
        doc.save('generated_report.docx')
        print("Content saved to 'generated_report.docx'")

class CustomWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom_factor = 1.0  # Default zoom factor
        self.min_zoom = 0.1  # Minimum zoom level
        self.max_zoom = 5.0  # Maximum zoom level

    def contextMenuEvent(self, event):
        """ Custom right-click context menu """
        menu = QMenu(self)

        # Add only the required options
        save_action = QAction("Save ", self)
        

        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.Reload))


        menu.addAction(save_action)
        menu.addAction(reload_action)

        # Show the custom menu at the mouse position
        menu.exec_(event.globalPos())

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:  # Zooming only with Ctrl + Mouse Wheel
            if event.angleDelta().y() > 0:  # Wheel up, zoom in
                self.zoom_in()
            elif event.angleDelta().y() < 0:  # Wheel down, zoom out
                self.zoom_out()
            event.accept()  # Prevent default scroll behavior
        else:
            event.ignore()  # Ignore wheel event if Ctrl is not pressed

    def zoom_in(self):
        if self.zoom_factor < self.max_zoom:  # Ensure zoom factor stays below max limit
            self.zoom_factor += 0.1
            self.zoom_factor = round(self.zoom_factor, 2)  # Round to avoid precision issues
            self.setZoomFactor(self.zoom_factor)

    def zoom_out(self):
        if self.zoom_factor > self.min_zoom:  # Ensure zoom factor stays above min limit
            self.zoom_factor -= 0.1
            self.zoom_factor = round(self.zoom_factor, 2)  # Round to avoid precision issues
            self.setZoomFactor(self.zoom_factor)
