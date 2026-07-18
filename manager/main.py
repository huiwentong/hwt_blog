"""HWT BLOG Manager — 管理后端系统入口。"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    # Fill screen height, keep original width
    from PySide6.QtGui import QScreen
    screen = QApplication.primaryScreen()
    if screen:
        screen_geom = screen.availableGeometry()
        window.resize(window.width(), screen_geom.height())
        window.move(screen_geom.x(), screen_geom.y())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()