from tkinter import *
from settings import config
from gui.SubWindows.bar import CustomedProgressbar


class SendWindow(Toplevel):
    def __init__(self, master):
        """发送时弹出的进度条子窗口"""
        super().__init__(master)
        # 三个进度条
        # 1：处理文件
        self.process_file_progressbar = CustomedProgressbar(
            self, text=config.loadLangDict()["ProcessFile"]
        )
        # 2：交换必要信息
        self.exchange_progressbar = CustomedProgressbar(
            self, text=config.loadLangDict()["ImportantMsgExchange"]
        )
        # 3：发送的状态
        self.send_state_progressbar = CustomedProgressbar(
            self, text=config.loadLangDict()["SendState"]
        )

        # 布局管理
        self.process_file_progressbar.pack()
        self.exchange_progressbar.pack()
        self.send_state_progressbar.pack()
