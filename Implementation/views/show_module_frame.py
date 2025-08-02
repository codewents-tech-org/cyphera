from PyQt5.QtWidgets import QMessageBox
import utils.interface_utils as interfaces
import models.helper as helper

def show_moduleframe(self, payload):
    try:
        frame_name = payload["data"]["module"]
        print(f"📥 Switching to module: {frame_name}")

        # Handle autosave before switching modules
        if interfaces.autosave_enabled and (interfaces.previous_module or interfaces.previous_tree) and interfaces.unsaved_changes:
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
            reply = QMessageBox.question(
                None, 'Unsaved Changes',
                "You have unsaved changes. Do you want to save them before switching?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if interfaces.previous_module and hasattr(interfaces.previous_module, "Submit_Changes"):
                    interfaces.previous_module.Submit_Changes()
                elif interfaces.previous_module and hasattr(interfaces.previous_module, "submit_changes"):
                    interfaces.previous_module.submit_changes()
                if interfaces.previous_tree and hasattr(interfaces.previous_tree, "Save_Tree"):
                    interfaces.previous_tree.Save_Tree()
                interfaces.unsaved_changes = False
            else:
                interfaces.unsaved_changes = False

        # Show Home tab if selected
        if frame_name == 'Home':
            self.show_HomeTab_content()
            interfaces.home_sub_modules[0].setVisible(True)
            interfaces.home_sub_modules[1].on_click()
            helper.Panel_selector = 'HomeTab'
            helper.homePanel_selector = 'HomeTab'
            return

        interfaces.previous_tree = None

        for module, submodule in interfaces.sub_modules.items():
            interfaces.sub_modules[module]['frame'].setVisible(module == frame_name)

        print(f"📥 Switching to submodule: {interfaces.sub_modules[frame_name]}")

        submodules_dict = payload["data"]["data"]["submodules"]
        current_sub = payload["data"]["data"].get("current_submodule")

        # ✅ Fallback if current_submodule is invalid
        if current_sub not in submodules_dict:
            print(f"⚠️ Submodule '{current_sub}' not found. Falling back to first available.")
            current_sub = next(iter(submodules_dict))
            payload["data"]["data"]["current_submodule"] = current_sub

        sub_data = submodules_dict[current_sub]
        sub_data["button"].on_click()
        sub_data["action"]()

        # Optional: hide submodule panel for settings
        self.sub_module_panel.setVisible(frame_name != 'Settings')

    except Exception as e:
        print(f"❌ Error in show_moduleframe: {e}")
        QMessageBox.critical(None, "Error", f"An error occurred while switching modules:\n{e}")
