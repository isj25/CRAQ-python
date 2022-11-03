import socket
import json
import time

HEADER = 16
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SUCCESSOR = 1
PREDECESSOR = 0

config_file = open("config.json","r+")
config = json.load(config_file)

PORT = config["cur_port"][1]
SERVER_IP = "192.168.1.12"
ADDRESS = (SERVER_IP, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def write_data(data):
    data_file = open("data.json","r+")
    all_data = json.load(data_file)
    key = data.partition("\n")[0]
    value = "\n".join(data.split("\n")[1:])
    if config["successor"] != "NULL":
        all_data[key] = { "data":value, "status":"dirty" }
    else:
        all_data[key] = { "data":value, "status":"clean" }
    data_file.seek(0)
    data_file.truncate(0)
    json.dump(all_data, data_file, indent=4)

def update_key_value_status(key):
    data_file = open("data.json","r+")
    all_data = json.load(data_file)
    all_data[key]["status"] = "clean"
    data_file.seek(0)
    data_file.truncate(0)
    json.dump(all_data, data_file, indent=4)

def send_data_to_node(next, data):
    if next and config["successor"] != "NULL":
        dest_address = (SERVER_IP, config["successor_port"][1])
    else:
        if config["successor"] == "NULL":
            data = data.partition("\n")[0]
        if config["predecessor"] == "NULL":
            return
        dest_address = (SERVER_IP, config["predecessor_port"][1])

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind((SERVER_IP, config["cur_port"][0]))
    client.connect(dest_address)
    message = data.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    client.close()
    time.sleep(91)

def handle_request(connection, address):
    print(f"{address} connected")
    connected_port = address[1]

    connected = True
    while connected:
        msg_length = connection.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            received_data = connection.recv(msg_length).decode(FORMAT)
            #connection.send("Write Successful".encode(FORMAT))
            connected = False
    connection.close()

    if connected_port == config["coordinator_port"][0] or connected_port == config["predecessor_port"][0]:
        print("Received write request")
        write_data(received_data)
        send_data_to_node(SUCCESSOR, received_data)

    elif connected_port == config["successor_port"][0]:
        print("Received ACK")
        update_key_value_status(received_data)
        send_data_to_node(PREDECESSOR, received_data)
    else:
        pass

def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        handle_request(conn, addr)

if __name__ == "__main__":
    start()
