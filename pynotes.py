import subprocess
import os
import platform
import configparser
import logging
import datetime
import argparse

class PyNotes:
    def __init__(self, config_path="~/.pynotes.ini"):
        self.config_path = config_path
        self.config = self.load_config()
        self.platform = platform.system()

        config_core = self.config.get("CORE", {})
        self.editor = config_core.get("default_editor") or self.get_default_editor()
        self.note_directory = config_core.get("note_directory") or "~/notes"
        self.default_extension = config_core.get("default_extension") or ".md"

        config_git = self.config.get("GIT", {})
        self.use_git = config_git.get("use_git", False)
        self.auto_push = config_git.get("auto_push", False)

        self.create_directory()


    def load_config(self):
        if not os.path.exists(os.path.expanduser(self.config_path)):
            logging.error("Config File Not Found\nUsing Defaults")
            return {}
        try:
            parser = configparser.ConfigParser()
            config_dict = {}
            parser.read(os.path.expanduser(self.config_path))
            for section in parser.sections():
                config_dict[section] = dict(parser.items(section))
            return config_dict
        except configparser.Error as e:
            logging.error(f"Error reading config file: {str(e)}\nUsing Defaults")
            return {}


    def create_directory(self):
        path = os.path.expanduser(self.note_directory)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            logging.error(f"Could not create notes directory\nError: {str(e)}")


    def get_default_editor(self):
        logging.info("Setting Default Editor")
        if self.platform == "Windows":
            editor = "notepad.exe"
        else:
            editor = os.environ.get("EDITOR", None)
            if not editor:
                command = ["which", "nano"]
                try:
                    subprocess.run(command, check=True, capture_output=True)
                    editor = "nano"
                except subprocess.CalledProcessError:
                    editor = "vim"
        logging.info(f"Using {editor} as default editor")
        return editor


    def _git_sync(self):
        if not self.use_git:
            logging.warning("Git Disabled")
            return
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        working_directory = os.path.expanduser(self.note_directory)
        try:
            subprocess.run(["git", "add", "."], check=True, cwd=working_directory)
            subprocess.run(["git", "commit", "-m", f"PyNote Update: {now}"], check=True, cwd=working_directory)
            logging.info("Git Sync Complete")
            if self.auto_push:
                subprocess.run(["git", "push", "-u", "origin"], check=True, cwd=working_directory)
        
        except subprocess.CalledProcessError as e:
            logging.error(f"Could Not Sync Git Repo\nError: {str(e)}")


    def _open_note(self, note_name: str) -> bool:
        if not note_name:
            logging.error("No Note Name Specified")
            exit(1)
        note_path = os.path.join(os.path.expanduser(self.note_directory), f"{note_name}{self.default_extension}")
        try:
            subprocess.run([self.editor, note_path], check=True)
            self._git_sync()
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Error when creating daily note\nError: {str(e)}")
            return False


    def daily_note(self) -> bool:
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        return self._open_note(today)

    def new_note(self, note_name: str="New_Note") -> bool:
        return self._open_note(note_name)

    def edit_note(self, note_name: str) -> bool:
        if not note_name:
            logging.error("No Note Name Specified")
            exit(1)
        if os.path.exists(
            os.path.join(os.path.expanduser(self.note_directory), f"{note_name}{self.default_extension}")
        ):
            return self._open_note(note_name)
        else:
            logging.warning(f"Note: `{note_name}{self.default_extension} does not exist")
            return False


    def get_argparser(self):
        description = "A Simple utility designed to make note taking in the terminal easy"
