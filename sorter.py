import os
import shutil
import json
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow, QFileDialog, QDialog, QTableWidget, QTableWidgetItem, QMessageBox, QDialogButtonBox
)
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import Qt

SETTINGS_FILE = "settings.json"

# Default settings
DEFAULT_SOURCE_DIR = ""
DEFAULT_PREDEFINED_DIRS = {
    "Category 1": "",
    "Category 2": "",
}
DEFAULT_CATEGORY_HOTKEYS = {
    "Category 1": "1",
    "Category 2": "2",
}

# Global variables to be loaded from settings
SOURCE_DIR = DEFAULT_SOURCE_DIR
PREDEFINED_DIRS = DEFAULT_PREDEFINED_DIRS.copy()
CATEGORY_HOTKEYS = DEFAULT_CATEGORY_HOTKEYS.copy()

SKIP_KEY = "s"  # Key to skip the current image
UNDO_KEY = "z"  # key to undo last sorting operation

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")


def load_settings():
    global SOURCE_DIR, PREDEFINED_DIRS, CATEGORY_HOTKEYS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
            SOURCE_DIR = data.get('source_dir', DEFAULT_SOURCE_DIR)
            PREDEFINED_DIRS = data.get('predefined_dirs', DEFAULT_PREDEFINED_DIRS.copy())
            CATEGORY_HOTKEYS = data.get('category_hotkeys', DEFAULT_CATEGORY_HOTKEYS.copy())
        except (json.JSONDecodeError, KeyError):
            # Use defaults if file is corrupted
            pass


def save_settings():
    data = {
        'source_dir': SOURCE_DIR,
        'predefined_dirs': PREDEFINED_DIRS,
        'category_hotkeys': CATEGORY_HOTKEYS
    }
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)


class CategoryConfigDialog(QDialog):
    def __init__(self, categories, hotkeys, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Categories")
        self.resize(760, 420)

        layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Category", "Target Directory", "Hotkey"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        controls = QHBoxLayout()
        add_button = QPushButton("Add Row")
        remove_button = QPushButton("Remove Selected")
        controls.addWidget(add_button)
        controls.addWidget(remove_button)
        controls.addStretch()
        layout.addLayout(controls)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)

        add_button.clicked.connect(self.add_row)
        remove_button.clicked.connect(self.remove_selected_rows)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.populate_table(categories, hotkeys)
        self.new_categories = {}
        self.new_hotkeys = {}

    def populate_table(self, categories, hotkeys):
        self.table.setRowCount(len(categories))
        for row, (label, target_dir) in enumerate(categories.items()):
            self.table.setItem(row, 0, QTableWidgetItem(label))
            self.table.setItem(row, 1, QTableWidgetItem(target_dir))
            self.table.setItem(row, 2, QTableWidgetItem(hotkeys.get(label, "")))
        self.table.resizeColumnsToContents()

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(""))
        self.table.setItem(row, 1, QTableWidgetItem(""))
        self.table.setItem(row, 2, QTableWidgetItem(""))

    def remove_selected_rows(self):
        selected_rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()}, reverse=True)
        for row in selected_rows:
            self.table.removeRow(row)

    def get_entries(self):
        entries = []
        for row in range(self.table.rowCount()):
            category_item = self.table.item(row, 0)
            target_dir_item = self.table.item(row, 1)
            hotkey_item = self.table.item(row, 2)
            category = category_item.text().strip() if category_item else ""
            target_dir = target_dir_item.text().strip() if target_dir_item else ""
            hotkey = hotkey_item.text().strip() if hotkey_item else ""
            if category or target_dir or hotkey:
                entries.append((category, target_dir, hotkey))
        return entries

    def accept(self):
        entries = self.get_entries()
        categories = {}
        hotkeys = {}
        errors = []

        for row, (category, target_dir, hotkey) in enumerate(entries, start=1):
            if not category:
                errors.append(f"Row {row}: category name is required.")
            if not target_dir:
                errors.append(f"Row {row}: target directory is required.")
            if category in categories:
                errors.append(f"Row {row}: duplicate category '{category}'.")
            if hotkey and hotkey.lower() in (existing.lower() for existing in hotkeys.values()):
                errors.append(f"Row {row}: duplicate hotkey '{hotkey}'.")
            categories[category] = target_dir
            if hotkey:
                hotkeys[category] = hotkey

        if errors:
            QMessageBox.warning(self, "Invalid Configuration", "\n".join(errors))
            return

        self.new_categories = categories
        self.new_hotkeys = hotkeys
        super().accept()


class HistoryWindow(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sort History")
        self.resize(600, 400)
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Source", "Destination"])
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.update_history(history)

    def update_history(self, history):
        self.table.setRowCount(len(history))
        for row, entry in enumerate(history):
            src, dst = entry[:2]
            self.table.setItem(row, 0, QTableWidgetItem(src))
            self.table.setItem(row, 1, QTableWidgetItem(dst))
        self.table.resizeColumnsToContents()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        load_settings()
        self.prompt_for_source_dir_if_needed()
        self.setWindowTitle("Image Sorter")
        self.image_files = self.get_image_files(SOURCE_DIR)
        self.current_index = 0
        self.history = []  # To store (src, dst, index) tuples for undo & display

        # Widgets
        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.path_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttons_layout = QHBoxLayout()
        self.category_buttons = []
        self.build_category_buttons()

        # Add skip button
        skip_btn = QPushButton(f"Skip ({SKIP_KEY})")
        skip_btn.clicked.connect(self.skip_image)
        self.skip_btn = skip_btn  # Store reference if needed

        # Add undo button
        undo_btn = QPushButton(f"Undo ({UNDO_KEY})")
        undo_btn.clicked.connect(self.undo_last)
        self.undo_btn = undo_btn

        # Add history button
        history_btn = QPushButton("Show History")
        history_btn.clicked.connect(self.show_history)
        self.history_btn = history_btn

        # Layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.image_label)
        layout.addWidget(self.path_label)
        layout.addLayout(self.buttons_layout)

        # Add skip, undo, and history buttons in their own horizontal layout under the category buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(skip_btn)
        bottom_layout.addWidget(undo_btn)
        bottom_layout.addWidget(history_btn)
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

        self.setCentralWidget(central_widget)
        self.create_menu()

        self.load_image()

    def prompt_for_source_dir_if_needed(self):
        global SOURCE_DIR
        if not SOURCE_DIR or not os.path.isdir(SOURCE_DIR):
            dir_path = QFileDialog.getExistingDirectory(self, "Select Source Directory")
            if dir_path:
                SOURCE_DIR = dir_path
                save_settings()
            else:
                QMessageBox.warning(self, "No Source Directory", "A source directory is required to run the application.")
                sys.exit(1)

    def get_image_files(self, directory):
        return [
            os.path.join(directory, f)
            for f in sorted(os.listdir(directory))
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ]

    def load_image(self):
        if self.current_index < len(self.image_files):
            image_path = self.image_files[self.current_index]
            pixmap = QPixmap(image_path)
            if pixmap.width() > 800 or pixmap.height() > 600:
                pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
            self.path_label.setText(image_path)
        else:
            self.image_label.setText("No more images.")
            self.path_label.setText("")

    def build_category_buttons(self):
        for btn, _, _ in self.category_buttons:
            self.buttons_layout.removeWidget(btn)
            btn.deleteLater()
        self.category_buttons.clear()

        for label, target_dir in PREDEFINED_DIRS.items():
            hotkey = CATEGORY_HOTKEYS.get(label, "")
            btn_text = f"{label} ({hotkey})" if hotkey else label
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, d=target_dir: self.move_and_next(d))
            self.buttons_layout.addWidget(btn)
            self.category_buttons.append((btn, hotkey, target_dir))

    def create_menu(self):
        settings_menu = self.menuBar().addMenu("Settings")
        configure_action = QAction("Configure Categories", self)
        configure_action.triggered.connect(self.open_config_dialog)
        settings_menu.addAction(configure_action)
        change_source_action = QAction("Change Source Directory", self)
        change_source_action.triggered.connect(self.change_source_dir)
        settings_menu.addAction(change_source_action)

    def open_config_dialog(self):
        dialog = CategoryConfigDialog(PREDEFINED_DIRS, CATEGORY_HOTKEYS, self)
        if dialog.exec():
            PREDEFINED_DIRS.clear()
            PREDEFINED_DIRS.update(dialog.new_categories)
            CATEGORY_HOTKEYS.clear()
            CATEGORY_HOTKEYS.update(dialog.new_hotkeys)
            self.build_category_buttons()
            self.update_history_window()
            save_settings()

    def change_source_dir(self):
        global SOURCE_DIR
        dir_path = QFileDialog.getExistingDirectory(self, "Select New Source Directory")
        if dir_path:
            SOURCE_DIR = dir_path
            save_settings()
            self.image_files = self.get_image_files(SOURCE_DIR)
            self.current_index = 0
            self.history.clear()
            self.load_image()
            self.update_history_window()

    def move_and_next(self, target_dir):
        if self.current_index < len(self.image_files):
            src = self.image_files.pop(self.current_index)
            dst = os.path.join(target_dir, os.path.basename(src))
            shutil.move(src, dst)
            self.history.append((src, dst, self.current_index))  # Save for undo
            self.load_image()
            self.update_history_window()

    def undo_last(self):
        if not self.history:
            return
        src, dst, index = self.history.pop()
        if os.path.exists(dst):
            shutil.move(dst, src)
            self.image_files.insert(index, src)
            self.current_index = index
            self.load_image()
            self.update_history_window()

    def skip_image(self):
        if self.current_index < len(self.image_files):
            self.current_index += 1
            self.load_image()

    def keyPressEvent(self, event):
        key = event.text().lower()
        # Check for Ctrl+Z (undo)
        if key == UNDO_KEY:
            self.undo_last()
            return
        # Check category hotkeys
        for btn, hotkey, target_dir in self.category_buttons:
            if hotkey and key == hotkey.lower():
                self.move_and_next(target_dir)
                return
        # Skip hotkey
        if key == SKIP_KEY:
            self.skip_image()

    def update_history_window(self):
        # Update the history window if it's open
        if hasattr(self, "history_window") and self.history_window.isVisible():
            self.history_window.update_history(self.history)

    def show_history(self):
        if not hasattr(self, "history_window") or not self.history_window.isVisible():
            self.history_window = HistoryWindow(self.history, self)
        else:
            self.history_window.update_history(self.history)
        self.history_window.show()
        self.history_window.raise_()
        self.history_window.activateWindow()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())