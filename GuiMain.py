import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel
from PyQt6.QtGui import QIcon, QPalette, QColor

class InputButtonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.input_box = QLineEdit(self)
        self.input_box.setFixedSize(700, 30)
        self.input_box.setPlaceholderText("请输入搜索关键词")
        self.input_box.setStyleSheet("border: 1px solid gray; border-radius: 5px;")

        self.button = QPushButton("搜  索", self)
        self.button.setFixedSize(70, 40)
        self.button.clicked.connect(self.on_button_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.input_box)
        layout.addSpacing(50)
        layout.addWidget(self.button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def on_button_clicked(self):
        print("按钮被点击了！")
        print("输入框内容:", self.input_box.text())

class SubWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(220, 220, 220))
        self.setPalette(palette)

class PagerWidget(QWidget):
    def __init__(self, parent=None, max_pages=1, button_width=30, button_height=30, button_spacing=10):
        super().__init__(parent)
        self.max_pages = max_pages
        self.current_page = 1
        self.button_width = button_width
        self.button_height = button_height
        self.button_spacing = button_spacing
        self.init_ui()

    def init_ui(self):
        self.prev_button = QPushButton("<", self)
        self.prev_button.setFixedSize(self.button_width, self.button_height)
        self.prev_button.clicked.connect(self.on_prev_clicked)

        self.page_label = QLabel(f"第{self.current_page}页 共{self.max_pages}页", self)

        self.next_button = QPushButton(">", self)
        self.next_button.setFixedSize(self.button_width, self.button_height)
        self.next_button.clicked.connect(self.on_next_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.prev_button)
        layout.addSpacing(self.button_spacing)
        layout.addWidget(self.page_label)
        layout.addSpacing(self.button_spacing)
        layout.addWidget(self.next_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def on_prev_clicked(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_page_label()
            print(f"上一页: 第{self.current_page}页")

    def on_next_clicked(self):
        if self.current_page < self.max_pages:
            self.current_page += 1
            self.update_page_label()
            print(f"下一页: 第{self.current_page}页")

    def update_page_label(self):
        self.page_label.setText(f"第{self.current_page}页 共{self.max_pages}页")

    def set_max_pages(self, max_pages):
        self.max_pages = max_pages
        self.update_page_label()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        window_title = "双面的影视爬虫"
        window_width = 1000
        window_height = 600
        self.setWindowTitle(window_title)
        self.setFixedSize(window_width, window_height)

        icon_path = "static/icon/shuangmian.ico"
        self.setWindowIcon(QIcon(icon_path))

        self.input_button_widget = InputButtonWidget(self)
        self.sub_window = SubWindow(self)

        container = QWidget()
        self.setCentralWidget(container)

        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_button_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(input_layout)

        sub_layout = QVBoxLayout()
        sub_layout.addWidget(self.sub_window)
        sub_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.addLayout(sub_layout)

        container.setLayout(main_layout)

        self.pager_widget = PagerWidget(container, max_pages=1)
        pager_width = 200
        pager_height = 30
        pager_x = window_width - pager_width - 20
        pager_y = window_height - pager_height - 20
        self.pager_widget.setGeometry(pager_x, pager_y, pager_width, pager_height)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
