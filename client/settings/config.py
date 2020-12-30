import json
import os
from tkinter.messagebox import showerror
import base64

SETTINGS_FILENAME = "./settings/settings.json"
LANG_DIR = "./settings/Languages"


def loadLangList():
    try:
        lang_list = os.listdir(LANG_DIR)
    except:
        showerror(title="错误！", message="Languages文件夹丢失！程序无法启动", )
        exit(1)
    for i in range(len(lang_list)):
        this_lang = lang_list[i]
        lang_list[i] = this_lang.split(".")[0]
    return lang_list


default_dict = {
    "Language": loadLangList()[0],
    "Auth": "",
    "Username": "",
    "Password": "",
    "RememberAuth": False,
    "RemoteServer": "http://192.168.31.217",
    "OfflineTransServer": "http://192.168.31.217",
    "OfflineTransPort": 5000,
    "MyIP": "",
    "ListeningPort": 12345,
    "UserKeys": []

}
USER_KEY = {
    "username": "",
    "keys": []

}


def checkIntegrity(d: dict):
    for key in default_dict.keys():
        if key not in d.keys():
            return False
    return True


def loadMyIP():
    settings = loadSettings()
    return settings["MyIP"]


def loadOfflineTransServerInfo():
    settings = loadSettings()
    return settings["OfflineTransServer"], settings["OfflineTransPort"]


def loadListeningPort():
    settings = loadSettings()
    return settings["ListeningPort"]


def loadRemoteServer():
    settings = loadSettings()
    return settings["RemoteServer"]


def loadSettings():
    try:
        with open(SETTINGS_FILENAME, "r", encoding="utf-8") as f:
            parsed_result = json.load(f)
        if checkIntegrity(parsed_result):
            return parsed_result
        else:
            raise Exception
    except:
        with open(SETTINGS_FILENAME, "w")as f:
            json.dump(obj=default_dict, fp=f, ensure_ascii=False)
        return default_dict


def loadLang():
    settings = loadSettings()
    return settings["Language"]


def loadLangDict():
    lang = loadLang()
    with open(os.path.join(LANG_DIR, lang + ".json"), "r", encoding="utf-8")as f:
        lang_dict = json.load(f)
    return lang_dict


def loadUsernamePassword():
    d = loadSettings()
    return d["Username"], d["Password"]


def loadRememberPasswordOption():
    d = loadSettings()
    return d["RememberAuth"]


def loadAuthToken():
    d = loadSettings()
    return d["Auth"]


def loadProperPrivateKey(public, username):
    settings = loadSettings()
    user_key_list = settings["UserKeys"]
    for user_key in user_key_list:
        if user_key["username"] == username:
            for k in user_key["keys"]:
                if k[0] == public:
                    return k[1]


def saveSettings(new_settings: dict):
    with open(SETTINGS_FILENAME, "w")as f:
        json.dump(new_settings, f, ensure_ascii=False)


def changeKeys(public, private, username):
    settings = loadSettings()

    user_key_list = settings["UserKeys"]
    for user_key in user_key_list:
        if user_key["username"] == username:
            if len(user_key["keys"]) == 999:
                user_key["keys"].pop(0)
            user_key["keys"].append((public, private))
            saveSettings(settings)
            return
    new_user_key = USER_KEY.copy()
    new_user_key["username"] = username
    new_user_key["keys"].append((public, private))
    settings["UserKeys"].append(new_user_key)
    saveSettings(settings)


def changeLang(new_lang: str):
    settings = loadSettings()
    settings["Language"] = new_lang
    saveSettings(settings)


def changeAuthTokens(auth_token):
    d = loadSettings()
    d["Auth"] = auth_token
    saveSettings(d)


def changeRememberAuthOption(new_option):
    d = loadSettings()
    d["RememberAuth"] = new_option
    saveSettings(d)


def changeUserPass(username, password):
    d = loadSettings()
    d["Password"] = password
    d["Username"] = username
    saveSettings(d)
