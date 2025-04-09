import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QTextEdit, QFrame, QButtonGroup, QRadioButton, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import logging

from set_ini import SettingDialog


class MovieCrawlerGUI(QMainWindow):
    def __init__(self, button_data, is_radio=True):
        super().__init__()
        self.current_page = 1
        self.total_pages = len(button_data)
        self.button_data = button_data
        self.is_radio = is_radio
        self.button_group = QButtonGroup() if is_radio else None
        self.buttons = []
        self.selected_states = {}  # 用于保存按钮的选择状态
        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("双面的影视爬虫")
        self.setGeometry(100, 100, 800, 600)

        # 设置窗口图标
        icon_path = "static/icon/shuangmian.ico"
        self.setWindowIcon(QIcon(icon_path))

        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)  # 增加组件间距
        main_layout.setContentsMargins(20, 20, 20, 20)  # 边距保持不变

        # 设置按钮
        settings_button = QPushButton("设置", self)
        settings_button.setStyleSheet("""font-size: 12px; padding: 5px 10px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;""")
        settings_button.setFixedSize(60, 30)
        settings_button.clicked.connect(self.on_settings_clicked)

        # 创建一个新的布局用于放置设置按钮
        settings_layout = QHBoxLayout()
        settings_layout.addStretch()
        settings_layout.addWidget(settings_button)

        # 版本信息
        version_label = QLabel("双面的影视爬虫GUI", self)
        version_label.setStyleSheet("""font-size: 14px; color: #666; text-align: center;""")
        version_layout = QHBoxLayout()
        version_layout.addStretch()
        version_layout.addWidget(version_label)
        version_layout.addLayout(settings_layout)

        main_layout.addLayout(version_layout)

        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("请输入想看的影视")
        self.search_input.setStyleSheet("""font-size: 16px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; flex: 1;""")
        search_button = QPushButton("搜索", self)
        search_button.setStyleSheet("""font-size: 16px; padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;""")
        search_button.setFixedSize(100, 40)
        search_button.clicked.connect(self.on_search_clicked)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        # 将搜索框添加到主布局
        main_layout.addLayout(search_layout)

        # 显示结果区域
        result_frame = QFrame(self)
        result_frame.setFrameShape(QFrame.Shape.Box)
        result_frame.setFrameShadow(QFrame.Shadow.Raised)
        result_frame.setStyleSheet("""background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 10px; padding: 10px;""")
        result_layout = QVBoxLayout(result_frame)

        # 结果文本区域
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""font-size: 14px; background-color: #f9f9f9; border: none; padding: 10px;""")
        self.result_text.setFixedHeight(10)  # 调整为合适的高度

        # 按钮区域
        self.button_frame = QFrame(self)
        self.button_layout = QVBoxLayout(self.button_frame)
        self.update_buttons()

        # 将按钮区域添加到 result_layout 中，并设置对齐方式为顶部对齐
        result_layout.addWidget(self.button_frame, alignment=Qt.AlignmentFlag.AlignTop)

        # 将结果文本区域添加到 result_layout 中
        result_layout.addWidget(self.result_text)

        # 分页导航
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("上一页", self)
        self.prev_button.setStyleSheet("""font-size: 14px; padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;""")
        self.prev_button.setFixedSize(100, 40)
        self.prev_button.clicked.connect(self.on_prev_clicked)
        self.page_info_label = QLabel(f"第{self.current_page}页 共{self.total_pages}页", self)
        self.page_info_label.setStyleSheet("""font-size: 14px; color: #666; margin-left: 10px; margin-right: 10px;""")
        self.next_button = QPushButton("下一页", self)
        self.next_button.setStyleSheet("""font-size: 14px; padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;""")
        self.next_button.setFixedSize(100, 40)
        self.next_button.clicked.connect(self.on_next_clicked)
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addWidget(self.next_button)
        result_layout.addLayout(pagination_layout)

        # 将结果显示区域添加到主布局
        main_layout.addWidget(result_frame)

        # 确定按钮
        confirm_button = QPushButton("确定", self)
        confirm_button.setStyleSheet("""font-size: 16px; padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;""")
        confirm_button.setFixedSize(100, 40)
        confirm_button.clicked.connect(self.on_confirm_clicked)

        # 将确定按钮添加到主窗口左下角
        bottom_left_layout = QHBoxLayout()
        bottom_left_layout.addWidget(confirm_button)
        bottom_left_layout.addStretch()
        main_layout.addLayout(bottom_left_layout)

        # 将免责声明添加到主窗口下方
        disclaimer_label = QLabel("资源均来自于第三方接口,与本作者无关,切勿相信,如若被骗,概不负责", self)
        disclaimer_label.setStyleSheet("""font-size: 14px; color: #666; text-align: center;""")
        main_layout.addWidget(disclaimer_label)

    def update_buttons(self, selected_states=None):
        # 清空按钮区域
        for button in self.buttons:
            button.deleteLater()
        self.buttons.clear()

        # 获取当前页的数据
        current_data = self.button_data[self.current_page - 1]

        # 创建按钮
        for text in current_data:
            if self.is_radio:
                button = QRadioButton(text, self)
            else:
                button = QCheckBox(text, self)
            self.buttons.append(button)
            self.button_layout.addWidget(button)
            if self.is_radio:
                self.button_group.addButton(button)

        # 恢复选择状态
        if selected_states is not None:
            for button, state in zip(self.buttons, selected_states):
                button.setChecked(state)

    def on_search_clicked(self):
        logging.info("搜索按钮被点击")
        query = self.search_input.text()
        logging.info(f"搜索关键词: {query}")
        # 这里可以添加搜索逻辑

    def on_prev_clicked(self):
        if self.current_page > 1:
            # 保存当前按钮的选择状态
            selected_states = [button.isChecked() for button in self.buttons]
            self.selected_states[self.current_page] = selected_states

            self.current_page -= 1
            logging.info(f"上一页按钮被点击, 当前页码: {self.current_page}")
            self.update_page_info()
            self.update_buttons(self.selected_states.get(self.current_page, []))

    def on_next_clicked(self):
        if self.current_page < self.total_pages:
            # 保存当前按钮的选择状态
            selected_states = [button.isChecked() for button in self.buttons]
            self.selected_states[self.current_page] = selected_states

            self.current_page += 1
            logging.info(f"下一页按钮被点击, 当前页码: {self.current_page}")
            self.update_page_info()
            self.update_buttons(self.selected_states.get(self.current_page, []))

    def on_confirm_clicked(self):
        logging.info("确定按钮被点击")
        # 收集所有页的选中状态
        all_selected_buttons = []
        for page, states in self.selected_states.items():
            current_data = self.button_data[page - 1]
            for text, state in zip(current_data, states):
                if state:
                    all_selected_buttons.append(text)

        logging.info(f"选中的按钮列表: {all_selected_buttons}")
        # 这里可以添加确定按钮的逻辑

    def on_settings_clicked(self):
        logging.info("设置按钮被点击")
        # 这里可以添加设置按钮的逻辑

    def update_page_info(self):
        self.page_info_label.setText(f"第{self.current_page}页 共{self.total_pages}页")

    def update_button_data(self, new_button_data, is_radio):
        logging.info(new_button_data)
        self.is_radio = is_radio

        # 获取每页展示数量
        settings_dialog = SettingDialog()
        settings = settings_dialog.settings
        items_per_page = int(settings['items_per_page'])

        # 将一维列表转换为二维列表
        self.button_data = [new_button_data[i:i + items_per_page] for i in range(0, len(new_button_data), items_per_page)]
        self.total_pages = len(self.button_data)
        self.current_page = 1
        self.update_page_info()
        self.update_buttons()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    button_data = [
        ["按钮1", "按钮2", "按钮3"],
        ["按钮4", "按钮5", "按钮6"],
        ["按钮7", "按钮8", "按钮9"]
    ]
    window = MovieCrawlerGUI(button_data, is_radio=False)
    window.show()
    sys.exit(app.exec())
