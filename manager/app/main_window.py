"""Main window — assembles all tabs with a server connection."""
import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QStatusBar,
)
from PySide6.QtCore import Qt

from app.db_manager import DbManager, DEFAULT_API_BASE
from app.widgets.style import DARK_STYLE
from app.widgets.article_tab import ArticleTab
from app.widgets.tool_tab import ToolTab
from app.widgets.media_tab import MediaTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HWT BLOG — 管理后端系统")
        self.setMinimumSize(1100, 800)
        self.setStyleSheet(DARK_STYLE)

        self._db_manager: DbManager | None = None

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # ── server connection row ──
        conn_row = QHBoxLayout()
        conn_row.addWidget(QLabel("服务器:"))
        self.url_input = QLineEdit(DEFAULT_API_BASE)
        self.url_input.setPlaceholderText("http://62.234.134.129:8000/api")
        conn_row.addWidget(self.url_input, 1)
        self.connect_btn = QPushButton("🔌 连接")
        self.connect_btn.clicked.connect(lambda: self._connect())
        conn_row.addWidget(self.connect_btn)
        main_layout.addLayout(conn_row)

        # ── connection status ──
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        # ── tabs ──
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)

        # ── status bar ──
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 — 请连接服务器")

        # Try default server
        self._connect(DEFAULT_API_BASE)

    def _connect(self, base_url: str | None = None):
        base_url = (base_url or self.url_input.text().strip()).rstrip("/")
        if not base_url:
            return
        try:
            self._db_manager = DbManager(base_url)
            stats = self._db_manager.get_stats()
            self.status_label.setText(
                f"<span style='color:#00ff41'>✓ 已连接: {base_url}</span>"
            )
            self.status_bar.showMessage(
                f"📊 文章: {stats['articles']}  |  "
                f"工具: {stats['tools']}  |  "
                f"媒体: {stats['media']}  |  "
                f"H5: {stats['h5_pages']}  |  "
                f"总浏览量: {stats['views']}"
            )
            self._rebuild_tabs()
        except Exception as e:
            self.status_label.setText(
                f"<span style='color:#ff1744'>✗ 连接失败: {e}</span>"
            )
            self._db_manager = None

    def _rebuild_tabs(self):
        """Recreate the tab contents with the current db_manager."""
        if not self._db_manager:
            return
        for i in range(self.tabs.count() - 1, -1, -1):
            self.tabs.removeTab(i)
        self.tabs.addTab(ArticleTab(self._db_manager), "📝 文章")
        self.tabs.addTab(ToolTab(self._db_manager), "🔧 工具")
        self.tabs.addTab(MediaTab(self._db_manager), "🎵 媒体")
