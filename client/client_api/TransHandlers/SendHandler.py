from client_api.Sockets import client
from settings import config
from client_api.lib import compress, RSAkey, crypt, md5_hash
from tkinter.messagebox import *
from client_api.CONST import *
from gui.SubWindows import SendWindow
import time
import os
from threading import Thread


class FileTransSendHandler:
    def __init__(
            self, master, server_ip, username,
            filename, filepath, rsa_pk, ):
        """处理文件发送事件
        在点击发送按钮后实例化，与 server_ip 建立通信，加密文件及相关信息后，握手、交换共享信息、传送文件
        :param master: 弹出含有进度条的子窗口时需要指定 master
        :param server_ip: 接收方的 ip 地址
        :param username: 发送方的用户名，握手阶段提供
        :param filename: 待发送的文件名，握手阶段提供
        :param filepath: 待发送的文件，点击发送按钮时已对文件的存在性进行了验证
        :param rsa_pk: 接收方的 RSA 公钥
        """

        # 初始化
        self.master = master
        self.client_socket = client.ClientSocket(server_ip, )
        self.username = username
        self.filename = filename
        self.filepath = filepath
        self.rsa_pk = rsa_pk
        # 压缩、解密的文件都放在临时文件夹中
        if not os.path.exists(TMP_DIR):
            os.mkdir(TMP_DIR)
        self.compressed_file_path = ZIP_FILEPATH.format(self.filename)
        self.encrypted_file_path = ENCRYPTED_FILEPATH.format(self.filename)

        # aes初始化
        self.aes_key = crypt.get_session_key(secret_key=str(time.time()) + self.username + self.filename)
        self.aes_iv = crypt.get_session_key(secret_key=str(time.time()))
        self.aes = crypt.AESCryptor(self.aes_key, self.aes_iv)
        self.new_win = None

    def startSending(self):
        """新建一个线程，开始发送（防止ui无响应）"""
        t = Thread(target=self._send)
        t.start()

    def _send(self):
        """实际进行与接收方客户端通信的方法，由 startSending 方法新建一个线程来调用"""
        # 弹出有 progressbar 的窗口
        self.new_win: SendWindow
        self.popWindow()

        # 文件处理
        self.compressFile()
        self.new_win.process_file_progressbar.changeProgressByPercentage(0.2)
        self.encryptFile()
        self.new_win.process_file_progressbar.changeProgressByPercentage(0.2)

        # 计算加密后文件的大小
        file_size = os.path.getsize(self.encrypted_file_path)

        # 做个hash，进行完整性校验
        _hash = self.hashEncryptedFile()
        self.new_win.process_file_progressbar.changeProgressByPercentage(0.2)

        # 加密会话密钥和 iv 初始值
        encrypted_iv = self.rsaEncrypt(self.aes_iv)
        encrypted_aes_key = self.rsaEncrypt(self.aes_key)
        self.new_win.process_file_progressbar.changeProgressByPercentage(0.2)

        # 开启一个文件io，用以读出二进制数据
        encrypted_file_io = open(self.encrypted_file_path, "rb")
        self.new_win.process_file_progressbar.changeProgressByPercentage(0.18)

        # 握手
        state = self.client_socket.sendHELLO()
        if not state:
            return self._error()
        self.new_win.exchange_progressbar.changeProgressByPercentage(0.2)

        # 发送发送方的基本信息，即 username 和 filename
        state = self.client_socket.sendBasicInfo(self.username, self.filename)
        if not state:
            # 此处弹出的错误对话框应为 "Denied"
            return self._error(msg="Denied")
        self.new_win.exchange_progressbar.changeProgressByPercentage(0.2)

        # 发送文件的大小
        state = self.client_socket.sendSize(file_size)
        if not state:
            return self._error()
        self.new_win.exchange_progressbar.changeProgressByPercentage(0.1)

        # 发送使用的公钥，防止接收方不能正确找到对应的私钥进行解密
        state = self.client_socket.sendPublicKey(self.rsa_pk)
        if not state:
            return self._error()
        self.new_win.exchange_progressbar.changeProgressByPercentage(0.1)

        # 发送加密后的aes密钥
        state = self.client_socket.sendAesKey(encrypted_aes_key)
        if not state:
            return self._error()
        self.new_win.exchange_progressbar.changeProgressByPercentage(0.1)

        # 发送iv值
        state = self.client_socket.sendIv(encrypted_iv)
        if not state:
            return self._error()
        self.new_win.exchange_progressbar.changeProgressByPercentage(0.1)

        # 发送hash
        state = self.client_socket.sendHash(_hash)
        if not state:
            return self._error()
        self.new_win.exchange_progressbar.changeProgressByPercentage(0.1999)

        # 准备进行文件传输了，每次从 io 中读出 BUFFER_SIZE 的字节
        tmp_data = encrypted_file_io.read(BUFFER_SIZE)
        while tmp_data:
            state = self.client_socket.sendMsg(tmp_data)
            if not state:
                return self._error()
            # 进度条增加相应的量
            self.new_win.send_state_progressbar.changeProgressByPercentage(
                (len(tmp_data) - 1) / file_size, pause=False
            )
            tmp_data = encrypted_file_io.read(BUFFER_SIZE)
        showinfo(message=loadLangDict()["SendSucceed"])

    def popWindow(self):
        """弹出含有进度条的窗口"""
        if self.new_win:
            # 如果new_win已经出现过，则报错
            showerror(message=config.loadLangDict()["OnlyOneTransPermitted"])
            return False
        else:
            self.new_win = SendWindow(self.master)
            return True

    def compressFile(self):
        """封装了文件压缩的过程"""
        compress.file_compress(self.filepath, self.compressed_file_path)

    def rsaEncrypt(self, content):
        """封装了 rsa 加密的过程"""
        return RSAkey.rsa_encrypt(self.rsa_pk, content)

    def hashEncryptedFile(self, ):
        """封装了做 HASH 的过程"""
        return md5_hash.do_hash(self.encrypted_file_path)

    def encryptFile(self):
        """封装了文件加密的过程"""
        self.aes.encrypt(self.compressed_file_path, self.encrypted_file_path)

    @staticmethod
    def _error(msg="TransError"):
        """错误处理，弹出错误窗口"""
        showerror(title=config.loadLangDict()["Error"],
                  message=config.loadLangDict()[msg])
