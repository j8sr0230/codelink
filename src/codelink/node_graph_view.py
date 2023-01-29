import tkinter as tk


class NodeGraphView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.pack(fill="both", expand=True)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self.node_graph_scene = tk.Canvas(self, bg="#FFFFFF", scrollregion=(0, 0, 10000, 10000))
        self.node_graph_scene.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W+tk.E)

        self.hor_bar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hor_bar.grid(row=1, column=0, sticky=tk.E+tk.W)
        self.hor_bar.config(command=self.node_graph_scene.xview)
        self.ver_bar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.ver_bar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.ver_bar.config(command=self.node_graph_scene.yview)
        self.node_graph_scene.config(xscrollcommand=self.hor_bar.set, yscrollcommand=self.ver_bar.set)

        self.controller = None

        # Test drawing
        self.node_graph_scene.create_line(10, 10, 1000, 500)

    def set_controller(self, controller):
        self.controller = controller
