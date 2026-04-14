# Image Sorter

A simple cross-platform PyQt6 GUI tool to quickly sort images from a source directory into predefined category folders using buttons or keyboard shortcuts.

## Features

- Displays images from a source directory one by one.
- Assign, undo, and skip images with a button or hotkey.
- View sort history in a separate, non-blocking window.
- Configure source directory, category folders, and hotkeys from the app.
- Supports common image formats: PNG, JPG, JPEG, BMP, GIF, WEBP.

## Usage

1. Run the application:

```bash
python sorter.py
```

2. On first launch, choose the source directory when prompted.

3. Use the `Settings` menu to configure categories:
   - `Configure Categories` lets you add/edit category names, target directories, and hotkeys.
   - `Change Source Directory` lets you select a different source folder.

4. Images will appear one at a time. Use the category buttons or hotkeys to move images to the target folder.

## Controls

- **Category Buttons / Hotkeys:** Move the current image to the selected category.
- **Skip Button / Hotkey:** Skip the current image without moving it. Press <kbd>s</kbd>.
- **Undo Button / Shortcut:** Undo the last sort operation. Press <kbd>z</kbd>.
- **Show History:** Opens a window showing a table of recent sort operations (source and destination).

## Configuration

The app stores settings in `settings.json` in the same folder as `sorter.py`.

If the settings file is missing or invalid, the app falls back to default category placeholders.

## Requirements

- Python 3.x
- PyQt6

Install PyQt6 with:

```bash
pip install PyQt6
```
