import tkinter as tk


DARK_BACKGROUND = "#1D1D1D"
LIGHT_BACKGROUND = "#383838"
FOREGROUND = "#292929"

GRID_WIDTH = 5000
MINOR_TICK = 20
MAJOR_TICK_FACTOR = 5
MARKER_RADIUS = 4

RESIZE_BORDER_WIDTH = 50
DEFAULT_FONT = "Helvetica 12"


class NodeGraphView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=DARK_BACKGROUND)
        self.pack(fill="both", expand=True)

        self.info_label = tk.Label(self, text="1.0", font=DEFAULT_FONT, bg=DARK_BACKGROUND, fg=LIGHT_BACKGROUND)
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
        for x in range(-GRID_WIDTH, GRID_WIDTH, MINOR_TICK * MAJOR_TICK_FACTOR):
            for y in range(-GRID_WIDTH, GRID_WIDTH + 1, MINOR_TICK * MAJOR_TICK_FACTOR):
                self.create_oval((x - MARKER_RADIUS, y - MARKER_RADIUS, x + MARKER_RADIUS, y + MARKER_RADIUS),
                                 width=1, outline=LIGHT_BACKGROUND, fill=LIGHT_BACKGROUND, tags="grid")

        # Draw test nodes
        self.create_rectangle([10, 10, 160, 110], fill=FOREGROUND, outline="red", width=1, tags="node")
        self.create_rectangle([100, 100, 260, 210], fill=FOREGROUND, outline="green", width=1, tags="node")
        self.tag_bind('node', '<Enter>', self.on_enter_item)
        self.tag_bind('node', '<Leave>', self.on_leave_item)

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

    def update_scale(self, multiplier):
        self.scene_scale *= multiplier
        self.update_info_text("{0:.1f}".format(self.scene_scale))

    def update_info_text(self, msg):
        self.info_label.config(text=msg)

    def get_minor_width(self):
        minor_tick_line = self.find_withtag("minor_tick")[0]
        return self.coords(minor_tick_line)[2] - self.coords(minor_tick_line)[0]

    def get_grid_origin(self):
        grid_origin_item = self.find_withtag("grid")[0]
        item_coords = self.coords(grid_origin_item)
        item_center = ((item_coords[0] + item_coords[2]) / 2, (item_coords[1] + item_coords[3]) / 2)
        return item_center

    def snap_to_grid(self, position, item_click_offset):
        origin = self.get_grid_origin()
        minor = self.get_minor_width()

        x_snap = round((((position[0] - item_click_offset[0] - origin[0]) // minor) * minor) + origin[0])
        y_snap = round((((position[1] - item_click_offset[1] - origin[1]) // minor) * minor) + origin[1])
        return x_snap, y_snap
