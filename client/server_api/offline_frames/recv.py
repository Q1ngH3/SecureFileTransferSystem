from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import *
from base64 import b64decode, b64encode
from server_api import Auth, Contacts, Offline
from client_api.CONST import *
from client_api.lib import compress, RSAkey, crypt
import os


class RecvFrame(LabelFrame):
    def __init__(self, master):
        super().__init__(master, text=config.loadLangDict()["OfflineRecv"])
        self.refresh_state_label = Label(self)
        self.choice_var = IntVar(self)
        self.single_recv_list = []
        self.refresh_button = Button(
            self, text=config.loadLangDict()["Refresh"], command=self.refresh_request)
        self.path_var = StringVar(self)
        self.sel_path_button = Button(
            self,
            text=config.loadLangDict()["SelectPath"],
            command=lambda: self.path_var.set(askdirectory())
        )
        self.path_label = Label(self, textvariable=self.path_var)
        self.save_button = Button(
            self,
            text=config.loadLangDict()["Save"],
            command=self._save
        )
        self.delete_button = Button(
            self,
            text=config.loadLangDict()["Delete"],
            foreground="red",
            command=self._delete
        )

    def refresh_request(self):
        self._unpack()
        status, requests = Offline.listRequests(Auth.getUsernameByAuth()[1])
        r_list = requests["list"]
        cnt = 0
        if status:
            if not r_list:
                self.refresh_state_label.config(
                    foreground="green",
                    text=config.loadLangDict()["NoRequests"]
                )
            for r in r_list:
                sender = r["sender"]
                receiver = r["recver"]
                filename = r["filename"]
                iv = r["iv"]
                pub_key = r["pub_key"]
                aes = r["rsa_session_key"]
                f = _SingleRecvFrame(
                    self,
                    self.choice_var,
                    cnt,
                    sender,
                    receiver,
                    filename,
                    pub_key,
                    iv,
                    aes
                )
                self.single_recv_list.append(f)
                cnt += 1
            self.refresh_state_label.config(
                foreground="green",
                text=config.loadLangDict()["RefreshSucceed"]
            )
        else:
            self.refresh_state_label.config(
                foreground="red",
                text=config.loadLangDict()["RefreshFailed"]
            )
        self.pack()

    def pack(self):
        self.refresh_state_label.pack()
        for s in self.single_recv_list:
            s.pack()
        self.refresh_button.pack()
        self.sel_path_button.pack()
        self.path_label.pack()
        self.save_button.pack()
        self.delete_button.pack()
        super().pack()

    def _delete(self):
        choice = self.choice_var.get()
        f = self.single_recv_list[choice]
        Offline.receiveFile(f.sender, f.receiver, f.filename)[1]
        self.refresh_request()

    def _save(self):
        try:
            if not os.path.exists(TMP_DIR):
                os.mkdir(TMP_DIR)
            save_path = self.path_var.get()
            if not os.path.exists(save_path):
                showerror(title=loadLangDict()["Error"],
                          message=loadLangDict()["PathNotExist"])
                return
            choice = self.choice_var.get()
            f: _SingleRecvFrame = self.single_recv_list[choice]
            private_key = loadProperPrivateKey(f.b64_public_k, f.receiver)
            aes_key = RSAkey.rsa_decrypt(private_key, b64decode(f.b64_aes.encode()))
            iv = RSAkey.rsa_decrypt(private_key, b64decode(f.b64_iv.encode()))
            aes = crypt.AESCryptor(aes_key, iv)
            encrypted_path = ENCRYPTED_FILEPATH.format(f.filename)
            zipped_path = ZIP_FILEPATH.format(f.filename)
            plain_path = os.path.join(save_path, f.filename)
            with open("recv_key", "wb")as fi:
                fi.write(b"aes:" + aes_key + b"\n" + iv)

            with open(encrypted_path, "wb")as fi:
                C = Offline.receiveFile(f.sender, f.receiver, f.filename)[1]
                fi.write(C)
            aes.decrypt(encrypted_path, zipped_path)
            compress.file_decompress(zipped_path, plain_path)
            showinfo(title=loadLangDict()["Succeed"],
                     message=loadLangDict()["FileSavedTo"] + plain_path)
        except Exception as e:
            raise e
            showerror(title=loadLangDict()["Error"],
                      message=loadLangDict()["SaveFailed"])
        self.refresh_request()

    def _unpack(self):
        self.refresh_state_label.pack_forget()
        for s in self.single_recv_list:
            s.destroy()
        self.single_recv_list = []
        self.refresh_button.pack_forget()
        self.sel_path_button.pack_forget()
        self.path_label.pack_forget()
        self.save_button.pack_forget()
        self.delete_button.pack_forget()


class _SingleRecvFrame(Frame):
    def __init__(self, master, var, value, sender, receiver, filename, public_key, iv, aes_key):
        super().__init__(master)
        self.radio_button = Radiobutton(self, variable=var, value=value)
        self.sender_label = Label(self, text=sender)
        self.sender = sender
        self.receiver = receiver
        self.filename = filename
        self.filename_label = Label(self, text=filename)
        self.b64_public_k = public_key
        self.b64_iv = iv
        self.b64_aes = aes_key

    def pack(self):
        super().pack()
        self.radio_button.grid(row=0, column=0)
        self.sender_label.grid(row=0, column=1)
        self.filename_label.grid(row=0, column=2)
