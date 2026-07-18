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
from app.cos.cos_client import CosClient

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

        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("链接 URL（可选，点击浏览选择文件自动转换）")
        self.url_browse_btn = QPushButton("浏览…")
        self.url_browse_btn.clicked.connect(self._browse_url)
        url_row.addWidget(self.url_input, 1)
        url_row.addWidget(self.url_browse_btn)

        cover_row = QHBoxLayout()
        self.cover_input = QLineEdit()
        self.cover_input.setPlaceholderText("封面图片 URL（可选，点击浏览选择文件自动转换）")
        self.cover_browse_btn = QPushButton("浏览…")
        self.cover_browse_btn.clicked.connect(self._browse_cover)
        cover_row.addWidget(self.cover_input, 1)
        cover_row.addWidget(self.cover_browse_btn)

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
        form_layout.addLayout(url_row)
        form_layout.addLayout(cover_row)

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
                    self.db.signal_sync()
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
            self.db.signal_sync()
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

    def _local_path_to_url(self, file_path: str) -> str:
        """Convert a local Windows drive path to the public server URL.

        Images, music, and video files are uploaded to Tencent Cloud COS,
        and the COS URL is returned. Other files fall back to local server mapping.
        """
        import os
        from urllib.parse import quote

        ext = os.path.splitext(file_path)[1].lower()
        media_extensions = {".mp3", ".wav", ".flac", ".mp4", ".mkv", ".avi",
                           ".mov", ".webm", ".jpg", ".jpeg", ".png", ".gif", ".webp"}

        if ext in media_extensions and os.path.isfile(file_path):
            cos_url = self._upload_to_cos(file_path)
            if cos_url:
                return cos_url

        # Fallback: original local server URL logic
        drive = os.path.splitdrive(file_path)[0].upper()
        rel = file_path[len(drive):].lstrip("\\/").replace("\\", "/")
        segments = [quote(s, safe="") for s in rel.split("/")]
        encoded_path = "/".join(segments)
        mapping = {
            "P:":  ("music",    f"https://62.234.134.129/music/{encoded_path}"),
            "X:":  ("movies",   f"https://62.234.134.129/movies/{encoded_path}"),
            "V:":  ("pictures", f"https://62.234.134.129/pictures/{encoded_path}"),
        }
        if drive in mapping:
            return mapping[drive][1]
        return quote(file_path.replace("\\", "/"), safe="/")

    def _upload_to_cos(self, file_path: str) -> str | None:
        """Upload a local file to Tencent Cloud COS and return its public URL.

        Args:
            file_path: 本地文件路径

        Returns:
            COS 公开访问 URL，上传失败则返回 None
        """
        import os
        try:
            cos = CosClient.from_config()
            base_name = os.path.basename(file_path)
            # Determine media subfolder from file extension
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
            result = cos.upload_file(file_path, cos_key)
            if result.success:
                return cos.get_file_url(cos_key)
            else:
                print(f"COS upload failed: {result.message}")
                return None
        except Exception as e:
            print(f"COS upload error: {e}")
            return None

    def _create_thumbnail(self, file_path: str, max_size: int = 400) -> str | None:
        """Generate a thumbnail image next to the original file. Returns thumbnail path or None."""
        from PySide6.QtGui import QImage
        import os
        # Only create thumbnails for image files
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
            return None
        img = QImage(file_path)
        if img.isNull():
            return None
        thumb = img.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        thumb_path = os.path.splitext(file_path)[0] + "_thumb.jpg"
        if not thumb.save(thumb_path, "JPEG", quality=85):
            return None
        return thumb_path

    def _browse_url(self):
        """Open file dialog for media and auto-fill URL + type."""
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择媒体文件", "",
            "所有媒体 (*.mp3 *.wav *.flac *.mp4 *.mkv *.avi *.mov *.jpg *.jpeg *.png *.gif *.webp);;所有文件 (*)",
        )
        if not file_path:
            return

        url = self._local_path_to_url(file_path)
        self.url_input.setText(url)

        # Auto-detect media type from drive letter
        import os
        drive = os.path.splitdrive(file_path)[0].upper()
        drive_type_map = {"P:": "music", "X:": "movie", "V:": "photo"}
        if drive in drive_type_map:
            detected = drive_type_map[drive]
            for i in range(self.type_combo.count()):
                if self.type_combo.itemData(i) == detected:
                    self.type_combo.setCurrentIndex(i)
                    break

        # Auto-fill title from filename
        base = os.path.splitext(os.path.basename(file_path))[0]
        if not self.title_input.text():
            self.title_input.setText(base)

        # Auto-generate thumbnail for image files and fill cover field
        thumb_path = self._create_thumbnail(file_path, 400)
        if thumb_path:
            cover_url = self._local_path_to_url(thumb_path)
            self.cover_input.setText(cover_url)

        # Auto-generate compressed preview + thumbnail for video files (any type)
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".mp4", ".mkv", ".avi", ".mov", ".webm"):
            import subprocess

            # 1. Compressed preview (muted, low-res)
            preview_path = os.path.splitext(file_path)[0] + "_preview" + ext
            if not os.path.exists(preview_path):
                try:
                    subprocess.run(
                        ["ffmpeg", "-i", file_path,
                         "-vf", "scale=480:-2",
                         "-c:v", "libx264", "-preset", "fast",
                         "-crf", "35", "-an",
                         "-y", preview_path],
                        capture_output=True, timeout=120, check=True,
                    )
                except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    pass  # ffmpeg not available or encode failed — skip gracefully

            # 2. Thumbnail frame (first frame as cover image)
            thumb_path = os.path.splitext(file_path)[0] + "_thumb.jpg"
            if not os.path.exists(thumb_path):
                try:
                    subprocess.run(
                        ["ffmpeg", "-i", file_path,
                         "-vframes", "1",
                         "-vf", "scale=400:-2",
                         "-y", thumb_path],
                        capture_output=True, timeout=30, check=True,
                    )
                    thumb_url = self._local_path_to_url(thumb_path)
                    self.cover_input.setText(thumb_url)
                except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    pass  # skip gracefully

    def _browse_cover(self):
        """Open file dialog for cover image."""
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择封面图片", "",
            "图片 (*.jpg *.jpeg *.png *.gif *.webp *.bmp);;所有文件 (*)",
        )
        if not file_path:
            return

        url = self._local_path_to_url(file_path)
        self.cover_input.setText(url)

        # Auto-generate thumbnail for selected cover image
        thumb_path = self._create_thumbnail(file_path, 400)
        if thumb_path:
            thumb_url = self._local_path_to_url(thumb_path)
            self.cover_input.setText(thumb_url)

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