# PyNotes
---
A simple CLI tool to help create and manage markdown based notes directly in your terminal


## Key Features
- Easily create and edit note right in your terminal
- Supports any text editor, allowing you to use your favorite
- Supports most file types for the notes
- Seamlessly integrates git

## Installation

### Recommended Method: (pipx)
The vast majority of modern linux distros will prevent changes to the global python environment.
To bypass that its recommended to use `pipx`

#### Install pipx

`Debian/Ubuntu`
```bash
sudo apt update
sudo apt install pipx
```

`Fedora`
```bash
sudo dnf install pipx
```

`Arch`
```bash
sudo pacman -Syu
sudo pacman -S python-pipx
```
#### Install pynotes

You can now install PyNotes directly from GitHub

```bash
# Install directly from GitHub
pipx install git+https://github.com/redjordan2539/PyNotes.git

# Or you can clone the project and install locally
git clone https://github.com/redjordan2539/PyNotes.git
cd pynotes
pipx install .
```
#### Ensure pipx install packages are on path
By default pipx installs packages at `~/.local/bin` which is usually not on your PATH. If after you install PyNotes with pipx you see a warning stating that your path needs to be updated simply run the below command

```bash
pipx ensurepath
```

### Manual Way:
If you are using virtual environments or prefer to modify your global python environment you can install pynotes using your regular version of pip or pip3.

```bash
# Install directly from GitHub
pip install git+https://github.com/redjordan2539/PyNotes.git
# Or you can clone the project and install locally
git clone https://github.com/redjordan2539/PyNotes.git
pip install .
```

## Setup

PyNotes allows the use of a ini file to set application settings that persist between uses.
Its recommended to take a look at the default ini file and make changes to suit your needs.
As of now the expected location for the ini file is `~/pynotes.ini`. This is subject to change in the future.

If no ini file is used, or there are errors in the file defaults will be built at runtime. These defaults are set based on your system including platform and system environment variables. They should work for most users with fairly standard setups.  

### Default ini file
Below is the default ini file. 
It has sensible defaults for most linux users.


```ini
# ===
# PyNotes Config File
# This file lets you set application values that persist between uses of PyNotes
# Lines starting with # are comments
# ===

[CORE]
# This sets the default text editor to use
# If this is not set, than your systems default text editor will be used
# Windows - Defaults to notepad.exe
# Linux/MacOS/other Unix like systems - Defaults to what is set in $EDITOR or nano if installed. If nano is
# not installed vim will be used as the default
# This can be set to any text editor in your system path
default_editor = nano

# This sets the root directory for your notes folder
# This can be any valid directory path
# ~ is supported to specify the current user's home directory
note_directory = ~/notes

# The default file type for new note files created
# This can be any file type that your editor supports
# suggested file types are .md, .txt or .org
default_extension = .md


[GIT]
# This determines if git is enabled.
# It is highly recommended to use git with PyNotes to ensure version control and data integrity
# Defaults to False if not set
# Accepted options: True, true, False, false
use_git = True

# This option determines if git push is called after editing or creating a note
# This will not work if you do not have a remote origin set or are offline when used
# If this is disabled and you use a remote origin like github, you will need to run `git push -u origin` 
# to push commits to your remote origin
# Defaults to False if not set
# Accepted options: True, true, False, false
auto_push = True
```

## Usage

### Create or edit today's daily note
```bash
pynotes daily
```
this will open your specified text editor. Once your edits are done, or you exit the editor if you have git enabled all new changes, included ones not done by pynotes, will be git added and a git commit will be generated with a generic update message.
If you have a git auto_push enabled and have a remote origin set, pynotes will try to automatically push changes to your remote

### Create a new note
```bash
pynotes new <file_name>
```
Will create a new note file with optional provided filename from the user. If no filename is provided it will default to `New_Note`.
As with the daily notes command this will perform all git operations if enabled once note is closed.

### Edit exisiting note
```bash
pynotes edit file_name
```
Edits exisiting, if it exists. Throws error is no file name is provided or if file name specified does not exist.
As with above commands this will also trigger git sync operations. 