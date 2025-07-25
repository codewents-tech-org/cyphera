
from PyQt5.QtWidgets import QMessageBox
import utils.interface_utils as interfaces

def show_submoduleframe(self, payload):
    try:
        frame_name = payload["data"]["name"]
        module = payload["data"]["module"]
        print(f"📂 Attempting to switch to frame: {frame_name} in module: {module}")
        frame = payload["data"]["frame"]

        # Autosave logic before switching frames
        if interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
            if interfaces.previous_module:
                # ✅ Check for 'Submit_Changes()' (Camel Case)
                if hasattr(interfaces.previous_module, "Submit_Changes"):
                    interfaces.previous_module.Submit_Changes()
                # ✅ Check for 'submit_changes()' (Lowercase)
                elif hasattr(interfaces.previous_module, "submit_changes"):
                    interfaces.previous_module.submit_changes()
            
            if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
                interfaces.previous_tree.Save_Tree()

        elif not interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
            reply = QMessageBox.question(
                None, 'Unsaved Changes',
                "You have unsaved changes. Do you want to save them before switching?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                if interfaces.previous_module:
                    # ✅ Check for 'Submit_Changes()' (Camel Case)
                    if hasattr(interfaces.previous_module, "Submit_Changes"):
                        interfaces.previous_module.Submit_Changes()
                    # ✅ Check for 'submit_changes()' (Lowercase)
                    elif hasattr(interfaces.previous_module, "submit_changes"):
                        interfaces.previous_module.submit_changes()
                
                if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
                    interfaces.previous_tree.Save_Tree()
            
            elif reply == QMessageBox.No:
                interfaces.unsaved_changes = False 
        
        if frame:
            if frame_name!="Home": 
                if self.Action_layer.indexOf(frame) == -1:
                    self.Action_layer.addWidget(frame)
                self.Action_layer.setCurrentWidget(frame)
                interfaces.previous_module = frame  # Track last opened module
                interfaces.previous_mainmodule = module  # Track last opened main module
                frame.load_data()
                interfaces.sub_modules[module]["current_submodule"] = frame_name
    except Exception as e:
        print(f"❌ Error while switching to frame: {e}")
        QMessageBox.critical(None, "Error", f"Failed to switch to frame:\n{str(e)}")