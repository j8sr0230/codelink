import tkinter as tk


NODE_BACKGROUND = "#545454"


class NodeView:
    def __init__(self, node_graph_view):
        self.node_graph_view = node_graph_view

        self.id = None
        self.width = 200
        self.height = 100
        self.pos_x = 50
        self.pos_y = 50

    def paint(self):
        self.id = self.node_graph_view.create_rectangle([0, 0, self.width, self.height], fill=NODE_BACKGROUND,
                                                        outline="yellow", width=1, tags="node")
        self.node_graph_view.moveto(self.id, self.pos_x, self.pos_y)
