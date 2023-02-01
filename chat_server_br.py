from socket import *
from threading import *
import pymysql
import json
import datetime
from datetime import timedelta, datetime, time


class MultiChatServer:

    def __init__(self):
        self.clients = []
        self.final_received_message = ""
        self.s_sock = socket(AF_INET, SOCK_STREAM)
        self.ip = '127.0.0.1'
        self.port = 5959
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s_sock.bind((self.ip, self.port))
        print('클라이언트 대기중. . . ')
        self.s_sock.listen(3)
        self.accept_client()

    def accept_client(self):
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)
                self.open_db()
                self.c.execute('SELECT * FROM network_project.chat')
                chat_list = self.c.fetchall()

                # DB에서 가져온 데이터를 튜플리스트화
                list_chat_info = []
                for i in range(len(chat_list)):
                    for j in range(len(chat_list[i])):
                        if type(chat_list[i][j]) == datetime:
                            list_chat_info.append(chat_list[i][j].strftime('%D %T'))
                        else:
                            list_chat_info.append(chat_list[i][j])

                setdata = json.dumps(list_chat_info)
                c_socket.send(setdata.encode())

                self.conn.close()

                # print(list_chat_info)
            print(f'{ip},:,{str(port)}가 접속하었습니다.')
            cth = Thread(target=self.receive_messages, args=(c_socket,),daemon=True)
            cth.start()

    def open_db(self):
        self.conn = pymysql.connect(host='10.10.21.102', user='lilac', password='0000', db='network_project',charset='utf8')
        self.c = self.conn.cursor()

    # 데이터를 수신하여 접속한 모든 클라이언트에게 채팅
    def receive_messages(self, c_socket):
        while True:
            try:
                incoming_message = c_socket.recv(256)
                if not incoming_message:
                    break
            except:
                continue
            else:
                self.final_received_message = incoming_message.decode('utf-8')
                self.send_all_clients(c_socket)

                print(self.final_received_message)

                self.open_db()
                self.c.execute (f"INSERT INTO testchat VALUES (now(), '{self.final_received_message[1]}', '{self.final_received_message[2]}')")
                self.conn.commit()

        c_socket.close()

    def send_all_clients(self, senders_socket):
        sendall_message = f"[{self.final_received_message[0]}] [{self.final_received_message[1]}]\n{self.final_received_message[2]}"
        for client in self.clients:
            socket, (ip, port) = client
            if socket is not senders_socket:
                try:
                    socket.sendall(sendall_message.encode())
                except:
                    self.clients.remove(client)
                    print("{},{} 연결이 종료되었습니다".format(ip, port))


if __name__ == "__main__":
    MultiChatServer()
