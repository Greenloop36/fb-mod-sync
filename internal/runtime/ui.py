"""

    User Interface
    @gl36

    20/06/2025

"""

# Imports
from tkinter import messagebox, filedialog

import ttkbootstrap as ttk
import ttkbootstrap.dialogs.dialogs as dialogs
from ttkbootstrap.constants import *

# Class
class App:
    def __init__(self, window_title: str):
        # Properties
        self.menus: dict[str, ttk.Menu] = {}

        # Initialise Tk
        self.root = ttk.Window(title=window_title, themename="darkly")
        self.root.resizable(False, False)

        # Create UI - Change as necessary

        ## Menubar
        self.menubar = ttk.Menu(self.root)
    
    def create_menu(self, name: str):
        menu = ttk.Menu(self.menubar)

        self.menus[name] = menu
        self.menubar.add_cascade(label=name, menu=menu)
    
    def create_menubutton(self, menu_name: str, button_name: str, command):
        self.menus[menu_name].add_command(label=button_name, command=command)

if __name__ == "__main__":
    App("Test app").root.mainloop()