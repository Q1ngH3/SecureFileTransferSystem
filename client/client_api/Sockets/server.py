from client_api.CONST import *
import socket
import json


class ServerSocket:
    def __init__(self):
        """封装了server用来监听的socket"""
        self.listening_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.listening_socket.bind((LISTENING_ADDR, LISTENING_PORT))
        self.connection_socket: socket.socket = None
        self.client_addr = None

    def listen(self, num):
        """调用listen_socket进行监听"""
        self.listening_socket.listen(num)

    def accept(self):
        """封装了socket.accept()方法"""
        try:
            self.connection_socket, self.client_addr = self.listening_socket.accept()
        except:
            pass

    def recvBasicInfo(self):
        basic_info = self.connection_socket.recv(BUFFER_SIZE).decode()
        basic_info_dict: dict = json.loads(basic_info)
        if "username" in basic_info_dict.keys() and "filename" in basic_info_dict.keys():
            return True, basic_info_dict
        else:
            return False, None

    def recvHELLO(self):
        """接收HELLO, 收到了返回true，否则返回false"""
        received_msg = self.connection_socket.recv(BUFFER_SIZE).decode()
        if received_msg == HELLO:
            return True
        else:
            return False

    def accept_prepared(self):
        """接收PREPARED, 预留，自定义的协议中未使用"""
        received_msg = self.connection_socket.recv(BUFFER_SIZE).decode()
        if received_msg == PREPARED:
            return True, None
        else:
            return False, None

    def recvIv(self):
        """接收iv值，iv为bytes
        :return : 一个元组，（True/False, msg/None)
        """
        received_msg = self.connection_socket.recv(BUFFER_SIZE)
        try:
            return True, received_msg
        except:
            return False, None

    def recvSize(self):
        """返回待接收文件的大小（数值）
        :return: int """
        received_msg = self.connection_socket.recv(BUFFER_SIZE).decode()
        try:
            size = int(received_msg)
            return True, size
        except:
            return False, None

    def recvAES(self):
        """接收AES:bytes，返回tuple"""
        received_msg = self.connection_socket.recv(BUFFER_SIZE)
        if received_msg:
            return True, received_msg
        else:
            return False, None

    def recvMsg(self, msg_size):
        """接收bytes类型的msg，返回tuple"""
        received_msg = self.connection_socket.recv(msg_size)
        if received_msg:
            return True, received_msg
        else:
            return False, None

    def recvMd5(self):
        """接收md5，返回tuple"""
        received_msg = self.connection_socket.recv(BUFFER_SIZE).decode()
        if received_msg:
            return True, received_msg
        else:
            return False, None

    def recvPublicKey(self):
        """接收加密方使用的公钥，返回tuple"""
        received_msg = self.connection_socket.recv(BUFFER_SIZE).decode()
        if received_msg:
            return True, received_msg
        else:
            return False, None

    def sendOK(self):
        """发送OK"""
        self.connection_socket.send(OK.encode())

    def sendDONE(self):
        """发送OK"""
        self.connection_socket.send(DONE.encode())

    def sendREJECT(self):
        """发送OK"""
        self.connection_socket.send(REJECT.encode())
