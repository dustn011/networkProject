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

    # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다
    def accept_client(self):
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)  # 접속된 소켓을 목록에 추가

                # DB를 열고 로그인한 계정으로 보낸 메세지
                chat_alldata = pymysql.connect(host='10.10.21.102', user='lilac', password='0000', db='network_project',
                                               charset='utf8')
                # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
                all_chat = chat_alldata.cursor()

                # 오늘 로그인한 사람의 출석 상황을 보고싶어
                sql = f"SELECT * FROM chat"

                # execute 메서드로 db에 sql 문장 전송
                all_chat.execute(sql)

                chat_info = all_chat.fetchall()
                # DB 닫아주기
                chat_alldata.close()
                list_chat_info = []

                # DB에서 가져온 튜플 리스트화
                for i in range(len(chat_info)):
                    for j in range(len(chat_info[i])):
                        if type(chat_info[i][j]) == datetime:
                            list_chat_info.append(chat_info[i][j].strftime('%D %T'))
                        else:
                            list_chat_info.append(chat_info[i][j])

                setdata = json.dumps(list_chat_info)        # json.dumps로 리스트의 값들 바이트형으로 바꿔줌
                c_socket.send(setdata.encode())             # 연결된 소켓에 채팅 로그 데이터 보내줌

            print(datetime.now().strftime('%D %T'), '주소:', ip, ' 포트번호:', str(port), '가 연결되었습니다')

            ctn = Thread(target=self.receive_messages, args=(c_socket,), daemon=True)    # 수신 스레드
            ctn.start()     # 스레드 시작

    # 데이터를 수신하여 모든 클라이언트에게 전송하고 수신한 데이터를 DB에 저장한다
    # ↑ 수신한 데이터를 DB에 저장하고 DB가 갱신되면 실행되는 trigger을 써서 다시 DB를 가져온다. 가져온 DB를 모든 클라이언트에게 전송한다(이거 아님)
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
                self.send_all_clients(c_socket)      # 열려있는 모든 클라이언트들에게 메세지 보내기

                # DB 열기
                chat_data = pymysql.connect(host='10.10.21.102', user='lilac', password='0000', db='network_project',
                                            charset='utf8')
                # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
                chat_db = chat_data.cursor()

                # insert문 넣어주기
                insert_sql = f"INSERT INTO chat VALUES (now(), '{self.recived_message[1]}', '{self.recived_message[2]}')"

                # execute 메서드로 db에 sql 문장 전송
                chat_db.execute(insert_sql)
                # insert문 실행
                chat_data.commit()
                # DB 닫아주기
                chat_data.close()
        c_socket.close()

    def send_all_clients(self, senders_socket):
        sendall_message = f"[{self.recived_message[0]}] [{self.recived_message[1]}]\n{self.recived_message[2]}"

        for client in self.clients:     # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket:    # 송신 클라이언트는 제외
                try:
                    socket.sendall(sendall_message.encode())
                except:     # 연결 종료
                    self.clients.remove(client)     # 소켓 제거
                    print(f"{datetime.now().strftime('%D %T')}, {ip}, {port} 연결이 종료되었습니다")


if __name__ == "__main__":
    MultiChatServer()