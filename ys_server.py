# threading 모듈을 이용한 TCP 멀티 채팅 서버 프로그램

from socket import *
from threading import *
import pymysql
from datetime import timedelta, datetime, time

class MultiChatServer:

    # 소켓을 생성하고 연결되면 accept_client() 호출
    def __init__(self):
        self.clients = []   # 접속된 클라이언트 소켓 목록을 넣을 리스트
        self.final_recived_message = ""     # 최종 수신 메시지
        self.s_sock = socket(AF_INET, SOCK_STREAM)      # 소켓 생성
        self.ip = '10.10.21.102'
        self.port = 2500
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s_sock.bind((self.ip, self.port))
        print("클라이언트 접속 대기 중...")
        self.s_sock.listen(5)
        self.accept_client()

    # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다
    def accept_client(self):
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)     # 접속된 소켓을 목록에 추가
            print(datetime.now().strftime('%D %T'), '주소:', ip, ' 포트번호:', str(port), '가 연결되었습니다')
            ctn = Thread(target=self.receive_messages, args=(c_socket,))    # 수신 스레드
            ctn.start()     # 스레드 시작

    # 데이터를 수신하여 모든 클라이언트에게 전송하고 수신한 데이터를 DB에 저장한다
    # ↑ 수신한 데이터를 DB에 저장하고 DB가 갱신되면 실행되는 trigger을 써서 다시 DB를 가져온다. 가져온 DB를 모든 클라이언트에게 전송한다
    def receive_messages(self, c_socket):
        while True:
            try:
                incoming_message = c_socket.recv(256)
                if not incoming_message:    # 연결이 종료됨
                    break
            except:
                continue
            else:
                self.final_recived_message = incoming_message.decode('utf-8')
                self.send_all_clients(c_socket)      # 열려있는 모든 클라이언트들에게 메세지 보내기

                split_message = self.final_recived_message.split('.')
                spent_time = split_message[0]
                sender = split_message[1]
                sent_message = split_message[2]

                # DB 열기
                chat_data = pymysql.connect(host='10.10.21.102', user='lilac', password='0000', db='network_project',
                                            charset='utf8')
                # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
                chat_db = chat_data.cursor()

                # insert문 넣어주기
                insert_sql = f"INSERT INTO chat VALUES ('{sender}', '{sent_message}', now())"

                # execute 메서드로 db에 sql 문장 전송
                chat_db.execute(insert_sql)
                # insert문 실행
                chat_data.commit()
                # DB 닫아주기
                chat_data.close()
        c_socket.close()

    def send_all_clients(self, senders_socket):
        for client in self.clients:     # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket:    # 송신 클라이언트는 제외
                try:
                    socket.sendall(self.final_recived_message.encode())
                except:     # 연결 종료
                    self.clients.remove(client)     # 소켓 제거
                    print(f"{datetime.now().strftime('%D %T')}, {ip}, {port} 연결이 종료되었습니다")


if __name__ == "__main__":
    MultiChatServer()