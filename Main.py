# Main.py
import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication
from GuiMain import MovieCrawlerGUI
from get_data import MovieScraper
from set_ini import SettingDialog  # 导入 SettingDialog 类

class CustomMovieCrawlerGUI(MovieCrawlerGUI):
    def __init__(self, button_data, is_radio=True):
        super().__init__(button_data, is_radio)
        self.is_radio = is_radio
        self.movie_scraper = MovieScraper()
        self.last_query = None  # 添加一个变量来存储上次的查询关键词
        self.results = None  # 添加一个变量来存储搜索结果
        self.selected_button = None  # 新增实例变量来存储选中的单选按钮

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

        # 调用 MovieScraper 的 search_movies 方法进行搜索
        self.results = self.movie_scraper.search_movies(query)  # 将结果存储在实例变量中
        self.process_results_and_update_ui(True)

    def process_results_and_update_ui(self, is_radio):
        # 处理结果并更新UI的逻辑
        datas = pd.Series(self.results)
        cache = datas.index.to_list().copy()
        print(cache)

        # 将 cache 转换成二维列表，每个子列表包含 10 个元素
        n = 10
        cache_2d = [cache[i:i + n] for i in range(0, len(cache), n)]

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
            self.handle_selected_radio_button(selected_button)
        else:
            print(f"选中的多选按钮列表: {selected_buttons}")
            self.handle_selected_check_buttons(selected_buttons)

        # 清除上次输入的缓存
        self.last_query = None

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
                self.movie_scraper.dow_mp4(ts_list, dow_path, n)  # 使用 n 参数
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
