
from PyQt5.QtWidgets import QMessageBox
import utils.interface_utils as interfaces
import models.helper as helper

def show_moduleframe(self, payload):
    try:
        frame_name = payload["data"]["module"]
        print(f"📥 Switching to module: {frame_name}")
        # Handle autosave before switching modules
        if interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
            # Check if submit_changes() or Submit_Changes() exists before calling
            if interfaces.previous_module and hasattr(interfaces.previous_module, "Submit_Changes"):
                interfaces.previous_module.Submit_Changes()
                interfaces.unsaved_changes = False
            elif interfaces.previous_module and hasattr(interfaces.previous_module, "submit_changes"):
                interfaces.previous_module.submit_changes()
                interfaces.unsaved_changes = False
            if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
                interfaces.previous_tree.Save_Tree()
                interfaces.unsaved_changes = False
        elif not interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
            # Show a popup to confirm if the user wants to discard changes
            reply = QMessageBox.question(
                None, 'Unsaved Changes',
                "You have unsaved changes. Do you want to save them before switching?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            # Handle user's choice
            if reply == QMessageBox.Yes:
                if interfaces.previous_module and hasattr(interfaces.previous_module, "Submit_Changes"):
                    interfaces.previous_module.Submit_Changes()
                    interfaces.unsaved_changes = False
                elif interfaces.previous_module and hasattr(interfaces.previous_module, "submit_changes"):
                    interfaces.previous_module.submit_changes()
                    interfaces.unsaved_changes = False
                if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
                    interfaces.previous_tree.Save_Tree()
                    interfaces.unsaved_changes = False
            elif reply == QMessageBox.No:
                interfaces.unsaved_changes = False

        if frame_name == 'Home':
            self.show_HomeTab_content()
            interfaces.home_sub_modules[0].setVisible(True)
            interfaces.home_sub_modules[1].on_click()
            helper.Panel_selector = 'HomeTab'
            helper.homePanel_selector = 'HomeTab'
        else:
            interfaces.previous_tree = None

            for module, submodule in interfaces.sub_modules.items():
                # Hide all submodule buttons except the one for the current module
                if module != frame_name:
                    interfaces.sub_modules[module]['frame'].setVisible(False)
                elif module == frame_name:
                    interfaces.sub_modules[module]['frame'].setVisible(True)
            print(f"📥 Switching to submodule: {interfaces.sub_modules[frame_name]}")
            payload["data"]["data"]["submodules"][payload["data"]["data"]["current_submodule"]]["button"].on_click()
            payload["data"]["data"]["submodules"][payload["data"]["data"]["current_submodule"]]["action"]()

            if frame_name=='Settings':
                self.sub_module_panel.setVisible(False)
            else: 
                self.sub_module_panel.setVisible(True)
    except Exception as e:
        print(f"❌ Error in show_moduleframe: {e}")
        QMessageBox.critical(None, "Error", f"An error occurred while switching modules: {e}")