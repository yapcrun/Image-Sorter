import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow, QFileDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Set your source directory and predefined target directories here
SOURCE_DIR = "/home/lain/Pictures/wallpapers"
PREDEFINED_DIRS = {
    "Category 1": "/home/lain/Pictures/TEST",
    "Category 2": "/path/to/target/category2",
    "Category 3": "/path/to/target/category3",
    "Category 4": "/path/to/target/category4"
}
# Define hotkeys for each category (must match PREDEFINED_DIRS order)
CATEGORY_HOTKEYS = {
    "Category 1": "1",
    "Category 2": "2",
    "Category 3": "3",
    "Category 4": "4"
}
SKIP_KEY = "s"  # Key to skip the current image


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Sorter")
        self.image_files = self.get_image_files(SOURCE_DIR)
        self.current_index = 0

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

        # Add skip button (will be placed in its own layout below)
        skip_btn = QPushButton("Skip (S)")
        skip_btn.clicked.connect(self.skip_image)
        self.skip_btn = skip_btn  # Store reference if needed

        # Layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.image_label)
        layout.addWidget(self.path_label)
        layout.addLayout(self.buttons_layout)

        # Add skip button in its own horizontal layout under the category buttons
        skip_layout = QHBoxLayout()
        skip_layout.addStretch()
        skip_layout.addWidget(skip_btn)
        skip_layout.addStretch()
        layout.addLayout(skip_layout)

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
            self.current_index += 1
            self.load_image()

    def skip_image(self):
        if self.current_index < len(self.image_files):
            self.current_index += 1
            self.load_image()

    def keyPressEvent(self, event):
        key = event.text().lower()
        # Check category hotkeys
        for btn, hotkey, target_dir in self.category_buttons:
            if hotkey and key == hotkey.lower():
                self.move_and_next(target_dir)
                return
        # Skip hotkey
        if key == SKIP_KEY:
            self.skip_image()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())