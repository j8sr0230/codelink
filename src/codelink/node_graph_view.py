import tkinter as tk


SCENE_SIZE = 10000
SCENE_COLOR = "#1D1D1D"

GRID_DOT_SIZE = 4
GRID_STEP = 100
GRID_COLOR = "#393939"


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
        self.ver_bar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.ver_bar.grid(row=0, column=1, sticky=tk.N+tk.S)

        self.pack(fill="both", expand=True)

        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def draw_grid(self):
        self.node_graph_scene.delete("grid")

        viewport_left = int(self.node_graph_scene.xview()[0] * SCENE_SIZE)
        viewport_right = int(self.node_graph_scene.xview()[1] * SCENE_SIZE)
        viewport_top = int(self.node_graph_scene.yview()[0] * SCENE_SIZE)
        viewport_bottom = int(self.node_graph_scene.yview()[1] * SCENE_SIZE)

        grid_left = GRID_STEP * (viewport_left // GRID_STEP)
        grid_right = GRID_STEP * (viewport_right // GRID_STEP) + GRID_STEP
        grid_top = GRID_STEP * (viewport_top // GRID_STEP)
        grid_bottom = GRID_STEP * (viewport_bottom // GRID_STEP) + GRID_STEP

        for x in range(grid_left, grid_right, GRID_STEP):
            for y in range(grid_top, grid_bottom, GRID_STEP):
                self.node_graph_scene.create_oval(x, y, x + GRID_DOT_SIZE, y + GRID_DOT_SIZE, width=0,
                                                  fill=GRID_COLOR, tags="grid")

        # self.node_graph_scene.scale("all", 0, 0, .5, .5)
