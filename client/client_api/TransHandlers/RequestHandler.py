from gui.SubWindows import RecvWindow
from client_api.Sockets import server
from tkinter.messagebox import *
import settings.config as c
from threading import Thread
from client_api.CONST import *
import os
from time import time
from client_api.lib import compress, RSAkey, crypt, md5_hash
import shutil


class FileTransRequestHandler:
    def __init__(self, master, ):
        """处理文件接收事件
        在用户 Login 后实例化，监听端口，收到请求并完成握手后，弹窗，接收文件
        :param master: 弹出含有进度条的子窗口时需要指定 master
        """
        # 初始化 
        self.master = master
        self.server_socket = server.ServerSocket()
        self.server_socket.listen(5)

        # 几个需要在随后使用到的变量
        self.new_win: RecvWindow = None
        self.RECEIVED = b''
        self.alive = True

    def popWindow(self):
        """确认要接收文件时，弹出此窗口"""
        if self.new_win:
            # 如果new_win已经出现过，则报错
            showerror(message=c.loadLangDict()["OnlyOneTransPermitted"])
            return False
        else:
            self.new_win = RecvWindow(self.master)
            return True

    def startListenThread(self):
        """新建一个线程，处理文件接收"""
        t = Thread(target=self._provideService)
        t.start()

    def _provideService(self):
        """真正处理文件接收的函数，由 startListenThread 调用"""
        while self.alive:
            try:
                # 接收对 socket 的请求
                self.server_socket.accept()
                # 如果第一条不是HALLO, 则不继续处理
                if not self.server_socket.recvHELLO():
                    continue
                self.server_socket.sendOK()

                # 接收发送方的基本信息
                state, info = self.server_socket.recvBasicInfo()
                info: dict
                if not state:
                    continue
                else:
                    pass
                # 弹窗，询问用户是否接收
                choice = askyesno(
                    title=c.loadLangDict()["Notice"],
                    message=c.loadLangDict()["TransRequestTemplate"].format(info["username"], info["filename"]))
                # 如果选择不接收，发送 REJECT 并 continue，接收的话就发送 OK
                if not choice:
                    self.server_socket.sendREJECT()
                    continue
                else:
                    self.server_socket.sendOK()

                # 弹出接收窗口
                state = self.popWindow()
                # 弹窗中发生了错误，直接continue
                if not state:
                    continue
                # 进度条+10%
                self.new_win.exchange_progressbar.changeProgressByPercentage(0.1)

                # 接受file_size
                state, size = self.server_socket.recvSize()
                # 接受错误
                if not state:
                    self._popErrorMsg()
                    continue
                self.FILE_SIZE = int(size)
                # 进度条+20%
                self.new_win.exchange_progressbar.changeProgressByPercentage(0.2)
                # 发送OK
                self.server_socket.sendOK()

                # 接收加密方使用的公钥
                state, self.public_key = self.server_socket.recvPublicKey()
                if not state:
                    self._popErrorMsg()
                    continue
                self.server_socket.sendOK()
                # 从自己的私钥环中找到此公钥对应的私钥
                self.private_key = c.loadProperPrivateKey(self.public_key, c.loadUsernamePassword()[0])

                # 接受AES_KEY
                state, AES_KEY = self.server_socket.recvAES()
                if not state:
                    raise Exception
                # 进度条+30%，发送OK
                self.new_win.exchange_progressbar.changeProgressByPercentage(0.2)
                self.AES_KEY = AES_KEY
                self.server_socket.sendOK()

                # 接收iv
                state, IV = self.server_socket.recvIv()
                if not state:
                    raise Exception
                self.IV = IV
                self.new_win.exchange_progressbar.changeProgressByPercentage(0.2)
                self.server_socket.sendOK()

                # 接受HASH
                state, received_hash = self.server_socket.recvMd5()
                if not state:
                    self._popErrorMsg()
                    continue
                # 进度条+30%
                self.new_win.exchange_progressbar.changeProgressByPercentage(0.29)
                self.server_socket.sendOK()

                # 开始接收文件
                RECEIVED_SIZE = 0
                RECEIVED = b''
                while RECEIVED_SIZE < self.FILE_SIZE:
                    state, newly_received = self.server_socket.recvMsg(BUFFER_SIZE)
                    if not state:
                        break
                    RECEIVED += newly_received
                    RECEIVED_SIZE += len(newly_received)
                    self.new_win.recv_state_progressbar. \
                        changeProgressByPercentage(
                        (len(newly_received) / self.FILE_SIZE), pause=False)
                    self.server_socket.sendOK()

                # 开始进行解密操作
                if not os.path.exists(RECEIVED_DIR):
                    os.mkdir(RECEIVED_DIR)
                if not os.path.exists(TMP_DIR):
                    os.mkdir(TMP_DIR)
                self.IV = RSAkey.rsa_decrypt(self.private_key, self.IV)
                self.AES_KEY = RSAkey.rsa_decrypt(self.private_key, self.AES_KEY)
                self._AES = crypt.AESCryptor(self.AES_KEY, self.IV)

                # 初始化路径
                self.encrypted_file_path = ENCRYPTED_FILEPATH.format(str(time()))
                self.zip_file_path = ZIP_FILEPATH.format(info["filename"])
                self.plain_file_path = PLAIN_FILEPATH.format(info["filename"])
                self.new_win: RecvWindow
                self.new_win.save_file_progressbar.changeProgressByPercentage(0.2)
                # 将加密的文件写入 encrypted_file_path
                with open(self.encrypted_file_path, "wb")as f:
                    f.write(RECEIVED)
                self.new_win.save_file_progressbar.changeProgressByPercentage(0.1)
                # 验证hash
                _hash = md5_hash.do_hash(self.encrypted_file_path)
                if not _hash == received_hash:
                    self._popErrorMsg("HashError")
                    return
                self.new_win.save_file_progressbar.changeProgressByPercentage(0.1)
                # 解密文件
                self._AES.decrypt(self.encrypted_file_path, self.zip_file_path)
                self.new_win.save_file_progressbar.changeProgressByPercentage(0.2)
                # 解压缩文件
                compress.file_decompress(self.zip_file_path, self.plain_file_path)
                self.new_win.save_file_progressbar.changeProgressByPercentage(0.2)

                # 销毁new_win
                self.new_win.save_file_progressbar.changeProgressByPercentage(0.2)
                self.new_win: RecvWindow.destrop()
                self.new_win = None

                # 删除TMP
                shutil.rmtree(TMP_DIR)
                showinfo(
                    message=loadLangDict()["Succeed"] + loadLangDict()["FileSavedTo"] + self.plain_file_path)

            except Exception as e:
                if self.alive:
                    self._popErrorMsg()
                    self.new_win: RecvWindow.destroy()
                    self.new_win = None

    @staticmethod
    def _popErrorMsg(msg="TransError"):
        """出错时弹窗"""
        showerror(message=c.loadLangDict()[msg])

    def stop(self):
        """注销时调用stop，结束监听的线程"""
        self.alive = False
        self.server_socket.listening_socket.close()
