import os
from settings import *

HELLO = 'HELLO'
OK = "OK"
PREPARED = 'PREPARED'
DONE = "DONE"
REJECT = "REJECT"
BUFFER_SIZE = 1024  # 每次传输的数据包的size,根据需求调整,小了可能会很慢
TMP_DIR = "./TMP"

ZIP_FILEPATH = os.path.join(TMP_DIR, "{}.ZIP")
ENCRYPTED_FILEPATH = os.path.join(TMP_DIR, "EN_{}.ZIP")
RECEIVED_DIR = "./RECEIVED"
PLAIN_FILEPATH = os.path.join(RECEIVED_DIR, "{}")
LISTENING_ADDR = '0.0.0.0'
LISTENING_PORT = loadListeningPort()
MY_IP = loadMyIP()
