from PyQt6.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon  # 导入 QIcon 模块

from utils import resource_path


class SearchPopup:
    def __init__(self, parent: QWidget):
        self.parent = parent
        self.popup = None

    def show_popup(self):
        # 创建并显示搜索弹窗
        if not self.popup or not self.popup.isVisible():  # 防止重复创建弹窗
            self.popup = QMessageBox(self.parent)
            self.popup.setWindowTitle("搜索中...")
            self.popup.setText("正在搜索，请稍候...")

            # 设置窗口图标
            icon_path = resource_path("static/icon/shuangmian.ico")  # 图标路径
            self.popup.setWindowIcon(QIcon(icon_path))  # 设置图标

            self.popup.show()
            print("弹窗已显示")
        else:
            print("弹窗已存在且处于显示状态")

    def close_popup(self):
        print("close_popup 方法被调用")  # 添加调试信息
        if self.popup and self.popup.isVisible():
            self.popup.close()
            print("弹窗已关闭")
        else:
            print("弹窗不存在或未显示，无法关闭")