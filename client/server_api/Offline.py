import settings
from urllib import parse
import requests
import json

server, port = settings.loadOfflineTransServerInfo()
session = requests.Session()
session.trust_env = False


def sendFile(sender, receiver, filename, rsa_session_key, iv, pub_key, file_content):
    url = parse.urljoin(server, "transfer")
    d = {
        "sender": sender,
        "recver": receiver,
        "filename": filename,
        "rsa_session_key": rsa_session_key,
        "iv": iv,
        "pub_key": pub_key,
        "file_content": file_content
    }
    response = session.post(url=url, data=json.dumps(d), )
    print(json.dumps(d))
    return response.status_code == 200


def listRequests(username):
    url = parse.urljoin(server, "query")
    d = {
        "username": username
    }
    response = session.post(url=url, data=json.dumps(d), )
    if response.status_code == 200:
        tmp = '{"list":' + response.content.decode() + "}"
        tmp = json.loads(tmp.replace("'", '"'))
        return True, tmp
    else:
        return False, None


def receiveFile(sender, receiver, filename):
    url = parse.urljoin(server, "recvive")
    d = {
        "sender": sender,
        "recver": receiver,
        "filename": filename
    }
    response = session.post(url=url, data=json.dumps(d))
    if response.status_code == 200:
        from base64 import b64decode
        j = json.loads(response.content)
        return True, b64decode(j["file_content"].encode())
    else:
        return False, None
