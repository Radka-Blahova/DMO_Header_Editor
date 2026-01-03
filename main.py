"""
DMO Header Editor
-----------------

Graphical tool for parsing, validating, and rebuilding DMO measurement files.

This script serves as the application entry point.
It launches the CustomTkinter GUI (defined in gui.py),
which allows users to:
 - Select one or more .DMO files
 - Validate header and body structure
 - Generate standardized headers based on predefined rules
 - Save processed files into a selected output folder

Modules:
 - gui.py ............ Graphical interface and user interaction
 - controller.py ..... Core processing logic (validation, saving, feedback)
 - source.py ......... File parsing and header manipulation
 - validator.py ...... Validation routines for input and output data
"""

from gui import start_gui


if __name__ == "__main__":
    start_gui()
