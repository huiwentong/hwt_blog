"""Article management tab."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QMessageBox, QMenu,
)
from PySide6.QtCore import Qt

from app.validation import validate_article
from app.db_manager import DbManager
from app.cos.cos_client import CosClient
import re

CATEGORIES = ["Tech", "Architecture", "Life", "Review", "General"]


class ArticleTab(QWidget):
    def __init__(self, db_manager: DbManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._setup_ui()
        self._refresh_table()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # ── Form ──
        form_group = QGroupBox("✏️  添加新文章")
        form_layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("文章标题（必填）")

        self.summary_input = QTextEdit()
        self.summary_input.setPlaceholderText("文章摘要（必填）")
        self.summary_input.setMaximumHeight(80)

        self.md_browse_btn = QPushButton("📂 选择 Markdown 文件...")
        self.md_browse_btn.clicked.connect(self._browse_md)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("文章正文 Markdown（处理后自动填入，可手动编辑）")
        self.content_input.setMinimumHeight(200)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORIES)
        row1.addWidget(self.category_combo)
        row1.addSpacing(20)
        row1.addWidget(QLabel("标签:"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("逗号分隔，如 Rust,编程,教程")
        row1.addWidget(self.tags_input, 1)
        form_layout.addWidget(self.title_input)
        form_layout.addWidget(QLabel("摘要:"))
        form_layout.addWidget(self.summary_input)
        form_layout.addLayout(row1)
        form_layout.addWidget(QLabel("正文:"))
        form_layout.addWidget(self.md_browse_btn)
        form_layout.addWidget(self.content_input)

        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        form_layout.addWidget(self.feedback_label)

        btn_row = QHBoxLayout()
        self.submit_btn = QPushButton("$ 提交文章")
        self.submit_btn.setProperty("cssClass", "primary")
        self.submit_btn.clicked.connect(self._submit)
        self.clear_btn = QPushButton("清空表单")
        self.clear_btn.clicked.connect(self._clear_form)
        btn_row.addStretch()
        btn_row.addWidget(self.clear_btn)
        btn_row.addWidget(self.submit_btn)
        form_layout.addLayout(btn_row)
        form_group.setLayout(form_layout)

        # ── Table ──
        table_group = QGroupBox("📋  最近文章（右键删除）")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "标题", "分类", "标签", "浏览量", "创建时间"])
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
        splitter.setSizes([450, 250])
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
        delete_action = menu.addAction("❌ 删除文章")
        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == delete_action:
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除文章 \"{title}\" (ID: {record_id}) 吗？\n此操作不可撤销。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    self.db.delete_article(record_id)
                    self.db.signal_sync()
                    self._refresh_table()
                    QMessageBox.information(self, "完成", "文章已删除。")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"删除失败: {e}")

    def _browse_md(self):
        """Open file dialog to select a Markdown file, process it, and fill the form."""
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Markdown 文件", "",
            "Markdown 文件 (*.md);;所有文件 (*)",
        )
        if not file_path:
            return

        self._process_md_file(file_path)

    def _process_md_file(self, md_path: str):
        """Read a Markdown file, upload local media to COS, and fill form fields."""
        import os
        from urllib.parse import urlparse, unquote

        md_dir = os.path.dirname(os.path.abspath(md_path))

        try:
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "读取失败", f"无法读取文件:\n{e}")
            return

        base = os.path.splitext(os.path.basename(md_path))[0]
        if not self.title_input.text():
            self.title_input.setText(base)

        self.feedback_label.setText(
            "<span style='color:#ffab00'>⏳ 正在扫描并上传本地媒体文件到 COS…</span>"
        )
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        processed_content = self._process_media_refs(md_content, md_dir)
        self.content_input.setPlainText(processed_content)

        self.feedback_label.setText(
            "<span style='color:#00ff41'>✅ Markdown 已处理，媒体文件已上传至 COS</span>"
        )

    MEDIA_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp",
                        ".mp4", ".mkv", ".avi", ".mov", ".webm",
                        ".mp3", ".wav", ".flac"}

    def _process_media_refs(self, md_content: str, md_dir: str) -> str:
        """Find local media references in MD content, upload to COS, and replace paths."""
        import os
        from collections import defaultdict

        replacements = {}

        # Pattern 1: Markdown images and links: [text](path) or ![alt](path)
        md_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

        # Pattern 2: HTML tags with src attribute (img, video, audio, source)
        html_src = re.compile(
            r"<(?:img|video|audio|source)\s[^>]*src\s*=\s*[\"']([^\"']+)[\"']",
            re.IGNORECASE
        )

        candidate_paths = set()

        for match in md_pattern.finditer(md_content):
            p = match.group(2).strip()
            if p and not p.startswith(("http://", "https://", "data:", "#", "mailto:")):
                candidate_paths.add(p)

        # Debug: log all HTML src matches
        html_matches = list(html_src.finditer(md_content))
        print(f"[COS DEBUG] HTML src matches found: {len(html_matches)}")
        for match in html_matches:
            p = match.group(1).strip()
            print(f"[COS DEBUG]   HTML src: {p}")
            if p and not p.startswith(("http://", "https://", "data:", "#")):
                candidate_paths.add(p)

        print(f"[COS DEBUG] Total candidates: {len(candidate_paths)}")
        for rel_path in sorted(candidate_paths):
            resolved = self._resolve_media_path(rel_path, md_dir)
            print(f"[COS DEBUG]   Candidate: {rel_path}")
            print(f"[COS DEBUG]     resolved: {resolved}")
            print(f"[COS DEBUG]     isfile: {os.path.isfile(resolved) if resolved else False}")
            if resolved and os.path.isfile(resolved):
                ext = os.path.splitext(resolved)[1].lower()
                is_media = ext in self.MEDIA_EXTENSIONS
                print(f"[COS DEBUG]     ext: {ext}, is_media: {is_media}")
                if ext in self.MEDIA_EXTENSIONS:
                    cos_url = self._upload_single_to_cos(resolved)
                    if cos_url:
                        replacements[rel_path] = cos_url

        for old_path, new_url in sorted(replacements.items(), key=lambda x: -len(x[0])):
            md_content = md_content.replace(old_path, new_url)

        return md_content

    def _resolve_media_path(self, path: str, md_dir: str) -> str | None:
        """Resolve a potentially relative media path to an absolute file path."""
        import os

        path = path.replace("\\", "/")

        if os.path.isabs(path):
            return os.path.normpath(path)

        abs_path = os.path.normpath(os.path.join(md_dir, path))
        if os.path.isfile(abs_path):
            return abs_path

        return None

    def _upload_single_to_cos(self, file_path: str) -> str | None:
        """Upload a single media file to COS and return its public URL."""
        import os
        try:
            cos = CosClient.from_config()
            base_name = os.path.basename(file_path)
            ext = os.path.splitext(base_name)[1].lower()

            image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
            music_exts = {".mp3", ".wav", ".flac"}
            video_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm"}

            if ext in music_exts:
                folder = "music"
            elif ext in video_exts:
                folder = "movies"
            else:
                folder = "pictures"

            cos_key = f"media/{folder}/{base_name}"

            # Skip upload if file already exists on COS
            if cos.file_exists(cos_key):
                print(f"COS already exists, skip upload: {cos_key}")
                return cos.get_file_url(cos_key)

            result = cos.upload_file(file_path, cos_key)
            if result.success:
                return cos.get_file_url(cos_key)
            else:
                print(f"COS upload failed: {result.message}")
                return None
        except Exception as e:
            print(f"COS upload error: {e}")
            return None

    def _submit(self):
        title = self.title_input.text()
        summary = self.summary_input.toPlainText()
        content = self.content_input.toPlainText()
        category = self.category_combo.currentText()
        tags = self.tags_input.text()

        result = validate_article(title, summary, content, category, tags)

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
            self.db.add_article(title, summary, content, category, tags)
            self.db.signal_sync()
            parts.append("<span style='color:#00ff41'>✓ 文章发布成功！</span>")
            self.feedback_label.setText("<br>".join(parts))
            self._clear_form()
            self._refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def _clear_form(self):
        self.title_input.clear()
        self.summary_input.clear()
        self.content_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.tags_input.clear()
        self.feedback_label.clear()

    def _refresh_table(self):
        rows = self.db.get_recent_articles()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["title"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["category"]))
            self.table.setItem(i, 3, QTableWidgetItem(row["tags"]))
            self.table.setItem(i, 4, QTableWidgetItem(str(row["views"])))
            created = row.get("created_at", "")
            if created and "T" in created:
                created = created.split(".")[0].replace("T", " ")
            self.table.setItem(i, 5, QTableWidgetItem(str(created)))