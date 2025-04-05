from PyQt6.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon  # 导入 QIcon 模块

class SearchPopup:
    def __init__(self, parent: QWidget):
        self.parent = parent
        self.popup = None

    def show_popup(self):
        # 创建并显示搜索弹窗
        self.popup = QMessageBox(self.parent)
        self.popup.setWindowTitle("搜索中...")
        self.popup.setText("正在搜索，请稍候...")
        self.popup.setStandardButtons(QMessageBox.StandardButton.NoButton)  # 不显示任何按钮

        # 设置窗口图标
        icon_path = "static/icon/shuangmian.ico"  # 图标路径
        self.popup.setWindowIcon(QIcon(icon_path))  # 设置图标

        self.popup.show()

    def close_popup(self):
        if self.popup:
            self.popup.close()

def main():
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("主窗口")
    window.setGeometry(100, 100, 300, 200)

    layout = QVBoxLayout()
    window.setLayout(layout)

    search_popup = SearchPopup(window)

    show_button = QPushButton("显示弹窗")
    show_button.clicked.connect(search_popup.show_popup)
    layout.addWidget(show_button)

    close_button = QPushButton("关闭弹窗")
    close_button.clicked.connect(search_popup.close_popup)
    layout.addWidget(close_button)

    window.show()
    app.exec()

if __name__ == "__main__":
    main()
