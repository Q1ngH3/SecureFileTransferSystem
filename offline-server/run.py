#coding:utf-8
from flask import Flask,request
import json,random,string
import sys,os,time
from database import app,db,Request_list

app.config["DEBUG"] = False

SUCCESS = {"return code" : 0}

def ranstr(num):
    salt = ''.join(random.sample(string.ascii_letters + string.digits, num))
    return salt

'''
example:
{
    "sender" : "xxxx",
    "recver" : "xxxx",
    "filename" : "xxxx",
    "rsa_session_key" : "xxxx",
    "iv" : "xxxx",
    "pub_key" : "xxxx",
    "file_content" : "xxxx"
}
'''
@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_data().decode()
    data = json.loads(data)
    # 取出数据
    sender = data['sender']
    recver = data['recver']
    filename = data['filename']
    rsa_session_key = data['rsa_session_key']
    iv = data['iv']
    pub_key = data['pub_key']
    file_content = data['file_content']

    if os.path.exists('upload/'+filename):
        filename = filename + '_' + ranstr(4)
    
    tmp = Request_list(sender=sender,recver=recver,filename=filename,rsa_session_key=rsa_session_key,iv=iv,pub_key=pub_key)
    db.session.add(tmp)
    db.session.commit()

    with open('upload/'+filename,'wb') as f:
        f.truncate()
        f.write(file_content.encode())
    
    ret = {
        'server_filename' : filename
    }

    return ret


'''
example:
{
    "username" = "xxxxx" 
}
'''
@app.route('/query', methods=['POST'])
def query():
    data = request.get_data().decode()
    data = json.loads(data)
    recver = data['username']

    result = Request_list.query.filter_by(recver=recver).all()
    list = []
    for i in result:
        content = { 
            'sender': i.sender, 
            'recver': i.recver, 
            'filename' : i.filename,
            'iv' : i.iv,
            'pub_key' : i.pub_key,
            'rsa_session_key' : i.rsa_session_key }
        list.append(content)
        content = {}
    
    return str(list)


'''
example:
{
    "sender" : "xxxxx",
    "recver" : "xxxxx",
    "filename" : "xxxxx"
}
'''
@app.route('/recvive', methods=['POST'])
def recvive():
    data = request.get_data().decode()
    data = json.loads(data)
    sender = data['sender']
    recver = data['recver']
    filename = data['filename']

    with open('upload/'+filename,'r') as f:
        file_data = f.read()

    result = Request_list.query.filter_by(sender=sender,recver=recver,filename=filename).first()

    content = {
        'filename' : filename,
        'iv' : result.iv,
        'pub_key' : result.pub_key,        
        'rsa_session_key' : result.rsa_session_key,
        'file_content' : file_data
    }
    db.session.delete(result)
    db.session.commit()
    return content

if __name__ == '__main__':
    if not os.path.exists('upload/'):
        os.mkdir('upload')

    #db.drop_all()  #清空数据库中的表
    db.create_all() #建立所有表,已有则不再新建
    app.run('0.0.0.0',5000) #可自己修改端口