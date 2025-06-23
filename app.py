"""

    Application Root
    @gl36

    20/06/2025

"""

# Imports
import sys
sys.dont_write_bytecode = True

from internal.lib import file_system, project_types
from internal.runtime import updater

import os
import requests
import webbrowser

from tkinter import filedialog

import ttkbootstrap as ttk
import ttkbootstrap.dialogs.dialogs as dialogs
from ttkbootstrap.constants import *

def void() -> None:
    pass

# Project
class UiHeader:
    def __init__(self, master: ttk.Window, title: str, pad: int, description: str):
        self.frame = ttk.Frame(master)
        self.frame.grid(sticky="w", row=1)

        self.label_title = ttk.Label(self.frame, text=title, font={"family": "Helvetica", "weight": "bold", "size": 17}, anchor="w")
        self.label_title.grid(padx=(pad, 50), pady=(pad, 0), sticky="w")

        if description:
            self.label_description = ttk.Label(self.frame, text=description, anchor="w")
            self.label_description.grid(padx=pad, pady=(0, pad), sticky="w")

class PathBox:
    def __init__(self, master: str, label: str, stringvar: ttk.StringVar, padding: int, help_text: str = None):
        # Properties
        self._str_var = stringvar
        self._help_text = help_text

        # Ui
        self.frame = ttk.Frame(master)
        self.frame.grid(sticky="w")

        self.label = ttk.Label(self.frame, text=label, anchor="w")
        self.label.grid(row=0, column=0, padx=padding, pady=padding, sticky="w")

        self.entry = ttk.Entry(self.frame, textvariable=stringvar, width=50)
        self.entry.grid(row=0, column=1, padx=(0, padding), sticky="w")

        self.button_browse = ttk.Button(self.frame, text="Browse", bootstyle="secondary", command=self.browse)
        self.button_browse.grid(row=0, column=2, padx=(0, padding), sticky="w")

        if help_text:
            self.button_help = ttk.Button(self.frame, text="?", bootstyle="secondary", command=self.help)
            self.button_help.grid(row=0, column=3, padx=(0, padding), sticky="w")
    
    def help(self):
        dialogs.Messagebox.show_info(
            self._help_text,
            "Information"
        )
    
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

        self.entry_destination = PathBox(self.ui.root, "Mods Directory", self.var_destination, 15,
            "This is your mods folder. To get this file:\n"
            "- Open CurseForge and select your profile\n"
            "- Click the three dots next to the Play button\n"
            "- Click the \"Open Folder\" button from the list\n"
            "- Open the \"mods\" folder, and then copy the path\n"
            "- Paste the copied path into the text box to the left.\n\n"
            "You will only have to do this once! Your settings are saved automatically."
            )

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
        self.button_Refresh = ttk.Button(self.container_main_buttons, text="Verify local files", bootstyle="secondary", command=self.refresh)
        self.button_Refresh.grid(sticky="e")

        ### button: Sync
        self.button_sync = ttk.Button(self.container_main_buttons, text="Sync Mods", bootstyle="primary", command=self.sync)
        self.button_sync.grid(sticky="e", padx=15, row=0, column=1)

        self.ui.root.update()

        # Check for updates
        can_update: bool = self.check_for_updates()

        # if can_update:
        #     try:
        #         Banner(self.ui.root, f"A software update is available.")
        #     except Exception as e:
        #         print(e)

        # Apply settings
        self.var_destination.set(self.settings.get_setting("destination_dir"))

    # 
    def check_for_updates(self) -> bool:
        # return True
        update_available, newest_version = self.updater.is_update_available(self.project_version)
        if update_available:
            dialogs.Messagebox.show_info(
                f"A new version, {newest_version}, is available.\nTo install it, click on File > Software Update.",
                "Software Update"
            )

        return update_available

    def update_config(self):
        # Update saved dest dir
        destination: str = self.var_destination.get() or ""

        if os.path.exists(destination):
            self.settings.set_setting("destination_dir", destination)
    

    # UI Interaction
    def sync(self):
        destination: str = self.var_destination.get() or ""

        if not os.path.exists(destination):
            dialogs.Messagebox.show_error("Cannot sync: invalid destination directory", "Error", alert=True)
            return

        synchro = updater.Updater("Greenloop36", "fb-server_mods", destination, "Mods", "synchronising mods...", self.ui.root)
        success, result = synchro.update()

        if success:
            dialogs.Messagebox.show_info(f"Synchronised successfully.", "Information", alert=True)
        else:
            dialogs.Messagebox.show_error(f"Sync failed!\n{result}", "Error", alert=True)

    def refresh(self):
        # Variables
        directory: str = self.var_destination.get() or ""

        
        server_files: list[str] = []
        local_files: list[str]  = []

        problems: list[str] = []

        # Verify
        if not os.path.exists(directory):
            return dialogs.Messagebox.show_warning(
                f"You must set a destination directory.",
                "Warning"
            )
        
        if os.path.basename(directory) != "mods":
            choice: str = dialogs.Messagebox.yesno(f"Are you sure that this is your mods folder?", "Warning", alert=True)
            if choice != "Yes": return
        
        # Get
        try:
            response = requests.get(f"https://api.github.com/repos/{self.config["sync_location"]}/contents/")
        except Exception as e:
            return dialogs.Messagebox.show_error(
                f"Refresh failed!\n{type(e).__name__}: {e}",
                "Error"
            )
        
        # Parse response
        for data in response.json():
            file_name: str = data["name"]
            # file_hash: str = data["sha"]

            # server_files[file_name] = file_hash
            server_files.append(file_name)

        # Parse local files
        for root, _, dir_files in os.walk(directory):
            for name in dir_files:
                if name.startswith("."): continue

                full_path: str = os.path.join(root, name)

                # Hash
                # try:
                #     with open(full_path, "rb") as f:
                #         hash: str = hashlib.sha1(f.read()).hexdigest()
                # except Exception as e:
                #     return dialogs.Messagebox.show_error(
                #         f"Failed to read {name}!\n{type(e).__name__}: {e}",
                #         "Error"
                #     )
                
                local_files.append(name)
        
        # Find problems
        for name in server_files:
            if name not in local_files:
                problems.append(f'Missing file "{name}"!')
                continue

            # if local_files[name] != hash:
            #     print(f"{local_files[name]}\n{hash}\n")
            #     problems.append(f'Local file "{name}" mismatch between server!')
        
        # Report problems
        if len(problems) == 0:
            return dialogs.Messagebox.show_info(
                "No problems found!",
                "Information"
            )
        else:
            result: str = ""

            for i in problems:
                result += f"- {i}\n"
            
            result += "\nPlease synchronise your files."

            return dialogs.Messagebox.show_warning(result, "Problems detected")

    def quit(self):
        self.update_config()

        try: self.ui.root.destroy()
        except: pass
    
    def software_update(self):
        update_available, new_version = self.updater.is_update_available(self.project_version)

        if not update_available:
            choice: str = dialogs.Messagebox.yesno("You are already running the latest version.\nUpdate anyway?", "Software Update", alert=True)

            if choice == "No":
                return
        
        # Updater does not support updating as .exe
        if file_system.is_running_as_exe():
            choice: str = dialogs.Messagebox.yesno("Cannot update as an .exe file.\nOpen the releases page to download manually?", "Software Update", alert=True)

            if choice == "Yes":
                url: str = f"https://github.com/{self.project["repository"]["owner"]}/{self.project["repository"]["name"]}/releases/latest"
                # print(url)
                webbrowser.open(url)

            return

        
        choice: str = dialogs.Messagebox.okcancel("Perform a software update?", "Software Update")

        if choice == "OK":
            success, result = self.updater.update()

            if success:
                dialogs.Messagebox.show_info("Update successful. The software will now exit.", "Software Update")
                self.quit()
            else:
                return dialogs.Messagebox.show_warning(f"Update failed. Try again later.\n\n{result}", "Software Update")
    
    def information(self):
        dialogs.Messagebox.show_info(
            f"You are currently running version {self.project_version} of {self.project["project_information"]["name"]}.\n\n"
            f"This project is licensed under the GPL-3.0 license.\nFor more information, view the LICENSE file."
            ,
            "Information"
        )

# Runtime
if __name__ == "__main__":
    instance = App()
    instance.ui.root.mainloop()
    instance.quit()