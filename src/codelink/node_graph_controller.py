class NodeGraphController:
    def __init__(self, model, view):
        self.mode = model
        self.view = view

        self.left_mouse_down = False
        self.selected_item = None
        self.selected_item_origin = None
        self.event_start_position = None

    def move_from(self, event):
        self.left_mouse_down = True

        items = self.view.find_withtag("current")
        if len(items) > 0:
            # If item selected, save item, origin and event position
            self.selected_item = items[0]
            self.selected_item_origin = self.view.coords(items[0])[:2]
            self.event_start_position = (self.view.canvasx(event.x), self.view.canvasy(event.y))

            # Modify selected canvas item
            self.view.tag_raise(items[0])
            self.view.itemconfig(items[0], width=3)
        else:
            # If nothing selected, prepare for canvas dragging
            self.view.scan_mark(event.x, event.y)

    def move(self, event):
        if self.left_mouse_down:
            if self.selected_item:
                # If item selected, move it to current mouse position
                current_mouse_position = (self.view.canvasx(event.x), self.view.canvasy(event.y))
                item_origin_offset_x = self.event_start_position[0] - self.selected_item_origin[0]
                item_origin_offset_y = self.event_start_position[1] - self.selected_item_origin[1]
                self.view.moveto(self.selected_item, current_mouse_position[0] - item_origin_offset_x,
                                 current_mouse_position[1] - item_origin_offset_y)
            else:
                # If nothing selected, move canvas to current mouse position
                self.view.scan_dragto(event.x, event.y, gain=1)
        self.view.update()

    # noinspection PyUnusedLocal
    def move_to(self, event):
        self.left_mouse_down = False

        if self.selected_item:
            # Reset selected canvas item
            self.view.itemconfig(self.selected_item, width=1)

            # Clear selection
            self.selected_item = None
            self.selected_item_origin = None
            self.event_start_position = None
