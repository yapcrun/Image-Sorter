# Image Sorter

A simple cross-platform PyQt6-based GUI tool to quickly sort images from a source directory into predefined category folders using buttons or keyboard shortcuts.

## Features

- Displays images from a source directory one by one.
- Assign, undo, and skip images with a button or hotkey.
- View a sortable history of all sort operations in a separate, non-blocking window.
- Customizable source, target directories, and hotkeys.
- Supports common image formats: PNG, JPG, JPEG, BMP, GIF, WEBP.

## Usage

1.**Set Source and Target Directories**

Edit the following variables at the top of [`sorter.py`](sorter.py):

```python
SOURCE_DIR = r"/path/to/source/directory"

PREDEFINED_DIRS = {
    "Category 1": r"/path/to/target/category1",
    "Category 2": r"/path/to/target/category2",
    "Category 3": r"/path/to/target/category3",
    "Category 4": r"/path/to/target/category4"
}
```

2.**Define the hotkeys for each category**

Hotkey names **must** match category names!

```python
CATEGORY_HOTKEYS = {
    "Category 1": "1",
    "Category 2": "2",
    "Category 3": "3",
    "Category 4": "4"
}
```

3.**Run the Application**

```bash
python path/to/Image-Sorter/sorter.py
```

## Controls

- **Category Buttons / Hotkeys:** Move the current image to the selected category. Use the button or press the assigned hotkey (e.g., <kbd>1</kbd>, <kbd>2</kbd>, etc.).
- **Skip Button / Hotkey:** Skip the current image without moving it. Use the button or press <kbd>s</kbd>.
- **Undo Button / Shortcut:** Undo the last sort operation. Use the button or press <kbd>Z</kbd>.
- **Show History:** Opens a window showing a two-column table of all sort operations (source and destination).

## Requirements

### System

- Python 3.x

### Python/pip

- PyQt6

Install with:

```bash
pip install PyQt6
```
