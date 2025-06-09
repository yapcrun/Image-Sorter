import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow, QFileDialog, QDialog, QTableWidget, QTableWidgetItem
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Set your source directory and predefined target directories here
SOURCE_DIR = r"/path/to/source/directory"

# Feel free to change category names (must also be changed in hotkeys below)
PREDEFINED_DIRS = {
    "Category 1": r"/path/to/target/category1",
    "Category 2": r"/path/to/target/category2",
    "Category 3": r"/path/to/target/category3",
    "Category 4": r"/path/to/target/category4"
}
# Define hotkeys for each category (must match PREDEFINED_DIRS order)
CATEGORY_HOTKEYS = {
    "Category 1": "1",
    "Category 2": "2",
    "Category 3": "3",
    "Category 4": "4"
}
SKIP_KEY = "s"  # Key to skip the current image
UNDO_KEY = "z"  # key to undo last sorting operation

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")


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
        for row, (src, dst) in enumerate(history):
            self.table.setItem(row, 0, QTableWidgetItem(src))
            self.table.setItem(row, 1, QTableWidgetItem(dst))
        self.table.resizeColumnsToContents()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Sorter")
        self.image_files = self.get_image_files(SOURCE_DIR)
        self.current_index = 0
        self.history = []  # To store (src, dst) tuples for undo & display

        # Widgets
        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.path_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttons_layout = QHBoxLayout()
        self.category_buttons = []

        # Add buttons for each predefined directory with hotkeys
        for label, target_dir in PREDEFINED_DIRS.items():
            hotkey = CATEGORY_HOTKEYS.get(label, "")
            btn_text = f"{label} ({hotkey})" if hotkey else label
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, d=target_dir: self.move_and_next(d))
            self.buttons_layout.addWidget(btn)
            self.category_buttons.append((btn, hotkey, target_dir))

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

        self.load_image()

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

    def move_and_next(self, target_dir):
        if self.current_index < len(self.image_files):
            src = self.image_files[self.current_index]
            dst = os.path.join(target_dir, os.path.basename(src))
            shutil.move(src, dst)
            self.history.append((src, dst))  # Save for undo
            self.current_index += 1
            self.load_image()
            self.update_history_window()

    def undo_last(self):
        if not self.history:
            return
        src, dst = self.history.pop()
        if os.path.exists(dst):
            shutil.move(dst, src)
            # After undo, show the undone image again
            self.current_index = max(0, self.current_index - 1)
            self.image_files.insert(self.current_index, src)
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