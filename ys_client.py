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


class Client(QWidget, form_class):
    client_socket = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Ui 페이지 0번째 페이지로 고정
        self.stackedWidget.setCurrentIndex(0)

        # 이름 입력하고 채팅방 입장하기
        self.led_insertName.returnPressed.connect(self.method_moveChattingPage)
        self.btn_joinChat.clicked.connect(self.method_moveChattingPage)

        # 채팅방 나가기
        self.btn_leaveChat.clicked.connect(self.method_leaveChattingRoom)

        # 메세지 보내기
        self.btn_sendMessage.clicked.connect(self.method_sendMessage)
        self.led_sendMessage.returnPressed.connect(self.method_sendMessage)

        # 소켓 만들기
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
    def method_moveChattingPage(self):
        if not bool(self.led_insertName.text()):
            QMessageBox.information(self, '입력 오류', '이름을 입력해주세요')
        else:
            self.lbl_wellcome.setText(f'{self.led_insertName.text()}님 환영합니다')
            self.listwdg_connectionPeople.addItem(self.led_insertName.text())
            self.listwdg_chattingBox.addItem(f"[{datetime.now().strftime('%D %T')}] [🐶링컨이🐶]\n{self.led_insertName.text()}님이 채팅방에 입장하셨습니다")

            # 리스트 위젯 스크롤바 아래로 고정
            self.listwdg_chattingBox.scrollToBottom()
            self.listwdg_connectionPeople.scrollToBottom()

            # 알람 서버로 전송
            alarm = ['plzReceiveAlarm', datetime.now().strftime('%D %T'), self.led_insertName.text()]     # 인덱스 0번에 식별자 'alarm'넣어줌
            send_alarm = json.dumps(alarm)
            self.client_socket.send(send_alarm.encode('utf-8'))
            self.stackedWidget.setCurrentIndex(1)

    # 메시지 보내기 메서드
    def method_sendMessage(self):
        sender_name = self.led_insertName.text()
        message = self.led_sendMessage.text()
        message_datetime = datetime.now().strftime("%D %T")

        # 시간, 이름, 메시지 내용 순으로 리스트에 저장
        send_messageList = ['plzReceiveMessage', message_datetime, sender_name, message]
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
        self.receiveThr = Thread(target=self.receive_message, args=(self.client_socket,), daemon=True)
        self.receiveThr.start()

    # 스레드에서 실행되는 메시지 받기 메서드. identifier번으로 식별자 구분
    def receive_message(self, so):
        while True:
            try:
                buf = so.recv(9999)
            except:
                print('연결 종료')
                break
            else:
                message_log = json.loads(buf.decode('utf-8'))
                identifier = message_log.pop(0)     # identifier = 식별자 -> 추출
                print(identifier)
                if not buf:     # 연결이 종료됨
                    break
                # 처음 입장했을 때 모든 채팅 내역 출력
                elif identifier == 'allChat_data':
                    a = 1
                    setting = ''
                    for i in range(len(message_log)):
                        if message_log[i] == '채팅':
                            pass
                        elif a%3 != 0:
                            setting += f"[{message_log[i]}] "
                            a += 1
                        else:
                            self.listwdg_chattingBox.addItem(setting + '\n' + message_log[i] + '')
                            setting = ''
                            # 리스트 위젯 스크롤바 아래로 고정
                            self.listwdg_chattingBox.scrollToBottom()
                            a += 1
                # 현재 접속 인원 출력(처음 입장, 누가 퇴장했을 때 갱신됨)
                elif identifier == 'allConnection_data':
                    self.listwdg_connectionPeople.clear()
                    for i in range(len(message_log)):
                        self.listwdg_connectionPeople.addItem(message_log[i])
                        self.listwdg_connectionPeople.scrollToBottom()
                # 다른 클라이언트에서 보낸 메세지 전체 메시지창에 출력
                elif identifier == 'plzReceiveMessage':
                    self.listwdg_chattingBox.addItem(message_log[0])
                    # 리스트 위젯 스크롤바 아래로 고정
                    self.listwdg_chattingBox.scrollToBottom()
                # 다른 클라이언트에서 입장한 알림 전체 메시지창에 출력, 입장한 사람들 리스트에 넣어주기
                elif identifier == 'plzReceiveAlarm':
                    self.listwdg_chattingBox.addItem(message_log[0])
                    self.listwdg_connectionPeople.addItem(message_log[1])
                    # 리스트 위젯 스크롤바 아래로 고정
                    self.listwdg_chattingBox.scrollToBottom()
                    self.listwdg_connectionPeople.scrollToBottom()
                elif identifier == 'plzReceiveLeaveMessage':
                    self.listwdg_chattingBox.addItem(message_log[0])
                    # 리스트 위젯 스크롤바 아래로 고정
                    self.listwdg_chattingBox.scrollToBottom()

    # 채팅방 나가기 메서드
    def method_leaveChattingRoom(self):
        # 채팅방 퇴장 알림 전송 인덱스 0번에 식별자 'plzReceiveLeaveMainChat'넣어줌
        leaveMainChat = ['plzSendAllThatImGone', datetime.now().strftime('%D %T'), self.led_insertName.text()]

        send_leaveMainChat = json.dumps(leaveMainChat)
        self.client_socket.send(send_leaveMainChat.encode('utf-8'))

        self.led_insertName.clear()
        self.stackedWidget.setCurrentIndex(0)

    # 유저가 종료했을 경우 (함수를 따로 실행 안해도 종료하면 알아서 실행됨)
    def closeEvent(self, QCloseEvent):
        # 채팅방 안나가고 종료하면 DB에 퇴장 로그 남기고 소켓 닫음
        if bool(self.led_insertName.text()):
            self.method_leaveChattingRoom()     # 접속 종료 알림 보내기, DB에 퇴장 로그 남기기
            # 서버에 소켓을 닫는다고 시그널 보냄
            exitsocketsignal = ['plzDisconnectSocket']
            send_exitsocketsignal = json.dumps(exitsocketsignal)  # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
            self.client_socket.send(send_exitsocketsignal.encode('utf-8'))  # 연결된 소켓(서버)에 채팅 로그 데이터 보내줌
        # 채팅방 나가고 종료하면 DB에 퇴장 로그 안남겨도 됨. 소켓만 닫음
        else:
            # 서버에 소켓을 닫는다고 시그널 보냄
            exitsocketsignal = ['plzDisconnectSocket']
            send_exitsocketsignal = json.dumps(exitsocketsignal)  # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
            self.client_socket.send(send_exitsocketsignal.encode('utf-8'))  # 연결된 소켓(서버)에 채팅 로그 데이터 보내줌
        self.client_socket.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindow = Client()

    myWindow.show()

    app.exec_()