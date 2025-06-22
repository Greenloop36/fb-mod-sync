"""

    Project File System
    @gl36

    20/06/2025

"""

# Imports
import os
import sys
import io
import typing

import usersettings
import json
import yaml

# Classes
class SettingsHelper:
    def __init__(self, app_id: str, default_settings: dict[str, any]):
        self.settings = usersettings.Settings(app_id)

        for key, value in default_settings.items():
            self.settings.add_setting(key, type(value), default=value)
        
        self.settings.load_settings()
    
    def get_setting(self, key: str) -> any:
        return self.settings[key]
    
    def set_setting(self, key: str, value: any, auto_save: bool = True):
        self.settings[key] = value

        if auto_save:
            self.save()
    
    def save(self):
        self.settings.save_settings()

class FileSystem:
    def __init__(self, app_path: str):
        self.app_path: str = app_path
        self.base_path: str = None

        if getattr(sys, "frozen", False):
            # Running in a .exe
            self.base_path = sys._MEIPASS
        else:
            # Running a regular script
            self.base_path = os.path.dirname(os.path.abspath(app_path))
    
    def get_path(self, relative_path: str) -> str:
        return os.path.join(self.base_path, relative_path)
    
    def get_resource(self, path: str, path_is_relative: bool = True) -> io.TextIOWrapper:
        if path_is_relative:
            path = self.get_path(path)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f'Unknown path {path}')
        
        return open(path, "r")

    def read_resource(self, path: str, file_type: typing.Literal["yaml", "json"] | None = None) -> str | dict:
        file = self.get_resource(path, True)

        if file_type == "json":
            return json.loads(file.read())
        elif file_type == "yaml":
            return yaml.safe_load(file)
        else:
            return file.read()