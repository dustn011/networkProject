from socket import *
from threading import *
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

from_class = uic.loadUiType("chat_test.ui")[0]

class WindowClass(QWidget,from_class):
    client_socket = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initialize_socket()
        self.test_thread()
        self.btn_send.clicked.connect(self.send_chat)

    def initialize_socket(self):
        ip = input('ip addr : ')
        if ip == '':
            ip = '127.0.0.1'
        port = 5959
        self.client_socket = socket(AF_INET,SOCK_STREAM)
        self.client_socket.connect((ip,port))

    def send_chat(self):
        senders_name = self.lineEdit.text()
        message = self.sendmessage.text()
        data = (f"{senders_name} : {message}").encode('utf-8')
        self.receivemessage.append(data.decode('utf-8')+'\n')
        print(self.client_socket)
        print(data)
        self.client_socket.send(data)
        self.sendmessage.clear()
        print(senders_name)

    def test_thread(self):
        cThread = Thread(target=self.receive_message, args=(self.client_socket,),daemon=True)
        cThread.start()

    def receive_message(self,so):
        while True:
            buf = so.recv(2560)
            if not buf:
                break
            self.receivemessage.append(buf.decode()+'\n')
        so.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()


