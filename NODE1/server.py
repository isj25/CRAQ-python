import socket
import json
import time
import threading

HEADER = 16
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SUCCESSOR = 1
PREDECESSOR = 0
NODE_FAILURE = 2

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

def send_data_to_node(successor, data):
    global config
    print("successor port",config["successor_port"][1])
    time.sleep(45)
    node_failed = 0
    if successor and config["successor"] != "NULL":
        dest_address = (SERVER_IP, config["successor_port"][1])
    else:
        if config["successor"] == "NULL":
            data = data.partition("\n")[0]
        dest_address = (SERVER_IP, config["predecessor_port"][1])

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind((SERVER_IP, config["cur_port"][0]))
    try:
        original_dest_address = dest_address
        client.connect(dest_address)
    except Exception:
        print("Node Failure")
        coordinator_port = config["coordinator_port"][1]
        dest_address = (SERVER_IP, coordinator_port)
        client.connect(dest_address)
        indication_bit = str(NODE_FAILURE).encode(FORMAT)
        indication_bit += b' ' * (1 - len(indication_bit))    #extend to 1 byte
        client.send(indication_bit)
        if successor:
            failed_port = config["successor_port"][1]
        else:
            failed_port = config["predecessor_port"][1]
        node_failed = 1
        original_data = data
        data = str(failed_port)

    message = data.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    client.close()
    if node_failed:
        print("System recovered")
        time.sleep(46)
        new_config_file = open("config.json","r+")
        config = json.load(new_config_file)
        send_data_to_node(successor, original_data)

def handle_request(connection, address):
    global config
    print(f"{address} connected")
    connected_port = address[1]

    new_config_file = open("config.json","r+")
    config = json.load(new_config_file)

    connected = True
    while connected:
        msg_length = connection.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            received_data = connection.recv(msg_length).decode(FORMAT)
            #connection.send("Write Successful".encode(FORMAT))
            connected = False

    if connected_port == config["coordinator_port"][0] or connected_port == config["predecessor_port"][0]:
        connection.close()
        print("Received write request")
        write_data(received_data)
        send_data_to_node(SUCCESSOR, received_data)

    elif connected_port == config["successor_port"][0]:
        connection.close()
        print("Received ACK")
        update_key_value_status(received_data)
        if config["predecessor"] != "NULL":
            send_data_to_node(PREDECESSOR, received_data)
    else:
        print(received_data)
        if (threading.activeCount() - 1) > 1:
            print("Node is busy")
            if config["predecessor"] == "NULL":            
                read_value = "port " + str(-1)
            else:
                read_value = "port " + str(config["predecessor_port"][1])
        else:
            with open("data.json","r") as data_file:
                all_data = json.load(data_file)
                read_value = "value " + all_data[received_data]["data"]
            time.sleep(15)
        connection.send(read_value.encode(FORMAT))
        connection.close()

def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_request, args=(conn,addr))
        thread.start()
        time.sleep(3)
        #print(f"Active Connections: {threading.activeCount() - 1}")
        #handle_request(conn, addr)

if __name__ == "__main__":
    start()
