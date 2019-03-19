# coding=utf-8
import os
import signal
import sys
import time
import tkinter.filedialog as flog
from socket import socket

# 文件库位置
file_path = flog.askdirectory(title='选择数据目录')
print(file_path)


class Tftpserver():
    def __init__(self, connfd):
        self.connfd = connfd

    def do_list(self):
        filelist = os.listdir(file_path)
        if not filelist:
            self.connfd.send('n'.encode())
            return None
        else:
            self.connfd.send('y'.encode())
        time.sleep(0.5)
        files = ''
        for fn in filelist:
            if fn[0] != '.' and os.path.isfile(file_path + '/' + fn):
                files = files + fn + ','
        self.connfd.send(files.encode())

    def do_get(self, filename):
        try:
            fd = open(file_path + '/' + filename, 'rb')
        except:
            self.connfd.send(b'n')
            return
        self.connfd.send('y')
        time.sleep(0.3)
        for line in fd:
            self.connfd.send(line)
        fd.close()
        time.sleep(0.2)
        self.connfd.send(b'##')
        print('发送成功')

    def do_put(self, filename):
        try:
            fd = open(file_path + '/' + filename, 'wb')
        except:
            self.connfd.send(b'n')
            return
        for line in fd:
            self.connfd.send(line)
        time.sleep(0.3)
        self.connfd.send(b'##')

    def do_quit(self):
        print('客户端退出')
        sys.exit(0)


def main():
    #    if len(sys,argv)<3:
    #        print('argv is error')
    #        sys.exit(1)
    host = '127.0.0.1'
    port = 8899
    addr = (host, port)
    buffersize = 1024

    sockfd = socket()
    sockfd.bind(addr)
    sockfd.listen(5)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    while 1:
        try:
            connfd, addr = sockfd.accept()
            print('客户端%s:%s登录' % (connfd, addr))
            pid = os.fork()

            if pid < 0:
                print('创建子进程失败')
                connfd.close()
            elif pid == 0:
                sockfd.close()

                # 创建与客户端通信的对象
                tftp = Tftpserver(connfd)

                while 1:
                    data = connfd.recv(buffersize).decode()
                    if data == 'list':
                        tftp.do_list()
                    elif data == 'get':
                        filename = data.split(' ')[-1]
                        tftp.do_get(filename)
                    elif data == 'put':
                        filename = data.split(' ')[-1]
                        tftp.do_put(filename)
                    elif data == 'quit':
                        tftp.do_quit()

            else:
                connfd.close()
                continue

        except KeyboardInterrupt:
            print('退出')
            sockfd.close()
            sys.exit(0)
        except Exception as E:
            print(E)


if __name__ == '__main__':
    main()
