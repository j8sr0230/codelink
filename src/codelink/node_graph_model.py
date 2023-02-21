class NodeGraphModel:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)
        print(self.nodes)
