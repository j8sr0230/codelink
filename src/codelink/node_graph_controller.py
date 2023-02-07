from node_graph_view import RESIZE_SQUARE, MINOR_TICK, MAJOR_TICK_FACTOR


class NodeGraphController:
    def __init__(self, model, view):
        self.mode = model
        self.view = view

        self.left_mouse_down = False
        self.selected_item = None
        self.item_event_offset = None

    def move_from(self, mouse_event):
        self.left_mouse_down = True

        items = self.view.find_withtag("current")
        if len(items) > 0 and "node" in self.view.gettags(items[0]):
            # If selected item is node, save item and offset between event and item origin
            self.selected_item = items[0]
            self.item_event_offset = (self.view.canvasx(mouse_event.x) - self.view.coords(items[0])[0],
                                      self.view.canvasy(mouse_event.y) - self.view.coords(items[0])[1])

            # Modify selected item
            self.view.tag_raise(items[0])
            self.view.itemconfig(items[0], width=3)
        else:
            # If no node selected, prepare for canvas dragging
            self.view.scan_mark(mouse_event.x, mouse_event.y)

    def move(self, mouse_event):
        if self.left_mouse_down:
            if self.selected_item:
                # If node selected
                current_mouse_position = (self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y))

                # Calculate current node and event data
                item_coords = self.view.coords(self.selected_item)
                current_item_width = item_coords[2] - item_coords[0]
                current_item_height = item_coords[3] - item_coords[1]
                resize_x_area_start = item_coords[0] + current_item_width - RESIZE_SQUARE
                resize_y_area_start = item_coords[1] + current_item_height - RESIZE_SQUARE

                if (current_mouse_position[0] > resize_x_area_start) and \
                        (current_mouse_position[1] > resize_y_area_start):
                    # If mouse position within resize area, resize node
                    scaled_minor_tick = self.view.get_minor_width()
                    print(scaled_minor_tick)
                    self.view.coords(self.selected_item,
                                     item_coords[0],
                                     item_coords[1],
                                     (current_mouse_position[0] // scaled_minor_tick) * scaled_minor_tick,
                                     (current_mouse_position[1]) * (scaled_minor_tick/MINOR_TICK))
                else:
                    # If mouse position outside resize area, move node
                    self.view.moveto(self.selected_item,
                                     (current_mouse_position[0] - self.item_event_offset[0]) // MINOR_TICK * MINOR_TICK,
                                     (current_mouse_position[1] - self.item_event_offset[1]) // MINOR_TICK * MINOR_TICK)
            else:
                # If nothing selected, move canvas to current mouse position
                self.view.scan_dragto(mouse_event.x, mouse_event.y, gain=1)

    # noinspection PyUnusedLocal
    def move_to(self, mouse_event):
        self.left_mouse_down = False

        if self.selected_item:
            # Reset selected item
            self.view.itemconfig(self.selected_item, width=1)

            # Clear selection
            self.selected_item = None
            self.item_event_offset = None

    def zoom(self, mouse_event):
        if mouse_event.delta > 0:
            self.view.scale("all", self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y), 1.1, 1.1)
            self.view.update_scale(1.1)
        else:
            self.view.scale("all", self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y), 0.9, 0.9)
            self.view.update_scale(0.9)

            self.view.get_minor_width()

        if self.view.scene_scale < 0.8:
            self.view.itemconfigure("grid", state="normal")
        else:
            self.view.itemconfigure("grid", state="normal")
