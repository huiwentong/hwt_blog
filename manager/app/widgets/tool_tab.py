"""Tool management tab."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QMessageBox, QMenu,
)
from PySide6.QtCore import Qt
from app.convert_h5 import convert_h5
from app.validation import validate_tool
from app.db_manager import DbManager
import re
import os

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

        h5_row = QHBoxLayout()
        self.h5_browse_btn = QPushButton("(H5) 选择静态h5文件...")
        self.h5_browse_btn.clicked.connect(self._browse_h5)
        self.h5_status_label = QLabel("")
        h5_row.addWidget(self.h5_browse_btn)
        h5_row.addWidget(self.h5_status_label, 1)
        form_layout.addLayout(h5_row)

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

    def _slugify(self, name: str) -> str:
        s = name.lower()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"[\s_]+", "-", s)
        s = s.strip("-")
        return s if s else "h5-page"

    def _browse_h5(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择静态H5文件", "",
            "HTML 文件 (*.html *.htm);;所有文件(*.*)",
        )
        if not file_path:
            return
        try:
            try:
                html_content = convert_h5(file_path)
            except:
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                    
        except Exception as e:
            QMessageBox.critical(self, "读取失败", f"无法读取文件: {e}")
            return
        title_match = __import__("re").search(chr(60)+"title[^"+chr(62)+"]*"+chr(62)+"(.*?)"+chr(60)+"/title"+chr(62), html_content, __import__("re").IGNORECASE | __import__("re").DOTALL)
        base_name = __import__("os").path.splitext(__import__("os").path.basename(file_path))[0]
        page_title = title_match.group(1).strip() if title_match else base_name
        slug = self._slugify(base_name)
        try:
            self.db.add_h5_page(slug, html_content)
        except ValueError:
            idx = 2
            while True:
                new_slug = f"{slug}-{idx}"
                try:
                    self.db.add_h5_page(new_slug, html_content)
                    slug = new_slug
                    break
                except ValueError:
                    idx += 1
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"H5页面保存失败: {e}")
            return
        self.name_input.setText(page_title)
        self.desc_input.setPlainText(f"静态H5页面: {base_name}")
        self.url_input.setText(f"https://hwthuiwentong.com/api/tools/h5/{slug}")
        self.h5_status_label.setText(f"<span style='color:#00ff41'>H5页已保存，slug={slug}</span>")

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
        delete_action = menu.addAction("删除工具")
        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == delete_action:
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除工具 \u201c{name}\u201d (ID: {record_id}) 吗？\n此操作不可撤销。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    self.db.delete_tool(record_id)
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
        self.h5_status_label.clear()

    def _refresh_table(self):
        rows = self.db.get_recent_tools()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["category"]))
            self.table.setItem(i, 3, QTableWidgetItem(row["icon"]))
            self.table.setItem(i, 4, QTableWidgetItem(row["url"]))