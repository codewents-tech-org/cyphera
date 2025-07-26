
from Attack_Paths.controllers.tree_importer import TreeImporter

class TreeLoader:
    """
    A helper class to load a nested tree structure into a TechnicalTreeScene.
    """

    def __init__(self, scene):
        """
        Initializes the TreeLoader.

        Args:
            scene (TechnicalTreeScene): The scene where nodes will be added.
        """
        self.scene = scene

    def load(self, tree_data: dict):
        """
        Loads the entire tree structure recursively into the scene.

        Args:
            tree_data (dict): Root node of the tree.
        """
        self.scene.initialize_parameters()
        self.scene.node_counter = 0

        def load_node(data: dict, parent_id: str = None):
            tree_id = f"{self.scene.tat_id}_node_{self.scene.node_counter}"
            self.scene.node_counter += 1
            node_type = data.get("node_type")
            if data.get("selected_path"):
                self.scene.selectedPath.append(tree_id)

            if node_type == "head":
                self.scene.add_head_node(
                    tree_id=tree_id,
                    label=data.get("node_label", ""),
                    text=data.get("node_Text", ""),
                    x=data.get("x", 0),
                    y=data.get("y", 0),
                    af_value=data.get("af_value", "0"),
                    af_level=data.get("af_level", "High"),
                    rf_value=data.get("rf_value", ""),
                    rf_level=data.get("rf_level", ""),
                    gate=data.get("gate", "AND"),
                )
                parent_id = tree_id

            elif node_type == "intermediate":
                node = self.scene.add_intermediate_node(
                    tree_id,
                    data.get("node_label", ""),
                    data.get("node_Text", ""),
                    data.get("x", 0),
                    data.get("y", 0),
                    gate=data.get("gate", "AND"),
                    parent_id=parent_id
                )

            elif node_type == "leaf":
                node = self.scene.add_leaf_node(
                    tree_id,
                    data.get("node_label", ""),
                    data.get("node_Text", ""),
                    data.get("x", 0),
                    data.get("y", 0),
                    data.get("af_value", "0"),
                    data.get("af_level", "High"),
                    values=data.get("values", []),
                    parent_id=parent_id
                )
                return
                
            elif node_type == "technical head" or node_type == "control head":
                node = self.scene.add_treehead_node(
                    tree_id,
                    data.get("node_label", ""),
                    data.get("node_Text", ""),
                    data.get("x", 0),
                    data.get("y", 0),
                    gate=data.get("gate", "AND"),
                    parent_id=parent_id
                )
                node["node_type"] = node_type
                
                def load_subtree_node(data: dict, parent_id: str = None):
                    tree_id = f"{self.scene.tat_id}_node_{self.scene.node_counter}"
                    self.scene.node_counter += 1
                    node_type = data.get("node_type")
                    if data.get("selected_path"):
                        self.scene.selectedPath.append(tree_id)

                    if node_type == "intermediate" or node_type == "technical head":
                        node = self.scene.add_intermediate_node(
                            tree_id,
                            data.get("node_label", ""),
                            data.get("node_Text", ""),
                            data.get("x", 0),
                            data.get("y", 0),
                            gate=data.get("gate", "AND"),
                            parent_id=parent_id
                        )
                        node_item = node["node"]
                        node_item.setEnabled(False)
                        node_item.setFlag(node_item.ItemIsSelectable, False)
                        node_item.setAcceptHoverEvents(False)
                        if hasattr(node_item, "gate_button"):
                            node_item.gate_button.setEnabled(False)

                    elif node_type == "leaf":
                        node = self.scene.add_leaf_node(
                            tree_id,
                            data.get("node_label", ""),
                            data.get("node_Text", ""),
                            data.get("x", 0),
                            data.get("y", 0),
                            data.get("af_value", "0"),
                            data.get("af_level", "High"),
                            values=data.get("values", []),
                            parent_id=parent_id
                        )
                        node_item = node["node"]
                        node_item.setEnabled(False)
                        node_item.setFlag(node_item.ItemIsSelectable, False)
                        node_item.setAcceptHoverEvents(False)
                        if hasattr(node_item, "gate_button"):
                            node_item.gate_button.setEnabled(False)
                        return
                
                    for child in data.get("childrens", []):
                        load_subtree_node(child, tree_id)
                for child in data.get("childrens", []):
                    load_subtree_node(child, tree_id)
                return

            for child in data.get("childrens", []):
                load_node(child, tree_id)

        load_node(tree_data)
        self.scene.tree_layout.apply_layout_positions(self.scene.tree_nodes)
