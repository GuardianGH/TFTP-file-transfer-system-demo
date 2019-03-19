# coding=utf-8
from socket import socket
import sys
import os
import time
import tkinter.filedialog as flog


class Tftpclient():
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_liebiao(self):
        self.sockfd.send('list'.encode())

        # 服务器回复y/n
        data = self.sockfd.recv(1024).decode()
        if data == 'y':
            data = self.sockfd.recv(4096).decode()
            files = data.split(',')
            print('文件列表如下')
            for f in files:
                print(f)
            print('文件列表展示完毕')
        else:
            print('请求失败')

    def do_xiazai(self, filename):
        self.sockfd.send(('G ' + filename).encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'y':
            fd = open(filename, 'wb')
            while 1:
                fdata = self.sockfd.recv(1024)

                if fdata == '##':
                    break

                fd.write(fdata)
            fd.close()
            print('%s　下载完成' % filename)
        else:
            print('服务器拒绝下载')

    def do_shangchuan(self):
        try:
            filename = flog.askopenfilename(titel='选择上传的文件')
            fd = open(filename, 'rb')
        except Exception as E:
            print('出错', E)
            return
        fname = os.path.basename(filename)
        self.sockfd.send(('P ' + fname).encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'y':

            while 1:
                wdata = fd.read(1024)
                if not wdata:
                    time.sleep(0.3)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(wdata)
            fd.close()

    def do_guanbi(self):
        self.sockfd.send('quit'.encode())
        print('关闭')
        sys.exit(0)


def main():
    host = '127.0.0.1'
    port = int(input('输入服务器端口：'))
    addr = (host, port)
    #    buffersize = 1024

    sockfd = socket()
    sockfd.connect(addr)

    # 创建客户端请求对象
    tftp = Tftpclient(sockfd)

    while 1:
        print("""
        --------命令选项----------
        -------1.文件列表---------
        -------2.下载文件---------
        -------3.上传文件---------
        -------4.退出服务---------
        -------------------------
        
        """)
        com = input('选择命令（1、2、3、4）：')
        if com == '1':
            tftp.do_liebiao()
        elif com == '2':
            filename = input('输入文件名:')
            tftp.do_xiazai(filename)
        elif com == '3':
            tftp.do_shangchuan()
        elif com == '4':
            tftp.do_guanbi()
        else:
            print('输入错误')
            time.sleep(2)


if __name__ == '__main__':
    main()
