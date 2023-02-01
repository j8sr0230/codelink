import tkinter as tk


SCENE_COLOR = "#1D1D1D"


class NodeGraphView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=SCENE_COLOR)
        self.pack(fill="both", expand=True)

        self.bind("<Button-1>", self.on_left_down)
        self.bind("<ButtonRelease-1>", self.on_left_up)
        self.bind("<Motion>", self.on_move)

        self.controller = None

        # Draw test object
        self.create_rectangle([10, 10, 160, 110], fill="#292929", outline="#898989", width=1)

    def set_controller(self, controller):
        self.controller = controller

    def on_left_down(self, event):
        self.controller.register_selection(event)

    def on_left_up(self, event):
        self.controller.clear_selection(event)

    def on_move(self, event):
        self.controller.move_selection(event)
