from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'root'
    password = 'xqh000521'
    database = 'offline-server'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s?charset=utf8' % (user,password,database)
    # 设置sqlalchemy自动跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    # 查询时会显示原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = True
    
    # 禁止自动提交数据处理
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

# 读取配置
app.config.from_object(Config)

# 创建数据库sqlalchemy工具对象
db = SQLAlchemy(app)

class Request_list(db.Model):
    # 定义表名
    __tablename__ = 'Request_list'
    
    # 定义字段
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    sender = db.Column(db.String(64),index=True)
    recver = db.Column(db.String(64),index=True)
    filename = db.Column(db.String(64))
    rsa_session_key = db.Column(db.String(64))
    iv = db.Column(db.String(64))
    pub_key = db.Column(db.String(64))