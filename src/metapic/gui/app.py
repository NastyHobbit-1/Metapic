from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetaPic")
        central = QWidget()
        layout = QVBoxLayout(central)
        self.pick = QPushButton("Select Folder…")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.pick)
        layout.addWidget(self.log)
        self.setCentralWidget(central)
        self.pick.clicked.connect(self.choose)

    def choose(self):
        d = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if d:
            self.log.append(f"[+] Selected: {d}")
            # TODO: wire into CLI core via a controller

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Main(); w.resize(800, 600); w.show()
    sys.exit(app.exec())
