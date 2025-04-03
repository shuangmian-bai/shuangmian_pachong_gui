import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, \
    QMessageBox, QLabel, QCheckBox
from PyQt6.QtGui import QIcon, QPalette, QColor
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QRadioButton
from PyQt6.QtCore import pyqtSignal

class InputButtonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.current_page = 1  # 添加当前页码属性
        self.init_ui()
        # 连接信号在 MainWindow 初始化 pager_widget 后进行
        # self.main_window.pager_widget.page_changed.connect(self.on_page_changed)  # 连接信号

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
        search_query = self.input_box.text()
        if not search_query:
            QMessageBox.warning(self, "输入错误", "请输入搜索关键词")
            return

        self.current_page = 1  # 重置页码
        self.fetch_and_update_data(search_query)

    def on_page_changed(self, page):
        self.current_page = page
        search_query = self.input_box.text()
        self.fetch_and_update_data(search_query)

    def fetch_and_update_data(self, search_query):
        try:
            datas, max_pages = self.fetch_data(search_query, self.current_page)
            self.main_window.datas = datas
            self.main_window.update_max_pages(max_pages)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据获取失败: {str(e)}")

    def fetch_data(self, search_query, page):
        BASE_URL = 'https://www.bnjxjd.com'
        SEARCH_URL = f'{BASE_URL}/vodsearch.html'
        cache = SEARCH_URL.replace('.html', '')
        SEARCH_PAGE_URL_TEMPLATE = f'{cache}/page/{{}}/wd/{{}}.html'

        data_api = SEARCH_PAGE_URL_TEMPLATE.format(page, search_query)
        response = requests.get(data_api, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        max_pages = self.extract_max_pages(soup)
        datas = self.extract_datas(soup, BASE_URL)
        return datas, max_pages

    def extract_max_pages(self, soup):
        try:
            page = soup.select('body > div:nth-child(1) > div > div > div.stui-pannel__ft > ul > li:nth-child(7) > a')[0]
            page = page.get('href')
            page = page.split('/')[3]
            return int(page)
        except (IndexError, ValueError):
            return 1

    def extract_datas(self, soup, base_url):
        datas = {}
        for item in soup.select('body > div:nth-child(1) > div > div > div.stui-pannel__bd.clearfix > ul > li'):
            ti = item.select_one('.stui-vodlist__thumb.lazyload').get('title')
            path = base_url + item.select_one('a').get('href')
            ty = item.select('.pic-text1.text-right')[0].text
            ji = item.select('.pic-text.text-right')[0].text

            text = f'{ti}__{ty}__{ji}'
            datas[text] = path
        return datas

class SubWindow(QWidget):
    def __init__(self, parent=None, options=None, checkbox_mode=False):
        super().__init__(parent)
        self.options = options if options is not None else []
        self.checkbox_mode = checkbox_mode
        self.init_ui()

    def init_ui(self):
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(220, 220, 220))
        self.setPalette(palette)

        self.setFixedSize(900, 400)

        self.radio_buttons = []
        self.check_boxes = []
        layout = QVBoxLayout()
        for option in self.options:
            if self.checkbox_mode:
                check_box = QCheckBox(option, self)
                layout.addWidget(check_box)
                self.check_boxes.append(check_box)
            else:
                radio_button = QRadioButton(option, self)
                layout.addWidget(radio_button)
                self.radio_buttons.append(radio_button)

        self.setLayout(layout)

    def update_options(self, options):
        for widget in self.radio_buttons + self.check_boxes:
            widget.deleteLater()
        self.radio_buttons.clear()
        self.check_boxes.clear()

        layout = self.layout()
        for option in options:
            if self.checkbox_mode:
                check_box = QCheckBox(option, self)
                layout.addWidget(check_box)
                self.check_boxes.append(check_box)
            else:
                radio_button = QRadioButton(option, self)
                layout.addWidget(radio_button)
                self.radio_buttons.append(radio_button)

    def get_selected_option(self):
        if self.checkbox_mode:
            selected_options = [check_box.text() for check_box in self.check_boxes if check_box.isChecked()]
            return selected_options
        else:
            for radio_button in self.radio_buttons:
                if radio_button.isChecked():
                    return radio_button.text()
            return None

class PagerWidget(QWidget):
    page_changed = pyqtSignal(int)  # 添加信号

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
            self.page_changed.emit(self.current_page)  # 发射信号
            print(f"上一页: 第{self.current_page}页")

    def on_next_clicked(self):
        if self.current_page < self.max_pages:
            self.current_page += 1
            self.update_page_label()
            self.page_changed.emit(self.current_page)  # 发射信号
            print(f"下一页: 第{self.current_page}页")

    def update_page_label(self):
        self.page_label.setText(f"第{self.current_page}页 共{self.max_pages}页")

    def set_max_pages(self, max_pages):
        self.max_pages = max_pages
        self.update_page_label()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.datas = {}
        self.init_ui()

    def init_ui(self):
        window_title = "双面的影视爬虫"
        window_width = 1000
        window_height = 600
        self.setWindowTitle(window_title)
        self.setFixedSize(window_width, window_height)

        icon_path = "static/icon/shuangmian.ico"
        self.setWindowIcon(QIcon(icon_path))

        container = QWidget()
        self.setCentralWidget(container)

        main_layout = QVBoxLayout()

        # 初始化 pager_widget
        self.pager_widget = PagerWidget(container, max_pages=1)
        pager_width = 200
        pager_height = 30
        pager_x = window_width - pager_width - 20
        pager_y = window_height - pager_height - 20
        self.pager_widget.setGeometry(pager_x, pager_y, pager_width, pager_height)

        # 初始化 input_button_widget 并连接信号
        self.input_button_widget = InputButtonWidget(self)
        self.input_button_widget.main_window.pager_widget.page_changed.connect(self.input_button_widget.on_page_changed)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_button_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(input_layout)

        # 初始化 sub_window，默认为单选框
        self.sub_window = SubWindow(self, checkbox_mode=False)
        sub_layout = QVBoxLayout()
        sub_layout.addWidget(self.sub_window)
        sub_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.addLayout(sub_layout)

        # 添加确定按钮
        self.confirm_button = QPushButton("确定", self)
        self.confirm_button.setFixedSize(70, 40)
        self.confirm_button.clicked.connect(self.on_confirm_clicked)  # 连接点击事件

        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(self.confirm_button)
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(confirm_layout)

        container.setLayout(main_layout)

    def update_max_pages(self, max_pages):
        self.pager_widget.set_max_pages(max_pages)
        options = [text for text in self.datas.keys()]
        self.sub_window.update_options(options)

    def on_confirm_clicked(self):
        selected_option = self.sub_window.get_selected_option()
        if selected_option:
            if isinstance(selected_option, list):
                print(f"你点击了确认按钮，选中的数据是: {selected_option}")
                for option in selected_option:
                    self.process_selected_option(option)
            else:
                print(f"你点击了确认按钮，选中的数据是: {selected_option}")
                self.datas = {selected_option: self.datas[selected_option]}
                req = requests.get(self.datas[selected_option], headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(req.text, 'html.parser')
                sj = soup.select('.stui-content__playlist.clearfix')[0].select('a')
                cache = {i.text:'https://www.bnjxjd.com'+i.get('href') for i in sj}
                self.process_selected_option(selected_option)
        else:
            QMessageBox.warning(self, "选择错误", "请选择一个选项")

    def process_selected_option(self, option):
        try:
            print(self.datas[option])
        except KeyError:
            print(f"选项 {option} 不存在于数据中")
            QMessageBox.warning(self, "错误", f"选项 {option} 不存在于数据中")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
