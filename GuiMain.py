# 导入必要的库
import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, \
    QMessageBox, QLabel, QCheckBox
from PyQt6.QtGui import QIcon, QPalette, QColor
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QRadioButton
from PyQt6.QtCore import pyqtSignal

# 定义输入框和搜索按钮的组件类
class InputButtonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sj = []
        self.main_window = parent  # 父窗口引用
        self.current_page = 1  # 当前页码属性
        self.init_ui()  # 初始化UI

    def init_ui(self):
        # 创建输入框并设置样式
        self.input_box = QLineEdit(self)
        self.input_box.setFixedSize(700, 30)  # 设置固定大小
        self.input_box.setPlaceholderText("请输入搜索关键词")  # 设置占位符文本
        self.input_box.setStyleSheet("border: 1px solid gray; border-radius: 5px;")  # 设置边框样式
        self.max_pages = 1

        # 创建搜索按钮并绑定点击事件
        self.button = QPushButton("搜  索", self)
        self.button.setFixedSize(70, 40)  # 设置按钮大小
        self.button.clicked.connect(self.on_button_clicked)  # 绑定点击事件

        # 布局管理器
        layout = QHBoxLayout()
        layout.addWidget(self.input_box)  # 添加输入框到布局
        layout.addSpacing(50)  # 添加间距
        layout.addWidget(self.button)  # 添加按钮到布局
        layout.setContentsMargins(0, 0, 0, 0)  # 设置内容边距为0
        self.setLayout(layout)  # 设置布局

    # 搜索按钮点击事件处理函数
    def on_button_clicked(self):
        search_query = self.input_box.text()  # 获取输入框中的文本
        if not search_query:
            QMessageBox.warning(self, "输入错误", "请输入搜索关键词")  # 如果为空，弹出警告框
            return

        self.current_page = 1  # 搜索时重置页码为第一页
        self.fetch_and_update_data(search_query)  # 调用数据获取和更新方法

    # 分页信号触发时更新数据
    def on_page_changed(self, page):
        self.current_page = page  # 更新当前页码
        search_query = self.input_box.text()  # 获取输入框中的文本
        self.fetch_and_update_data(search_query)  # 调用数据获取和更新方法

    # 数据获取和更新方法
    def fetch_and_update_data(self, search_query):
        try:
            if len(self.sj) < self.current_page:
                datas, self.max_pages = self.fetch_data(search_query, self.current_page)  # 获取数据和最大页数
                self.sj.append(datas)
            datas = self.sj[self.current_page-1]
            self.main_window.datas = datas  # 更新主窗口的数据
            self.main_window.update_max_pages(self.max_pages)  # 更新主窗口的最大页数
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据获取失败: {str(e)}")  # 如果发生异常，弹出错误框

    # 数据抓取方法
    def fetch_data(self, search_query, page):
        BASE_URL = 'https://www.bnjxjd.com'  # 基础URL
        SEARCH_URL = f'{BASE_URL}/vodsearch.html'  # 搜索URL
        cache = SEARCH_URL.replace('.html', '')  # 替换模板中的后缀
        SEARCH_PAGE_URL_TEMPLATE = f'{cache}/page/{{}}/wd/{{}}.html'  # 搜索页面模板

        data_api = SEARCH_PAGE_URL_TEMPLATE.format(page, search_query)  # 格式化URL
        response = requests.get(data_api, headers={'User-Agent': 'Mozilla/5.0'})  # 发送HTTP请求
        response.raise_for_status()  # 检查请求状态
        soup = BeautifulSoup(response.text, 'html.parser')  # 解析HTML

        max_pages = self.extract_max_pages(soup)  # 提取最大页数
        datas = self.extract_datas(soup, BASE_URL)  # 提取数据
        return datas, max_pages  # 返回数据和最大页数

    # 提取最大页数
    def extract_max_pages(self, soup):
        try:
            page = soup.select('body > div:nth-child(1) > div > div > div.stui-pannel__ft > ul > li:nth-child(7) > a')[0]
            page = page.get('href')  # 获取链接
            page = page.split('/')[3]  # 提取页码
            return int(page)  # 返回整数类型的页码
        except (IndexError, ValueError):
            return 1  # 如果提取失败，默认返回1

    # 提取数据
    def extract_datas(self, soup, base_url):
        datas = {}
        for item in soup.select('body > div:nth-child(1) > div > div > div.stui-pannel__bd.clearfix > ul > li'):
            ti = item.select_one('.stui-vodlist__thumb.lazyload').get('title')  # 获取标题
            path = base_url + item.select_one('a').get('href')  # 获取路径
            ty = item.select('.pic-text1.text-right')[0].text  # 获取类型
            ji = item.select('.pic-text.text-right')[0].text  # 获取集数

            text = f'{ti}__{ty}__{ji}'  # 构造显示文本
            datas[text] = path  # 存储数据
        return datas  # 返回数据字典

# 定义子窗口类，用于显示选项
class SubWindow(QWidget):
    def __init__(self, parent=None, options=None, checkbox_mode=False):
        super().__init__(parent)
        self.options = options if options is not None else []  # 初始化选项列表
        self.checkbox_mode = checkbox_mode  # 是否为多选模式
        self.init_ui()  # 初始化UI

    def init_ui(self):
        self.setAutoFillBackground(True)  # 自动填充背景
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(220, 220, 220))  # 设置背景颜色
        self.setPalette(palette)

        self.setFixedSize(900, 400)  # 设置固定大小

        self.radio_buttons = []  # 单选按钮列表
        self.check_boxes = []  # 复选框列表
        layout = QVBoxLayout()  # 垂直布局
        for option in self.options:
            if self.checkbox_mode:
                check_box = QCheckBox(option, self)  # 创建复选框
                layout.addWidget(check_box)  # 添加到布局
                self.check_boxes.append(check_box)  # 添加到复选框列表
            else:
                radio_button = QRadioButton(option, self)  # 创建单选按钮
                layout.addWidget(radio_button)  # 添加到布局
                self.radio_buttons.append(radio_button)  # 添加到单选按钮列表

        self.setLayout(layout)  # 设置布局

    # 更新选项
    def update_options(self, options):
        for widget in self.radio_buttons + self.check_boxes:
            widget.deleteLater()  # 删除旧的控件
        self.radio_buttons.clear()  # 清空单选按钮列表
        self.check_boxes.clear()  # 清空复选框列表

        layout = self.layout()  # 获取布局
        for option in options:
            if self.checkbox_mode:
                check_box = QCheckBox(option, self)  # 创建复选框
                layout.addWidget(check_box)  # 添加到布局
                self.check_boxes.append(check_box)  # 添加到复选框列表
            else:
                radio_button = QRadioButton(option, self)  # 创建单选按钮
                layout.addWidget(radio_button)  # 添加到布局
                self.radio_buttons.append(radio_button)  # 添加到单选按钮列表

    # 获取选中的选项
    def get_selected_option(self):
        if self.checkbox_mode:
            selected_options = [check_box.text() for check_box in self.check_boxes if check_box.isChecked()]
            return selected_options  # 返回选中的复选框文本列表
        else:
            for radio_button in self.radio_buttons:
                if radio_button.isChecked():
                    return radio_button.text()  # 返回选中的单选按钮文本
            return None  # 如果没有选中，返回None

# 定义分页组件类
class PagerWidget(QWidget):
    page_changed = pyqtSignal(int)  # 定义信号

    def __init__(self, parent=None, max_pages=1, button_width=30, button_height=30, button_spacing=10):
        super().__init__(parent)
        self.max_pages = max_pages  # 最大页数
        self.current_page = 1  # 当前页码
        self.button_width = button_width  # 按钮宽度
        self.button_height = button_height  # 按钮高度
        self.button_spacing = button_spacing  # 按钮间距
        self.init_ui()  # 初始化UI

    def init_ui(self):
        self.prev_button = QPushButton("<", self)  # 上一页按钮
        self.prev_button.setFixedSize(self.button_width, self.button_height)  # 设置按钮大小
        self.prev_button.clicked.connect(self.on_prev_clicked)  # 绑定点击事件

        self.page_label = QLabel(f"第{self.current_page}页 共{self.max_pages}页", self)  # 页码标签

        self.next_button = QPushButton(">", self)  # 下一页按钮
        self.next_button.setFixedSize(self.button_width, self.button_height)  # 设置按钮大小
        self.next_button.clicked.connect(self.on_next_clicked)  # 绑定点击事件

        layout = QHBoxLayout()  # 水平布局
        layout.addWidget(self.prev_button)  # 添加上一页按钮
        layout.addSpacing(self.button_spacing)  # 添加间距
        layout.addWidget(self.page_label)  # 添加页码标签
        layout.addSpacing(self.button_spacing)  # 添加间距
        layout.addWidget(self.next_button)  # 添加下一页按钮
        layout.setContentsMargins(0, 0, 0, 0)  # 设置内容边距为0
        self.setLayout(layout)  # 设置布局

    # 上一页按钮点击事件
    def on_prev_clicked(self):
        if self.current_page > 1:
            self.current_page -= 1  # 当前页码减1
            self.update_page_label()  # 更新页码标签
            self.page_changed.emit(self.current_page)  # 发射信号

    # 下一页按钮点击事件
    def on_next_clicked(self):
        if self.current_page < self.max_pages:
            self.current_page += 1  # 当前页码加1
            self.update_page_label()  # 更新页码标签
            self.page_changed.emit(self.current_page)  # 发射信号

    # 更新页码标签
    def update_page_label(self):
        self.page_label.setText(f"第{self.current_page}页 共{self.max_pages}页")

    # 设置最大页数
    def set_max_pages(self, max_pages):
        self.max_pages = max_pages  # 更新最大页数
        self.update_page_label()  # 更新页码标签

# 主窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.datas = {}  # 数据字典
        self.init_ui()  # 初始化UI

    def init_ui(self):
        window_title = "双面的影视爬虫"  # 窗口标题
        window_width = 1000  # 窗口宽度
        window_height = 600  # 窗口高度
        self.setWindowTitle(window_title)  # 设置窗口标题
        self.setFixedSize(window_width, window_height)  # 设置固定大小

        icon_path = "static/icon/shuangmian.ico"  # 图标路径
        self.setWindowIcon(QIcon(icon_path))  # 设置窗口图标

        container = QWidget()  # 创建容器
        self.setCentralWidget(container)  # 设置为中心部件

        main_layout = QVBoxLayout()  # 主布局为垂直布局

        # 初始化分页组件
        self.pager_widget = PagerWidget(container, max_pages=1)
        pager_width = 200  # 分页组件宽度
        pager_height = 30  # 分页组件高度
        pager_x = window_width - pager_width - 20  # 分页组件X坐标
        pager_y = window_height - pager_height - 20  # 分页组件Y坐标
        self.pager_widget.setGeometry(pager_x, pager_y, pager_width, pager_height)  # 设置位置和大小

        # 初始化输入框和搜索按钮组件，并连接分页信号
        self.input_button_widget = InputButtonWidget(self)
        self.input_button_widget.main_window.pager_widget.page_changed.connect(self.input_button_widget.on_page_changed)

        input_layout = QHBoxLayout()  # 输入框和按钮布局
        input_layout.addWidget(self.input_button_widget)  # 添加输入框和按钮组件
        input_layout.setContentsMargins(0, 0, 0, 0)  # 设置内容边距为0
        main_layout.addLayout(input_layout)  # 添加到主布局

        # 初始化子窗口，默认为单选框
        self.sub_window = SubWindow(self, checkbox_mode=False)
        sub_layout = QVBoxLayout()  # 子窗口布局
        sub_layout.addWidget(self.sub_window)  # 添加子窗口
        sub_layout.setContentsMargins(50, 50, 50, 50)  # 设置内容边距
        main_layout.addLayout(sub_layout)  # 添加到主布局

        # 添加确定按钮
        self.confirm_button = QPushButton("确定", self)
        self.confirm_button.setFixedSize(70, 40)  # 设置按钮大小
        self.confirm_button.clicked.connect(self.on_confirm_clicked)  # 绑定点击事件

        confirm_layout = QHBoxLayout()  # 确定按钮布局
        confirm_layout.addWidget(self.confirm_button)  # 添加确定按钮
        confirm_layout.setContentsMargins(0, 0, 0, 0)  # 设置内容边距为0
        main_layout.addLayout(confirm_layout)  # 添加到主布局

        container.setLayout(main_layout)  # 设置容器布局

    # 更新最大页数
    def update_max_pages(self, max_pages):
        self.pager_widget.set_max_pages(max_pages)  # 更新分页组件的最大页数
        options = [text for text in self.datas.keys()]  # 获取数据键值作为选项
        self.sub_window.update_options(options)  # 更新子窗口选项

    # 确认按钮点击事件
    def on_confirm_clicked(self):
        selected_option = self.sub_window.get_selected_option()  # 获取选中的选项
        if selected_option:
            if isinstance(selected_option, list):  # 如果是多选模式
                print(f"你点击了确认按钮，选中的数据是: {selected_option}")
                for option in selected_option:
                    self.process_selected_option(option)  # 处理每个选中的选项
            else:  # 如果是单选模式
                print(f"你点击了确认按钮，选中的数据是: {selected_option}")
                self.datas = {selected_option: self.datas[selected_option]}  # 更新数据
                req = requests.get(self.datas[selected_option], headers={'User-Agent': 'Mozilla/5.0'})  # 发送请求
                soup = BeautifulSoup(req.text, 'html.parser')  # 解析HTML
                sj = soup.select('.stui-content__playlist.clearfix')[0].select('a')  # 提取链接
                self.input_button_widget.sj = {i.text: 'https://www.bnjxjd.com' + i.get('href') for i in sj}  # 构造缓存数据
                self.process_selected_option(selected_option)  # 处理选中的选项
        else:
            QMessageBox.warning(self, "选择错误", "请选择一个选项")  # 如果没有选中，弹出警告框

    # 处理选中的选项
    def process_selected_option(self, option):
        try:
            print(self.datas[option])  # 打印选中的数据
        except KeyError:
            print(f"选项 {option} 不存在于数据中")  # 如果选项不存在，打印错误信息
            QMessageBox.warning(self, "错误", f"选项 {option} 不存在于数据中")  # 弹出错误框

if __name__ == "__main__":
    app = QApplication(sys.argv)  # 创建应用程序实例
    window = MainWindow()  # 创建主窗口实例
    window.show()  # 显示窗口
    sys.exit(app.exec())  # 进入程序主循环
