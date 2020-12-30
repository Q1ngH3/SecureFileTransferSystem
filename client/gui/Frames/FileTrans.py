from tkinter import *
from tkinter.filedialog import askopenfilename
from settings import config
from server_api import Contacts, Auth
from client_api.TransHandlers import FileTransSendHandler


class FileTransFrame(Frame):
    def __init__(self, master):
        """文件传输界面"""
        super().__init__(master)
        # 联系人labelframe
        self.contact_list_labelframe = LabelFrame(
            self,
            text=config.loadLangDict()["AddedContact"]
        )
        # - 状态label
        self.refresh_contact_state_label = Label(self.contact_list_labelframe, )
        # - 刷新按钮
        self.contact_list_refresh_button = Button(
            self.contact_list_labelframe,
            text=config.loadLangDict()["Refresh"],
            command=self.refresh_contact_labelframe
        )
        # - 单选的var，选择接受方
        self.contact_list_choice_var = IntVar(
            self.contact_list_labelframe
        )
        self.contact_frame_list = []
        # 选择文件
        # - 记录文件的var
        self.file_path_var = StringVar(self)
        # - 显示var值的label
        self.file_path_label = Label(
            self,
            textvariable=self.file_path_var
        )
        # - 选择文件button
        self.sel_trans_file_button = Button(
            self,
            text=config.loadLangDict()["SelectTransFile"],
            command=lambda: self.file_path_var.set(askopenfilename())
        )
        # 发送按钮
        self.send_button = Button(
            self,
            text=config.loadLangDict()["Send"],
            command=self._sendFile
        )
        # 布局
        # - 联系人labelframe布局
        self.contact_list_labelframe.pack()
        self.refresh_contact_state_label.pack()
        self.contact_list_refresh_button.pack()
        # - 文件按钮label布局
        self.sel_trans_file_button.pack()
        self.file_path_label.pack()
        # - 发送button
        self.send_button.pack()

    def refresh_contact_labelframe(self):
        """刷新contact列表"""
        # 先取消之前的布局
        self.contact_list_refresh_button.pack_forget()
        for c in self.contact_frame_list:
            c: SingleContactFrame
            c.destroy()
        self.contact_frame_list = []
        # 重新添加
        state, contact_list = Contacts.getContactList()
        if state:
            if contact_list:
                # 成功拉取到了 contact list
                self.refresh_contact_state_label.config(
                    foreground="green",
                    text=config.loadLangDict()["RefreshSucceed"]
                )
                # 记录了每个contact_frame对应的var数值
                cnt = 0
                for c in contact_list:
                    f = SingleContactFrame(
                        self.contact_list_labelframe,
                        self.contact_list_choice_var,
                        cnt,
                        c,
                        Auth.isUserOnline(c),
                        *Auth.getReceiverInfo(c)
                    )
                    f.pack()
                    self.contact_frame_list.append(f)
            else:
                self.refresh_contact_state_label.config(
                    foreground="green",
                    text=config.loadLangDict()["NoContacts"]
                )
        else:
            self.refresh_contact_state_label.config(
                foreground="red",
                text=config.loadLangDict()["RefreshFailed"]
            )

        self.contact_list_refresh_button.pack()

    def _sendFile(self):
        """初始化，并实例化一个send handler"""
        file_path = self.file_path_var.get()
        choice = self.contact_list_choice_var.get()
        choice_frame: SingleContactFrame = self.contact_frame_list[choice]
        public_key = choice_frame.public_key
        ip = choice_frame.ip
        name = choice_frame.username
        filename = file_path.split("/")[-1]
        h = FileTransSendHandler(self.master, ip, name, filename, file_path, public_key)
        h.startSending()


class SingleContactFrame(Frame):
    def __init__(
            self, master, variable, value,
            username, online_state, public_key, ip, port):
        """单个联系人的 frame
        用于存放 widget 和记录一些相关信息
        :param master: master
        :param variable: 关联的variable
        :param value: 本frame对应的值
        :param username: 用户名
        :param online_state: 在线状态
        :param public_key: 接收方的公钥
        :param ip: 接收方的ip
        :param port: 接收方的端口（保留参数，实际上未使用）
        """
        super().__init__(master)
        self.radiobutton = Radiobutton(self, variable=variable, value=value)
        self.username_label = Label(self, text=username)
        self.state_label = Label(self, )
        self.public_key = public_key
        self.ip = ip
        self.port = port
        self.username = username
        if online_state:
            self.state_label.config(
                foreground="green",
                text=config.loadLangDict()["Online"]
            )
        else:
            self.state_label.config(
                foreground='red',
                text=config.loadLangDict()["Offline"]
            )

        # 布局
        self.radiobutton.grid(row=0, column=0)
        self.username_label.grid(row=0, column=1)
        self.state_label.grid(row=0, column=2)
