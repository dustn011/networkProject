from socket import *
from threading import *
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import json
import time
from datetime import datetime

from_class = uic.loadUiType("ui/testtest.ui")[0]

class WindowClass(QWidget, from_class):
    client_socket = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initialize_socket()
        self.test_thread()
        self.set_chattingLog = 0
        self.stackedWidget.setCurrentIndex(0)
        # 입장하기 버튼 클릭시 메인페이지로 이동
        self.start_btn.clicked.connect(self.mainhome)
        # 전체체팅방 전송버튼 클릭시 메세지 송출
        self.btn_send.clicked.connect(self.send_chat)

    def initialize_socket(self):
        ip = input('접속할 ip를 입력해주세요 : ')
        if ip == '':
            ip = '127.0.0.1'
        port = 5959
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((ip, port))

    def send_chat(self):
        sender_name = self.nameline.text()
        message = self.sendmessage.text()
        message_datetime = datetime.now().strftime("%D %T")

        # 시간, 이름, 메시지 내용 순으로 리스트에 저장
        send_messageList = [message_datetime, sender_name, message]
        setMessageData = json.dumps(send_messageList)  # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
        self.client_socket.send(setMessageData.encode('utf-8'))  # 연결된 소켓(서버)에 채팅 로그 데이터 보내줌

        # 리스트 위젯에 작성한 글 append해줌
        self.receivemessage.addItem(f"[{sender_name}][{message_datetime}]\n{message}\n")
        self.sendmessage.clear()  # 작성한 글은 전송 후 ui에서 지워줌
        # 리스트 위젯 스크롤바 아래로 고정
        self.receivemessage.scrollToBottom()

        # data = (f"{senders_name} : {message}").encode('utf-8')
        # self.receivemessage.addItem(f"[{senders_name}]\n{message}\n")
        # print(self.client_socket)
        # # print(data)
        # self.client_socket.send(data)
        # self.sendmessage.clear()
        # # print(senders_name)

    def mainhome(self):
        if not bool(self.nameline.text()):
            QMessageBox.information(self, '입력 오류', '이름을 입력해주세요')
        else:
            self.user_name.setText(f'{self.nameline.text()}님 환영합니다')
            self.stackedWidget.setCurrentIndex(1)

    def test_thread(self):
        cThread = Thread(target=self.receive_message, args=(self.client_socket,), daemon=True)
        cThread.start()

    def receive_message(self, so):
        while True:
            buf = so.recv(2560)
            if not buf:
                break
            elif self.set_chattingLog == 0:
                message_log = json.loads(buf.decode('utf-8'))
                a = 1
                setting = ''
                for i in range(len(message_log)):
                    if a % 3 != 0:
                        setting += f"[{message_log[i]}] "
                    else:
                        self.receivemessage.addItem(setting + '\n' + message_log[i] + '\n')
                        setting = ''
                a += 1
                self.set_chattingLog += 1
            else:
                self.receivemessage.addItem(buf.decode() + '\n')
                # 리스트 위젯 스크롤바 아래로 고정
            self.receivemessage.scrollToBottom()
            time.sleep(0.1)
            so.close()

        #self.receivemessage.append(buf.decode() + '\n')
        # so.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
