# Main.py
import sys
from PyQt6.QtWidgets import QApplication
from GuiMain import MovieCrawlerGUI


class CustomMovieCrawlerGUI(MovieCrawlerGUI):
    def __init__(self, button_data, is_radio=True):
        super().__init__(button_data, is_radio)
        self.is_radio = is_radio

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
        ["按钮1", "按钮2", "按钮3", "按钮4", "按钮5"],
    ]

    # 创建窗口实例
    window = CustomMovieCrawlerGUI(button_data, is_radio=True)
    window.show()

    sys.exit(app.exec())
