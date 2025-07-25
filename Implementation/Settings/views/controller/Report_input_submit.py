import os
import shutil
import glob
import models.Parameters as P
import sqlite3
from PyQt5.QtWidgets import QMessageBox

class FooterDatabase:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.logo1_path = P.Report_Logo
        self.logo2_path = P.Report_footer_Logo
        self.logo_path = P.Report_footer_Logo
        self.footer_place = P.Footer_placeholder
        self.init_db()
        self.create_footer_table()

    def init_db(self):
        try:
            global conn, cursor
            report_assets_folder = os.path.join(P.project_path, "Report Assets")
            os.makedirs(report_assets_folder, exist_ok=True)  # Create folder if not exist

            db_path = os.path.join(report_assets_folder, "FooterDatabase.db")
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error initializing footer database: {e}")

    def create_footer_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Report_Footer (
                    id TEXT PRIMARY KEY,
                    footer_text TEXT
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error creating footer table: {e}")

    def save_footer_text(self, footer_text):
        try:
            # Delete existing row
            self.cursor.execute("DELETE FROM Report_Footer WHERE id = ?", ("footer-1",))

            # Insert new footer
            self.cursor.execute("INSERT INTO Report_Footer (id, footer_text) VALUES (?, ?)", ("footer-1", footer_text))
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error saving footer text: {e}")

    def fetch_footer_text(self):
        try:
            self.cursor.execute("SELECT footer_text FROM Report_Footer WHERE id = ?", ("footer-1",))
            result = self.cursor.fetchone()
            if result:
                return result['footer_text']
            else:
                return None
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error fetching footer text: {e}")
            return None
        
    def fetch_logo_path(self):
        try:
            footer_logo_folder = os.path.join(P.project_path, "Report Assets", "footer_logo")
            header_images = glob.glob(os.path.join(footer_logo_folder, "*"))
            if header_images:
                return header_images[0]  # Return first image (only one exists)
            else:
                return self.footer_place
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error fetching logo image: {e}")
            return None    
        
    def fetch_header_logo_path(self):
        try:
            header_logo_folder = os.path.join(P.project_path, "Report Assets", "report_header")
            header_images = glob.glob(os.path.join(header_logo_folder, "*"))
            if header_images:
                return header_images[0]  # Return first (latest) image
            else:
                return self.footer_place
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error fetching header logo image: {e}")
            return None
        
    def fetch_heading_image_path(self):
        try:
            heading_image_folder = os.path.join(P.project_path, "Report Assets", "report_heading")
            heading_images = glob.glob(os.path.join(heading_image_folder, "*"))
            if heading_images:
                return heading_images[0]  # Return first (latest) image
            else:
                return self.footer_place
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error fetching heading image: {e}")
            return None
    
    def close_connection(self):
        if self.conn:
            self.conn.close()

def save_browsed_files(heading_path, header_path, footer_logo_path):
    """
    Copies the heading and header image files to specified folders.
    """
    project_path = P.project_path
    report_assets_folder = os.path.join(project_path, "Report Assets")  # Parent folder
    os.makedirs(report_assets_folder, exist_ok=True)

    if heading_path:
        heading_dest = os.path.join(report_assets_folder, "report_heading")
        os.makedirs(heading_dest, exist_ok=True)
        for file in glob.glob(os.path.join(heading_dest, "*")):
            os.remove(file)
        shutil.copy(heading_path, heading_dest)
    
    if header_path:
        header_dest = os.path.join(report_assets_folder, "report_header")
        os.makedirs(header_dest, exist_ok=True)
        for file in glob.glob(os.path.join(header_dest, "*")):
            os.remove(file)
        shutil.copy(header_path, header_dest)

    if footer_logo_path:
        footer_logo_dest = os.path.join(report_assets_folder, "footer_logo")
        os.makedirs(footer_logo_dest, exist_ok=True)
        for file in glob.glob(os.path.join(footer_logo_dest, "*")):
            os.remove(file)
        shutil.copy(footer_logo_path, footer_logo_dest)    

    

