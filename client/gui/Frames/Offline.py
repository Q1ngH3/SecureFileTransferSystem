from tkinter import *
from server_api.offline_frames import *


class OfflineTransFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.send_frame = SendFrame(self)
        self.send_frame.pack()
        self.recv_frame = RecvFrame(self)
        self.recv_frame.pack()


# # 发送请求labelframe
# self.send_request_labelframe = LabelFrame(self)
# # - 状态label
# self.refresh_request_state_label = Label(self.send_request_labelframe, )
# # - 刷新按钮
# self.contact_list_refresh_button = Button(
#     self.contact_list_labelframe,
#     text=config.loadLangDict()["Refresh"],
#     command=self.refresh_contact_labelframe







