from tkinter import *
from tkinter.ttk import Combobox
import settings.config as c
from server_api import Auth
from gui.SubWindows import RegisterWindow
from client_api.TransHandlers import *
from threading import Thread
from client_api.lib import RSAkey
from time import sleep


class LoginFrame(Frame):
    def __init__(self, master):
        """登录界面，继承 Frame，存放各种组件"""
        # 初始化
        super().__init__(master)
        self.config(width="100", height="200")

        # 获取当前使用的语言的键值对
        self.language_dict = c.loadLangDict()

        # 语言设置功能的label+var+combobox
        self.lang_label = Label(self, text=self.language_dict["Language"])
        self.lang_var = StringVar(self, value=c.loadLang())
        self.lang_var.trace("w", self._changeLang)
        self.lang_combobox = Combobox(self, textvariable=self.lang_var)
        self.lang_combobox.config(values=c.loadLangList())

        # 是否正确登录的state_label
        self.auth_success_or_not_label = Label(
            self
        )

        # 记录密码checkbutton
        self.remember_auth_var = BooleanVar(
            self, value=c.loadRememberPasswordOption()
        )
        self.remember_auth_checkbutton = Checkbutton(
            self,
            text=self.language_dict["RememberAuth"],
            variable=self.remember_auth_var,
            onvalue=True,
            offvalue=False
        )

        # 用户名的label，var，entry
        self.username_label = Label(self, text=self.language_dict["Username"])
        self.username_var = StringVar(self, value=c.loadUsernamePassword()[0])
        self.username_entry = Entry(self, textvariable=self.username_var)

        # 密码的label，var，entry
        self.password_label = Label(self, text=self.language_dict["Password"])
        self.password_var = StringVar(self, value=c.loadUsernamePassword()[1])
        self.password_entry = Entry(self, textvariable=self.password_var)

        # 登录按钮，command为self._login
        self.login_button = Button(self, text=self.language_dict["Login"], command=self._login)

        # 注册按钮，点击后应弹出新窗口
        self.register_button = Button(self, text=self.language_dict["Register"], command=self._register)

        # 服务器连通性 label 和显示状态的 label
        self.connection_tag_label = Label(self, text=self.language_dict["ConnectionTag"])
        self.connection_state_label = Label(self, text="pending...")
        # 开启对服务器连通性的测试
        t = Thread(target=self._testConnection)
        t.start()

        # 登录状态Label
        self.auth_state_tag = Label(self, text=self.language_dict["AuthState"])
        # 一个布尔值，记录了当前的状态，false为未登录，true为登录
        self.auth_state_var = BooleanVar(self, value=False)
        # 登录状态改变时触发callback
        self.auth_state_var.trace("w", self._changeAuthState)
        # 初始时state_label一定为not logged in
        self.auth_state_label = Label(self, text=self.language_dict["Offline"], foreground="red")

        # 布局
        self.pack()
        self.lang_label.pack()
        self.lang_combobox.pack()
        self.auth_success_or_not_label.pack()
        self.username_label.pack()
        self.username_entry.pack()
        self.password_label.pack()
        self.password_entry.pack()
        self.remember_auth_checkbutton.pack()
        self.login_button.pack()
        self.register_button.pack()
        self.connection_tag_label.pack()
        self.connection_state_label.pack()
        self.auth_state_tag.pack()
        self.auth_state_label.pack()

    def _login(self, *args):
        """点击 登录 按钮触发的回调函数
        与服务器通信，完成认证及auth token的记录
        """
        state, msg = Auth.authLogin(self.username_var.get(), self.password_var.get())
        if state:
            # 返回值不为None，说明认证成功，此时保存相应的auth_token
            self.auth_state_var.set(True)
            c.changeAuthTokens(msg)

            # 修改显示状态的label为：Online
            self.auth_state_label.config(text=self.language_dict["Online"], foreground="green")

            # 如果勾选了记录密码，则将user和pass都记录到setting中
            if self.remember_auth_var.get():
                c.changeUserPass(
                    self.username_var.get(),
                    self.password_var.get()
                )
                c.changeRememberAuthOption(True)
            else:
                # 如果没勾选，要清除记录的用户名和密码
                c.changeUserPass("", "")
                c.changeRememberAuthOption(False)

            # 把登录按钮换成注销按钮hhh
            self.login_button.config(
                text=self.language_dict["Logout"],
                command=self._logout,
                foreground="red"
            )

            # 登录状态的state_label显示登录成功
            self.auth_success_or_not_label.config(
                text=self.language_dict["AuthSucceed"],
                foreground="green"
            )

            # 把输入用户名和密码的entry设置为disable
            self._changeInputEntriesState(False)

            # 开始周期性发送心跳
            t = HeartbeatSender()
            t.start()

            # 生成新的公私钥, 将公钥传给服务器
            public, private = RSAkey.rsa_key_generate()
            c.changeKeys(public, private, self.username_var.get())
            Auth.updateInfo(public)

            # 实例化 FileTransRequestHandler
            self.request_handler = FileTransRequestHandler(self)
            self.request_handler.startListenThread()
        else:
            # 返回值为None，说明此时认证失败，显示相应错误信息
            self.auth_success_or_not_label.config(text=msg, foreground="red")

    def _logout(self, *args):
        """注销 回调函数"""
        state = Auth.authLogout()
        self.auth_state_var.set(False)
        self.auth_state_label.config(
            text=self.language_dict["Offline"],
            foreground="red"
        )
        # 把注销按钮换成登录按钮hhh
        self.login_button.config(
            text=self.language_dict["Login"],
            command=self._login,
            foreground="black"
        )

        # 把disable的entry都复原
        self._changeInputEntriesState(True)
        self.request_handler.stop()

    def _register(self, *args):
        """注册 的回调函数"""
        RegisterWindow(self)

    def _changeAuthState(self, *args):
        """更改当前的登录状态的 state_label"""
        import gui
        self.master: gui.MainWindow
        if self.auth_state_var.get():
            # True, 在线，显示为绿色
            self.auth_state_label.config(
                text=self.language_dict["Online"],
                foreground="green")
            self.master.isOnline_var.set(True)
        else:
            # False，离线，显示为红色
            self.auth_state_label.config(text=self.language_dict["Offline"], foreground="red")
            self.master.isOnline_var.set(False)

    def _changeConnectionStateButtonsState(self, state: bool):
        """更改展示服务器连通性的 state_label"""
        if state:
            str_state = "normal"
        else:
            str_state = "disable"
        self.login_button.config(state=str_state)
        self.register_button.config(state=str_state)

    def _changeInputEntriesState(self, state: bool):
        """更改输入框Entry的状态"""
        if state:
            state_str = "normal"
        else:
            state_str = "disable"
        self.password_entry.config(state=state_str)
        self.username_entry.config(state=state_str)
        self.remember_auth_checkbutton.config(state=state_str)

    def _testConnection(self):
        """测试连通性"""
        while True:
            status = Auth.testConnection()
            # status为bool，true为可连通服务器，false为无法连通
            if status:
                self.connection_state_label.config(
                    foreground="green",
                    text=self.language_dict["ConnectionGood"]
                )
                self._changeConnectionStateButtonsState(True)
            else:
                self.connection_state_label.config(
                    foreground="red",
                    text=self.language_dict["ConnectionBad"]
                )
                self._changeConnectionStateButtonsState(False)
                # 让界面恢复离线状态
                self.auth_state_label.config(
                    text=self.language_dict["Offline"],
                    foreground="red"
                )
                try:
                    self._logout()
                except:
                    pass
            sleep(2)

    def _changeLang(self, *args):
        """更改语言"""
        c.changeLang(self.lang_var.get())


class HeartbeatSender(Thread):
    def __init__(self):
        """向服务器发送状态，标明当前用户未因断网等情况还没来得及logout就离线了"""
        super().__init__(target=self._heartbeat)
        self._terminated = FALSE

    def _heartbeat(self):
        while not self._terminated:
            Auth.sendHeartbeatThenSleep()
