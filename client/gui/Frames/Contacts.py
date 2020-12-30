from tkinter import *
from server_api import Contacts
import settings.config as c


class ContactsFrame(Frame):
    def __init__(self, master):
        """联系人的页面，可以对联系人进行新增，也可以选择是否通过联系人申请"""
        super().__init__(master)
        # 联系人申请labelframe
        # - list, 用于存放所有的好友申请（request_frame）
        self.request_frame_list = []
        # - commit_labelframe, 用于存放所有的request_frame
        self.commit_labelframe = LabelFrame(
            self, text=c.loadLangDict()["ContactRequests"]
        )
        self.refresh_state_label = Label(self.commit_labelframe)
        self.refresh_button = Button(
            self.commit_labelframe,
            text=c.loadLangDict()["Refresh"],
            command=self.refresh_request_labelframe
        )
        # - accept button
        self.accept_button = Button(
            self.commit_labelframe,
            text=c.loadLangDict()["AcceptRequests"],
            command=self._acceptRequests
        )

        # 添加好友的labelframe
        self.send_request_labelframe = LabelFrame(
            self, text=c.loadLangDict()["Add"]
        )
        # - 回显状态
        self.send_request_state_label = Label(
            self.send_request_labelframe,
        )
        # - var, entry, button，添加联系人的按钮，记录联系人username的var和entry
        self.send_request_var = StringVar(self, )
        self.send_request_entry = Entry(
            self.send_request_labelframe,
            textvariable=self.send_request_var,
        )
        self.send_request_button = Button(
            self.send_request_labelframe,
            text=c.loadLangDict()["AddContact"],
            command=self._sendRequest
        )
        # 布局管理
        self.commit_labelframe.pack()
        self.refresh_state_label.pack()
        self.refresh_button.pack()
        self.accept_button.pack()

        self.send_request_labelframe.pack()
        self.send_request_state_label.pack()
        self.send_request_entry.pack()
        self.send_request_button.pack()

    def _acceptRequests(self):
        """点击接受申请按钮时的 回调函数"""
        # 遍历所有的联系人申请（frame）
        for r_f in self.request_frame_list:
            r_f: RequestFrame
            if r_f.getState():
                # 如果checkbutton被勾选，接收他的申请
                self._acceptSingleRequest(r_f.relation_id)
        self.refresh_state_label.config(
            foreground="green",
            text=c.loadLangDict()["AcceptFinished"]
        )

    @staticmethod
    def _acceptSingleRequest(relation_id):
        """接收单个联系人的申请"""
        return Contacts.acceptRequest(relation_id)

    def _sendRequest(self):
        """发送申请的回调函数"""
        # 获取用户名
        username = self.send_request_var.get()
        # 获取返回的error_code
        error_code = Contacts.sendContactRequest(username)
        if error_code == 0:
            # 无错误，更改状态label的显示
            self.send_request_state_label.config(
                text=c.loadLangDict()["SendSuccess"],
                foreground="green"
            )
        elif error_code == 4041:
            # 无此用户
            self.send_request_state_label.config(
                text=c.loadLangDict()["UsernameNotFound"],
                foreground="red"
            )
        elif error_code == 6001:
            # 已经发送过
            self.send_request_state_label.config(
                text=c.loadLangDict()["AlreadySent"],
                foreground="red"
            )

    def refresh_request_labelframe(self):
        """刷新好友申请的回调函数，可由外部调用，如登录后会进行一次刷新"""
        # 拉取列表
        state, requests_list = Contacts.getContactRequestList()
        if state:
            # 清除之前的布局
            self.refresh_button.pack_forget()
            self.accept_button.pack_forget()
            for r in self.request_frame_list:
                r: RequestFrame
                r.pack_forget()
            self.request_frame_list = []
            # 重新进行布局
            for r in requests_list:
                username = r[0]
                relation_id = r[1]
                r_f = RequestFrame(self.commit_labelframe, username, relation_id)
                self.request_frame_list.append(r_f)
                r_f.pack()
            # 根据状态更改state label
            if requests_list:
                self.refresh_state_label.config(
                    text=c.loadLangDict()["RefreshSucceed"],
                    foreground="green"
                )
            else:
                self.refresh_state_label.config(
                    text=c.loadLangDict()["NoNewRequests"],
                    foreground='green'
                )
            # 两个button的布局
            self.refresh_button.pack()
            self.accept_button.pack()

        else:
            self.refresh_state_label.config(
                text=c.loadLangDict()["RefreshFailed"],
                foreground="red"
            )

    def _denyRequests(self):
        """预留，如果服务端支持拒绝好友申请的话会加以完善"""
        for r_f in self.request_frame_list:
            r_f: RequestFrame
            if r_f.getState():
                self._denySingleRequest()

    def _denySingleRequest(self):
        """预留"""
        pass


class RequestFrame(Frame):
    def __init__(self, master, sender: str, relation_id: int):
        """每一个好友申请的界面，保存了相应的widget和一些关键信息

        :param master: master
        :param sender: 发送方
        :param relation_id: 关系号，确认请求时使用
        """
        super().__init__(master)
        self.isChecked_var = BooleanVar(self)
        self.relation_id = relation_id
        self.checkbutton = Checkbutton(
            self, variable=self.isChecked_var,
            text=sender,
            onvalue=True,
            offvalue=False)
        self.checkbutton.pack()

    def getState(self):
        a = self.isChecked_var.get()
        return a
