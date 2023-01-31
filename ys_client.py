# TCP 멀티 채팅 클라이언트 프로그램

import json
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5 import uic
from datetime import timedelta, datetime
from socket import *
from threading import *

form_class = uic.loadUiType("ui/chat.ui")[0]


class test(QWidget, form_class):
    client_socket = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Ui 페이지 0번째 페이지로 고정
        self.stackedWidget.setCurrentIndex(0)

        # 메세지 보내기
        self.btn_sendMessage.clicked.connect(self.method_sendMessage)
        self.led_sendMessage.returnPressed.connect(self.method_sendMessage)

        # 이름 입력하고 채팅방 입장하기
        self.led_insertName.returnPressed.connect(self.method_moveChattingRoom)
        self.btn_joinChat.clicked.connect(self.method_moveChattingRoom)

        # 채팅방 나가기
        self.btn_leaveChat.clicked.connect(self.method_leaveChattingRoom)

        self.initialize_socket()

        # 스레드 함수 실행
        self.listen_thread()
        self.set_chattingLog = 0

    # 소켓 설정 메서드
    def initialize_socket(self):
        ip = input("서버 IP를 입력해주세요(default=10.10.21.102): ")
        if ip == '':
            ip = '10.10.21.102'
        port = 6666

        # TCP socket을 생성하고 server와 연결
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((ip, port))

    # 채팅방 입장하기 메서드
    def method_moveChattingRoom(self):
        if not bool(self.led_insertName.text()):
            QMessageBox.information(self, '입력 오류', '이름을 입력해주세요')
        else:
            self.lbl_wellcome.setText(f'{self.led_insertName.text()}님 환영합니다')
            self.listwdg_chattingBox.addItem(f"\n<<< [{datetime.now().strftime('%D %T')}] [{self.led_insertName.text()}] 님이 채팅방에 입장하셨습니다 >>> \n")
            # 리스트 위젯 스크롤바 아래로 고정
            self.listwdg_chattingBox.scrollToBottom()

            # 서버로 전송
            alarm = [datetime.now().strftime('%D %T'), self.led_insertName.text()]
            send_alarm = json.dumps(alarm)
            self.client_socket.send(send_alarm.encode('utf-8'))
            self.stackedWidget.setCurrentIndex(1)

    # 채팅방 나가기 메서드
    def method_leaveChattingRoom(self):
        self.led_insertName.clear()
        self.stackedWidget.setCurrentIndex(0)

    # 메시지 보내기 메서드
    def method_sendMessage(self):
        sender_name = self.led_insertName.text()
        message = self.led_sendMessage.text()
        message_datetime = datetime.now().strftime("%D %T")

        # 시간, 이름, 메시지 내용 순으로 리스트에 저장
        send_messageList = [message_datetime, sender_name, message]
        setMessageData = json.dumps(send_messageList)  # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
        self.client_socket.send(setMessageData.encode('utf-8'))  # 연결된 소켓(서버)에 채팅 로그 데이터 보내줌

        # 리스트 위젯에 작성한 글 append해줌
        self.listwdg_chattingBox.addItem(f"[{message_datetime}] [{sender_name}]\n{message}")
        self.led_sendMessage.clear()    # 작성한 글은 전송 후 ui에서 지워줌

        # 리스트 위젯 스크롤바 아래로 고정
        self.listwdg_chattingBox.scrollToBottom()

    # 메시지를 받는 메서드 스레드로 실행
    def listen_thread(self):
        # 데이터 수신 thread를 생성하고 시작
        t = Thread(target=self.receive_message, args=(self.client_socket,), daemon=True)
        t.start()

    # 스레드에서 실행되는 메시지 받기 메서드
    def receive_message(self, so):
        while True:
            buf = so.recv(9999)
            if not buf:     # 연결이 종료됨
                break
            elif self.set_chattingLog == 0:         # 처음 입장했을 때 모든 내역 출력
                message_log = json.loads(buf.decode('utf-8'))
                a = 1
                setting = ''
                for i in range(len(message_log)):
                    if a%3 != 0:
                        setting += f"[{message_log[i]}] "
                    else:
                        self.listwdg_chattingBox.addItem(setting + '\n' + message_log[i] + '')
                        setting = ''
                        # 리스트 위젯 스크롤바 아래로 고정
                        self.listwdg_chattingBox.scrollToBottom()
                    a += 1
                self.set_chattingLog += 1
            else:
                self.listwdg_chattingBox.addItem(buf.decode())
                # 리스트 위젯 스크롤바 아래로 고정
                self.listwdg_chattingBox.scrollToBottom()
            time.sleep(0.1)
        so.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindow = test()

    myWindow.show()

    app.exec_()