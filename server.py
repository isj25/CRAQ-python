# from flask import Flask
# import json
# import os

# configFile = open(__file__.split('/')[-2]+'/serverConfig.json')
# config = json.load(configFile)

# PORT = config['port']
# app = Flask(__name__)




# @app.route('/')
# def hello():
#     return "server running on port "+str(PORT)

# if __name__ == "__main__":
#     print("server started on",PORT)
   
#     app.run(host = "localhost",port = PORT,debug=True)







import socket
import json

HEADER = 16
PORT = 5053
SERVER_IP = "192.168.1.12"
ADDRESS = (SERVER_IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(ADDRESS)

# def send(msg):
#     message = msg.encode(FORMAT)
#     msg_length = len(message)
#     send_length = str(msg_length).encode(FORMAT)
#     send_length += b' ' * (HEADER - len(send_length))
#     client.send(send_length)
#     client.send(message)
#     print(client.recv(2048).decode(FORMAT))

# send("Hello brother")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

config_file = open("config.json","r+")
config = json.load(config_file)

def write_data(data):
    data_file = open("data.json","r+")
    all_data = json.load(data_file)
    key = data.partition("\n")[0]
    value = "\n".join(data.split("\n")[1:])
    all_data[key] = { "data":value, "status":"dirty" }
    data_file.seek(0)
    data_file.truncate(0)
    json.dump(all_data, data_file, indent=4)

def send_data_to_successor(data):
    if config["successor"] != "NULL":
        ADDRESS1 = (SERVER_IP, config["successor_port"])
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDRESS1)

        message = data.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)

def handle_request(connection, address):
    print(f"{address} connected")
    connected_port = address[1]

    if connected_port == config["coordinator_port"][0] or connected_port == config["predecessor_port"][0]:
        connected = True
        while connected:
            msg_length = connection.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                received_data = connection.recv(msg_length).decode(FORMAT)
                print("Received write request")
                write_data(received_data)
                send_data_to_successor(received_data)
                connection.send("Write Successful".encode(FORMAT))
                connected = False
        connection.close()

    elif connected_port == config["successor_port"]:
        pass
    else:
        pass

def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        handle_request(conn, addr)

if __name__ == "__main__":
    start()
