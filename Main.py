import os
import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QThread, pyqtSignal
from GuiMain import MovieCrawlerGUI
from get_data import MovieScraper
from set_ini import SettingDialog  # 导入 SettingDialog 类
from search_popup import SearchPopup  # 导入搜索弹窗类
from progress_popup import ProgressPopup  # 导入进度条弹窗类
from dow_mp4 import DownloadProgress  # 导入 DownloadProgress 类


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

    def __init__(self, movie_scraper, results, selected_buttons, settings, progress_signal, gui_instance):
        super().__init__()
        self.movie_scraper = movie_scraper
        self.results = results
        self.selected_buttons = selected_buttons
        self.settings = settings
        self.progress_signal = progress_signal
        self.gui_instance = gui_instance  # 传递 GUI 实例以访问其属性

    def run(self):
        for button in self.selected_buttons:
            try:
                cache = self.results[button]
                # 调用 get_m3u8
                m3u8 = self.movie_scraper.get_m3u8(cache)
                if not m3u8:
                    print(f"无法获取 m3u8 文件: {button}")
                    continue

                # 获取 ts 列表
                ts_list = self.movie_scraper.get_ts_list(m3u8)
                if not ts_list:
                    print(f"无法获取 ts 列表: {button}")
                    continue

                # 构建下载路径
                dow_path = os.path.join(self.settings.get('dow_path', '.'),
                                        f"{self.gui_instance.selected_button + button}.mp4")
                n = int(self.settings.get('n', 150))  # 获取 n 参数并转换为整数

                if not dow_path:
                    print("下载路径未设置，无法下载视频")
                    continue

                # 打印调试信息
                print(f"下载路径: {dow_path}")

                # 下载视频
                self.movie_scraper.dow_mp4(ts_list, dow_path, n, self.progress_signal)
                print(f"处理多选按钮: {button} 下载完成")
            except Exception as e:
                import traceback
                print(f"处理多选按钮: {button} 时发生错误: {e}")
                traceback.print_exc()  # 打印详细的错误堆栈信息
        self.process_finished.emit()


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
        self.download_progress = DownloadProgress()  # 创建下载进度信号实例
        self.download_progress.progress_updated.connect(self.update_progress)

    def on_search_clicked(self):
        print("自定义：搜索按钮被点击")
        query = self.search_input.text()
        print(f"搜索关键词: {query}")

        # 检查输入是否为空或与上次输入相同
        if not query or query == self.last_query:
            print("输入为空或与上次输入相同，不做处理")
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
        print("搜索完成")
        self.results = results
        self.process_results_and_update_ui(True)

    def process_results_and_update_ui(self, is_radio):
        # 处理结果并更新UI的逻辑
        datas = pd.Series(self.results)
        cache = datas.index.to_list().copy()
        print(cache)

        # 将 cache 转换成二维列表，每个子列表包含 10 个元素
        n = 10
        cache_2d = [cache[i:i + n] for i in range(0, len(cache), n)]

        # 关闭搜索弹窗
        self.search_popup.close_popup()

        # 更新按钮数据
        self.update_button_data(cache_2d, is_radio)

    def on_confirm_clicked(self):
        # 自定义确定按钮的逻辑
        print("自定义：确定按钮被点击")
        selected_buttons = [button.text() for button in self.buttons if button.isChecked()]

        if not selected_buttons:
            print("没有选中的按钮，不做处理")
            return  # 如果没有选中任何按钮，则直接返回

        if self.is_radio:
            selected_button = selected_buttons[0]
            print(f"选中的单选按钮: {selected_button}")

            # 显示搜索弹窗
            self.search_popup.show_popup()

            # 处理单选按钮的逻辑
            self.handle_selected_radio_button(selected_button)

            # 关闭搜索弹窗
            self.search_popup.close_popup()
        else:
            print(f"选中的多选按钮列表: {selected_buttons}")
            # 读取 Settings.ini
            settings_dialog = SettingDialog()
            settings = settings_dialog.settings  # 直接使用 settings_dialog.settings

            # 启动处理复选框按钮的线程
            self.process_check_buttons_thread = ProcessCheckButtonsThread(self.movie_scraper, self.results,
                                                                          selected_buttons, settings,
                                                                          self.download_progress.progress_updated, self)
            self.process_check_buttons_thread.process_finished.connect(self.on_process_finished)
            self.process_check_buttons_thread.start()

            # 显示进度条弹窗
            self.progress_popup.set_task_names([f"下载 {button}" for button in selected_buttons])
            self.progress_popup.set_task_amount(f"下载 {selected_buttons[0]}", 1)  # 初始化进度条
            self.progress_popup.show()

        # 清除上次输入的缓存
        self.last_query = None

    def on_process_finished(self):
        print("处理复选框按钮完成")
        self.progress_popup.close()  # 关闭进度条弹窗

    def handle_selected_radio_button(self, button):
        # 处理单选按钮的逻辑
        print(f"处理单选按钮: {button}")
        self.selected_button = button  # 更新实例变量
        url1 = self.results[button]
        datas = self.movie_scraper.get_ji(url1)
        self.results = datas
        self.process_results_and_update_ui(False)
        # 在这里添加具体的处理逻辑

    def handle_selected_check_buttons(self, buttons_list):
        # 处理多选按钮的逻辑
        for button in buttons_list:
            try:
                cache = self.results[button]
                # 调用 get_m3u8
                m3u8 = self.movie_scraper.get_m3u8(cache)
                if not m3u8:
                    print(f"无法获取 m3u8 文件: {button}")
                    continue

                # 获取 ts 列表
                ts_list = self.movie_scraper.get_ts_list(m3u8)
                if not ts_list:
                    print(f"无法获取 ts 列表: {button}")
                    continue

                # 读取 Settings.ini
                settings_dialog = SettingDialog()
                settings = settings_dialog.settings  # 直接使用 settings_dialog.settings
                dow_path = settings.get('dow_path', './/') + self.selected_button + '__' + button + '.mp4'
                n = int(settings.get('n', 150))  # 获取 n 参数并转换为整数

                if not dow_path:
                    print("下载路径未设置，无法下载视频")
                    continue
                # 下载视频
                self.movie_scraper.dow_mp4(ts_list, dow_path, n, self.progress_signal)  # 使用 n 参数
                print(f"处理多选按钮: {button} 下载完成")
            except Exception as e:
                print(f"处理多选按钮: {button} 时发生错误: {e}")

    def show_settings_dialog(self):
        """显示设置对话框"""
        dialog = SettingDialog()  # 设置父窗口为当前窗口
        dialog.exec()

    def on_settings_clicked(self):
        print("设置按钮被点击")
        self.show_settings_dialog()  # 调用显示设置对话框的方法

    def show_search_popup(self):
        """显示搜索弹窗"""
        self.search_popup.exec()

    def update_progress(self, completed, total):
        task_name = f"下载 {self.selected_button}"
        self.progress_popup.set_task_amount(task_name, total)
        self.progress_popup.update_task_completed_amount(task_name, completed)

    def closeEvent(self, event):
        # 确保所有线程已经结束或处理完
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.terminate()
        if self.process_check_buttons_thread and self.process_check_buttons_thread.isRunning():
            self.process_check_buttons_thread.terminate()

        # 退出应用程序
        QApplication.quit()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 定义按钮数据
    button_data = [
        []
    ]

    # 创建窗口实例
    window = CustomMovieCrawlerGUI(button_data, is_radio=True)
    window.show()

    sys.exit(app.exec())
