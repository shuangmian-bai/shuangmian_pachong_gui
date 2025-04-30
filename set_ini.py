import os
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QLabel, QHBoxLayout
from PyQt6.QtGui import QIcon, QFont, QIntValidator
from configparser import ConfigParser, NoSectionError
from utils import process_path
import logging
from utils import resource_path


class SettingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设置")
        self.setFixedSize(400, 300)  # 将高度从 250 调整为 300

        # 初始化布局
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)  # 增加组件间距
        self.layout.setContentsMargins(20, 20, 20, 20)  # 边距保持不变

        # 下载路径部分
        dow_path_layout = QHBoxLayout()
        self.dow_path_label = QLabel("下载路径:")
        self.dow_path_label.setStyleSheet("""font-size: 14px; color: #333;""")
        self.dow_path_input = QLineEdit()
        self.dow_path_input.setStyleSheet("""font-size: 14px; padding: 8px; border: 1px solid #ccc; border-radius: 5px;""")

        # 加载文件夹图标
        folder_icon = QIcon(resource_path("static/icon/folder.png"))
        if folder_icon.isNull():
            logging.warning("警告：文件夹图标未正确加载！请检查路径：static/icon/folder.png")

        self.dow_path_button = QPushButton("选择路径")
        self.dow_path_button.setIcon(folder_icon)
        self.dow_path_button.setStyleSheet("""font-size: 14px; padding: 8px 16px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;""")
        self.dow_path_button.clicked.connect(self.select_dow_path)

        dow_path_layout.addWidget(self.dow_path_label)
        dow_path_layout.addWidget(self.dow_path_input)
        dow_path_layout.addWidget(self.dow_path_button)
        self.layout.addLayout(dow_path_layout)

        # 并发数量部分
        n_layout = QHBoxLayout()
        self.n_label = QLabel("并发数量:")
        self.n_label.setStyleSheet("""font-size: 14px; color: #333;""")
        self.n_input = QLineEdit()
        self.n_input.setStyleSheet("""font-size: 14px; padding: 8px; border: 1px solid #ccc; border-radius: 5px;""")

        # 添加验证器，限制只能输入大于0的整数
        validator = QIntValidator(1, 9999, self)  # 你可以根据需要调整范围
        self.n_input.setValidator(validator)

        n_layout.addWidget(self.n_label)
        n_layout.addWidget(self.n_input)
        self.layout.addLayout(n_layout)

        # 每页展示数量部分
        items_per_page_layout = QHBoxLayout()
        self.items_per_page_label = QLabel("每页展示数量:")
        self.items_per_page_label.setStyleSheet("""font-size: 14px; color: #333;""")
        self.items_per_page_input = QLineEdit()
        self.items_per_page_input.setStyleSheet("""font-size: 14px; padding: 8px; border: 1px solid #ccc; border-radius: 5px;""")

        # 添加验证器，限制只能输入大于0的整数
        validator = QIntValidator(1, 9999, self)  # 你可以根据需要调整范围
        self.items_per_page_input.setValidator(validator)

        items_per_page_layout.addWidget(self.items_per_page_label)
        items_per_page_layout.addWidget(self.items_per_page_input)
        self.layout.addLayout(items_per_page_layout)

        # 日志保留天数部分
        log_days_layout = QHBoxLayout()
        self.log_days_label = QLabel("日志保留天数:")
        self.log_days_label.setStyleSheet("""font-size: 14px; color: #333;""")
        self.log_days_input = QLineEdit()
        self.log_days_input.setStyleSheet("""font-size: 14px; padding: 8px; border: 1px solid #ccc; border-radius: 5px;""")

        # 添加验证器，限制只能输入大于0的整数
        validator = QIntValidator(1, 9999, self)
        self.log_days_input.setValidator(validator)

        log_days_layout.addWidget(self.log_days_label)
        log_days_layout.addWidget(self.log_days_input)
        self.layout.addLayout(log_days_layout)

        # 保存按钮
        self.save_button = QPushButton("保存设置")
        self.save_button.setStyleSheet("""font-size: 16px; padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;""")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

        # 设置窗口布局
        self.setLayout(self.layout)

        # 初始化配置
        self.config = ConfigParser()
        self.settings = self.load_settings()

        # 将当前设置显示在输入框中
        self.dow_path_input.setText(self.settings['dow_path'])
        self.n_input.setText(self.settings['n'])
        self.items_per_page_input.setText(self.settings['items_per_page'])
        self.log_days_input.setText(self.settings['log_days'])

    def load_settings(self):
        """加载设置"""
        static_folder = resource_path('static')
        ini_file_path = os.path.join(static_folder, 'Settings.ini')

        if not os.path.exists(ini_file_path):
            with open(ini_file_path, 'w', encoding='utf-8') as configfile:
                configfile.write("[Settings]\ndow_path=./下载/\nn=150\nitems_per_page=10\nlog_days=7\n")

        self.config.read(ini_file_path, encoding='utf-8')  # 指定编码为 utf-8

        # 设置默认值
        dow_path = self.config.get('Settings', 'dow_path', fallback='./下载/')
        n = self.config.get('Settings', 'n', fallback='150')
        items_per_page = self.config.get('Settings', 'items_per_page', fallback='10')
        log_days = self.config.get('Settings', 'log_days', fallback='7')  # 默认保留7天日志

        return {'dow_path': dow_path, 'n': n, 'items_per_page': items_per_page, 'log_days': log_days}

    def select_dow_path(self):
        """选择下载路径"""
        dow_path = QFileDialog.getExistingDirectory(self, "选择下载路径")
        if dow_path:
            dow_path = process_path(dow_path)
            self.dow_path_input.setText(dow_path)

    def save_settings(self):
        """保存设置到 ini 文件"""
        dow_path = self.dow_path_input.text()
        n = self.n_input.text()
        items_per_page = self.items_per_page_input.text()
        log_days = self.log_days_input.text()

        dow_path = process_path(dow_path)

        # 更新 ini 文件
        static_folder = resource_path('static')
        ini_file_path = os.path.join(static_folder, 'Settings.ini')
        self.config.set('Settings', 'dow_path', dow_path)
        self.config.set('Settings', 'n', n)
        self.config.set('Settings', 'items_per_page', items_per_page)
        self.config.set('Settings', 'log_days', log_days)

        # 写入文件
        try:
            with open(ini_file_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            logging.info("设置已保存！")
        except IOError as e:
            logging.error(f"文件写入失败: {e}")

        self.accept()  # 关闭弹窗