import tkinter as tk


NODE_BACKGROUND = "#545454"
NODE_FOREGROUND = "#E5E5E5"
NODE_FONT = "Helvetica 12"
TITLE_FONT_SIZE = 12


class NodeView:
    def __init__(self, node_graph_view, x, y):
        self.node_graph_view = node_graph_view
        self.pos_x = x
        self.pos_y = y
        self.name = "Node"
        self.width = 200
        self.height = 100

        self.id = self.node_graph_view.create_rectangle([0, 0, self.width, self.height], fill=NODE_BACKGROUND,
                                                        outline="yellow", width=1, tags="node")
        self.node_graph_view.moveto(self.id, self.pos_x, self.pos_y)
        self.node_graph_view.create_text(self.pos_x, self.pos_y, font=(NODE_FONT, TITLE_FONT_SIZE), text=self.name,
                                         fill=NODE_FOREGROUND, anchor=tk.NW, tags="text")
        text = tk.Entry(self.node_graph_view, font=(NODE_FONT, TITLE_FONT_SIZE))
        self.node_graph_view.create_window(300, 300, window=text, width=200, tags="txt")

        self.controller = None

    def set_controller(self, controller):
        self.controller = controller
