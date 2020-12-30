from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import random
import time
import hashlib


class AESCryptor(object):
    def __init__(self, key, iv):
        """类初始化
        :param key: 密钥（字节流）
        :param iv: CBC模式中使用的 IV
        """
        self.key = key
        self.mode = AES.MODE_CBC
        self.iv = iv  # iv值采用会话密钥同样的生成办法。【需要传给接收方】
        self.cryptor = AES.new(self.key, self.mode, self.iv)

    def encrypt(self, plain_file_path, cipher_file_path):
        """加密函数
        :param plain_file_path: 待加密文件的路径
        :param cipher_file_path: 加密后文件的路径
        """

        # 这里密钥key长度应该为16（AES-128）, 24（AES-192）,或者32 （AES-256）Bytes 长度

        # 如果text不足16位就用空格补足为16位，如果大于16当时不是16的倍数，那就补足为16的倍数。
        length = 16
        with open(plain_file_path, "rb")as f:
            plaintext = f.read()
        plaintext_len = len(plaintext)
        padding_len = (16 - plaintext_len % 16) % 16
        plaintext += b' ' * padding_len
        ciphertext = self.cryptor.encrypt(plaintext)
        # 统一把加密后的字符串转化为16进制字符串
        with open(cipher_file_path, "wb")as f:
            f.write(ciphertext)

    def decrypt(self, cipher_file_path, plain_file_path, ):
        """
        解密函数
        :param cipher_file_path: 加密的文件的路径
        :param plain_file_path: 待加密文件的路径
        """
        with open(cipher_file_path, "rb")as f:
            ciphertext = f.read()
            plaintext = self.cryptor.decrypt(ciphertext)
        with open(plain_file_path, "wb")as f:
            f.write(plaintext)


def get_session_key(length=16, secret_key=None, allowed_chars=None):
    """会话密钥生成函数
    :param length: 会话密钥长度，AES-128密钥长度16位
    :param secret_key: 可以添加用户自身信息，也可采用默认值
    :param allowed_chars: 用于设置会话密钥的字符集
    :return:length长度的会话密钥
    """
    if secret_key is None:
        secret_key = "BUPT_FileTransfer_made_by_5_guys"
    if allowed_chars is None:
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)~`"

    random.seed(
        hashlib.sha256(
            ("%s%s%s" % (
                random.getstate(),
                time.time(),
                secret_key)).encode('utf-8')
        ).digest())

    ret = ''.join(random.choice(allowed_chars) for i in range(length))

    return ret.encode()



