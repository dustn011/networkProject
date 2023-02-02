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

        # 채팅방 만들기
        self.btn_insertTeamChat.clicked.connect(self.newchat)
        self.listwdg_teamChat.itemClicked.connect(self.newchatroom)
        self.btn_leaveTeamChat.clicked.connect(self.outchat)
        self.btn_teamChatSendMessage.clicked.connect(self.newSend)


    # 소켓 설정 메서드
    def initialize_socket(self):
        ip = input("서버 IP를 입력해주세요(default=10.10.21.102): ")
        if ip == '':
            ip = '10.10.21.118'
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
            self.listwdg_chattingBox.addItem(f"\n<<< [{datetime.now().strftime('%D %T')}] [{self.led_insertName.text()}] 님이 채팅방에 입장하셨습니다 >>> \n")
            # 리스트 위젯 스크롤바 아래로 고정
            self.listwdg_chattingBox.scrollToBottom()
            self.listwdg_connectionPeople.scrollToBottom()

            # 알람 서버로 전송
            alarm = ['plzReceiveAlarm', datetime.now().strftime('%D %T'), self.led_insertName.text()]     # 인덱스 0번에 식별자 'alarm'넣어줌
            send_alarm = json.dumps(alarm)
            self.client_socket.send(send_alarm.encode('utf-8'))
            self.stackedWidget.setCurrentIndex(1)



    # 채팅방 나가기 메서드
    def method_leaveChattingRoom(self):
        self.led_insertName.clear()
        self.stackedWidget.setCurrentIndex(0)

    # 메시지를 받는 메서드 스레드로 실행
    def listen_thread(self):
        # 데이터 수신 thread를 생성하고 시작
        t = Thread(target=self.receive_message, args=(self.client_socket,), daemon=True)
        t.start()

    # 스레드에서 실행되는 메시지 받기. 메서드 message_log[0]번으로 식별자 구분
    def receive_message(self, so):
        while True:
            buf = so.recv(9999)
            print(buf.decode('utf-8'))
            message_log = json.loads(buf.decode('utf-8'))
            print(message_log)
            print('1111111111111111111111111111111111111')
            if not buf:     # 연결이 종료됨
                break
            # 처음 입장했을 때 모든 채팅 내역 출력
            elif message_log[0] == 'allChat_data':
                message_log.pop(0)
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
            # 처음 입장했을 때 현재 접속 인원 출력
            elif message_log[0] == 'allConnection_data':
                message_log.pop(0)
                for i in range(len(message_log)):
                    self.listwdg_connectionPeople.addItem(message_log[i])
                    self.listwdg_connectionPeople.scrollToBottom()
            # 다른 클라이언트에서 보낸 메세지 전체 메시지창에 출력
            elif message_log[0] == 'plzReceiveMessage':
                message_log.pop(0)
                self.listwdg_chattingBox.addItem(message_log[0])
                # 리스트 위젯 스크롤바 아래로 고정
                self.listwdg_chattingBox.scrollToBottom()

            # 다른 클라이언트에서 입장한 알림 전체 메시지창에 출력, 입장한 사람들 리스트에 넣어주기
            elif message_log[0] == 'plzReceiveAlarm':
                message_log.pop(0)
                self.listwdg_chattingBox.addItem(message_log[0])
                self.listwdg_connectionPeople.addItem(message_log[1])
                # 리스트 위젯 스크롤바 아래로 고정
                self.listwdg_chattingBox.scrollToBottom()
                self.listwdg_connectionPeople.scrollToBottom()

            # 다른 클라이언트 채팅방목록 보여주기
            elif message_log[0] == 'plzReceiveNewchat':
                message_log.pop(0)
                for i in range(len(message_log)):
                    self.listwdg_teamChatChattingBox.addItem(message_log[i])
                    self.listwdg_teamChatChattingBox.scrollToBottom()

                # 다른 클라이언트 채팅방목록 보여주기
            elif message_log[0] == 'allNewChat_data':
                message_log.pop(0)

                for i in range(len(message_log)):
                    self.listwdg_teamChat.addItem(message_log[i])
                    self.listwdg_teamChat.scrollToBottom()

            # 새로운 채팅내용
            elif message_log[0] == '지난메세지':
                message_log.pop(0)
                print(message_log)
                for i in range(0,len(message_log),+2):
                    self.listwdg_teamChatChattingBox.addItem(f"보낸사람 : {message_log[i]}  메세지: {message_log[i+1]}")
                    self.listwdg_teamChatChattingBox.scrollToBottom()

        so.close()

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

    def newchat(self):
        # 새로운 채팅방 이름 설정
        chatname = self.led_insertTeamChat.text()
        # 채팅방이름을 리스트에 저장
        send_newchatlist = ['plzReceiveNewchat',chatname]
        # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
        send_newchat = json.dumps(send_newchatlist)
        # 연결된 소켓(서버)에 채팅 로그 데이터 보내줌
        self.client_socket.send(send_newchat.encode('utf-8'))
        # 새채팅방을 채팅방리스트에 append해줌
        self.listwdg_teamChat.addItem(chatname)
        # 채팅방이름은 ui에서 지워줌
        self.led_insertTeamChat.clear()

    def newchatroom(self):
        self.listwdg_teamChatChattingBox.clear()
        # 신규채팅방으로 이동
        self.stcwdg_teamchatting.setCurrentIndex(1)
        self.label_teamChatName.setText(self.listwdg_teamChat.currentItem().text())
        text = self.listwdg_teamChat.currentItem().text()
        send_newchatNamelist = ['채팅방이름', text]
        send_newchatName = json.dumps(send_newchatNamelist)
        self.client_socket.send(send_newchatName.encode('utf-8'))
        # 스크롤 맨 아래로 고정
        self.listwdg_teamChatChattingBox.scrollToBottom()



    def outchat(self):
        self.stcwdg_teamchatting.setCurrentIndex(0)
        self.listwdg_teamChatChattingBox.clear()

    def newSend(self):
        sender_name = self.led_insertName.text()
        message = self.led_teamChatSendMessage.text()
        roomname = self.label_teamChatName.text()
        message_datetime = datetime.now().strftime("%D %T")

        # 시간, 이름, 메시지 내용 순으로 리스트에 저장
        newsend_messageList = ['plzReceiveNewMessage',roomname, sender_name, message]
        setNewMessageData = json.dumps(newsend_messageList)  # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
        self.client_socket.send(setNewMessageData.encode('utf-8'))  # 연결된 소켓(서버)에 채팅 로그 데이터 보내줌

        # 리스트 위젯에 작성한 글 append해줌
        self.listwdg_teamChatChattingBox.addItem(f"[{message_datetime}] [{sender_name}]\n[{message}]")
        self.led_teamChatSendMessage.clear()  # 작성한 글은 전송 후 ui에서 지워줌

        # 리스트 위젯 스크롤바 아래로 고정
        self.listwdg_teamChatChattingBox.scrollToBottom()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Client()
    myWindow.show()
    app.exec_()