import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel, QPushButton
from PyQt6.QtCore import QDir
from PyQt6.QtGui import QIcon
from progress_utils import update_task_completed_amount, set_task_amount
import traceback

import logging

logger = logging.getLogger(__name__)


class ProgressPopup(QDialog):
    """ 进度条弹窗窗口 """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("进度条弹窗")
        self.setFixedSize(400, 300)

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

        # 新增：连接关闭事件到终止下载线程的方法
        self.rejected.connect(self.terminate_download_threads)

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
            progress_bar.setStyleSheet("""QProgressBar {
                    border: 1px solid #666;
                    border-radius: 5px;
                    background-color: #f0f0f0; /* 背景色 */
                    color: #333; /* 文字颜色 */
                    text-align: center; /* 文本对齐方式改为居中 */
                }
                QProgressBar::chunk {
                    background-color: #666; /* 进度条颜色 */
                    width: 10px;
                    margin: 1px;
                }""")
            h_layout.addWidget(progress_bar)

            # 添加百分比标签
            percent_label = QLabel("0%")
            h_layout.addWidget(percent_label)

            # 将水平布局添加到主布局
            main_layout.insertLayout(main_layout.count() - 1, h_layout)

            # 保存进度条引用
            self.progress_bars.append((progress_bar, percent_label))

    def set_task_amount(self, task_name, task_amount):
        """ 设置指定任务的任务量 """
        set_task_amount(self, task_name, task_amount)

    def update_task_completed_amount(self, task_name, completed_amount):
        """ 更新指定任务的完成量 """
        update_task_completed_amount(self, task_name, completed_amount)

    def update_progress(self, task_idx):
        """ 更新指定任务的进度条 """
        if 0 <= task_idx < len(self.progress_bars):
            total_amount = self.task_amounts[task_idx]
            completed_amount = self.task_completed_amounts[task_idx]
            if total_amount == 0:
                progress = 0
            else:
                progress = (completed_amount / total_amount) * 100
            self.progress_bars[task_idx][0].setValue(int(progress))
            self.progress_bars[task_idx][1].setText(f"{int(progress)}%")

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

    def on_progress_popup_closed(self):
        """ 处理进度条弹窗关闭事件 """
        print("进度条弹窗被关闭")
        # 这里可以添加终止下载线程的逻辑
        # 例如：self.parent().process_check_buttons_thread.terminate()

    # 新增：终止下载线程的方法
    def terminate_download_threads(self):
        """ 终止所有与下载相关的线程 """
        try:
            parent = self.parent()
            if hasattr(parent, "process_check_buttons_thread") and parent.process_check_buttons_thread:
                parent.process_check_buttons_thread.stop()  # 设置停止标志
                logger.info("已发送停止信号给下载线程")
        except Exception as e:
            logger.error("终止下载线程时发生错误", exc_info=True)
            traceback.print_exc()

    def closeEvent(self, event):
        """ 在关闭弹窗时终止下载线程 """
        self.terminate_download_threads()
        super().closeEvent(event)