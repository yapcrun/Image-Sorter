# Image Sorter

A simple cross-platform PyQt6-based GUI tool to quickly sort images from a source directory into predefined category folders using buttons or keyboard shortcuts.

## Features

- Displays images from a source directory one by one.
- Assign images to categories with a single button click or hotkey.
- Skip images with a dedicated button or hotkey.
- Customizable source, target directories, and hotkeys.
- Supports common image formats: PNG, JPG, JPEG, BMP, GIF, WEBP.

## Usage

1. **Set Source and Target Directories**

   Edit the following variables at the top of [`sorter.py`](sorter.py):

   ```python
   SOURCE_DIR = "C:/users/lain/Pictures"

   PREDEFINED_DIRS = {
       "Category 1": r"/path/to/target/category1",
       "Category 2": r"/path/to/target/category2",
       "Category 3": r"/path/to/target/category3",
       "Category 4": r"/path/to/target/category4"
   }

2. **Define the hotkeys for each category**

Hotkey names **must** match category names!

```python
CATEGORY_HOTKEYS = {
    "Category 1": "1",
    "Category 2": "2",
    "Category 3": "3",
    "Category 4": "4"
}
```

3. **Run the Application**
```bash
python path/to/Image-Sorter/sorter.py
```

## Requirements

**PIP**
```bash
pip install PyQt6
```