# TCP 멀티 채팅 서버 프로그램

from socket import *
from threading import *
from datetime import timedelta, datetime, time
import pymysql
import json


class MultiChatServer:

    # 소켓을 생성하고 연결되면 accept_client() 호출
    def __init__(self):
        self.clients = []                   # 접속된 클라이언트 소켓 목록을 넣을 리스트
        self.final_recived_message = ""     # 수신 메시지를 문자열로 저장할 빈 문자열

        self.s_sock = socket(AF_INET, SOCK_STREAM)      # 서버 소켓 생성
        self.ip = '10.10.21.102'
        self.port = 6666
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s_sock.bind((self.ip, self.port))
        print("클라이언트 접속 대기 중...")
        self.s_sock.listen(2)
        self.accept_client()

        self.connectedMember = []       # 현재 접속한 사람 리스트

    # 모든 채팅 DB에서 가져오기
    def method_getAllChat(self):
        chat_alldata = pymysql.connect(host='10.10.21.102', user='lilac', password='0000', db='network_project',
                                       charset='utf8')
        # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
        all_chat = chat_alldata.cursor()

        # 채팅 로그를 불러와줘
        sql = f"SELECT spent_time, sender, sent_message FROM allchatting_log"

        # execute 메서드로 db에 sql 문장 전송
        all_chat.execute(sql)

        chat_info = all_chat.fetchall()

        # DB 닫아주기
        chat_alldata.close()

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
        chat_allconnection = pymysql.connect(host='10.10.21.102', user='lilac', password='0000', db='network_project',
                                       charset='utf8')
        # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
        all_connection = chat_allconnection.cursor()
        # 접속 멤버 로그를 불러와줘
        sql = f"SELECT connection_person FROM connection_stat"

        # execute 메서드로 db에 sql 문장 전송
        all_connection.execute(sql)

        connection_data = all_connection.fetchall()

        # DB 닫아주기
        chat_allconnection.close()

        list_connection_info = ['allConnection_data']

        # DB에서 가져온 튜플 리스트화
        for i in range(len(connection_data)):
            for j in range(len(connection_data[i])):
                list_connection_info.append(connection_data[i][j])

        return list_connection_info

    # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다
    def accept_client(self):
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)  # 접속된 소켓을 목록에 추가

                list_chat_info = self.method_getAllChat()   # 모든 채팅 DB에서 가져오기
                setdata = json.dumps(list_chat_info)        # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
                c_socket.send(setdata.encode())             # 연결된 소켓에 채팅 로그 데이터 보내줌

                list_connection_info = self.method_getAllConnection()   # 모든 접속자 DB에서 가져오기
                setdata = json.dumps(list_connection_info)              # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
                c_socket.send(setdata.encode())                         # 연결된 소켓에 채팅 로그 데이터 보내줌

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
                # print(self.recived_message)
                if self.recived_message[0] == 'plzReceiveMessage':
                    self.sendMessage_all_clients(c_socket)      # 열려있는 모든 클라이언트들에게 메세지 보내기
                elif self.recived_message[0] == 'plzReceiveAlarm':
                    self.sendAlarm_all_clients(c_socket)        # 열려있는 모든 클라이언트들에게 알림 보내기
                elif self.recived_message[0] ==  'byebye':
                    self.disconnect_socket(c_socket)            # 소켓 연결 끊기
                elif self.recived_message[0] == 'plzReceiveLeaveMainChat':
                    self.sendLeaveMessage(c_socket)
        c_socket.close()

    # 모든 클라이언트로 퇴장 메시지 보내기
    def sendLeaveMessage(self, senders_socket):
        print('안녕히계세요')
        leaveMessage = ['plzReceiveLeaveMessage',
                   f"\n<<< [{self.recived_message[1]}] [{self.recived_message[2]}] 님이 채팅방에서 나가셨습니다 >>>\n"]
        sendall_leaveMessage = json.dumps(leaveMessage)
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket:  # 송신 클라이언트는 제외
                try:
                    socket.sendall(sendall_leaveMessage.encode())
                except:  # 메시지가 전송되지 않으면 연결 종료된 소켓이므로 지워준다
                    self.clients.remove(client)  # 소켓 제거
                    print(f"{datetime.now().strftime('%D %T')}, {ip}, {port} 연결이 종료되었습니다")
            elif socket is senders_socket:
                # DB 열기
                leave_data = pymysql.connect(host='10.10.21.102', user='lilac', password='0000', db='network_project',
                                            charset='utf8')
                # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
                chat_db = leave_data.cursor()

                # insert문 넣어주기(언제몇시몇분에 ip주소와 port번호가 무엇인 누군가가 퇴장했습니다)
                insert_sql = f"INSERT INTO connection_log VALUES (now(), '{self.recived_message[2]}', '퇴장', '{ip}', '{port}')"
                # delete문으로 현재 접속 인원 지워버리기
                update_sql = f"DELETE FROM connection_stat WHERE connection_person = '{self.recived_message[2]}' AND ip = '{ip}' AND port = '{port}'"

                # execute 메서드로 db에 insertSql 문장 전송
                chat_db.execute(insert_sql)
                # execute 메서드로 db에 updateSql 문장 전송
                chat_db.execute(update_sql)

                # insert문 실행
                leave_data.commit()
                # DB 닫아주기
                leave_data.close()

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
            elif socket is senders_socket:
                # DB 열기
                chat_data = pymysql.connect(host='10.10.21.102', user='lilac', password='0000', db='network_project',
                                            charset='utf8')
                # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
                chat_db = chat_data.cursor()

                # insert문 넣어주기(언제몇시몇분에 ip주소와 port번호가 무엇인 누군가가 채팅을 쳤습니다)
                insert_sql = f"INSERT INTO allchatting_log VALUES (now(), '{self.recived_message[2]}', '{self.recived_message[3]}', '{ip}', '{port}')"

                # execute 메서드로 db에 sql 문장 전송
                chat_db.execute(insert_sql)
                # insert문 실행
                chat_data.commit()
                # DB 닫아주기
                chat_data.close()

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
            elif socket is senders_socket:
                # DB 열기
                chat_data = pymysql.connect(host='10.10.21.102', user='lilac', password='0000',
                                            db='network_project',
                                            charset='utf8')
                # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
                chat_db = chat_data.cursor()

                # insert문 넣어주기(언제몇시몇분에 ip주소와 port번호가 무엇인 누군가가 입장했습니다)
                insertLog_sql = f"INSERT INTO connection_log VALUES (now(), '{self.recived_message[2]}', '입장', '{ip}', '{port}')"
                insertStat_sql = f"INSERT INTO connection_stat VALUES ('{self.recived_message[2]}', '{ip}', '{port}')"

                # execute 메서드로 db에 sql 문장 전송
                chat_db.execute(insertLog_sql)
                chat_db.execute(insertStat_sql)

                # insert문 실행
                chat_data.commit()
                # DB 닫아주기
                chat_data.close()

    # 클라이언트에서 연결 끊는다고 시그널 보내면 소켓 리스트에서 해당 클라이언트 연결 소켓 지움
    def disconnect_socket(self, senders_socket):
        for client in self.clients:
            socket, (ip, port) = client
            if socket is senders_socket:
                self.clients.remove(client)  # 전체 클라이언트 소켓 리스트에서 해당 소켓 제거
                socket.close()
                print(f"{datetime.now().strftime('%D %T')}, 주소: {ip}, 포트번호: {port} 연결이 종료되었습니다")


if __name__ == "__main__":
    MultiChatServer()