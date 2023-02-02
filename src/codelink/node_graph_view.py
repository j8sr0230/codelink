import tkinter as tk


SCENE_COLOR = "#1D1D1D"


class NodeGraphView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=SCENE_COLOR)
        self.pack(fill="both", expand=True)

        self.bind("<Button-1>", self.on_mouse_left_down)
        self.bind("<ButtonRelease-1>", self.on_mouse_left_up)
        self.bind("<Motion>", self.on_mouse_move)

        self.controller = None

        # Draw test items
        self.create_rectangle([10, 10, 160, 110], fill="#292929", outline="#898989", width=1, tags="node")
        self.create_rectangle([100, 100, 260, 210], fill="#292929", outline="#898989", width=1, tags="node")

    def set_controller(self, controller):
        self.controller = controller

    def on_mouse_left_down(self, mouse_event):
        self.controller.move_from(mouse_event)

    def on_mouse_left_up(self, mouse_event):
        self.controller.move_to(mouse_event)

    def on_mouse_move(self, mouse_event):
        self.controller.move(mouse_event)
