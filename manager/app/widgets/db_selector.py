"""Database file selector widget."""
import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QFileDialog, QLabel,
)
from PySide6.QtCore import Signal


class DbSelector(QWidget):
    """Widget to select a SQLite database file."""

    db_changed = Signal(str)  # emits the selected file path

    def __init__(self, default_path: str = "", parent=None):
        super().__init__(parent)
        self._current_path = default_path
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("📁 数据库文件:")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("选择或输入 .db 文件路径…")
        self.path_input.setText(self._current_path)
        self.path_input.textChanged.connect(self._on_path_changed)

        self.browse_btn = QPushButton("浏览…")
        self.browse_btn.clicked.connect(self._browse)

        layout.addWidget(label)
        layout.addWidget(self.path_input, 1)
        layout.addWidget(self.browse_btn)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 SQLite 数据库文件", "",
            "SQLite 数据库 (*.db);;所有文件 (*)",
        )
        if path:
            self.path_input.setText(path)

    def _on_path_changed(self, text: str):
        self._current_path = text
        self.db_changed.emit(text)

    @property
    def db_path(self) -> str:
        return self._current_path.strip()

    @db_path.setter
    def db_path(self, value: str):
        self.path_input.setText(value)