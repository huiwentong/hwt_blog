"""Tool management tab."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QMessageBox, QMenu,
)
from PySide6.QtCore import Qt

from app.validation import validate_tool
from app.db_manager import DbManager

TOOL_CATEGORIES = ["utility", "developer", "design", "database", "network"]
ICONS = ["🔧", "📝", "📸", "🎨", "📋", "🗄️", "🌐", "⚙️", "🛠️", "🧰"]


class ToolTab(QWidget):
    def __init__(self, db_manager: DbManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._setup_ui()
        self._refresh_table()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        form_group = QGroupBox("🔧  添加新工具")
        form_layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("工具名称（必填）")

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("工具描述（必填）")
        self.desc_input.setMaximumHeight(80)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("工具链接 URL（必填）")

        row = QHBoxLayout()
        row.addWidget(QLabel("图标:"))
        self.icon_combo = QComboBox()
        self.icon_combo.addItems(ICONS)
        row.addWidget(self.icon_combo)
        row.addSpacing(20)
        row.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(TOOL_CATEGORIES)
        row.addWidget(self.category_combo)
        row.addStretch()
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("描述:"))
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(self.url_input)
        form_layout.addLayout(row)

        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        form_layout.addWidget(self.feedback_label)

        btn_row = QHBoxLayout()
        self.submit_btn = QPushButton("$ 提交工具")
        self.submit_btn.setProperty("cssClass", "primary")
        self.submit_btn.clicked.connect(self._submit)
        self.clear_btn = QPushButton("清空表单")
        self.clear_btn.clicked.connect(self._clear_form)
        btn_row.addStretch()
        btn_row.addWidget(self.clear_btn)
        btn_row.addWidget(self.submit_btn)
        form_layout.addLayout(btn_row)
        form_group.setLayout(form_layout)

        table_group = QGroupBox("📋  已有工具（右键删除）")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "名称", "分类", "图标", "链接"])
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
        name_item = self.table.item(row, 1)
        name = name_item.text() if name_item else ""

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #1a1a2e; color: #d1d5db;
                    border: 1px solid #ff1744; border-radius: 4px; padding: 4px; }
            QMenu::item { padding: 6px 24px; border-radius: 2px; }
            QMenu::item:selected { background-color: #ff1744; color: #ffffff; }
        """)
        delete_action = menu.addAction("❌ 删除工具")
        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == delete_action:
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除工具 \"{name}\" (ID: {record_id}) 吗？\n此操作不可撤销。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    self.db.delete_tool(record_id)
                    self.db.signal_sync()
                    self._refresh_table()
                    QMessageBox.information(self, "完成", "工具已删除。")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"删除失败: {e}")

    def _submit(self):
        name = self.name_input.text()
        desc = self.desc_input.toPlainText()
        url = self.url_input.text()
        category = self.category_combo.currentText()
        icon = self.icon_combo.currentText()

        result = validate_tool(name, desc, url, category)

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
            self.db.add_tool(name, desc, url, category, icon)
            self.db.signal_sync()
            parts.append("<span style='color:#00ff41'>✓ 工具添加成功！</span>")
            self.feedback_label.setText("<br>".join(parts))
            self._clear_form()
            self._refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def _clear_form(self):
        self.name_input.clear()
        self.desc_input.clear()
        self.url_input.clear()
        self.icon_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.feedback_label.clear()

    def _refresh_table(self):
        rows = self.db.get_recent_tools()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["category"]))
            self.table.setItem(i, 3, QTableWidgetItem(row["icon"]))
            self.table.setItem(i, 4, QTableWidgetItem(row["url"]))