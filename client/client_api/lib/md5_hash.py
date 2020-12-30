import hashlib


def do_hash(file_path):
    """计算指定文件的md5 hash
    :param file_path: 文件的路径
    :return : hash（字符串）
    """
    with open(file_path, "rb")as f:
        cipher = f.read()
    return hashlib.md5(cipher).hexdigest()
