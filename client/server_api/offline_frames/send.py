from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import *
from base64 import b64decode, b64encode
from server_api import Auth, Contacts, Offline
from client_api.CONST import *
from client_api.lib import compress, RSAkey, crypt
import os


class SendFrame(LabelFrame):
    def __init__(self, master):
        """离线传输界面"""
        super().__init__(master, text=config.loadLangDict()["OfflineSend"])
        # - 状态label
        self.refresh_contact_state_label = Label(self)
        # - 刷新按钮
        self.contact_list_refresh_button = Button(
            self,
            text=config.loadLangDict()["Refresh"],
            command=self.refresh_contact_labelframe
        )
        # - 单选的var，选择接受方
        self.choice_var = IntVar(self)
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
        self._pack()

    def refresh_contact_labelframe(self):
        """刷新contact列表"""
        self._unpack()
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
                    f = _SingleSendFrame(
                        self,
                        self.choice_var,
                        cnt,
                        c,
                        Auth.getReceiverInfo(c)[0]
                    )
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
        self._pack()

    def _pack(self):
        self.refresh_contact_state_label.pack()
        for f in self.contact_frame_list:
            f.pack()

        self.contact_list_refresh_button.pack()
        # - 文件按钮label布局
        self.sel_trans_file_button.pack()
        self.file_path_label.pack()
        # - 发送button
        self.send_button.pack()

    def _unpack(self):
        # 先取消之前的布局
        self.refresh_contact_state_label.pack_forget()
        self.sel_trans_file_button.pack_forget()
        self.send_button.pack_forget()
        self.file_path_label.pack_forget()
        self.contact_list_refresh_button.pack_forget()
        for c in self.contact_frame_list:
            c: _SingleSendFrame
            c.destroy()
        self.contact_frame_list = []

    def _sendFile(self):
        if not os.path.exists(TMP_DIR):
            os.mkdir(TMP_DIR)
        # 路径信息
        plain_file_path = self.file_path_var.get()
        if not os.path.exists(plain_file_path):
            showerror(title=loadLangDict()["Error"],
                      message=loadLangDict()["PathNotExist"])
            return

        filename = plain_file_path.split('/')[-1]
        zipped_filepath = ZIP_FILEPATH.format(filename)
        encrypted_filepath = ENCRYPTED_FILEPATH.format(filename)
        # 密钥相关
        choice = self.choice_var.get()
        f: _SingleSendFrame = self.contact_frame_list[choice]
        public_key = f.public_key
        receiver = f.username
        iv = crypt.get_session_key()
        b64_iv = b64encode(
            RSAkey.rsa_encrypt(public_key, iv, )
        ).decode()
        aes_key = crypt.get_session_key()
        b64_aes_key = b64encode(
            RSAkey.rsa_encrypt(public_key, aes_key, )
        ).decode()
        with open("./key", "wb")as f:
            f.write(b"aes:" + aes_key + b"\n" + iv)
        # 实例化AES
        aes = crypt.AESCryptor(aes_key,iv)
        # 压缩
        compress.file_compress(plain_file_path, zipped_filepath)
        # 加密
        aes.encrypt(zipped_filepath, encrypted_filepath)
        with open(encrypted_filepath, "rb")as fi:
            content = b64encode(fi.read()).decode()

        Offline.sendFile(Auth.getUsernameByAuth()[1], receiver, filename, b64_aes_key, b64_iv, public_key, content)


class _SingleSendFrame(Frame):
    def __init__(
            self, master, variable, value,
            username, public_key, ):
        """单个联系人的 frame
        用于存放 widget 和记录一些相关信息
        :param master: master
        :param variable: 关联的variable
        :param value: 本frame对应的值
        :param username: 用户名
        :param public_key: 接收方的公钥
        """
        super().__init__(master)
        self.radiobutton = Radiobutton(self, variable=variable, value=value)
        self.username_label = Label(self, text=username)
        self.state_label = Label(self, )
        self.public_key = public_key
        self.username = username

        # 布局
        self.radiobutton.grid(row=0, column=0)
        self.username_label.grid(row=0, column=1)
        self.state_label.grid(row=0, column=2)
