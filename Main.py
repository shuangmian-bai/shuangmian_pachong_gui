import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication
from GuiMain import MovieCrawlerGUI
from get_data import MovieScraper


class CustomMovieCrawlerGUI(MovieCrawlerGUI):
    def __init__(self, button_data, is_radio=True):
        super().__init__(button_data, is_radio)
        self.is_radio = is_radio
        self.movie_scraper = MovieScraper()
        self.last_query = None  # 添加一个变量来存储上次的查询关键词
        self.results = None  # 添加一个变量来存储搜索结果

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
        datas = pd.Series(self.results)
        cache = datas.index.to_list().copy()
        print(cache)

        # 将 cache 转换成二维列表，每个子列表包含 10 个元素
        n = 10
        cache_2d = [cache[i:i + n] for i in range(0, len(cache), n)]
        print(cache_2d)

        # 更新按钮数据
        self.update_button_data(cache_2d)

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

    def handle_selected_radio_button(self, button):
        # 处理单选按钮的逻辑
        print(f"处理单选按钮: {button}")
        # 在这里添加具体的处理逻辑

    def handle_selected_check_buttons(self, buttons_list):
        # 处理多选按钮的逻辑
        for button in buttons_list:
            print(f"处理多选按钮: {button}")
        # 在这里添加具体的处理逻辑


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
