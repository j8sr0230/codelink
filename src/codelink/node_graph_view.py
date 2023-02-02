import tkinter as tk


SCENE_BACKGROUND_COLOR = "#1D1D1D"
SCENE_SIZE = 5000

GRID_COLOR = "#606060"
GRID_STEP = 100
GRID_DOT_SIZE = 6

RESIZE_SQUARE = 20


class NodeGraphView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=SCENE_BACKGROUND_COLOR)
        self.pack(fill="both", expand=True)

        self.bind("<Button-1>", self.on_mouse_left_down)
        self.bind("<ButtonRelease-1>", self.on_mouse_left_up)
        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<MouseWheel>", self.on_mouse_wheel)

        self.controller = None

        # Draw background
        self.draw_grid(SCENE_SIZE, GRID_COLOR, GRID_STEP, GRID_DOT_SIZE)

        # Draw test nodes
        self.create_rectangle([10, 10, 160, 110], fill="#292929", outline="#606060", width=1, tags="node")
        # self.tag_bind('node', '<Enter>', print)

        self.create_rectangle([100, 100, 260, 210], fill="#292929", outline="#606060", width=1, tags="node")

    def set_controller(self, controller):
        self.controller = controller

    def on_mouse_left_down(self, mouse_event):
        if self.controller:
            self.controller.move_from(mouse_event)

    def on_mouse_left_up(self, mouse_event):
        if self.controller:
            self.controller.move_to(mouse_event)

    def on_mouse_move(self, mouse_event):
        if self.controller:
            self.controller.move(mouse_event)

    def on_mouse_wheel(self, mouse_event):
        if self.controller:
            self.controller.zoom(mouse_event)

    def draw_grid(self, size, color, grid_step, grid_dot_size):
        for j in range(-size//2, size//2, grid_step):
            for i in range(-size//2, size//2, grid_step):
                x = i + grid_step // 2
                y = j + grid_step // 2
                self.create_oval((x, y, x + grid_dot_size, y + grid_dot_size), fill=color, tags="grid")
