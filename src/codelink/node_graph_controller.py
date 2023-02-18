from node_graph_view import RESIZE_BORDER_WIDTH, ZOOM_STEP

from node_view import NodeView
from node_controller import NodeController
from node_model import NodeModel


class NodeGraphController:
    def __init__(self, model, view):
        self.mode = model
        self.view = view

        self.mouse_mode = None
        self.selected_item = None
        self.item_click_offset = None

    def move_from(self, mouse_event):
        items = self.view.find_withtag("current")

        if len(items) > 0:
            if "node" in self.view.gettags(items[0]):
                # If selected item is node, save item and offset between click event and item origin
                self.selected_item = items[0]
                self.item_click_offset = (self.view.canvasx(mouse_event.x) - self.view.coords(items[0])[0],
                                          self.view.canvasy(mouse_event.y) - self.view.coords(items[0])[1])

                # Modify selected item
                self.view.tag_raise(items[0])
                self.view.itemconfig(items[0], width=2)
        else:
            # If nothing selected, prepare for canvas dragging
            self.view.scan_mark(mouse_event.x, mouse_event.y)

    def move(self, mouse_event):
        if self.selected_item:
            current_mouse_position = (self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y))

            # Calculate current item and event data
            item_coords = self.view.coords(self.selected_item)
            current_item_width = item_coords[2] - item_coords[0]
            resize_x_area_start = item_coords[0] + current_item_width - self.view.get_scale() * RESIZE_BORDER_WIDTH

            # Set mouse mode
            if current_mouse_position[0] > resize_x_area_start:
                if not self.mouse_mode:
                    self.mouse_mode = "resize_item"
            else:
                if not self.mouse_mode:
                    self.mouse_mode = "move_item"

            # Do action
            if self.mouse_mode == "resize_item":
                self.view.config(cursor="size_we")
                self.view.coords(self.selected_item, item_coords[0], item_coords[1], current_mouse_position[0],
                                 item_coords[3])
            elif self.mouse_mode == "move_item":
                snapped_xy = self.view.snap_to_grid(current_mouse_position, self.item_click_offset)
                self.view.moveto(self.selected_item, round(snapped_xy[0], 0), round(snapped_xy[1], 0))
        else:
            # If nothing selected, move canvas to current mouse position
            self.mouse_mode = "scroll_canvas"
            if self.mouse_mode == "scroll_canvas":
                self.view.scan_dragto(mouse_event.x, mouse_event.y, gain=1)

    # noinspection PyUnusedLocal
    def move_to(self, mouse_event):
        if self.selected_item:
            # Reset selected item
            self.view.itemconfig(self.selected_item, width=1)

            # Clear selection
            self.selected_item = None
            self.item_click_offset = None
            self.view.config(cursor="arrow")

        # Reset mouse mode
        self.mouse_mode = None

    def add_node(self, mouse_event):
        node_model = NodeModel()
        node_view = NodeView(self.view, self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y))
        node_controller = NodeController(node_model, node_view)
        node_view.set_controller(node_controller)

    def zoom(self, mouse_event):
        if mouse_event.delta > 0:
            self.view.scale("all", self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y),
                            ZOOM_STEP, ZOOM_STEP)
        else:
            self.view.scale("all", self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y),
                            1/ZOOM_STEP, 1/ZOOM_STEP)

        self.view.set_info_text(
            "Scale: {0:.1f}, Minor tick: {1:.1f} px".format(self.view.get_scale(), self.view.get_minor_width()))

        # Scale fonts and canvas window objects
        self.view.scaled_font.config(size=round(self.view.get_scale() * 30))

        win_obj_list = self.view.find_withtag("win")
        for obj_id in win_obj_list:
            self.view.itemconfig(obj_id, width=self.view.get_scale() * 200, height=self.view.get_scale() * 100)

        # Toggle grid
        if self.view.get_scale() < 0.7:
            self.view.itemconfigure("grid", state="hidden")
        else:
            self.view.itemconfigure("grid", state="normal")
