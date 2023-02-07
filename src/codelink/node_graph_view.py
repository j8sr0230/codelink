import tkinter as tk


DARK_BACKGROUND = "#1D1D1D"
LIGHT_BACKGROUND = "#606060"
FOREGROUND = "#292929"

HALF_SCENE_WIDTH = 1000
MINOR_TICK = 20
MAJOR_TICK_FACTOR = 5
MARKER_RADIUS = 5
RESIZE_SQUARE = 20

DEFAULT_FONT = "Helvetica 12"


class NodeGraphView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=DARK_BACKGROUND)
        self.pack(fill="both", expand=True)

        self.info_label = tk.Label(self, text="1.0", font=DEFAULT_FONT, bg=DARK_BACKGROUND, fg=LIGHT_BACKGROUND)
        self.info_label.pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)

        self.bind("<Button-1>", self.on_mouse_left_down)
        self.bind("<ButtonRelease-1>", self.on_mouse_left_up)
        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<MouseWheel>", self.on_mouse_wheel)

        self.controller = None
        self.scene_scale = 1.0

        # Draw background
        for x in range(0, HALF_SCENE_WIDTH + 1, MINOR_TICK * MAJOR_TICK_FACTOR):
            for y in range(0, HALF_SCENE_WIDTH, MINOR_TICK * MAJOR_TICK_FACTOR):
                self.create_oval((x - MARKER_RADIUS, y - MARKER_RADIUS,
                                  x + MARKER_RADIUS + 1, y + MARKER_RADIUS + 1), width=0, fill=LIGHT_BACKGROUND,
                                 tags="grid")

        # Draw invisible line to measure pixel distance of minor tick on scaled canvas
        self.create_line((0, 0, MINOR_TICK, 0), state="disabled", tags="minor_tick")

        self.get_minor_width()

        # Draw test nodes
        self.create_rectangle([10, 10, 160, 110], fill=FOREGROUND, outline=LIGHT_BACKGROUND, width=1, tags="node")
        self.create_rectangle([100, 100, 260, 210], fill=FOREGROUND, outline=LIGHT_BACKGROUND, width=1, tags="node")
        # self.tag_bind('node', '<Enter>', print)

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

    def set_controller(self, controller):
        self.controller = controller

    def update_scale(self, scale):
        self.scene_scale *= scale
        self.set_info_text("{0:.1f}".format(self.scene_scale))

    def set_info_text(self, msg):
        self.info_label.config(text=msg)

    def get_minor_width(self):
        minor_tick_line = self.find_withtag("minor_tick")[0]
        return self.coords(minor_tick_line)[2] - self.coords(minor_tick_line)[0]
