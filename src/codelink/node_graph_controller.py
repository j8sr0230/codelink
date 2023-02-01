class NodeGraphController:
    def __init__(self, model, view):
        self.mode = model
        self.view = view

        self.selected_item = None
        self.selected_item_origin = None
        self.selected_position = None

    def register_selection(self, event):
        if not self.selected_item:
            items = self.view.find_withtag("current")
            if len(items) > 0:
                self.selected_item = items[0]
                self.selected_item_origin = self.view.coords(items[0])[:2]
                self.selected_position = (self.view.canvasx(event.x), self.view.canvasy(event.y))
            else:
                self.selected_item = None
                self.selected_item_origin = None
                self.selected_position = None

    def clear_selection(self, event):
        self.selected_item = None
        self.selected_item_origin = None
        self.selected_position = None

    def move_selection(self, event):
        if self.selected_item:
            current_position = (self.view.canvasx(event.x), self.view.canvasy(event.y))
            offset_x = self.selected_position[0] - self.selected_item_origin[0]
            offset_y = self.selected_position[1] - self.selected_item_origin[1]

            self.view.moveto(self.selected_item, current_position[0] - offset_x,
                             current_position[1] - offset_y)
