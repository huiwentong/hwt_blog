"""Media management tab — music, photos, movies."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QMessageBox, QMenu,
)
from PySide6.QtCore import Qt

from app.validation import validate_media
from app.db_manager import DbManager

MEDIA_TYPES = [
    ("music", "♫ 音乐"),
    ("photo", "◷ 照片"),
    ("movie", "▶ 电影"),
]


class MediaTab(QWidget):
    def __init__(self, db_manager: DbManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._setup_ui()
        self._refresh_table()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        form_group = QGroupBox("🎵  添加新媒体")
        form_layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("媒体标题（必填）")

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("媒体描述（可选）")
        self.desc_input.setMaximumHeight(80)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("链接 URL（可选）")

        self.cover_input = QLineEdit()
        self.cover_input.setPlaceholderText("封面图片 URL（可选）")

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        for val, label in MEDIA_TYPES:
            self.type_combo.addItem(label, val)
        row1.addWidget(self.type_combo)
        row1.addStretch()

        form_layout.addWidget(self.title_input)
        form_layout.addLayout(row1)
        form_layout.addWidget(QLabel("描述:"))
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(self.url_input)
        form_layout.addWidget(self.cover_input)

        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        form_layout.addWidget(self.feedback_label)

        btn_row = QHBoxLayout()
        self.submit_btn = QPushButton("$ 提交媒体")
        self.submit_btn.setProperty("cssClass", "primary")
        self.submit_btn.clicked.connect(self._submit)
        self.clear_btn = QPushButton("清空表单")
        self.clear_btn.clicked.connect(self._clear_form)
        btn_row.addStretch()
        btn_row.addWidget(self.clear_btn)
        btn_row.addWidget(self.submit_btn)
        form_layout.addLayout(btn_row)
        form_group.setLayout(form_layout)

        table_group = QGroupBox("📋  已有媒体（右键删除）")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "标题", "类型", "描述", "创建时间"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        table_layout.addWidget(self.table)

        refresh_btn = QPushButton("⟳ 刷新列表")
        refresh_btn.clicked.connect(self._refresh_table)
        table_layout.addWidget(refresh_btn)
        table_group.setLayout(table_layout)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(form_group)
        splitter.addWidget(table_group)
        splitter.setSizes([300, 250])
        main_layout.addWidget(splitter)

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return
        row = item.row()
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        record_id = int(id_item.text())
        title_item = self.table.item(row, 1)
        title = title_item.text() if title_item else ""

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #1a1a2e; color: #d1d5db;
                    border: 1px solid #ff1744; border-radius: 4px; padding: 4px; }
            QMenu::item { padding: 6px 24px; border-radius: 2px; }
            QMenu::item:selected { background-color: #ff1744; color: #ffffff; }
        """)
        delete_action = menu.addAction("❌ 删除媒体")
        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == delete_action:
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除 \"{title}\" (ID: {record_id}) 吗？\n此操作不可撤销。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    self.db.delete_media(record_id)
                    self._refresh_table()
                    QMessageBox.information(self, "完成", "媒体已删除。")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"删除失败: {e}")

    def _submit(self):
        title = self.title_input.text()
        type_ = self.type_combo.currentData()
        desc = self.desc_input.toPlainText()
        url = self.url_input.text()
        cover = self.cover_input.text()

        result = validate_media(title, type_)

        parts = []
        if result.errors:
            for e in result.errors:
                parts.append(f"<span style='color:#ff1744'>✗ {e}</span>")
        if result.warnings:
            for w in result.warnings:
                parts.append(f"<span style='color:#ffab00'>⚠ {w}</span>")

        if result.errors:
            self.feedback_label.setText("<br>".join(parts))
            return

        try:
            self.db.add_media(title, type_, desc, url, cover)
            parts.append("<span style='color:#00ff41'>✓ 媒体添加成功！</span>")
            self.feedback_label.setText("<br>".join(parts))
            self._clear_form()
            self._refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def _clear_form(self):
        self.title_input.clear()
        self.desc_input.clear()
        self.url_input.clear()
        self.cover_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.feedback_label.clear()

    def _refresh_table(self):
        rows = self.db.get_recent_media()
        self.table.setRowCount(len(rows))
        type_labels = {"music": "♫ 音乐", "photo": "◷ 照片", "movie": "▶ 电影"}
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["title"]))
            t = type_labels.get(row["type"], row["type"])
            self.table.setItem(i, 2, QTableWidgetItem(t))
            self.table.setItem(i, 3, QTableWidgetItem(row.get("description", "")))
            created = row.get("created_at", "")
            if created and "T" in created:
                created = created.split(".")[0].replace("T", " ")
            self.table.setItem(i, 4, QTableWidgetItem(str(created)))