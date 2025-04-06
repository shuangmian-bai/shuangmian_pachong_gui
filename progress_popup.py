import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel, QPushButton
from PyQt6.QtCore import QThread, pyqtSignal, QDir
from PyQt6.QtGui import QIcon


class TaskThread(QThread):
    """ 任务执行线程 """
    progress_signal = pyqtSignal(int, int)  # 信号：发送任务索引和进度

    def __init__(self, tasks, task_amounts, task_completed_amounts):
        super().__init__()
        self.tasks = tasks
        self.task_amounts = task_amounts
        self.task_completed_amounts = task_completed_amounts  # 记录每个任务当前完成的数量

    def run(self):
        for idx, task in enumerate(self.tasks):
            total_amount = self.task_amounts[idx]
            completed_amount = self.task_completed_amounts[idx]
            if total_amount == 0:
                progress = 0
            else:
                progress = (completed_amount / total_amount) * 100
            self.progress_signal.emit(idx, int(progress))  # 发送进度信号
            self.msleep(50)  # 模拟任务耗时


class ProgressPopup(QDialog):
    """ 进度条弹窗窗口 """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("进度条弹窗")
        self.setFixedSize(400, 300)

        # 设置窗口图标
        icon_path = QDir.current().filePath("static/icon/shuangmian.ico")  # 获取图标文件路径
        self.setWindowIcon(QIcon(icon_path))  # 设置窗口图标

        # 布局管理
        main_layout = QVBoxLayout()

        # 动态添加任务名称和进度条
        self.progress_bars = []
        self.tasks = []
        self.task_amounts = []
        self.task_completed_amounts = []

        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button)

        # 设置主布局
        self.setLayout(main_layout)

        # 初始化任务线程
        self.task_thread = None

    def set_task_names(self, task_names):
        """ 设置任务名称列表并更新UI """
        self.tasks = task_names
        self.task_amounts = [0] * len(task_names)  # 初始化任务量为0
        self.task_completed_amounts = [0] * len(task_names)  # 初始化完成量为0
        self.progress_bars.clear()
        main_layout = self.layout()

        # 移除所有子布局
        for i in reversed(range(main_layout.count())):
            item = main_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

        # 动态添加任务名称和进度条
        for task in self.tasks:
            h_layout = QHBoxLayout()

            # 添加任务名称
            label = QLabel(task)
            h_layout.addWidget(label)

            # 添加冒号分隔符
            colon_label = QLabel(":")
            h_layout.addWidget(colon_label)

            # 添加进度条
            progress_bar = QProgressBar()
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)

            # 设置进度条样式
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #666;
                    border-radius: 5px;
                    background-color: #f0f0f0; /* 背景色 */
                    color: #666; /* 文字颜色 */
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #666; /* 进度条颜色 */
                    width: 10px;
                    margin: 1px;
                }
            """)
            h_layout.addWidget(progress_bar)

            # 将水平布局添加到主布局
            main_layout.insertLayout(main_layout.count() - 1, h_layout)

            # 保存进度条引用
            self.progress_bars.append(progress_bar)

        # 初始化任务线程
        self.task_thread = TaskThread(self.tasks, self.task_amounts, self.task_completed_amounts)
        self.task_thread.progress_signal.connect(self.update_progress)
        self.task_thread.start()

    def set_task_amount(self, task_name, task_amount):
        """ 设置指定任务的任务量 """
        if task_name in self.tasks:
            idx = self.tasks.index(task_name)
            self.task_amounts[idx] = task_amount
            self.restart_task_thread()

    def update_task_completed_amount(self, task_name, completed_amount):
        """ 更新指定任务的完成量 """
        if task_name in self.tasks:
            idx = self.tasks.index(task_name)
            self.task_completed_amounts[idx] += completed_amount
            self.restart_task_thread()

    def restart_task_thread(self):
        """ 重新启动任务线程 """
        if self.task_thread:
            self.task_thread.terminate()
        self.task_thread = TaskThread(self.tasks, self.task_amounts, self.task_completed_amounts)
        self.task_thread.progress_signal.connect(self.update_progress)
        self.task_thread.start()

    def clear_layout(self, layout):
        """ 清除布局中的所有子项 """
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                nested_layout = item.layout()
                if nested_layout:
                    self.clear_layout(nested_layout)  # 递归清理嵌套布局

    def update_progress(self, task_idx, progress):
        """ 更新指定任务的进度条 """
        if 0 <= task_idx < len(self.progress_bars):
            self.progress_bars[task_idx].setValue(progress)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 显示进度条弹窗
    popup = ProgressPopup()
    popup.show()

    # 示例任务名称列表
    task_names = ["任务1", "任务2", "任务3"]
    popup.set_task_names(task_names)

    # 设置任务量
    popup.set_task_amount("任务1", 200)
    popup.set_task_amount("任务2", 100)
    popup.set_task_amount("任务3", 300)

    # 更新任务3的完成量
    popup.update_task_completed_amount("任务3", 3)  # 进度条加1%

    sys.exit(app.exec())
