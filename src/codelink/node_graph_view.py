import tkinter as tk


class NodeGraphView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg="red")

        self.controller = None
        self.pack(fill="both", expand=True)
        self.update()

        # Rest of node graph drawing here
        print(self.winfo_width(), self.winfo_height())
        self.create_line(10, 0, 10, self.winfo_height())

    def set_controller(self, controller):
        self.controller = controller
