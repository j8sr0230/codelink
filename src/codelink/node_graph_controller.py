class NodeGraphController:
    def __init__(self, model, view):
        self.mode = model
        self.view = view

        self.init_ui_controls()

    def init_ui_controls(self):
        self.view.hor_bar.config(command=self.view.node_graph_scene.xview)
        self.view.ver_bar.config(command=self.view.node_graph_scene.yview)
        self.view.node_graph_scene.config(xscrollcommand=self.scroll_viewport, yscrollcommand=self.view.ver_bar.set)
        self.view.node_graph_scene.bind_all("<MouseWheel>", self.on_mousewheel)

    def scroll_viewport(self, first, last):
        self.view.hor_bar.set(first, last)
        self.view.draw_grid()

    def on_mousewheel(self, event):
        if (self.view.scene_scale >= 0.8) and (self.view.scene_scale <= 1.2):
            self.view.scale_viewport(event)
