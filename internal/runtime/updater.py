"""

    Software Updater
    @gl36

    20/06/2025
"""

## Imports
import tkinter as tk
from tkinter import ttk, filedialog

import logging
import traceback

import requests
import sys
import os
import threading

import zipfile
import tempfile
import shutil
import io

## Types
type Result = tuple[bool, str | None]

## Class
def format_error(exception: Exception, message: str = None) -> str:
    name: str = type(exception).__name__

    if message:
        message = f'{message} '
    else:
        message = ""

    logging.error(f'{name}: {exception}\n{traceback.format_exc()}')
    return f'{message}[{name}]: {str(exception)}'

class UpdaterInterface:
    def __init__(self, title: str, update_name: str, ui_master: tk.Tk | None = None) -> None:
        # Properties
        self.ui_master = ui_master
        self.title = title
        self.update_name = update_name

        self._loop: threading.Thread = None
        self._running: bool = False
        self._text_status: str = ""
        self._progress_current: float | int = 0
        self._progress_max: float | int = 0

        # Init
        if not self.ui_master:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(self.ui_master)

        self.root.title(title)
        
        # Create UI
        self.container = ttk.Frame(self.root, padding=10)
        self.container.grid()

        self.label_title = ttk.Label(self.container, text=self.update_name, anchor="w")
        self.label_title.pack(expand=True, fill="x")

        self.label_status = ttk.Label(self.container, text="preparing...", anchor="w")
        self.label_status.pack(expand=True, fill="x")

        self.progress_bar = ttk.Progressbar(self.container, length=300)
        self.progress_bar.pack(fill="x", expand=True, pady=(20, 0))
    
    def set_status(self, text: str = ""):
        self._text_status = text
    
    def set_progress(self, current: float | int = None, max: float| int = None):
        if current != None:
            self._progress_current = current
        
        if max != None:
            self._progress_max = max
    
    def poll(self):
        self.label_status.config(text=self._text_status)
        self.progress_bar["value"] = self._progress_current
        self.progress_bar.config(maximum=self._progress_max)

        self.root.update()
    
    # def _runloop(self):
    #     while self._running:
    #         self.poll()

    # def loop_start(self):
    #     self._loop = threading.Thread(target=self._runloop)
    #     self._running = True
    #     self._loop.start()
    
    # def loop_stop(self):
    #     self._running = False
    #     self._loop.join()
    
    def destroy(self):
        if self._running:
            self.root.destroy()

class Updater:
    def __init__(self,
            author: str,
            repository: str,
            directory: str,
            update_title: str = "Software Update",
            update_name: str = "performing software update...",
            ui_master: tk.Tk = None
        ) -> None:
        
        self.author = author
        self.repository = repository
        self.dir = directory
        self.ui_master = ui_master
        self.title = update_title
        self.update_name = update_name

        self.interface: UpdaterInterface = None
        self._update_result: Result = None
    
    def update(self) -> Result:
        # Init UI
        self.interface = UpdaterInterface(self.title, self.update_name, self.ui_master)

        # Run update
        update_thread = threading.Thread(target=self._update)
        update_thread.start()

        while update_thread.is_alive():
            self.interface.poll()
        
        # update_thread.join()

        self.interface.destroy()
        return self._update_result or (False, "Unknown error")

    def _update(self) -> Result:
        # Set UI
        self.interface.set_progress(0, 3)

        # Download new archive
        self.interface.set_status("downloading archive")
        try:
            download_response = requests.get(f'https://api.github.com/repos/{self.author}/{self.repository}/zipball')
            download_response.raise_for_status()
        except Exception as e:
            self._update_result = (False, format_error(e, "Download failed!"))
            return
        
        self.interface.set_progress(1)
        
        # Install the downloaded archive in a temporary file
        # try:
        #     installed_archive = tempfile.TemporaryFile(mode="wb", suffix=".zip")
        #     installed_archive.write(download_response.content)
        # except Exception as e:
        #     interface.destroy()
        #     return False, format_error(e, "Failed to install temporary archive!")
        
        # Extract the downloaded archive
        self.interface.set_status("extracting downloaded archive")
        try:
            # Create a temporary directory to extract to
            archive_dump = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)

            # Create a temporary buffer containing the zip data
            zip_buffer = io.BytesIO(download_response.content)
            
            # Extract the file
            with zipfile.ZipFile(zip_buffer, "r") as file:
                file.extractall(archive_dump.name)
            
            # The downloaded archive is no longer required, so remove it.
            # installed_archive.close()
            # del installed_archive
        except Exception as e:
            self._update_result = (False, format_error(e, "Failed to extract the downloaded archive!"))
            return
        
        self.interface.set_progress(2)
        
        # Remove the current files
        # interface.set_status("removing current installation")
        # try:
        #     shutil.rmtree(self.dir)
        #     os.makedirs(self.dir)
        # except Exception as e:
        #     
        #     return False, format_error(e, "Failed to remove the current installation!")
        
        # interface.set_progress(3)

        # Install the extracted data
        self.interface.set_status("installing update")
        try:
            for folder in os.listdir(archive_dump.name):
                shutil.copytree(f'{archive_dump.name}\\{folder}', self.dir, dirs_exist_ok=True)
        except Exception as e:
            self._update_result = (False, format_error(e, "Failed to install new files!"))
            return
        
        self.interface.set_progress(3)
        
        # Finish the update
        self.interface.set_status("finishing software update")
        archive_dump.cleanup()
        self._update_result = (True, None)

        return True, None
    
    def get_repository_file_content(self, path: str) -> Result:
        try:
            response = requests.get(f'https://raw.githubusercontent.com/{self.author}/{self.repository}/refs/heads/main/{path}')
            response.raise_for_status()
        except Exception as e:
            return False, format_error(e, f'Failed to get file {path}! ')
        else:
            return True, response.text
        
    def is_update_available(self, current_version: str) -> Result:
        success, result = self.get_repository_file_content("internal/data/VERSION")

        if not success:
            # The request failed, so assume there isnt
            return False, None
        else:
            result = result.replace("\n", "")

            if result == current_version:
                # 
                return False, None
            else:
                # An update is available
                return True, result            