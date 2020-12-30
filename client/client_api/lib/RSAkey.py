import rsa
from rsa import *


def rsa_key_generate():
    """产生公钥私钥，返回str形式的公私钥元组
    :return: （PublicKey对象）公钥，（PrivateKey对象）私钥
    """
    pub_key, pri_key = rsa.newkeys(1024)

    return str(pub_key), str(pri_key)


def rsa_encrypt(public_key, plain_text):
    """RSA公钥加密
    :param public_key: 公钥,字符串形式
    :param plain_text: 明文 bytes   TODO:RSA加密的是会话密钥，会话密钥随机生成是否为正常字符串？
    :return: 密文（字节流）
    """
    global pub, pla, a
    pub = public_key
    pla = plain_text
    exec('a =  rsa.encrypt(pla, {})'.format(pub), globals())
    return a


def rsa_decrypt(private_key, cipher_text):
    """
    RSA私钥解密
    :param private_key: 私钥
    :param cipher_text: 密文（字节流）
    :return: 明文（字节流）
    """
    global pri, ciph, a
    pri = private_key
    ciph = cipher_text
    exec('a =  rsa.decrypt(ciph, {})'.format(pri), globals())
    return a

