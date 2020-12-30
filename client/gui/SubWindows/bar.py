from tkinter import *
from tkinter.ttk import *


class CustomedProgressbar(Frame):
    def __init__(self, master, text):
        """每个进度条的frame"""
        super().__init__(master)
        # 初始化label
        self.tag = Label(self, text=text)
        # 初始化progressbar，设置长度为100
        self.DEFAULT_LENGTH = 100
        self.current_value = 0
        self.progressbar = Progressbar(
            self,
            takefocus=FALSE,
            length=self.DEFAULT_LENGTH + 1,
            value=0
        )
        self.added = []
        # 布局
        self.tag.pack()
        self.progressbar.pack()

    def changeProgressByPercentage(self, add_percentage, pause=True):
        """根据百分比调整进度条
        :param add_percentage: 增加的进度占总进度的百分比
        :param pause: 是否需要sleep一段时间，主要为了用户视觉上效果好一点hhh
        :type add_percentage: float
        :return:
        """

        add = self.DEFAULT_LENGTH * add_percentage

        while self.current_value + add >= 100:
            add -= 0.01
        self.added.append(add)
        self.progressbar.step(add)
        self.current_value += add
        from time import sleep
        if pause:
            sleep(0.3)
        else:
            sleep(0.01)

    def changeLabel(self, new_text, color="black"):
        """预留，用于改变label"""
        self.tag.config(
            text="new_text",
            foreground=color
        )
