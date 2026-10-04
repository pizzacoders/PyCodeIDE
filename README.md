# PyCodeIDE

PyCodeIDE is a lightweight desktop editor for Python and text files, built with Python and PyQt5.

## Features

- Create a project folder or open an existing folder.
- Browse top-level `.py`, `.txt`, and `.md` files.
- Open files in tabs, create Python files, and delete files from the project.
- Save the current file with **Ctrl+S** or save all open files with **Ctrl+Shift+S**.
- Randomize the editor theme. The selected theme is saved in `Configs/interface.cfg`.

## Requirements

- Python 3
- PyQt5

## Run from source

1. Clone this repository and open a terminal in the project directory.
2. Install PyQt5:

   ```bash
   python -m pip install PyQt5
   ```

3. Start the editor:

   ```bash
   python main.py
   ```

When the launcher opens, choose **Create New Project** or **Open Existing Project**.

## Using the editor

Double-click a file in the Explorer to open it. Use **New File** to create a Python file, and **Delete File** to remove the selected file. Save changes from the **File** menu or with the shortcuts above.

PyCodeIDE currently provides a basic text editing area; it does not include syntax highlighting or a code execution/debugging interface.
