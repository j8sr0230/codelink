import tkinter as tk
from tkinter.font import Font

from node_view import NodeView


DARK_BACKGROUND = "#1D1D1D"
LIGHT_BACKGROUND = "#383838"
DARK_FOREGROUND = "#545454"
LIGHT_FOREGROUND = "#E5E5E5"

DEFAULT_FONT_FAMILY = "Helvetica"
DEFAULT_FONT_SIZE = 12
DEFAULT_NODE_FONT_SIZE = 12

GRID_WIDTH = 4000
MINOR_TICK = 5
MAJOR_TICK_FACTOR = 20
MARKER_SIZE = 10

ZOOM_STEP = 1.1
RESIZE_BORDER_WIDTH = 50


class NodeGraphView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=DARK_BACKGROUND)

        # Instance Attributes
        self.controller = None
        self.default_node_font = Font(family=DEFAULT_FONT_FAMILY, size=DEFAULT_NODE_FONT_SIZE)

        # Setup GUI
        self.pack(fill="both", expand=True)
        self.info_label = tk.Label(self, text="Scale. 1.0, Minor tick: 5 px",
                                   font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE), bg=DARK_BACKGROUND,
                                   fg=LIGHT_FOREGROUND)
        self.info_label.pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)
        self.bind("<ButtonPress-1>", self.on_mouse_left_down)
        self.bind("<ButtonRelease-1>", self.on_mouse_left_up)
        self.bind("<B1-Motion>", self.on_mouse_move)
        self.bind("<MouseWheel>", self.on_mouse_wheel)

        # Draw (invisible) line to track size of scaled canvas items
        self.create_line((0, 0, MINOR_TICK, 0), tags="minor_tick")
        self.itemconfigure("minor_tick", state="hidden")
        self.create_line((0, 0, 100, 0), tags="scale_ref")
        self.itemconfigure("scale_ref", state="hidden")

        # Draw background
        self.paint_grid()

        # Draw test items
        n1 = self.create_rectangle([0, 0, 200, 100], fill=DARK_FOREGROUND, outline="red", width=1, tags="node")
        n2 = self.create_rectangle([0, 0, 200, 100], fill=DARK_FOREGROUND, outline="green", width=1, tags="node")
        self.moveto(n1, 0, 0)
        self.moveto(n2, 300, 200)

        frame = tk.Frame(self)
        lbl = tk.Label(frame, text="In 1", font=self.default_node_font)
        lbl.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        btn = tk.Button(frame, text="Ok", font=self.default_node_font)
        btn.pack(fill=tk.BOTH, expand=True)

        self.create_window(10, 10, anchor=tk.NW, window=frame, width=200, height=100, tags="win_obj")

    def set_controller(self, controller):
        self.controller = controller

    def set_info_text(self, msg):
        self.info_label.config(text=msg)

    def on_mouse_left_down(self, mouse_event):
        if self.controller:
            self.controller.move_from(mouse_event)

    def on_mouse_left_up(self, mouse_event):
        if self.controller:
            self.controller.move_to(mouse_event)

    def on_mouse_move(self, mouse_event):
        if self.controller:
            self.controller.move(mouse_event)

    def on_mouse_wheel(self, mouse_event):
        if self.controller:
            self.controller.zoom(mouse_event)

    def get_minor_width(self):
        minor_tick_line = self.find_withtag("minor_tick")[0]
        return self.coords(minor_tick_line)[2] - self.coords(minor_tick_line)[0]

    def get_scale(self):
        scale_ref_line = self.find_withtag("scale_ref")[0]
        return (self.coords(scale_ref_line)[2] - self.coords(scale_ref_line)[0]) / 100

    def set_scale(self, x_offset, y_offset, scale):
        win_obj_list = self.find_withtag("win_obj")
        win_obj_bbox_list = [self.bbox(obj_id) for obj_id in win_obj_list]

        self.scale("all", x_offset, y_offset, scale, scale)
        # self.default_node_font.config(size=round(scale * self.default_node_font.cget("size")))
        self.default_node_font.config(size=round(self.get_scale() * DEFAULT_NODE_FONT_SIZE))

        for idx, obj_id in enumerate(win_obj_list):
            obj_width = win_obj_bbox_list[idx][2] - win_obj_bbox_list[idx][0]
            obj_height = win_obj_bbox_list[idx][3] - win_obj_bbox_list[idx][1]
            self.itemconfig(obj_id, width=scale * obj_width, height=scale * obj_height)

    def scale_in(self, x_offset, y_offset):
        self.set_scale(x_offset, y_offset, ZOOM_STEP)

    def scale_out(self, x_offset, y_offset):
        self.set_scale(x_offset, y_offset, 1/ZOOM_STEP)

    def paint_grid(self):
        major_step = MINOR_TICK * MAJOR_TICK_FACTOR
        for x in range(-GRID_WIDTH, GRID_WIDTH + major_step, major_step):
            for y in range(-GRID_WIDTH, GRID_WIDTH + major_step, major_step):
                self.create_oval((x, y, x + MARKER_SIZE, y + MARKER_SIZE), fill=LIGHT_BACKGROUND, width=0, tags="grid")

    def get_grid_origin(self):
        grid_origin_item = self.find_withtag("grid")[0]
        item_coords = self.coords(grid_origin_item)
        return item_coords[0], item_coords[1]

    def get_snapped_pos(self, position, item_click_offset):
        origin = self.get_grid_origin()
        minor = self.get_minor_width()
        x_snap = (((position[0] - item_click_offset[0] - origin[0]) // minor) * minor) + origin[0]
        y_snap = (((position[1] - item_click_offset[1] - origin[1]) // minor) * minor) + origin[1]
        return x_snap, y_snap
