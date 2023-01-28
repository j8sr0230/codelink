from node_graph_view import NodeGraphView


class NodeGraphController:
    def __init__(self, model, view):
        self.mode = model
        self.view = view
