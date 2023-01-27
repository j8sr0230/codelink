import tkinter as tk


# class Navbar(tk.Frame): ...
# class Toolbar(tk.Frame): ...
# class Statusbar(tk.Frame): ...
# class Main(tk.Frame): ...


class AppView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # self.statusbar = Statusbar(self, ...)
        # self.toolbar = Toolbar(self, ...)
        # self.navbar = Navbar(self, ...)
        # self.main = Main(self, ...)

        # self.statusbar.pack(side="bottom", fill="x")
        # self.toolbar.pack(side="top", fill="x")
        # self.navbar.pack(side="left", fill="y")
        # self.main.pack(side="right", fill="both", expand=True)

        # Rest of your GUI here