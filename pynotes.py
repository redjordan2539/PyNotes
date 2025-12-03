#!/usr/bin/env python3
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
        self.config = self._load_config()
        self.platform = platform.system()

        config_core = self.config.get("CORE", {})
        self.editor = config_core.get("default_editor") or self._get_default_editor()
        self.note_directory = config_core.get("note_directory") or "~/notes"
        self.default_extension = config_core.get("default_extension") or ".md"

        config_git = self.config.get("GIT", {})
        self.use_git = config_git.get("use_git", False)
        self.auto_push = config_git.get("auto_push", False)

        self.parser = self._get_argparser()

        self._create_directory()


    def _load_config(self):
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


    def _create_directory(self):
        path = os.path.expanduser(self.note_directory)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            logging.error(f"Could not create notes directory\nError: {str(e)}")


    def _get_default_editor(self):
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
        if str(self.use_git).lower() == "false":
            logging.warning("Git Disabled")
            return
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        working_directory = os.path.expanduser(self.note_directory)
        try:
            subprocess.run(["git", "add", "."], check=True, cwd=working_directory)
            subprocess.run(
                ["git", "commit", "-m", f"PyNote Update: {now}"], 
                check=True, 
                cwd=working_directory,
                capture_output=True,
                text=True
                )
            logging.info("Git Sync Complete")
            if str(self.auto_push).lower() == "true":
                subprocess.run(
                    ["git", "push", "-u", "origin"], 
                    check=True, 
                    cwd=working_directory,
                    capture_output=True,
                    text=True
                    )
        
        except subprocess.CalledProcessError as e:
            output = (e.stdout or "") + (e.stderr or "")

            if "nothing to commit" in output:
                logging.info("No Changes to Commit")
            else:
                logging.error(f"Could Not Sync Git Repo\nError: {output}")

    def _get_argparser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="PyNotes",
            description="A Simple utility designed to make note taking in the terminal easy",
            formatter_class=argparse.RawTextHelpFormatter
            )

        subparser = parser.add_subparsers(dest="command", required=True)

        daily_parser = subparser.add_parser("daily", help="Creates or Opens today's daily note")
        daily_parser.set_defaults(func=self.daily_note)

        new_parser = subparser.add_parser("new", help="Create a new note")
        new_parser.add_argument(
            "note_name", 
            nargs="?", 
            default="New_Note", 
            type=str, 
            help="Name of the new note. Defaults to New_Note"
            )
        new_parser.set_defaults(func=self.new_note)

        edit_parser = subparser.add_parser("edit", help="Edit existing note")
        edit_parser.add_argument(
            "note_name",
            type=str,
            help="[Required] Name of note to edit"
        )
        edit_parser.set_defaults(func=self.edit_note)


        return parser
    
    def run(self):
        print("run")
        args = self.parser.parse_args()
        args.func(args)
        
    @staticmethod
    def _get_safe_path(base_dir, filename):
        base_dir = os.path.abspath(os.path.expanduser(base_dir))
        path = os.path.join(base_dir, filename)

        target_path = os.path.abspath(path)

        if os.path.commonpath([base_dir, target_path]) == base_dir:
            return target_path
        
        raise ValueError(f"Error: {filename} is outside of notes directory\nUnable to write outside notes directory")

    def _open_note(self, note_name: str) -> bool:
        if not note_name:
            logging.error("No Note Name Specified")
            exit(1)
        try:
            if not note_name.endswith(self.default_extension):
                note_name += self.default_extension
            note_path = self._get_safe_path(self.note_directory, note_name)
            subprocess.run([self.editor, note_path], check=True)
            self._git_sync()
            return True
        except ValueError as e:
            logging.error(str(e))
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"Error when creating daily note\nError: {str(e)}")
            return False


    def daily_note(self, args) -> bool:
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        return self._open_note(today)

    def new_note(self, args) -> bool:
        return self._open_note(args.note_name)

    def edit_note(self, args) -> bool:
        note_name = args.note_name
        if not note_name.endswith(self.default_extension):
                note_name += self.default_extension
        if not note_name:
            logging.error("No Note Name Specified")
            exit(1)
        if os.path.exists(
            os.path.join(os.path.expanduser(self.note_directory), f"{note_name}")
        ):
            return self._open_note(note_name)
        else:
            logging.warning(f"Note: `{note_name} does not exist")
            return False


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    app = PyNotes()
    app.run()

if __name__ == "__main__":
    main()
