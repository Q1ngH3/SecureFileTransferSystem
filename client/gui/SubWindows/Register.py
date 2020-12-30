from threading import Thread
from tkinter import *
import settings.config as c
from server_api import Auth


class RegisterWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        # 初始化各种组件
        # 通知，正确状态下不显示，当出错时显示
        self.announcement_label = Label(self, text='')
        # 用户名label及entry
        self.new_username_label = Label(self, text=c.loadLangDict()["Username"])
        self.new_username_var = StringVar(self)
        self.new_username_entry = Entry(
            self, textvariable=self.new_username_var
        )
        # 密码label及entry
        self.new_password_label = Label(self, text=c.loadLangDict()["Password"])
        self.new_password_var = StringVar(self)
        self.new_password_entry = Entry(
            self, textvariable=self.new_password_var
        )
        # 确认密码label及entry
        self.confirm_password_label = Label(self, text=c.loadLangDict()["ConfirmPassword"])
        self.confirm_password_var = StringVar(self)
        self.confirm_password_entry = Entry(
            self, textvariable=self.confirm_password_var
        )
        self.submit_button = Button(
            self,
            text=c.loadLangDict()["Confirm"],
            command=self._submit
        )
        # 邮箱的label及entry
        self.email_label = Label(
            self,
            text=c.loadLangDict()["Email"]
        )
        self.email_var = StringVar(self)
        self.email_entry = Entry(self, textvariable=self.email_var)
        # 获取验证码的button
        self.activate_code_button = Button(
            self,
            text=c.loadLangDict()["GetActivateCode"],
            command=self._getActivateCode
        )
        # 验证码的label和entry
        self.code_label = Label(
            self,
            text=c.loadLangDict()["ActivateCode"]
        )
        self.code_var = StringVar(self)
        self.code_entry = Entry(
            self,
            textvariable=self.code_var
        )
        # 组件布局
        self.announcement_label.pack()
        self.new_username_label.pack()
        self.new_username_entry.pack()

        self.new_password_label.pack()
        self.new_password_entry.pack()

        self.confirm_password_label.pack()
        self.confirm_password_entry.pack()

        self.email_label.pack()
        self.email_entry.pack()
        self.activate_code_button.pack()

        self.code_label.pack()
        self.code_entry.pack()
        self.submit_button.pack()

        # 开辟一个线程

    def _submit(self, *args):
        error_code, msg = Auth.authActivate(self.new_username_var.get(), self.code_var.get())
        if error_code == 0:
            self.announcement_label.config(
                foreground="green",
                text=c.loadLangDict()["Activated"]
            )
        else:
            self.announcement_label.config(
                foreground="red",
                text=msg
            )

    def _getActivateCode(self):
        if self._checkIntegrity():
            error_code = Auth.authRegister(self.username, self.password1, self.email)
            if error_code == 0:
                self.announcement_label.config(
                    foreground="green",
                    text=c.loadLangDict()["RegisterSucceed"]
                )
            else:
                self.announcement_label.config(
                    foreground="red",
                    text=c.loadLangDict()["RegisterFailed"]
                )

    def _checkIntegrity(self):
        self.username = self.new_username_var.get()
        self.password1 = self.new_password_var.get()
        self.password2 = self.confirm_password_var.get()
        self.email = self.email_var.get()
        # 有空余项
        if not (self.username and self.password1 and self.password2):
            self._dealEmptyEntry()
            return False
        # 俩密码不一致
        elif not self.password1 == self.password2:
            self._dealPassNotEqual()
            return False
        else:
            pass
        return True

    def _dealEmptyEntry(self):
        self.announcement_label.config(
            text=c.loadLangDict()["EntriesNotFilled"],
            foreground="red"
        )

    def _dealUsernameNotAvailable(self):
        self.announcement_label.config(
            text=c.loadLangDict()["UsernameDuplicates"],
            foreground="red"
        )

    def _dealPassNotEqual(self):
        self.announcement_label.config(
            text=c.loadLangDict()["PassNotEqual"],
            foreground="red"
        )

    def _dealRegisterSuccess(self):
        self.announcement_label.config(
            text=c.loadLangDict()["RegisterSucceed"],
            foreground="green"
        )


class _MyThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
