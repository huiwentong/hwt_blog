"""Main window — assembles all tabs with database selector."""
import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QLabel, QStatusBar, QMessageBox,
)
from PySide6.QtCore import Qt

from app.db_manager import DbManager
from app.widgets.style import DARK_STYLE
from app.widgets.db_selector import DbSelector
from app.widgets.article_tab import ArticleTab
from app.widgets.tool_tab import ToolTab
from app.widgets.media_tab import MediaTab


DEFAULT_DB = os.path.abspath('Z:/github/db/hwt_blog.db')


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

        # ── DB selector ──
        self.db_selector = DbSelector(default_path=DEFAULT_DB)
        self.db_selector.db_changed.connect(self._on_db_changed)
        main_layout.addWidget(self.db_selector)

        # ── connection status ──
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        # ── tabs ──
        self.tabs = QTabWidget()
        self.tab_article = QWidget()
        self.tab_tool = QWidget()
        self.tab_media = QWidget()
        self.tabs.addTab(self.tab_article, "📝 文章")
        self.tabs.addTab(self.tab_tool, "🔧 工具")
        self.tabs.addTab(self.tab_media, "🎵 媒体")
        main_layout.addWidget(self.tabs, 1)

        # ── status bar ──
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 — 请选择数据库文件")

        # Try default path
        if os.path.isfile(DEFAULT_DB):
            self._connect_db(DEFAULT_DB)

    def _on_db_changed(self, path: str):
        if not path:
            return
        if not os.path.isfile(path):
            self.status_label.setText(
                f"<span style='color:#ffab00'>⚠ 文件不存在: {path}</span>"
            )
            return
        self._connect_db(path)

    def _connect_db(self, path: str):
        try:
            self._db_manager = DbManager(path)
            stats = self._db_manager.get_stats()
            self.status_label.setText(
                f"<span style='color:#00ff41'>✓ 已连接: {path}</span>"
            )
            self.status_bar.showMessage(
                f"📊 文章: {stats['articles']}  |  "
                f"工具: {stats['tools']}  |  "
                f"媒体: {stats['media']}  |  "
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
        # Remove old tabs
        for i in range(self.tabs.count() - 1, -1, -1):
            self.tabs.removeTab(i)
        # Add new tabs
        self.tabs.addTab(ArticleTab(self._db_manager), "📝 文章")
        self.tabs.addTab(ToolTab(self._db_manager), "🔧 工具")
        self.tabs.addTab(MediaTab(self._db_manager), "🎵 媒体")