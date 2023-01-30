# GUI 채팅 클라이언트

import threading
import time
import pymysql
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QIntValidator
from datetime import timedelta, datetime, time

from socket import *
from threading import *

form_class = uic.loadUiType("ui/test.ui")[0]

class test(QWidget, form_class):
    client_socket = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initialize_socket()
        self.listen_thread()

        self.btn_sendMessage.clicked.connect(self.method_sendMessage)

    def initialize_socket(self):
        ip = input("server IP addr: ")
        if ip == '':
            ip = '10.10.21.102'
        port = 2500

        # TCP socket을 생성하고 server와 연결
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((ip, port))

    def method_sendMessage(self):
        sender_name = self.led_insertName.text()
        message = self.ted_message.text()

        message_datetime = datetime.now().strftime("%D %T")
        print(message_datetime)

        data = (f"{message_datetime}.{sender_name}.{message}").encode('utf-8')
        self.textEdit.append(f"[{message_datetime}]. [{sender_name}].\n{message}\n")
        self.client_socket.send(data)
        self.ted_message.clear()
        print(sender_name)
        pass

    def listen_thread(self):
        # 데이터 수신 thread를 생성하고 시작
        t = Thread(target=self.receive_message, args=(self.client_socket,), daemon=True)
        t.start()

    def receive_message(self, so):
        while True:
            buf = so.recv(2560)
            if not buf:     # 연결이 종료됨
                break
            self.textEdit.append(buf.decode()+'\n')
            # self.client_socket.send(buf)
        so.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindow = test()

    myWindow.show()

    app.exec_()