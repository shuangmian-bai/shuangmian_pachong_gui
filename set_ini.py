import os
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QLabel
from configparser import ConfigParser, NoSectionError

class SettingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设置")
        self.setGeometry(100, 100, 400, 200)

        # 初始化布局
        self.layout = QVBoxLayout()

        # 确保 static 文件夹存在
        static_folder = 'static'
        if not os.path.exists(static_folder):
            os.makedirs(static_folder)

        # 检查并初始化 ini 文件
        ini_file_path = os.path.join(static_folder, 'Settings.ini')
        if not os.path.exists(ini_file_path):
            with open(ini_file_path, 'w') as configfile:
                configfile.write("[Settings]\ndow_path=./下载/\nn=150\n")

        # 读取 ini 文件
        self.config = ConfigParser()
        try:
            self.config.read(ini_file_path)
            if not self.config.has_section('Settings'):
                raise NoSectionError('Settings')
        except NoSectionError:
            self.config.add_section('Settings')
            self.config.set('Settings', 'dow_path', './下载/')
            self.config.set('Settings', 'n', '150')
            with open(ini_file_path, 'w') as configfile:
                self.config.write(configfile)

        # 下载路径部分
        self.dow_path_label = QLabel("下载路径:")
        self.dow_path_input = QLineEdit(self.config.get('Settings', 'dow_path'))
        self.dow_path_button = QPushButton("选择路径")
        self.dow_path_button.clicked.connect(self.select_dow_path)

        # 并发数量部分
        self.n_label = QLabel("并发数量:")
        self.n_input = QLineEdit(self.config.get('Settings', 'n'))

        # 确定按钮
        self.save_button = QPushButton("保存设置")
        self.save_button.clicked.connect(self.save_settings)

        # 添加组件到布局
        self.layout.addWidget(self.dow_path_label)
        self.layout.addWidget(self.dow_path_input)
        self.layout.addWidget(self.dow_path_button)
        self.layout.addWidget(self.n_label)
        self.layout.addWidget(self.n_input)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def select_dow_path(self):
        """选择下载路径"""
        dow_path = QFileDialog.getExistingDirectory(self, "选择下载路径")
        if dow_path:
            self.dow_path_input.setText(dow_path)

    def save_settings(self):
        """保存设置到 ini 文件"""
        dow_path = self.dow_path_input.text()
        n = self.n_input.text()

        # 更新 ini 文件
        static_folder = 'static'
        ini_file_path = os.path.join(static_folder, 'Settings.ini')
        self.config.set('Settings', 'dow_path', dow_path)
        self.config.set('Settings', 'n', n)

        # 写入文件
        with open(ini_file_path, 'w') as configfile:
            self.config.write(configfile)

        print("设置已保存！")
        self.accept()  # 关闭弹窗

if __name__ == "__main__":
    app = QApplication([])
    dialog = SettingDialog()
    dialog.exec()
