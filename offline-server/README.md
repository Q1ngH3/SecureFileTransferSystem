一个及其简单的`flask`框架`http`离线传输`server`。

# Usage

1. 安装`flask`，`flask-sqlalchemy`，`pymysql`。

   ```bash
   pip install flask
   pip install flask-mysqldb
   pip install pymysql
   ```
   
2. 调整`database.py`中`mysql`的用户名，密码，数据库名称，开启`mysql`监听`3306`端口。

3. 运行`python ./run.py`。

# API

1. `http://127.0.0.1:5000/transfer`，由发送方发起，`POST`方式，向`server`传送已经压缩，加密，编码好的文件内容。

   `Body`例子：

   ```
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
   ```

2. `http://127.0.0.1:5000/query`，由接收方发起，`POST`方式，向`server`发送接收方的`username`，查询接收到了哪些发送请求。

   `Body`例子

   ```
   example:
   {
       "username" = "xxxxx" 
   }
   ```

3. `http://127.0.0.1:5000/recvive`，由接收方发起，`POST`方式，向`server`发送发送方，接收方和文件名，返回文件内容和密钥，iv等信息。

   `Body`例子

   ```
   example:
   {
       "sender" : "xxxxx",
       "recver" : "xxxxx",
       "filename" : "xxxxx"
   }
   ```

# 其他

上传中转的文件都将存放于`upload`文件夹中, `server`的端口可自行修改，默认是5000。