from node_graph_view import RESIZE_BORDER_WIDTH

from node_view import NodeView
from node_model import NodeModel


class NodeGraphController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.mouse_mode = None
        self.selected_item = None
        self.item_click_offset = None

        self.add_node()

    def set_selected_item(self, item, mouse_event):
        self.selected_item = item
        self.item_click_offset = (self.view.canvasx(mouse_event.x) - self.view.coords(self.selected_item.border_rect)[0],
                                  self.view.canvasy(mouse_event.y) - self.view.coords(self.selected_item.border_rect)[1])

    def move_from(self, mouse_event):
        print(self.selected_item)

        if self.selected_item:
            # Modify selected item
            self.view.tag_raise(self.selected_item.border_rect)
            self.view.tag_raise(self.selected_item.header_rect)
            self.view.tag_raise(self.selected_item.content_rect)
            #self.view.itemconfig(items[0], width=2)
        else:
            # If nothing selected, prepare for canvas dragging
            self.view.scan_mark(mouse_event.x, mouse_event.y)

    def move(self, mouse_event):
        if self.selected_item:

            current_mouse_position = (self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y))
            self.move_node_to(self.selected_item, current_mouse_position[0], current_mouse_position[1])
            #
            # # Calculate current item and event data
            # item_coords = self.view.coords(self.selected_item)
            # current_item_width = item_coords[2] - item_coords[0]
            # resize_x_area_start = item_coords[0] + current_item_width - self.view.get_scale() * RESIZE_BORDER_WIDTH
            #
            # # Set mouse mode
            # if current_mouse_position[0] > resize_x_area_start:
            #     if not self.mouse_mode:
            #         self.mouse_mode = "resize_item"
            # else:
            #     if not self.mouse_mode:
            #         self.mouse_mode = "move_item"
            #
            # # Do action
            # if self.mouse_mode == "resize_item":
            #     self.view.config(cursor="size_we")
            #     self.view.coords(self.selected_item, item_coords[0], item_coords[1], current_mouse_position[0],
            #                      item_coords[3])
            # elif self.mouse_mode == "move_item":
            #     snapped_xy = self.view.get_snapped_pos(current_mouse_position, self.item_click_offset)
            #     self.view.moveto(self.selected_item, round(snapped_xy[0], 0), round(snapped_xy[1], 0))
        else:
            # If nothing selected, move canvas to current mouse position
            self.mouse_mode = "scroll_canvas"
            if self.mouse_mode == "scroll_canvas":
                self.view.scan_dragto(mouse_event.x, mouse_event.y, gain=1)

    # noinspection PyUnusedLocal
    def move_to(self, mouse_event):
        if self.selected_item:
            # Clear selection
            self.selected_item = None
            self.item_click_offset = None
            self.view.config(cursor="arrow")

        # Reset mouse mode
        self.mouse_mode = None

    def zoom(self, mouse_event):
        if mouse_event.delta > 0:
            self.view.scale_in(self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y))
        else:
            self.view.scale_out(self.view.canvasx(mouse_event.x), self.view.canvasy(mouse_event.y))

        msg = "Scale: {0:.1f}, Minor tick: {1:.1f} px".format(self.view.get_scale(), self.view.get_minor_width())
        self.view.set_info_text(msg)

        # Toggle grid
        if self.view.get_scale() < 0.7:
            self.view.itemconfigure("grid", state="hidden")
        else:
            self.view.itemconfigure("grid", state="normal")

    def add_node(self):
        node_model = NodeModel()
        self.model.add_node(node_model)
        node_view = NodeView(self.view, 300, 50)
        #node_controller = NodeController(node_model, node_view)
        node_view.set_controller(self)

        n1 = self.view.create_rectangle([0, 0, 200, 100], fill="white", outline="red", width=1, tags="node")
        self.view.moveto(n1, 300, 100)

    def move_node_to(self, node, x, y):
        snapped_xy = self.view.get_snapped_pos((x, y), self.item_click_offset)
        #     self.view.moveto(self.selected_item, round(snapped_xy[0], 0), round(snapped_xy[1], 0))

        # self.view.moveto(node.border_rect, round(snapped_xy[0], 0), round(snapped_xy[1], 0))
        # self.view.moveto(node.header_rect, round(snapped_xy[0], 0), round(snapped_xy[1], 0))
        # self.view.moveto(node.content_rect, round(snapped_xy[0], 0), round(snapped_xy[1] + 30, 0))

        self.view.moveto(node.border_rect, x, y)
        self.view.moveto(node.header_rect, x, y)
        self.view.moveto(node.content_rect, x, y + 30)

        #self.view.move(node.border_rect, 5, 0)
        #self.view.move(node.header_rect, 5, 0)
        #self.view.move(node.content_rect, 5, 0)
