

def sync_tree_data(self, tree_dict: dict, scene_tree: dict, tree_type: str) -> bool:
    """
    Recursively updates in-scene tree node objects with values from tree_dict.
    
    Args:
        tree_dict (dict): The new tree structure loaded from backend or file.
        scene_tree (dict): The current tree_nodes structure in the QGraphicsScene.

    Returns:
        bool: True if any node values were updated, False otherwise.
    """
    updated = False

    def sync_node_values(src: dict, tgt: dict) -> bool:
        """
        Sync individual node properties if changed.
        """
        node_obj = tgt.get("node")
        node_type = src.get("node_type")

        # Fields to sync by type
        common_fields = ["node_label", "node_Text", "af_value", "af_level"]
        leaf_fields = ["values"]
        changed = False

        node_obj.title.setText(src.get("node_label"))
        node_obj.node_text.setPlainText(src.get("node_Text"))
        if node_type in ["head", "leaf"]:
            node_obj.af_value.setText(src.get("af_value"))
            node_obj.af_level.setPlainText(src.get("af_level"))
            if node_type == "head" and tree_type == "attack_tree":
                node_obj.rf_value.setText(src.get("rf_value"))
                node_obj.rf_level.setPlainText(src.get("rf_level"))

        # Leaf-specific
        if node_type == "leaf":
            for i, key in enumerate(src.get("values")):
                node_obj.values_label[i].setText(key)
                changed = True
        
        if node_type in ["head", "intermediate", "technical head", "control head"]:
            node_obj.gate_button.setText(src.get("gate"))

        if changed:
            node_obj.update()  # Redraw visual item
        return changed

    def recurse(src: dict, tgt: dict) -> bool:
        local_change = sync_node_values(src, tgt)
        total_change = local_change

        for src_child, tgt_child in zip(src.get("childrens", []), tgt.get("childrens", [])):
            if recurse(src_child, tgt_child):
                total_change = True
        return total_change

    updated = recurse(tree_dict, scene_tree)
    return updated
