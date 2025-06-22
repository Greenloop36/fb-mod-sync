"""

    Application Root
    @gl36

    20/06/2025

"""

# Imports
from internal.lib import file_system, project_types
from internal.runtime import ui, updater

import json
import sys

from tkinter import messagebox, filedialog

import ttkbootstrap as ttk
import ttkbootstrap.dialogs.dialogs as dialogs
from ttkbootstrap.constants import *

# Project
class App:
    def __init__(self):
        # Project Properties

        ## Project Data
        self.FileSystem = file_system.FileSystem(__file__)
        self.config: dict = self.FileSystem.read_resource("internal/data/config.yaml", "yaml")
        self.project: project_types.Project = self.FileSystem.read_resource("internal/data/project.yaml", "yaml")
        self.project_version: str = self.FileSystem.read_resource("internal/data/VERSION")
        self.default_settings: dict[str, any] = self.FileSystem.read_resource("internal/data/default_settings.json", "json")
        
        print(self.config)
        print(self.project)
        print(self.project_version)
        print(self.default_settings)

        self.settings = file_system.SettingsHelper(self.project["project_information"]["app_id"], self.default_settings)

# Runtime
if __name__ == "__main__":
    App()