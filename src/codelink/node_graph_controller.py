SCENE_SCALE_MIN = 0.75
SCENE_SCALE_MAX = 1.25


class NodeGraphController:
    def __init__(self, model, view):
        self.mode = model
        self.view = view

        self.left_mouse_down = False
        self.selected_item = None
        self.selected_item_origin = None
        self.event_start_position = None

        self.scene_scale = 1.0

    def move_from(self, mouse_event):
        self.left_mouse_down = True

        items = self.view.find_withtag("current")
        if len(items) > 0 and "node" in self.view.gettags(items[0]):
            # If selected item is node, save item, origin and event position on canvas
            self.selected_item = items[0]
            self.selected_item_origin = self.view.coords(items[0])[:2]
            self.event_start_position = (self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y))

            # Modify selected item
            self.view.tag_raise(items[0])
            self.view.itemconfig(items[0], width=3)
        else:
            # If no node selected, prepare for canvas dragging
            self.view.scan_mark(mouse_event.x, mouse_event.y)

    def move(self, mouse_event):
        if self.left_mouse_down:
            if self.selected_item:
                # If item selected, move it to current mouse position
                current_mouse_position = (self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y))
                item_origin_offset_x = self.event_start_position[0] - self.selected_item_origin[0]
                item_origin_offset_y = self.event_start_position[1] - self.selected_item_origin[1]
                self.view.moveto(self.selected_item, current_mouse_position[0] - item_origin_offset_x,
                                 current_mouse_position[1] - item_origin_offset_y)
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
            self.selected_item_origin = None
            self.event_start_position = None

    def zoom(self, mouse_event):
        if mouse_event.delta > 0:
            self.scene_scale *= 1.1
            if self.scene_scale <= SCENE_SCALE_MAX:
                self.view.scale("all", self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y), 1.1, 1.1)
            else:
                self.scene_scale = SCENE_SCALE_MAX
        else:
            self.scene_scale *= 0.9
            if self.scene_scale >= SCENE_SCALE_MIN:
                self.view.scale("all", self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y), 0.9, 0.9)
            else:
                self.scene_scale = SCENE_SCALE_MIN
        print(self.scene_scale)
