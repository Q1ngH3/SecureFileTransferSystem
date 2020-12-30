import requests
import settings.config as c
import json
from urllib import parse
from server_api.CONST import *
from client_api.CONST import *

# 重要！设置requests的请求不通过系统的全局代理
# 之后使用get或post都需要通过调用该session对象的方法
session = requests.Session()
session.trust_env = False

# 心跳频率
HEARTBEAT_FREQUENCY = 5 * 60


def updateInfo(public):
    """更新用户的信息
    MY_IP, LISTENING_PORT均从配置文件中获取
    :param public: 公钥

    """
    update_url = parse.urljoin(REMOTE_SERVER, "update_info")
    data = json.dumps({
        "public_key": public,
        "remote_addr": MY_IP,
        "remote_port": LISTENING_PORT
    })
    headers = {
        "Authorization": "JWT " + c.loadAuthToken()
    }
    response = session.post(url=update_url, headers=headers, data=data)
    print()


def getReceiverInfo(username):
    f_url = parse.urljoin(REMOTE_SERVER, "friends/list")
    headers = {
        "Authorization": "JWT " + c.loadAuthToken()
    }
    response = session.get(url=f_url, headers=headers)
    deserialized_content = json.loads(response.content)
    time_str = ''  # 形如：""
    for f in deserialized_content["friends"]:
        if f["main_user"]["username"] == username:

            p = f["main_user"]["public_key"], \
                f["main_user"]["remote_addr"], \
                f["main_user"]["remote_port"]
            return p
        elif f["friend"]["username"] == username:
            p = f["friend"]["public_key"], \
                f["friend"]["remote_addr"], \
                f["friend"]["remote_port"]
            return p


def authLogin(username: str, password: str):
    auth_info = dict()
    # 提取输入框中的username，password
    auth_info["username"] = username
    auth_info["password"] = password
    # 将认证所需的字典序列化为str
    json_auth_info = json.dumps(auth_info)
    # 登录时访问的url为host+/login
    login_url = parse.urljoin(REMOTE_SERVER, "/login")
    # 发起请求
    response = session.post(url=login_url, data=json_auth_info)
    # 解析返回的 json 字符串反序列化为 dict
    response_dict = json.loads(response.content)
    if response_dict["error_code"] == 0:
        return True, response_dict["auth"]
    else:
        return False, response_dict["error"]


def authActivate(username, code):
    activate_url = parse.urljoin(REMOTE_SERVER, "active")
    str_data = json.dumps({
        "username": username,
        "captcha_code": code
    })
    response = session.post(url=activate_url, data=str_data)
    response_dict = json.loads(response.content)
    if response_dict["error_code"] == 0:
        return 0, None
    else:
        return response_dict["error_code"], response_dict["error"]


def authLogout():
    logout_url = parse.urljoin(REMOTE_SERVER, "logout")
    d = dict()
    headers = {
        "Authorization": "JWT " + c.loadAuthToken()}
    serialized = json.dumps(d)
    try:
        response = session.get(url=logout_url, headers=headers, )
        if response.status_code == 200:
            return True
    except:
        pass
    return False


def authRegister(username, password, email):
    register_url = parse.urljoin(REMOTE_SERVER, "register")
    d = dict()
    d["username"] = username
    d["password"] = password
    d["email"] = email
    serialized = json.dumps(d)
    response = session.post(url=register_url, data=serialized)
    deserialized_content = json.loads(response.content)
    return deserialized_content["error_code"]


def testConnection():
    try:
        r = session.get(
            parse.urljoin(REMOTE_SERVER, "login"),
            timeout=1,
        )
        return True
    except Exception:
        return False


def sendHeartbeatThenSleep():
    heartbeat_url = parse.urljoin(REMOTE_SERVER, "heartbeat")
    headers = {
        "Authorization": "JWT " + c.loadAuthToken()
    }
    response = session.get(url=heartbeat_url, headers=headers)
    from time import sleep
    sleep(HEARTBEAT_FREQUENCY)


def isUserOnline(username):
    f_url = parse.urljoin(REMOTE_SERVER, "friends/list")
    headers = {
        "Authorization": "JWT " + c.loadAuthToken()
    }
    response = session.get(url=f_url, headers=headers)
    deserialized_content = json.loads(response.content)
    time_str = ''  # 形如：""
    for f in deserialized_content["friends"]:
        if f["main_user"]["username"] == username:
            if not ["main_user"]["online_status"]:
                return False
            time_str = f["main_user"]["last_active_time"]
            break
        elif f["friend"]["username"] == username:
            if not f["friend"]["online_status"]:
                return False
            time_str = f["friend"]["last_active_time"]
            break
    import time
    time_str = time_str.split("+")[0]
    timeArray = time.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    if int(time.time()) - timeStamp >= HEARTBEAT_FREQUENCY * 1.5:
        return False
    return True


def getUsernameByAuth():
    auth = c.loadAuthToken()
    url = parse.urljoin(loadRemoteServer(), "whoami")
    header = {
        "Authorization": "JWT "+auth
    }
    response = session.get(headers=header, url=url)
    if response.status_code == 200:
        content = json.loads(response.content)
        username = content["user"]["username"]
        return True, username
    else:
        return False, None
