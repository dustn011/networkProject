# TCP 멀티 채팅 서버 프로그램
import time
from socket import *
from threading import *
from datetime import timedelta, datetime
import pymysql
import json


class MultiChatServer:

    # 소켓을 생성하고 연결되면 accept_client() 호출
    def __init__(self):
        self.clients = []                   # 접속된 클라이언트 소켓 목록을 넣을 리스트
        self.final_recived_message = ""     # 수신 메시지를 문자열로 저장할 빈 문자열

        self.s_sock = socket(AF_INET, SOCK_STREAM)      # 서버 소켓 생성
        self.ip = '10.10.21.118'
        self.port = 6666
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s_sock.bind((self.ip, self.port))
        print("클라이언트 접속 대기 중...")
        self.s_sock.listen(2)
        self.accept_client()
        self.connectedMember = []       # 현재 접속한 사람 리스트

    def open_db(self):
        self.conn = pymysql.connect(host='10.10.21.102', user='lilac', password='0000', db='network_project', charset='utf8')
        self.c = self.conn.cursor()
    # 모든 채팅 DB에서 가져오기
    def method_getAllChat(self):
        self.open_db()
        # 채팅로그 불러오기
        self.c.execute("SELECT * FROM chat")
        chat_info = self.c.fetchall()
        self.conn.close()

        list_chat_info = ['allChat_data']

        # DB에서 가져온 튜플 리스트화
        for i in range(len(chat_info)):
            for j in range(len(chat_info[i])):
                if type(chat_info[i][j]) == datetime:
                    list_chat_info.append(chat_info[i][j].strftime('%D %T'))
                else:
                    list_chat_info.append(chat_info[i][j])

        return list_chat_info

    # 모든 접속 멤버 가져오기
    def method_getAllConnection(self):
        self.open_db()
        # 접속멤버 불러오기
        self.c.execute("SELECT connection_person FROM connection WHERE connection_stat = '입장'")
        connection_data = self.c.fetchall()
        self.conn.close()

        list_connection_info = ['allConnection_data']

        # DB에서 가져온 튜플 리스트화
        for i in range(len(connection_data)):
            for j in range(len(connection_data[i])):
                list_connection_info.append(connection_data[i][j])

        return list_connection_info

    def method_getAllNewChat(self):
        self.open_db()
        # 채팅로그 불러오기
        self.c.execute("SELECT DISTINCT chatlist FROM network_project.new_chat")
        Newchat_list = self.c.fetchall()
        self.conn.close()

        list_Newchat_info = ['allNewChat_data']

        # DB에서 가져온 튜플 리스트화
        for i in range(len(Newchat_list)):
            for j in range(len(Newchat_list[i])):
                list_Newchat_info.append(Newchat_list[i][j])

        print(list_Newchat_info)
        return list_Newchat_info




    # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다
    def accept_client(self):
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)  # 접속된 소켓을 목록에 추가

                list_chat_info = self.method_getAllChat()   # 모든 채팅 DB에서 가져오기
                setdata1 = json.dumps(list_chat_info)        # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
                c_socket.send(setdata1.encode())
                print(list_chat_info)# 연결된 소켓에 채팅 로그 데이터 보내줌

                list_connection_info = self.method_getAllConnection()   # 모든 접속자 DB에서 가져오기
                setdata2 = json.dumps(list_connection_info)              # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
                c_socket.send(setdata2.encode())                         # 연결된 소켓에 채팅 로그 데이터 보내줌
                print(list_connection_info)
                print('11111111111111111111111111111111111111111111')
                time.sleep(1)

                # 새로운 채팅방 리스트
                list_Newchat_info = self.method_getAllNewChat()
                setdata3 = json.dumps(list_Newchat_info)
                c_socket.send(setdata3.encode())
                print(list_Newchat_info)

                # # 새로운 채팅방 대화목록
                # list_Newchatroom_info = self.method_getAllNewChatroom()
                # setdata4 = json.dumps(list_Newchatroom_info)
                # c_socket.send(setdata4.encode())
                # print(list_Newchat_info)

            print(datetime.now().strftime('%D %T'), '주소:', ip, ' 포트번호:', str(port), '가 연결되었습니다')

            ctn = Thread(target=self.receive_messages, args=(c_socket,), daemon=True)    # 수신 스레드
            ctn.start()     # 스레드 시작

    # 데이터를 수신하여 모든 클라이언트에게 전송하고 수신한 데이터를 DB에 저장한다
    def receive_messages(self, c_socket):
        while True:
            try:
                incoming_message = c_socket.recv(9999)
                if not incoming_message:    # 연결이 종료됨
                    break
            except:
                continue
            else:
                self.recived_message = json.loads(incoming_message.decode('utf-8'))
                print(self.recived_message)
                if self.recived_message[0] == 'plzReceiveMessage':
                    self.sendMessage_all_clients(c_socket)      # 열려있는 모든 클라이언트들에게 메세지 보내기
                if self.recived_message[0] == 'plzReceiveAlarm':
                    self.sendAlarm_all_clients(c_socket)        # 열려있는 모든 클라이언트들에게 알림 보내기
                if self.recived_message[0] == 'plzReceiveNewchat':
                    self.sendNewchat_all_clients(c_socket)        # 열려있는 모든 클라이언트들에게 새채팅방 보내기
                if self.recived_message[0] == 'plzReceiveNewMessage':
                    self.sendNewMessage_all_clients(c_socket)          # 열려있는 모든 클라이언트들에게 새로운메세지 보내기
                if self.recived_message[0] == 'plzReceiveNewchatName':
                    # list_Newchatroom_info = self.method_getAllNewChatroom()
                    # setdata4 = json.dumps(list_Newchatroom_info)
                    # c_socket.send(setdata4.encode())
                    # print(list_Newchat_info)
                    self.method_getAllNewChatroom(c_socket)  # 열려있는 모든 클라이언트들에게 새로운메세지 보내기


        c_socket.close()

    def method_getAllNewChatroom(self,c_socket):
        message = ['plzReceiveNewchatName', f"[{self.recived_message[1]}]"]
        sendall_message = json.dumps(message)
        self.open_db()
        # 채팅로그 불러오기
        self.c.execute(f"select * from network_project.new_chat where chatlist = '{self.recived_message[1]}' and name is not null")
        Newchat_list = self.c.fetchall()

        print(Newchat_list)
        self.conn.close()

        if bool(Newchat_list) == False:
            pass
        else:
            list_Newchatroom_info = ['allNewChatroom_data']

            # DB에서 가져온 튜플 리스트화
            for i in range(len(Newchat_list)):
                for j in range(len(Newchat_list[i])):
                    list_Newchatroom_info.append(Newchat_list[i][j])

            setdata = json.dumps(Newchat_list)
            c_socket.send(setdata.encode())

            print(list_Newchatroom_info)
            return list_Newchatroom_info

    # 모든 클라이언트로 메시지 보내기
    def sendMessage_all_clients(self, senders_socket):
        message = ['plzReceiveMessage',
                   f"[{self.recived_message[1]}] [{self.recived_message[2]}]\n{self.recived_message[3]}"]
        sendall_message = json.dumps(message)
        for client in self.clients:     # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket:    # 송신 클라이언트는 제외
                try:
                    socket.sendall(sendall_message.encode())
                except:     # 메시지가 전송되지 않으면 연결 종료된 소켓이므로 지워준다
                    self.clients.remove(client)     # 소켓 제거
                    print(f"{datetime.now().strftime('%D %T')}, {ip}, {port} 연결이 종료되었습니다")

        self.open_db()
        # insert문 넣어주기(언제몇시몇분에 누가 채팅을 쳤습니다)
        self.c.execute(f"INSERT INTO chat VALUES (now(), '{self.recived_message[2]}', '{self.recived_message[3]}')")
        self.conn.commit()
        self.conn.close()


    # 모든 클라이언트로 알람 보내기
    def sendAlarm_all_clients(self, senders_socket):
        alarm = ['plzReceiveAlarm',
                 f"\n<<< [{self.recived_message[1]}] [{self.recived_message[2]}] 님이 채팅방에 입장하셨습니다 >>>\n",
                 self.recived_message[2]]
        sendall_Alarm = json.dumps(alarm)
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket:  # 송신 클라이언트는 제외
                try:
                    socket.sendall(sendall_Alarm.encode())      # 연결된 소켓(클라이언트)에 알람 데이터 보내줌
                except:  # 연결 종료
                    self.clients.remove(client)  # 소켓 제거
                    print(f"{datetime.now().strftime('%D %T')}, {ip}, {port} 연결이 종료되었습니다")

        self.open_db()
        # insert문 넣어주기(언제몇시몇분에 누가 입장했습니다)
        self.c.execute(f"INSERT INTO connection VALUES (now(), '{self.recived_message[2]}', '입장')")
        self.conn.commit()
        self.conn.close()

    # 모든 클라이언트에게 새채팅방 보내기
    def sendNewchat_all_clients(self, senders_socket):
        message = ['plzReceiveNewchat',f"[{self.recived_message[1]}]"]
        print(message)
        sendall_Newchat = json.dumps(message)
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket:  # 송신 클라이언트는 제외
                try:
                    socket.sendall(sendall_Newchat.encode())
                except:  # 메시지가 전송되지 않으면 연결 종료된 소켓이므로 지워준다
                    self.clients.remove(client)  # 소켓 제거
                    print(f"{datetime.now().strftime('%D %T')}, {ip}, {port} 연결이 종료되었습니다")

        self.open_db()
        # insert문 넣어주기(새로운 채팅방 저장)
        self.c.execute(f"INSERT INTO new_chat (chatlist) VALUES ('{self.recived_message[1]}')")
        self.conn.commit()
        self.conn.close()

    # 새채팅방에서 보낸 메세지 저장
    def sendNewMessage_all_clients(self, senders_socket):
        newmessage = ['plzReceiveNewMessage',
                   f"[{self.recived_message[1]}] [{self.recived_message[2]}]\n{self.recived_message[3]}"]
        print(newmessage)
        sendall_newmessage = json.dumps(newmessage)
        for client in self.clients:     # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket:    # 송신 클라이언트는 제외
                try:
                    socket.sendall(sendall_newmessage.encode())
                except:     # 메시지가 전송되지 않으면 연결 종료된 소켓이므로 지워준다
                    self.clients.remove(client)     # 소켓 제거
                    print(f"{datetime.now().strftime('%D %T')}, {ip}, {port} 연결이 종료되었습니다")

        self.open_db()
        # insert문 넣어주기(언제몇시몇분에 누가 채팅을 쳤습니다)
        self.c.execute(f"insert into network_project.new_chat (chatlist,name,message) value ('{self.recived_message[1]}','{self.recived_message[2]}','{self.recived_message[3]}')")
        self.conn.commit()
        self.conn.close()


if __name__ == "__main__":
    MultiChatServer()




