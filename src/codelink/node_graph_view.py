import tkinter as tk


class NodeGraphView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.controller = None
        self.pack(fill="both", expand=True)

        # Rest of node graph GUI here
        canvas = tk.Canvas(self)
        canvas.pack(fill="both", expand=True)
        canvas.create_line(10, 10, 50, 50)

    def set_controller(self, controller):
        self.controller = controller
