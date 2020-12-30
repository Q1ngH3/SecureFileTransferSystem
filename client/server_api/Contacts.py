import requests
from urllib import parse
from server_api.CONST import *
from settings import config
import json

session = requests.Session()
session.trust_env = False


def getMyName():
    _url = parse.urljoin(REMOTE_SERVER, "whoami")
    headers = {
        "Authorization": "JWT " + config.loadAuthToken()
    }
    response = session.get(url=_url, headers=headers)
    deserialized_content = json.loads(response.content)
    return deserialized_content["user"]["username"]


def getContactRequestList():
    """

    :return: 第一个是true or false，第二个是一个列表，列表里是元组，第一个参数是发送者的username，第二个参数是relation_id
    """
    request_list_url = parse.urljoin(REMOTE_SERVER, "friends/request/list")
    headers = {
        "Authorization": "JWT " + config.loadAuthToken()
    }
    response = session.get(url=request_list_url, headers=headers)
    deserialized_content = json.loads(response.content)
    if deserialized_content["error_code"] == 0:

        request_list = []
        for r in deserialized_content["request_list"]:
            request_list.append(
                (r["main_user"]["username"], r["relation_id"])
            )
        return True, request_list
    return False, None


def sendContactRequest(username):
    send_request_url = parse.urljoin(REMOTE_SERVER, "friends/add")
    headers = {
        "Authorization": "JWT " + config.loadAuthToken()
    }
    data = json.dumps({"username": username})
    response = session.post(url=send_request_url, data=data, headers=headers)
    deserialized_content = json.loads(response.content)
    return deserialized_content["error_code"]


def acceptRequest(relation_id):
    accept_url = parse.urljoin(REMOTE_SERVER, "friends/request/commit")
    data = json.dumps({"relation_id": relation_id})
    headers = {
        "Authorization": "JWT " + config.loadAuthToken()
    }
    response = session.post(url=accept_url, headers=headers, data=data)
    deserialized_content = json.loads(response.content)
    return deserialized_content["error_code"] == 0


def getContactList():
    get_contact_list_url = parse.urljoin(REMOTE_SERVER, "friends/list")
    headers = {
        "Authorization": "JWT " + config.loadAuthToken()
    }
    response = session.get(url=get_contact_list_url, headers=headers)
    deserialized_content = json.loads(response.content)
    if deserialized_content["error_code"] == 0:
        contact_list = []
        my_name = getMyName()
        for f in deserialized_content["friends"]:
            main_username = f["main_user"]["username"]
            friend_username = f["friend"]["username"]
            if main_username == getMyName():
                contact_list.append(friend_username)
            else:
                contact_list.append(main_username)
        return True, contact_list
    else:
        return False, None
