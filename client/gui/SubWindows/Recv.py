from tkinter import *
from settings import config
from gui.SubWindows.bar import CustomedProgressbar


class RecvWindow(Toplevel):
    def __init__(self, master):
        """接收时弹出的窗口，主要就是进度条"""
        super().__init__(master)
        # 三个进度条

        # 1：交换必要信息
        self.exchange_progressbar = CustomedProgressbar(
            self, text=config.loadLangDict()["ImportantMsgExchange"]
        )
        # 2：发送的状态
        self.recv_state_progressbar = CustomedProgressbar(
            self, text=config.loadLangDict()["RecvState"]
        )
        # 3：解密并保存
        self.save_file_progressbar = CustomedProgressbar(
            self, text=config.loadLangDict()["DecryptReceived"]
        )
        # 布局管理

        self.exchange_progressbar.pack()
        self.recv_state_progressbar.pack()
        self.save_file_progressbar.pack()
