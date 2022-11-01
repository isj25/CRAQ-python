import socket
import os
import threading

HEADER = 16
PORT = 5050
SERVER_IP = "192.168.1.12"
#SERVER_IP = socket.gethostbyname(socket.gethostname())
# gw = os.popen("ip -4 route show default").read().split()
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect((gw[2], 0))
# ipaddr = s.getsockname()[0]
# gateway = gw[2]
# host = socket.gethostname()
# print ("IP:", ipaddr, " GW:", gateway, " Host:", host)
ADDRESS = (SERVER_IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def register_node():
    pass

def write_data():
    pass

def read_data():
    pass

def handle_client(connection, address):
    print(f"Client with IP {address} connected")
    connected = True
    while connected:
        msg_length = connection.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = connection.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{address}] {msg}")
            conn.send("received".encode(FORMAT))
    connection.close()

def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn,addr))
        thread.start()
        print(f"Active Connections: {threading.activeCount() - 1}")

if __name__ == "__main__":
    print("Starting Coordinator")
    start()
