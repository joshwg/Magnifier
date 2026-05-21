# Desktop Magnifier

A simple desktop magnification tool that displays a real-time magnified view of the area around your mouse cursor.

## Features

- Resizable window (default 300x300 pixels)
- Adjustable magnification from 2x to 20x (default 3x)
- Real-time screen capture and display
- Easy-to-use menu interface

## Requirements

- Python 3.7+
- Pillow (PIL)
- mss

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```
2. You will need to modify the scripts to use your directory structure and not mine.

## Usage

Run the application:
```bash
python magnifier.py
```

Or use the batch file:
```bash
run.bat
```

- The window will show a magnified view of the desktop area around your mouse cursor
- Resize the window as needed by dragging the edges
- Use the "Magnification" menu to select zoom levels from 2x to 20x
- Use the "File" menu to quit the application
- The window title shows the current magnification level

## Adding to Start Menu (Windows)

To create a Start Menu shortcut:

1. Open PowerShell in the project directory
2. Run the shortcut creation script:
```powershell
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
```

This will create a "Desktop Magnifier" entry in your Start Menu that launches the application without showing a console window.

## How It Works

The application continuously captures the screen area around your mouse cursor and displays it magnified in the window. The capture area size adjusts based on the window size and magnification level to always fill the window with the magnified content.
