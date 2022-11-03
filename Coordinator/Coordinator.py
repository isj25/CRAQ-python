import socket
import os
import threading
import json
import shutil

HEADER = 16
PORT = 5052
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
READ = 0
WRITE = 1
NODE_FAILURE = 2

config_file = open("./Coordinator_config.json","r+")
config = json.load(config_file)
no_of_nodes = config["number_of_nodes"]
head_node = config["head_node"]
tail_node = config["tail_node"]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def register_node():
    global no_of_nodes
    global config
    global tail_node
    no_of_nodes = no_of_nodes + 1
    config["number_of_nodes"] += 1
    new_tail_node = "NODE" + str(no_of_nodes)
    shutil.copytree("../" + tail_node, "../" + new_tail_node)
    config["tail_node"] = new_tail_node
    tail_node = new_tail_node
    config["nodes_list"].append(new_tail_node)
    config_file.seek(0)
    config_file.truncate(0)
    json.dump(config, config_file, indent=4)

def write_data(data):
    key = data.partition("\n")[0]
    value = "\n".join(data.split("\n")[1:])
    print(f"We are writing files. Key:{key}, Value:{value}")
    ADDRESS1 = (SERVER_IP, 5054)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind(('192.168.1.12',5051))
    client.connect(ADDRESS1)

    message = data.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    client.close()

def handle_node_failure(failed_port):
    global head_node
    global tail_node
    global config
    global no_of_nodes

    ports = config["ports"]
    index = 0
    for src_dst_port in ports:
        if src_dst_port[1] == failed_port:
            break
        index += 1

    if index == 0:
        head_node = config["nodes_list"][index+1]
        config["head_node"] = head_node
        config["head_port"] = config["ports"][index+1]
        with open("../" + head_node + "/config.json", "r+") as node_config_file:
            node_config = json.load(node_config_file)
            node_config["predecessor"] = "NULL"
            node_config["predecessor_port"] = [-1, -1]
            node_config_file.seek(0)
            node_config_file.truncate(0)
            json.dump(node_config, node_config_file, indent=4)

    elif index == no_of_nodes - 1:
        tail_node = config["nodes_list"][index - 1]
        config["tail_node"] = tail_node
        config["tail_port"] = config["ports"][index-1]
        with open("../" + tail_node + "/config.json", "r+") as node_config_file:
            node_config = json.load(node_config_file)
            node_config["successor"] = "NULL"
            node_config["successor_port"] = [-1, -1]
            node_config_file.seek(0)
            node_config_file.truncate(0)
            json.dump(node_config, node_config_file, indent=4)

    else:
        prev_node = config["nodes_list"][index - 1]
        next_node = config["nodes_list"][index + 1]
        prev_port = config["ports"][index - 1]
        next_port = config["ports"][index + 1]

        with open("../" + prev_node + "/config.json", "r+") as node_config_file:
            node_config = json.load(node_config_file)
            node_config["successor"] = next_node
            node_config["successor_port"] = next_port
            node_config_file.seek(0)
            node_config_file.truncate(0)
            json.dump(node_config, node_config_file, indent=4)

        with open("../" + next_node + "/config.json", "r+") as node_config_file:
            node_config = json.load(node_config_file)
            node_config["predecessor"] = prev_node
            node_config["predecessor_port"] = prev_port
            node_config_file.seek(0)
            node_config_file.truncate(0)
            json.dump(node_config, node_config_file, indent=4)

    no_of_nodes -= 1
    config["number_of_nodes"] -= 1
    config["nodes_list"].pop(index)
    config["ports"].pop(index)
    config_file.seek(0)
    config_file.truncate(0)
    json.dump(config, config_file, indent=4)

def handle_client(connection, address):
    print(f"Client with IP {address} connected")
    connected = True
    while connected:
        indication_bit = connection.recv(1).decode(FORMAT)
        if indication_bit:
            indication_bit = int(indication_bit)
            msg_length = int(connection.recv(HEADER).decode(FORMAT))
            received_data = connection.recv(msg_length).decode(FORMAT)
            if indication_bit == READ:
                print(f"Received read request from [{address}]")
                #connection.send("Received read request".encode(FORMAT))
                connection.send(str(config["tail_port"][1]).encode(FORMAT))
            elif indication_bit == WRITE:
                print(f"Received write request from [{address}]")
                write_data(received_data)
                #connection.send("Write Successful".encode(FORMAT))
            elif indication_bit == NODE_FAILURE:
                failed_port = int(received_data)
                print(f"NODE with port {failed_port} failed")
                handle_node_failure(failed_port)
            connected = False
    print()
    connection.close()

def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn,addr))
        thread.start()
        print(f"Active Connections: {threading.activeCount() - 1}")

if __name__ == "__main__":
    Node_register = int(input("[Coordinator] Do you want to register a Node? [1]-Yes, [0]-No: "))
    if Node_register:
        register_node()
        print("New Node Created Successfully.\nTotal number of Nodes: ",no_of_nodes)
    print("Starting Coordinator...")
    start()
