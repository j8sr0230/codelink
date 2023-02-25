import tkinter as tk

NODE_BORDER_WHITE = "#E5E5E5"
NODE_HEADER_RED = "#83314A"
NODE_CONTENT = "#303030"

DEFAULT_HEADER_HEIGHT = 30
DEFAULT_NODE_HEIGHT = 100
DEFAULT_NODE_WIDTH = 200
DEFAULT_BRODER_WIDTH = 5

# NODE_FONT = "Helvetica 12"
# TITLE_FONT_SIZE = 12


class NodeView:
    def __init__(self, node_graph_view, x, y):
        # Instance Attributes
        self.controller = None

        # Setup GUI
        self.node_graph_view = node_graph_view
        self.pos_x = x
        self.pos_y = y

        self.border_rect = node_graph_view.create_rectangle([0, 0, DEFAULT_NODE_WIDTH, DEFAULT_NODE_HEIGHT],
                                                            fill=NODE_BORDER_WHITE, outline=NODE_BORDER_WHITE,
                                                            width=DEFAULT_BRODER_WIDTH, tags="border_rect")
        self.node_graph_view.moveto(self.border_rect, self.pos_x, self.pos_y)

        self.header_rect = node_graph_view.create_rectangle([0, 0, DEFAULT_NODE_WIDTH, DEFAULT_HEADER_HEIGHT],
                                                            fill=NODE_HEADER_RED, width=0, tags="header_rect")
        self.node_graph_view.moveto(self.header_rect, self.pos_x, self.pos_y)

        self.content_rect = node_graph_view.create_rectangle([0, 0, DEFAULT_NODE_WIDTH,
                                                              DEFAULT_NODE_HEIGHT - DEFAULT_HEADER_HEIGHT],
                                                             fill=NODE_CONTENT, width=0, tags="content_rect")
        self.node_graph_view.moveto(self.content_rect, self.pos_x, self.pos_y + DEFAULT_HEADER_HEIGHT)

        self.node_graph_view.tag_bind(self.header_rect, '<ButtonPress-1>', self.on_mouse_left_down)
        self.node_graph_view.tag_bind(self.content_rect, '<ButtonPress-1>', self.on_mouse_left_down)

        # self.node_graph_view.create_text(self.pos_x, self.pos_y, font=(NODE_FONT, TITLE_FONT_SIZE), text=self.name,
        #                                  fill=NODE_FOREGROUND, anchor=tk.NW, tags="text")
        # text = tk.Entry(self.node_graph_view, font=(NODE_FONT, TITLE_FONT_SIZE))
        # self.node_graph_view.create_window(300, 300, window=text, width=200, tags="txt")

        # frame = tk.Frame(self)
        # lbl = tk.Label(frame, text="In 1", font=self.default_node_font)
        # lbl.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        # btn = tk.Button(frame, text="Ok", font=self.default_node_font)
        # btn.pack(fill=tk.BOTH, expand=True)
        #
        # self.create_window(10, 10, anchor=tk.NW, window=frame, width=200, height=100, tags="win_obj")

    def set_controller(self, controller):
        self.controller = controller

    def on_mouse_left_down(self, mouse_event):
        if self.controller:
            self.controller.set_selected_item(self, mouse_event)

    def move_to(self, x, y):
        pass

