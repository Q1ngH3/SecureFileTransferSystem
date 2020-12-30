from client_api.CONST import *
import socket
import json
from functools import wraps


class ClientSocket:
    def __init__(self, server_ip, ):
        """与server_ip建立连接，并封装了各种进行报文交换的方法"""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, LISTENING_PORT))

    def checkFeedback(unwrapped_function):
        """一个装饰器，发包后检查是否返回了 OK"""

        @wraps(unwrapped_function)
        def wrapped(self_, *args, **kwargs):
            unwrapped_function(self_, *args, **kwargs)
            feedback = self_.client_socket.recv(BUFFER_SIZE).decode()

            if feedback == OK:
                return True
            else:
                return False

        return wrapped

    @checkFeedback
    def sendHELLO(self):
        """发送 HELLO"""
        self.client_socket.send(HELLO.encode())

    @checkFeedback
    def sendBasicInfo(self, username, filename):
        """发送username和filename"""
        self.client_socket.send(
            json.dumps({"username": username, "filename": filename}).encode()
        )

    @checkFeedback
    def sendSize(self, size):
        """发送传输文件的大小"""
        self.client_socket.send(
            str(size).encode()
        )

    @checkFeedback
    def sendHash(self, _hash):
        """发送HASH值"""
        self.client_socket.send(
            _hash.encode()
        )

    @checkFeedback
    def sendIv(self, iv: bytes):
        """发送IV值"""
        self.client_socket.send(
            iv
        )

    @checkFeedback
    def sendAesKey(self, key: bytes):
        """发送AES"""
        self.client_socket.send(
            key
        )

    @checkFeedback
    def sendMsg(self, msg: bytes):
        """发送字节流的msg"""
        self.client_socket.send(
            msg
        )

    @checkFeedback
    def sendPublicKey(self, key: str):
        """发送公钥"""
        self.client_socket.send(
            key.encode()
        )
