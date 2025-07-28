import json


class TreeBuilder:
    def __init__(self, rows):
        self.rows = rows
        self.nodes = {}
    
    def build(self):
        self._create_nodes()
        return self._build_tree()
    
    def _create_nodes(self):
        for row in self.rows:
            #print(row['node_id'])
            self.nodes[row['node_id']] = {
                'node_id':row['node_id'],
                'scope_id':row['scope_id'],
                'parent_id':row['parent_id'],
                'level':row['level'],
                'node_text':row['node_text'],
                'node_type':row['node_type'],
                'node_desc':row['node_desc'],
                'pos_x':row['pos_x'],
                'pos_y':row['pos_y'],
                'children': []
                
            }
    
    def _build_tree(self):
        root = []
        for node in self.nodes.values():
            #print(node)
            if not node['parent_id']:
                root.append(node)
                 
            else:
                parent = self.nodes.get(node['parent_id'])
                if parent:
                    parent['children'].append(node)
        return root

#if __name__ == "__main__":
#   
#    builder =TreeBuilder(rows)
#    result = builder.build()    
#    print(json.dumps(result))