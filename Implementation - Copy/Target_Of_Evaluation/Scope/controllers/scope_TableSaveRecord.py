
from PyQt5.QtWidgets import QMessageBox
import controllers.DatabaseCreator as DB
import Target_Of_Evaluation.Scope.controllers.scope_synchronizations as Sync
import Target_Of_Evaluation.Scope.controllers.scope_attack_tree_generator as SATG
import logging
logger = logging.getLogger(__name__)

def scope_submit_changes(table):
    logger.info("Submission of Scope")
    # DB.execute_db("DELETE FROM scope_home_mindmap")
    data = []
    for row in range(table.rowCount()):
        scope_id_item = table.item(row, 1)
        scope_name_item = table.item(row, 2)
        scope_comments_item = table.item(row, 3)

        if scope_id_item and scope_name_item and scope_comments_item:
            scope_id = scope_id_item.text()
            scope_name = scope_name_item.text()
            comments = scope_comments_item.text()
            values = (scope_id, scope_name, comments)
            data.append(values)
    
    if data:
        DB.executemany_db("""INSERT OR REPLACE INTO scope_home_mindmap (scope_id, scope_name, comments) VALUES (?, ?, ?) """, data)

    