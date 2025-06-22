"""

    Application Root
    @gl36

    20/06/2025

"""

# Imports
from internal.lib import file_system, project_types
from internal.runtime import updater

import os
import sys

from tkinter import messagebox, filedialog

import ttkbootstrap as ttk
import ttkbootstrap.dialogs.dialogs as dialogs
from ttkbootstrap.constants import *

def void() -> None:
    pass

# Project
class UiHeader:
    def __init__(self, master: ttk.Window, title: str, pad: int, description: str):
        self.frame = ttk.Frame(master)
        self.frame.grid(sticky="w")

        self.label_title = ttk.Label(self.frame, text=title, font={"family": "Helvetica", "weight": "bold", "size": 17}, anchor="w")
        self.label_title.grid(padx=(pad, 50), pady=(pad, 0), sticky="w")

        if description:
            self.label_description = ttk.Label(self.frame, text=description, anchor="w")
            self.label_description.grid(padx=pad, pady=(0, pad), sticky="w")

class PathBox:
    def __init__(self, master: str, label: str, stringvar: ttk.StringVar, padding: int):
        # Properties
        self._str_var = stringvar

        # Ui
        self.frame = ttk.Frame(master)
        self.frame.grid(sticky="w")

        self.label = ttk.Label(self.frame, text=label, anchor="w")
        self.label.grid(row=0, column=0, padx=padding, pady=padding, sticky="w")

        self.entry = ttk.Entry(self.frame, textvariable=stringvar, width=50)
        self.entry.grid(row=0, column=1, padx=(0, padding), sticky="w")

        self.button_browse = ttk.Button(self.frame, text="Browse", bootstyle="secondary", command=self.browse)
        self.button_browse.grid(row=0, column=2, padx=(0, padding), sticky="w")
    
    def browse(self):
        start_dir: str = self._str_var.get() or None
        selection: str = filedialog.askdirectory(initialdir=start_dir)

        if os.path.exists(selection):
            self._str_var.set(selection)
        
        # print(f"{selection=}")

class Interface:
    def __init__(self, window_title: str):
        # Properties
        self.menus: dict[str, ttk.Menu] = {}

        # Initialise Tk
        self.root = ttk.Window(title=window_title, themename="darkly")
        self.root.resizable(False, False)

class App:
    def __init__(self):
        # Project Properties

        ## Project Data
        self.FileSystem = file_system.FileSystem(__file__)
        self.config: dict = self.FileSystem.read_resource("internal/data/config.yaml", "yaml")
        self.project: project_types.Project = self.FileSystem.read_resource("internal/data/project.yaml", "yaml")
        self.project_version: str = self.FileSystem.read_resource("internal/data/VERSION")
        self.default_settings: dict[str, any] = self.FileSystem.read_resource("internal/data/default_settings.json", "json")

        self.ui = Interface(self.project["project_information"]["name"])
        self.settings = file_system.SettingsHelper(self.project["project_information"]["app_id"], self.default_settings)
        self.updater = updater.Updater(self.project["repository"]["owner"], self.project["repository"]["name"], os.path.dirname(__file__), ui_master=self.ui.root)

        # UI App

        ## Variables
        self.var_destination = ttk.StringVar()
        
        ## Menubar
        self.menubar = ttk.Menu(self.ui.root)
        self.ui.root.config(menu=self.menubar)

        ## File
        self.menu_file = ttk.Menu(self.menubar)
        self.menu_file.add_command(label="Software Update", command=self.software_update)
        self.menu_file.add_separator()
        self.menu_file.add_command(label=f"Information...", command=self.information)
        self.menu_file.add_command(label="Quit", command=self.quit)

        self.menubar.add_cascade(label="File", menu=self.menu_file)


        # self.ui.create_menu("File")
        # self.ui.create_menubutton("File", "Perform software update", self.software_update)

        ## Header
        self.app_header = UiHeader(self.ui.root, self.project["project_information"]["name"], 15, "Automatically sync active mods on the Frenchy Boi Minecraft server")

        ## Content
        self.app_content = ttk.Frame(self.ui.root)
        self.app_content.grid()

        self.entry_destination = PathBox(self.ui.root, "Mods Directory", self.var_destination, 15)

        ## Buttons
        self.frame_buttons = ttk.Frame(self.ui.root)
        self.frame_buttons.grid(sticky="nsew")
        self.frame_buttons.columnconfigure(1, weight=1)

        ### button: Quit
        self.button_quit = ttk.Button(self.frame_buttons, text="Quit", bootstyle="secondary", command=self.quit)
        self.button_quit.grid(sticky="w", padx=15)

        ## Main Buttons
        self.container_main_buttons = ttk.Frame(self.frame_buttons)
        self.container_main_buttons.grid(row=0, column=1, sticky="e", pady=15)

        ### button: Refresh
        self.button_Refresh = ttk.Button(self.container_main_buttons, text="Check for updates", bootstyle="secondary")
        self.button_Refresh.grid(sticky="e")

        ### button: Sync
        self.button_sync = ttk.Button(self.container_main_buttons, text="Sync Mods", bootstyle="primary", command=self.sync)
        self.button_sync.grid(sticky="e", padx=15, row=0, column=1)

        self.ui.root.update()

        # Check for updates
        self.check_for_updates()
    
    def check_for_updates(self):
        update_available, newest_version = self.updater.is_update_available(self.project_version)
        if update_available:
            dialogs.Messagebox.show_info(
            f"A new version, {newest_version}, is available.\nTo install it, click on File > Software Update.",
            "Software Update"
        )

    def update_config(self):
        # Update saved dest dir
        destination: str = self.var_destination.get() or ""

        if os.path.exists(destination):
            self.settings.set_setting("destination_dir", destination)
    
    def sync(self):
        destination: str = self.var_destination.get() or ""

        if not os.path.exists(destination):
            dialogs.Messagebox.show_error("Cannot sync: invalid destination directory", "Error", alert=True)
            return

        synchro = updater.Updater("Greenloop36", "fb-server_mods", destination, "Mods", "synchronising mods...", self.ui.root)

    def quit(self):
        self.update_config()
        self.ui.root.destroy()
    
    def software_update(self):
        update_available, new_version = self.updater.is_update_available(self.project_version)

        if not update_available:
            choice: str = dialogs.Messagebox.yesno("You are already running the latest version.\nUpdate anyway?", "Software Update", alert=True)

            if choice == "No":
                return
        
        choice: str = dialogs.Messagebox.okcancel("Perform a software update?", "Software Update")

        if choice == "OK":
            self.updater.update()
    
    def information(self):
        dialogs.Messagebox.show_info(
            f"You are currently running version {self.project_version} of {self.project["project_information"]["name"]}.\n\n"
            f"This project is licensed under the GPL-3.0 license.\nFor more information, view the LICENSE file."
            ,
            "Information"
        )

# Runtime
if __name__ == "__main__":
    App().ui.root.mainloop()