import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QColor

class MovieCrawlerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.total_pages = 1
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

        # 标题
        title_label = QLabel("资源均来自于第三方接口,与本作者无关,切勿相信,如若被骗,概不负责", self)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        """)
        main_layout.addWidget(title_label)

        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("请输入想看的影视")
        self.search_input.setStyleSheet("""
            font-size: 16px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            flex: 1;
        """)
        search_button = QPushButton("搜索", self)
        search_button.setStyleSheet("""
            font-size: 16px;
            padding: 10px 20px;
            background-color: #6c757d; /* 灰色 */
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        """)
        search_button.setFixedSize(100, 40)
        search_button.clicked.connect(self.on_search_clicked)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # 显示结果区域
        result_frame = QFrame(self)
        result_frame.setFrameShape(QFrame.Shape.Box)
        result_frame.setFrameShadow(QFrame.Shadow.Raised)
        result_frame.setStyleSheet("""
            background-color: #f9f9f9; /* 浅灰色 */
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 10px;
        """)
        result_layout = QVBoxLayout(result_frame)
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            font-size: 14px;
            background-color: #f9f9f9;
            border: none;
            padding: 10px;
        """)
        result_layout.addWidget(self.result_text)
        main_layout.addWidget(result_frame)

        # 分页导航
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("上一页", self)
        self.prev_button.setStyleSheet("""
            font-size: 14px;
            padding: 10px 20px;
            background-color: #6c757d; /* 灰色 */
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        """)
        self.prev_button.setFixedSize(100, 40)
        self.prev_button.clicked.connect(self.on_prev_clicked)
        self.page_info_label = QLabel(f"第{self.current_page}页 共{self.total_pages}页", self)
        self.page_info_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            margin-left: 10px;
            margin-right: 10px;
        """)
        self.next_button = QPushButton("下一页", self)
        self.next_button.setStyleSheet("""
            font-size: 14px;
            padding: 10px 20px;
            background-color: #6c757d; /* 灰色 */
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        """)
        self.next_button.setFixedSize(100, 40)
        self.next_button.clicked.connect(self.on_next_clicked)
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addWidget(self.next_button)
        main_layout.addLayout(pagination_layout)

        # 确定按钮
        confirm_button = QPushButton("确定", self)
        confirm_button.setStyleSheet("""
            font-size: 16px;
            padding: 10px 20px;
            background-color: #6c757d; /* 灰色 */
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        """)
        confirm_button.setFixedSize(100, 40)
        confirm_button.clicked.connect(self.on_confirm_clicked)
        main_layout.addWidget(confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # 设置按钮
        settings_button = QPushButton("设置", self)
        settings_button.setStyleSheet("""
            font-size: 16px;
            padding: 10px 20px;
            background-color: #6c757d; /* 灰色 */
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        """)
        settings_button.setFixedSize(100, 40)
        settings_button.clicked.connect(self.on_settings_clicked)
        main_layout.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_search_clicked(self):
        print("搜索按钮被点击")
        query = self.search_input.text()
        print(f"搜索关键词: {query}")
        # 这里可以添加搜索逻辑

    def on_prev_clicked(self):
        if self.current_page > 1:
            self.current_page -= 1
            print(f"上一页按钮被点击, 当前页码: {self.current_page}")
            self.update_page_info()
            # 这里可以添加加载上一页数据的逻辑

    def on_next_clicked(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            print(f"下一页按钮被点击, 当前页码: {self.current_page}")
            self.update_page_info()
            # 这里可以添加加载下一页数据的逻辑

    def on_confirm_clicked(self):
        print("确定按钮被点击")
        # 这里可以添加确定按钮的逻辑

    def on_settings_clicked(self):
        print("设置按钮被点击")
        # 这里可以添加设置按钮的逻辑

    def update_page_info(self):
        self.page_info_label.setText(f"第{self.current_page}页 共{self.total_pages}页")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieCrawlerGUI()
    window.show()
    sys.exit(app.exec())
