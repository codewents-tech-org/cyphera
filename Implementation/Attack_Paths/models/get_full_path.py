def build_parent_map(node_id, node_data, parent_map):
    """
    Recursively build a parent map from child to parent.
    """
    children = node_data.get('childrens', {})
    for child_id, child_data in children.items():
        parent_map[child_id] = node_id
        build_parent_map(child_id, child_data, parent_map)

def trace_to_root(node_id, parent_map):
    """
    Recursively trace the path from a leaf node to root using the parent map.
    """
    path = [node_id]
    while node_id in parent_map:
        node_id = parent_map[node_id]
        path.append(node_id)
    return path

def expand_paths(possible_path, input_tree):
    """
    From given leaf paths, expand them up to the root by tracing each leaf.
    """
    root_id = list(input_tree.keys())[0]
    tree_data = input_tree[root_id]

    # Build child->parent mapping
    parent_map = {}
    build_parent_map(root_id, tree_data, parent_map)

    # Expand each leaf in each path upward to root
    full_paths = []
    for leaf_combo in possible_path:
        combined_path = []
        for leaf_id in leaf_combo:
            leaf_to_root = trace_to_root(leaf_id, parent_map)
            combined_path.extend(leaf_to_root)
        full_paths.append(list(set(combined_path)))
    return full_paths
