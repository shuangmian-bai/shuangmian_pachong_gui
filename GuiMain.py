import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel
from PyQt6.QtGui import QIcon, QPalette, QColor
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QRadioButton

class InputButtonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
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
        # 常量定义
        BASE_URL = 'https://www.bnjxjd.com'
        SEARCH_URL = f'{BASE_URL}/vodsearch.html'
        cache = SEARCH_URL.replace('.html', '')
        SEARCH_PAGE_URL_TEMPLATE = f'{cache}/page/{{}}/wd/{{}}.html'

        data_api = SEARCH_PAGE_URL_TEMPLATE.format(1, self.input_box.text())
        req = requests.get(data_api, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(req.text, 'html.parser')

        # 提取最大页码
        try:
            page = soup.select('body > div:nth-child(1) > div > div > div.stui-pannel__ft > ul > li:nth-child(7) > a')[0]
            page = page.get('href')
            page = page.split('/')[3]
            max_pages = int(page)
        except (IndexError, ValueError):
            max_pages = 1  # 如果无法提取页码，默认为1

        soup = soup.select('body > div:nth-child(1) > div > div > div.stui-pannel__bd.clearfix > ul')[0].select('li')

        datas = {}
        for i in soup:
            ti = i.select_one('.stui-vodlist__thumb.lazyload').get('title')
            path = BASE_URL + i.select_one('a').get('href')
            ty = i.select('.pic-text1.text-right')[0].text
            ji = i.select('.pic-text.text-right')[0].text
            # yy = i.select('.text.text-overflow.text-muted.hidden-xs')[0].text

            text = f'{ti}__{ty}__{ji}'
            print(text)
            datas[text] = path

        # 更新MainWindow中的datas变量
        self.main_window.datas = datas
        # 更新MainWindow中的最大页码
        self.main_window.update_max_pages(max_pages)

class SubWindow(QWidget):
    def __init__(self, parent=None, options=None):
        super().__init__(parent)
        self.options = options if options is not None else []
        self.init_ui()

    def init_ui(self):
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(220, 220, 220))
        self.setPalette(palette)

        # 设置固定大小
        self.setFixedSize(900, 400)  # 根据需要调整宽度和高度

        # 创建单选框
        self.radio_buttons = []
        layout = QVBoxLayout()
        for option in self.options:
            radio_button = QRadioButton(option, self)
            layout.addWidget(radio_button)
            self.radio_buttons.append(radio_button)

        self.setLayout(layout)

    def update_options(self, options):
        # 清空现有的单选框
        for radio_button in self.radio_buttons:
            radio_button.deleteLater()
        self.radio_buttons.clear()

        # 创建新的单选框
        layout = self.layout()
        for option in options:
            radio_button = QRadioButton(option, self)
            layout.addWidget(radio_button)
            self.radio_buttons.append(radio_button)



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
        self.datas = {}  # 初始化全局datas变量
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

    def update_max_pages(self, max_pages):
        self.pager_widget.set_max_pages(max_pages)
        # 提取 datas 中的 text 内容
        options = [text for text in self.datas.keys()]
        # 更新 SubWindow 的选项
        self.sub_window.update_options(options)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
