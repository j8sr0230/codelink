import tkinter as tk


SCENE_SIZE = 4000
SCENE_COLOR = "#1D1D1D"

MAJOR_DOT_SIZE = 4
MAJOR_STEP = 100
MINOR_DOT_SIZE = 2
MINOR_DIV = 4
GRID_COLOR = "#282828"


class NodeGraphView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self.node_graph_scene = tk.Canvas(self, bg=SCENE_COLOR, scrollregion=(0, 0, SCENE_SIZE, SCENE_SIZE))
        self.node_graph_scene.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W+tk.E)

        self.hor_bar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hor_bar.grid(row=1, column=0, sticky=tk.E+tk.W)
        self.hor_bar.config(command=self.node_graph_scene.xview)
        self.ver_bar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.ver_bar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.ver_bar.config(command=self.node_graph_scene.yview)
        self.node_graph_scene.config(xscrollcommand=self.on_x_scroll, yscrollcommand=self.ver_bar.set)

        self.pack(fill="both", expand=True)

        self.grid = []
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def draw_grid(self):
        if len(self.grid) > 0:
            for grid_dot in self.grid:
                self.node_graph_scene.delete(grid_dot)
            self.grid = []

        left_bound = int(self.node_graph_scene.xview()[0] * SCENE_SIZE)
        right_bound = int(self.node_graph_scene.xview()[1] * SCENE_SIZE)
        top_bound = int(self.node_graph_scene.yview()[0] * SCENE_SIZE)
        bottom_bound = int(self.node_graph_scene.yview()[1] * SCENE_SIZE)

        left_pixel = MAJOR_STEP * (left_bound//MAJOR_STEP)
        right_pixel = MAJOR_STEP * (right_bound//MAJOR_STEP) + MAJOR_STEP
        top_pixel = MAJOR_STEP * (top_bound//MAJOR_STEP)
        bottom_pixel = MAJOR_STEP * (bottom_bound//MAJOR_STEP) + MAJOR_STEP

        for x in range(left_pixel, right_pixel, MAJOR_STEP):
            for y in range(top_pixel, bottom_pixel, MAJOR_STEP):
                grid_dot = self.node_graph_scene.create_oval(x, y, x + MAJOR_DOT_SIZE, y + MAJOR_DOT_SIZE,
                                                             width=0, fill=GRID_COLOR)
                self.grid.append(grid_dot)
        for x in range(left_pixel, right_pixel, MAJOR_STEP//MINOR_DIV):
            for y in range(top_pixel, bottom_pixel, MAJOR_STEP//MINOR_DIV):
                grid_dot = self.node_graph_scene.create_oval(x, y, x + MINOR_DOT_SIZE, y + MINOR_DOT_SIZE,
                                                             width=0, fill=GRID_COLOR)
                self.grid.append(grid_dot)

        # print(len(self.grid))

    def on_x_scroll(self, first, last):
        self.hor_bar.set(first, last)
        self.draw_grid()
