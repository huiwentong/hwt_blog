"""Common stylesheet for the dark hacker theme."""
DARK_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #0a0a0f;
    color: #d1d5db;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}

QTabWidget::pane {
    background-color: #0f0f1a;
    border: 1px solid #2d2d50;
    border-top: none;
    border-radius: 0 0 6px 6px;
}

QTabBar::tab {
    background-color: #1a1a2e;
    color: #9ca3af;
    border: 1px solid #2d2d50;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    padding: 8px 20px;
    margin-right: 2px;
    font-size: 13px;
    font-weight: bold;
}
QTabBar::tab:selected {
    background-color: #0f0f1a;
    color: #00ff41;
    border-color: #00cc33;
}
QTabBar::tab:hover:!selected {
    background-color: #252540;
    color: #e5e7eb;
}

QLabel {
    color: #d1d5db;
    font-size: 13px;
}
QLabel[cssClass="heading"] {
    color: #00ff41;
    font-size: 16px;
    font-weight: bold;
}
QLabel[cssClass="error"] {
    color: #ff1744;
    font-size: 12px;
}
QLabel[cssClass="warning"] {
    color: #ffab00;
    font-size: 12px;
}
QLabel[cssClass="success"] {
    color: #00ff41;
    font-size: 12px;
}
QLabel[cssClass="hint"] {
    color: #6b7280;
    font-size: 11px;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1a1a2e;
    color: #e5e7eb;
    border: 1px solid #2d2d50;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    selection-background-color: #00ff41;
    selection-color: #0a0a0f;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #00cc33;
}

QComboBox {
    background-color: #1a1a2e;
    color: #e5e7eb;
    border: 1px solid #2d2d50;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
}
QComboBox:focus {
    border-color: #00cc33;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #1a1a2e;
    color: #e5e7eb;
    selection-background-color: #00cc33;
    selection-color: #0a0a0f;
    border: 1px solid #2d2d50;
}

QPushButton {
    background-color: #1a1a2e;
    color: #00ff41;
    border: 1px solid #2d2d50;
    border-radius: 4px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #252540;
    border-color: #00cc33;
}
QPushButton:pressed {
    background-color: #00cc33;
    color: #0a0a0f;
}
QPushButton[cssClass="primary"] {
    background-color: #00cc33;
    color: #0a0a0f;
    border-color: #00ff41;
}
QPushButton[cssClass="primary"]:hover {
    background-color: #00ff41;
}

QGroupBox {
    border: 1px solid #2d2d50;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
    color: #00ff41;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

QTableWidget {
    background-color: #0f0f1a;
    color: #d1d5db;
    border: 1px solid #2d2d50;
    border-radius: 4px;
    gridline-color: #252540;
    selection-background-color: #252540;
    selection-color: #00ff41;
}
QTableWidget::item {
    padding: 4px 8px;
}
QHeaderView::section {
    background-color: #1a1a2e;
    color: #00ff41;
    border: 1px solid #2d2d50;
    padding: 6px;
    font-weight: bold;
}

QScrollBar:vertical {
    width: 8px;
    background: #0a0a0f;
}
QScrollBar::handle:vertical {
    background: #2d2d50;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #00cc33;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QStatusBar {
    background-color: #0a0a0f;
    color: #6b7280;
    border-top: 1px solid #2d2d50;
    font-size: 12px;
}
"""