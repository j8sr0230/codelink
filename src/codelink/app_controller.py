import tkinter as tk

from app_view import AppView


class AppController:
    def __init__(self, master):
        self.app_view = AppView(parent=master, width=600, height=400)
        self.app_view.pack(side="top", fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()
