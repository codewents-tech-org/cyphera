
from Attack_Paths.controllers.tree_loader import TreeLoader
from Attack_Paths.controllers.highlight_afr_path import update_arrow_lines, create_arrow_lines
from Attack_Paths.controllers.afr_data_process import process_tree_data
from Attack_Paths.components.make_tree_center_view import center_tree_in_view
from Attack_Paths.controllers.reset_tree_data import sync_tree_data
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_tree_items_with_data(self, tree_dict: dict, tree_type: str) -> None:
    """
    Loads a tree structure into the scene using TreeLoader.

    Args:
        tree_dict (dict): Nested tree definition to render.
    """
    new_hash = self._hash_tree(tree_dict)

    if new_hash == self._cached_tree_hash:
        logger.info("Tree already loaded. Reusing scene.")

        if not self._tree_modified and not self._tree_data_modified:
            logger.info("Tree not modified and no data changed. Reusing scene.")
            return  # ✅ Skip unnecessary processing
        
        elif not self._tree_modified and self._tree_data_modified:
            logger.info("Tree not modified and tree data changed. Reusing scene.")
            sync_tree_data(self, tree_dict, self.tree_nodes, tree_type)
            output = process_tree_data({"tree": self.tree_nodes, "tree_type": tree_type})
            self.selectedPath = output["init_afr"]["path"]
            update_arrow_lines(self.renderer, self.selectedPath, self.extracted_tree)
            self._tree_data_modified = False # Reset tracking
        
        logger.info("Tree modified. Reloading scene.")
        return  # ✅ Skip unnecessary processing
    
    self._cached_tree_hash = new_hash  # Update cache
    self._tree_modified = False  # Reset tracking
    self._tree_data_modified = False 

    view = self.views()[0] if self.views() else None
    if view:
        view.setUpdatesEnabled(False)

    self.initialize_parameters()
    loader = TreeLoader(self)
    try:
        loader.load(tree_dict)
        self.tree_layout.apply_layout_positions(self.tree_nodes)
        self.renderer, self.extracted_tree = create_arrow_lines(self, self.tree_nodes, self.rootnode_id, self.selectedPath)
        output = process_tree_data({"tree": self.tree_nodes, "tree_type": tree_type})
        self.selectedPath = output["init_afr"]["path"]
        update_arrow_lines(self.renderer, self.selectedPath, self.extracted_tree)
    except Exception as e:
        print("Error loading tree:", str(e))
    finally:
        if view:
            view.setUpdatesEnabled(True)
        center_tree_in_view(self)
