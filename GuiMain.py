import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QWidget
from PyQt6.QtGui import QIcon

# 定义窗口的宽度和高度
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class InputButtonWidget(QWidget):
    def __init__(self, parent=None, input_x=100, input_y=100, input_width=400, input_height=35, button_jiange=50):
        super().__init__(parent)
        self.input_x = input_x
        self.input_y = input_y
        self.input_width = input_width
        self.input_height = input_height
        self.button_jiange = button_jiange
        self._setup_ui()

    def _setup_ui(self):
        self._create_input_box()
        self._create_search_button()

    def _create_input_box(self):
        self.input_box = QLineEdit(self)
        self.input_box.setGeometry(self.input_x, self.input_y, self.input_width, self.input_height)

    def _create_search_button(self):
        button_x = self.input_x + self.input_width + self.button_jiange
        button_y = self.input_y
        button_width = self.input_height  # 假设按钮宽度与输入框高度相同
        button_height = self.input_height
        self.search_button = QPushButton("搜索", self)
        self.search_button.setGeometry(button_x, button_y, button_width, button_height)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("双面的影视爬虫")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)  # 设置窗口的位置和大小
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)  # 禁止窗口大小调整
        self.setWindowIcon(QIcon("static/icon/shuangmian.ico"))  # 设置窗口图标

        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建输入框和按钮组件
        self.input_button_widget = InputButtonWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
