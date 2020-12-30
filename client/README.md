# FileTranfer
大型程序设计-安全文件传输系统
## Usage
+ clone
+ api/var.py 中记录了服务器的域名，如果在本地运行服务端的话不用改
+ 确保tkinter，urllib，urllib3，requests库可正常使用
+ 命令行中运行python ./main_gui.py即可
## Functions
+ 用户的登录、注销、注册
+ 很方便地更改ui的语言，方法：在 gui/Languages文件夹中加入对应语言的json文件即可。json文件里的键值对可参考zh-CN.json编写
+ 定时进行与服务器的连通性测试，测试不通过会不让登录或注册
## *Settings*
+ 全部在settings.json中配置即可
  + `RemoteServer`: 服务器的地址
  + `MyIP`: 客户端ip
  + `ListeningPort`: 监听的端口
## **大体的设计思路（略有些混乱，但还算凑合）**
+ gui 文件夹中存放所有界面相关的模块
    + Frames 是存放各种组件的框架，每个界面对应一个frame
    + SubWindows 是弹出的窗口，在以下的情形会弹出窗口：
        1. 用户注册时
        2. 用户登录后，开始监听端口，收到请求且完成握手后（HELLO-OK)，弹出窗口，上面是接收的进度条
        3. 用户请求传送文件时会立即弹出一个子窗口，里头是进度条
    + config.py ：读写 settings.json 。*用户每登录一次便会新产生一个公私钥对，并post到服务器上*，settings中就记录了用户最近使用的两个公私钥对和其他的一些信息
+ server_api: 与服务器进行通信的模块，分为了登录、联系人、文件传输四个模块
+ client_api：与客户端进行通信的模块，
    + TransHandlers包：由于进行文件传输时需要记录大量的信息，并且与ui有联动的效果，所以完全重写了文件传输的api。调用的思路为：单击按钮->实例化一个handler->handler调用server.py和client.py的api实例化socket，进行信息的交互及文件的传输
    + Socket包：client.py server.py 进行socket通信，如收发hello等等消息
    + lib包：compress, crypto, RSAkey：压缩，加密
+ settings包：
  + config：配置settings.json
  + Language：语言文件
