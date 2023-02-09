import ctypes
import tkinter as tk

from node_graph_model import NodeGraphModel
from node_graph_view import NodeGraphView
from node_graph_controller import NodeGraphController


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # self.call('tk', 'scaling', 1.5)
        self.title("CodeLink")
        self.geometry("600x400")

        node_graph_model = NodeGraphModel()
        node_graph_view = NodeGraphView(self)
        node_graph_controller = NodeGraphController(node_graph_model, node_graph_view)
        node_graph_view.set_controller(node_graph_controller)


if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    app = App()
    app.mainloop()
