import tkinter as tk
from PIL import Image, ImageDraw, ImageTk


SCENE_BACKGROUND_COLOR = "#1D1D1D"
SCENE_SIZE = 6000

GRID_COLOR = "#606060"
GRID_STEP = 100
GRID_DOT_SIZE = 4


class NodeGraphView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=SCENE_BACKGROUND_COLOR)
        self.pack(fill="both", expand=True)

        self.bind("<Button-1>", self.on_mouse_left_down)
        self.bind("<ButtonRelease-1>", self.on_mouse_left_up)
        self.bind("<Motion>", self.on_mouse_move)

        self.controller = None

        # Draw background
        self.background_img = ImageTk.PhotoImage(
            self.draw_grid(SCENE_SIZE, SCENE_BACKGROUND_COLOR, GRID_COLOR, GRID_STEP, GRID_DOT_SIZE)
        )
        self.create_image(0, 0, anchor=tk.CENTER, image=self.background_img, tags="background")

        # Draw test nodes
        self.create_rectangle([10, 10, 160, 110], fill="#292929", outline="#606060", width=1, tags="node")
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

    @staticmethod
    def draw_grid(size, background_color, foreground_color, grid_step, grid_dot_size):
        grid_img = Image.new("RGB", (size, size), background_color)
        grid_img_draw = ImageDraw.Draw(grid_img)

        for j in range(0, size, grid_step):
            for i in range(0, size, grid_step):
                x = i + grid_step // 2
                y = j + grid_step // 2
                grid_img_draw.ellipse((x, y, x + grid_dot_size, y + grid_dot_size), fill=foreground_color)

        return grid_img
