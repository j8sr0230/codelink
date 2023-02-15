import tkinter as tk

from node_view import NodeView


DARK_BACKGROUND = "#1D1D1D"
LIGHT_BACKGROUND = "#383838"
DARK_FOREGROUND = "#545454"
LIGHT_FOREGROUND = "#E5E5E5"

GRID_WIDTH = 4000
MINOR_TICK = 5
MAJOR_TICK_FACTOR = 20
MARKER_SIZE = 10
ZOOM_STEP = 1.1

RESIZE_BORDER_WIDTH = 50
DEFAULT_FONT = "Helvetica 12"


class NodeGraphView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=DARK_BACKGROUND)
        self.pack(fill="both", expand=True)

        self.info_label = tk.Label(self, text="Scale. 1.0, Minor tick: 5 px", font=DEFAULT_FONT, bg=DARK_BACKGROUND,
                                   fg=LIGHT_FOREGROUND)
        self.info_label.pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)
        self.bind("<ButtonPress-1>", self.on_mouse_left_down)
        self.bind("<ButtonRelease-1>", self.on_mouse_left_up)
        self.bind("<B1-Motion>", self.on_mouse_move)
        self.bind("<MouseWheel>", self.on_mouse_wheel)

        self.controller = None
        self.scene_scale = 1.0

        # Draw (invisible) line to measure pixel distance of minor tick on scaled canvas
        self.create_line((0, 0, MINOR_TICK, 0), tags="minor_tick")
        self.itemconfigure("minor_tick", state="hidden")

        # Draw background
        self.paint_grid()

        # Draw test nodes
        n1 = self.create_rectangle([0, 0, 200, 100], fill=DARK_FOREGROUND, outline="red", width=1, tags="node")
        n2 = self.create_rectangle([0, 0, 200, 100], fill=DARK_FOREGROUND, outline="green", width=1, tags="node")
        self.moveto(n1, 0, 0)
        self.moveto(n2, 300, 200)
        self.tag_bind('node', '<Enter>', self.on_enter_item)
        self.tag_bind('node', '<Leave>', self.on_leave_item)

        n3 = NodeView(self)
        n3.paint()

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

    def on_enter_item(self, enter_event):
        pass
        # current_mouse_position = (self.canvasx(enter_event.x), self.canvasy(enter_event.y))
        # selected_item = self.find_closest(current_mouse_position[0], current_mouse_position[1])[0]
        # item_coords = self.coords(selected_item)
        # item_width = item_coords[2] - item_coords[0]
        # resize_x_area_start = item_coords[0] + item_width - self.get_scale() * RESIZE_BORDER_WIDTH
        # if current_mouse_position[0] > resize_x_area_start:
        #     self.config(cursor="size_we")

    # noinspection PyUnusedLocal
    def on_leave_item(self, enter_event):
        pass
        # self.config(cursor="arrow")

    def set_controller(self, controller):
        self.controller = controller

    def get_scale(self):
        return self.scene_scale

    def set_scale(self, multiplier):
        self.scene_scale *= multiplier
        self.set_info_text("Scale: {0:.1f}, Minor tick: {1:.1f} px".format(self.get_scale(), self.get_minor_width()))

    def set_info_text(self, msg):
        self.info_label.config(text=msg)

    def get_minor_width(self):
        minor_tick_line = self.find_withtag("minor_tick")[0]
        return self.coords(minor_tick_line)[2] - self.coords(minor_tick_line)[0]

    def get_grid_origin(self):
        grid_origin_item = self.find_withtag("grid")[0]
        item_coords = self.coords(grid_origin_item)
        return item_coords[0], item_coords[1]

    def snap_to_grid(self, position, item_click_offset):
        origin = self.get_grid_origin()
        minor = self.get_minor_width()
        x_snap = (((position[0] - item_click_offset[0] - origin[0]) // minor) * minor) + origin[0]
        y_snap = (((position[1] - item_click_offset[1] - origin[1]) // minor) * minor) + origin[1]
        return x_snap, y_snap

    def paint_grid(self):
        major_step = MINOR_TICK * MAJOR_TICK_FACTOR
        for x in range(-GRID_WIDTH, GRID_WIDTH + major_step, major_step):
            for y in range(-GRID_WIDTH, GRID_WIDTH + major_step, major_step):
                self.create_oval((x, y, x + MARKER_SIZE, y + MARKER_SIZE), fill=LIGHT_BACKGROUND, width=0, tags="grid")
