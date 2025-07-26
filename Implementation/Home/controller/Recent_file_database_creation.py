import sqlite3
import models.Parameters as P
from PyQt5.QtWidgets import QMessageBox
import re
import os

class Recent_file_DB_creation():
    def __init__(self):
        super().__init__()
        self.init_db()
        self.create_table()

    def init_db(self):
        global conn, cursor
        # close_db()
        self.conn = sqlite3.connect(P.recent_database_file_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()   

    def create_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Recent_Projects (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    path TEXT UNIQUE,
                    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    
                );
            """) 
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(None,"Database Error", f"Error initializing database: {e}")    

    def save_project(self, project_path):
        try:
            project_name = os.path.basename(project_path)  # Get filename with extension
            project_name = os.path.splitext(project_name)[0]
            self.cursor.execute("SELECT path FROM Recent_Projects WHERE path = ?", (project_path,))
            existing_project = self.cursor.fetchone()

            if existing_project is None:
                self.cursor.execute("SELECT MAX(CAST(SUBSTR(id, 8) AS INTEGER)) FROM Recent_Projects WHERE id LIKE 'RECENT-%'")
                last_number = self.cursor.fetchone()[0]  # Extract the last number
                
                new_id = f"RECENT-{(last_number + 1) if last_number else 1}"
                self.cursor.execute("""
                    INSERT INTO Recent_Projects (id, name, path, Timestamp) 
                    VALUES (?, ?, ?, datetime('now'))
                """, (new_id, project_name, project_path))
                self.conn.commit()
            else:
                self.update_project_timestamp(project_path)
        
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error saving project: {e}")


    def fetch_recent_projects(self):
        try:
            self.cursor.execute("SELECT name, path FROM Recent_Projects ORDER BY Timestamp DESC LIMIT 5")
            projects = self.cursor.fetchall()
            return projects  # Returns a list of rows [(name, path), (name, path), ...]
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error fetching projects: {e}")
            return []
        
    def update_project_timestamp(self, project_path):
        try:
            self.cursor.execute("""
                UPDATE Recent_Projects 
                SET Timestamp = datetime('now') 
                WHERE path = ?
            """, (project_path,))
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error updating project timestamp: {e}")    

    def delete_project(self, project_path):
        try:
            self.cursor.execute("DELETE FROM Recent_Projects WHERE path = ?", (project_path,))
            self.conn.commit()
            print(f"Deleted project from database: {project_path}")  
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", f"Error deleting project: {e}")
        
            
    
    def close_db(self):
    
        if self.conn:
            self.conn.close()
