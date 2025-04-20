import os
import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon  # 添加导入 QIcon
from GuiMain import MovieCrawlerGUI
from movie_scraper import MovieScraper  # 更新导入路径
from set_ini import SettingDialog  # 导入 SettingDialog 类
from search_popup import SearchPopup  # 导入搜索弹窗类
from progress_popup import ProgressPopup  # 导入进度条弹窗类
import logging
from logging.handlers import RotatingFileHandler
import traceback

# 配置日志记录器，显式指定编码为 utf-8
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG

# 创建文件处理器并设置编码
file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024*5, backupCount=5, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s'))

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s'))

# 将文件处理器和控制台处理器添加到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 添加全局异常捕获
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    if issubclass(exc_type, SystemExit):  # 如果是 SystemExit 异常，直接返回
        return
    logger.error("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))
    
    # 弹窗提醒用户
    error_message = f"发生未捕获的异常:\n{exc_value}"
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("错误")
    msg_box.setText("程序发生错误")
    msg_box.setInformativeText(error_message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

sys.excepthook = handle_exception

class SearchThread(QThread):
    search_finished = pyqtSignal(dict)  # 信号，用于通知搜索完成

    def __init__(self, movie_scraper, query):
        super().__init__()
        self.movie_scraper = movie_scraper
        self.query = query

    def run(self):
        results = self.movie_scraper.search_movies(self.query)
        self.search_finished.emit(results)  # 确保这里正确调用 emit

class ProcessCheckButtonsThread(QThread):
    process_finished = pyqtSignal()  # 信号，用于通知处理完成

    def __init__(self, movie_scraper, results, selected_buttons, settings, gui_instance, progress_popup):
        super().__init__()
        self.movie_scraper = movie_scraper
        self.results = results
        self.selected_buttons = selected_buttons
        self.settings = settings
        self.gui_instance = gui_instance  # 传递 GUI 实例以访问其属性
        self.progress_popup = progress_popup
        self.stop_flag = [False]  # 添加停止标志
        self.active_threads = []  # 新增：用于存储活跃的子线程

    def run(self):
        total_tasks = len(self.selected_buttons)
        self.progress_popup.set_task_amount("总任务", total_tasks)  # 设置总任务量
        for index, button in enumerate(self.selected_buttons):
            if self.stop_flag[0]:
                break  # 如果停止标志被设置，则终止循环
            try:
                cache = self.results[button]
                # 调用 get_m3u8
                m3u8 = self.movie_scraper.get_m3u8(cache)
                if not m3u8:
                    logger.info(f"无法获取 m3u8 文件: {button}")
                    continue

                # 获取 ts 列表
                ts_list = self.movie_scraper.get_ts_list(m3u8)
                if not ts_list:
                    logger.info(f"无法获取 ts 列表: {button}")
                    continue

                # 构建下载路径
                dow_path = os.path.join(self.settings.get('dow_path', '.'), f"{self.gui_instance.selected_button + button}.mp4")
                n = int(self.settings.get('n', 150))  # 获取 n 参数并转换为整数

                if not dow_path:
                    logger.info("下载路径未设置，无法下载视频")
                    continue

                # 打印调试信息
                logger.info(f"下载路径: {dow_path}")

                # 下载视频
                self.movie_scraper.dow_mp4(ts_list, dow_path, n, self.progress_popup, f"下载 {button}", self.stop_flag)
                logger.info(f"处理多选按钮: {button} 下载完成")
            except Exception as e:
                import traceback
                logger.error(f"处理多选按钮: {button} 时发生错误: {e}")
                traceback.print_exc()  # 打印详细的错误堆栈信息
            finally:
                self.progress_popup.set_task_amount(f"下载 {button}", len(ts_list))
        self.process_finished.emit()

    def stop(self):
        """ 设置停止标志并终止所有活跃线程 """
        self.stop_flag[0] = True
        for thread in self.active_threads:
            if thread.is_alive():
                thread.join(timeout=5)  # 等待子线程最多 5 秒
        logger.info("所有子线程已终止")

    # 新增：注册活跃线程
    def register_thread(self, thread):
        self.active_threads.append(thread)


class CustomMovieCrawlerGUI(MovieCrawlerGUI):
    def __init__(self, button_data, is_radio=True):
        super().__init__(button_data, is_radio)
        self.is_radio = is_radio
        self.movie_scraper = MovieScraper()
        self.last_query = None  # 添加一个变量来存储上次的查询关键词
        self.results = None  # 添加一个变量来存储搜索结果
        self.selected_button = None  # 新增实例变量来存储选中的单选按钮
        self.search_popup = SearchPopup(self)  # 全局化 SearchPopup 对象
        self.search_thread = None  # 初始化搜索线程
        self.process_check_buttons_thread = None  # 初始化处理复选框按钮的线程
        self.progress_popup = ProgressPopup()  # 创建进度条弹窗实例
        self.progress_popup.rejected.connect(self.on_progress_popup_closed)  # 连接 rejected 信号
        self.http_server_thread = None  # 初始化 HTTP 服务器线程

        # 连接搜索框的 returnPressed 信号到 on_search_clicked 方法
        self.search_input.returnPressed.connect(self.on_search_clicked)

    def on_search_clicked(self):
        logger.info("自定义：搜索按钮被点击")
        query = self.search_input.text()
        logger.info(f"搜索关键词: {query}")

        # 检查输入是否为空或与上次输入相同
        if not query or query == self.last_query:
            logger.info("输入为空或与上次输入相同，不做处理")
            return

        # 更新上次查询关键词
        self.last_query = query

        # 显示搜索弹窗
        self.search_popup.show_popup()

        # 启动搜索线程
        self.search_thread = SearchThread(self.movie_scraper, query)
        self.search_thread.search_finished.connect(self.on_search_finished)
        self.search_thread.start()

    def on_search_finished(self, results):
        logger.info("搜索完成")
        if not results:
            QMessageBox.warning(self, "提示", "未找到相关资源，请尝试其他关键词")
            return
        self.results = results
        self.process_results_and_update_ui(True)

    def process_results_and_update_ui(self, is_radio):
        # 处理结果并更新UI的逻辑
        datas = pd.Series(self.results)
        cache = datas.index.to_list().copy()
        logger.info(cache)

        # 关闭搜索弹窗
        self.search_popup.close_popup()

        # 更新按钮数据
        self.update_button_data(cache, is_radio)

    def on_confirm_clicked(self):
        # 自定义确定按钮的逻辑
        logger.info("自定义：确定按钮被点击")
        selected_buttons = [button.text() for button in self.buttons if button.isChecked()]

        if not selected_buttons:
            logger.info("没有选中的按钮，不做处理")
            return  # 如果没有选中任何按钮，则直接返回

        if self.is_radio:
            selected_button = selected_buttons[0]
            logger.info(f"选中的单选按钮: {selected_button}")

            # 显示搜索弹窗
            self.search_popup.show_popup()

            # 处理单选按钮的逻辑
            self.handle_selected_radio_button(selected_button)

            # 关闭搜索弹窗
            self.search_popup.close_popup()
        else:
            logger.info(f"选中的多选按钮列表: {selected_buttons}")
            # 读取 Settings.ini
            settings_dialog = SettingDialog()
            settings = settings_dialog.settings  # 直接使用 settings_dialog.settings

            # 显示搜索弹窗
            self.search_popup.show_popup()

            # 启动处理复选框按钮的线程
            self.process_check_buttons_thread = ProcessCheckButtonsThread(self.movie_scraper, self.results,
                                                                          selected_buttons, settings, self, self.progress_popup)
            self.process_check_buttons_thread.process_finished.connect(self.on_process_finished)
            self.process_check_buttons_thread.start()

            # 显示进度条弹窗（设置为模态对话框）
            self.progress_popup.set_task_names([f"下载 {button}" for button in selected_buttons])
            self.progress_popup.setModal(True)  # 设置为模态对话框
            self.progress_popup.show()

            # 关闭搜索弹窗
            self.search_popup.close_popup()

        # 清除上次输入的缓存
        self.last_query = None

    def on_process_finished(self):
        logger.info("处理复选框按钮完成")
        self.progress_popup.close()  # 关闭进度条弹窗

    def handle_selected_button(self, button, is_radio):
        """ 处理选中的按钮 """
        logger.info(f"处理按钮: {button}")
        url1 = self.results[button]
        datas = self.movie_scraper.get_ji(url1)
        self.results = datas
        self.process_results_and_update_ui(not is_radio)

    def handle_selected_radio_button(self, button):
        # 处理单选按钮的逻辑
        self.selected_button = button  # 更新实例变量
        self.handle_selected_button(button, True)

    def handle_selected_check_buttons(self, buttons_list):
        # 处理多选按钮的逻辑
        for button in buttons_list:
            try:
                self.handle_selected_button(button, False)
            except Exception as e:
                logger.error(f"处理多选按钮: {button} 时发生错误: {e}")

    def show_settings_dialog(self):
        """显示设置对话框"""
        dialog = SettingDialog()  # 设置父窗口为当前窗口
        dialog.exec()

    def on_settings_clicked(self):
        logger.info("设置按钮被点击")
        self.show_settings_dialog()  # 调用显示设置对话框的方法

    def show_search_popup(self):
        """显示搜索弹窗"""
        self.search_popup.exec()

    def update_progress(self, completed, total):
        task_name = f"下载 {self.selected_button}"
        self.progress_popup.set_task_amount(task_name, total)
        self.progress_popup.update_task_completed_amount(task_name, completed)

    def on_progress_popup_closed(self):
        logger.info("进度条弹窗被关闭")
        if self.process_check_buttons_thread and self.process_check_buttons_thread.isRunning():
            self.process_check_buttons_thread.stop()  # 设置停止标志
            QMessageBox.warning(self, "下载终止", "下载进程已终止")

    def closeEvent(self, event):
        """确保所有线程和资源在关闭时被释放"""
        # 停止搜索线程
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.terminate()

        # 停止处理复选框按钮的线程
        if self.process_check_buttons_thread and self.process_check_buttons_thread.isRunning():
            self.process_check_buttons_thread.stop()

        # 停止 HTTP 服务器线程
        if self.http_server_thread and self.http_server_thread.is_alive():
            logger.info("正在关闭 HTTP 服务器线程...")
            self.http_server_thread.join(timeout=5)

        # 关闭日志文件处理器
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)

        # 调用父类的 closeEvent 方法
        super().closeEvent(event)

def set_global_icon(app):
    """设置全局图标"""
    icon_path = "static/icon/shuangmian.ico"
    app.setWindowIcon(QIcon(icon_path))

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        set_global_icon(app)  # 调用全局图标设置

        # 定义按钮数据
        button_data = [
            []
        ]

        # 创建窗口实例
        window = CustomMovieCrawlerGUI(button_data, is_radio=True)
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        logger.error("主程序发生异常", exc_info=True)
        traceback.print_exc()
