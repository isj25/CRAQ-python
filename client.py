import socket

HEADER = 16
PORT = 5052
SERVER_IP = "192.168.1.12"
ADDRESS = (SERVER_IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
READ = 0
WRITE = 1

def contact_node(port, key):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node_address = (SERVER_IP, port)
    client.connect(node_address)

    message = key.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))   #extend to 16 bytes
    client.send(send_length)
    client.send(message)
    received_data = client.recv(256).decode(FORMAT).split(" ")
    client.close()
    if received_data[0] == "value":
        print("Value: ", "".join(received_data[1:]))
    elif received_data[0] == "port":
        port = int(received_data[1])
        if port == -1:
            print("Read Failed")
        else:
            contact_node(port, key)

def send_data(choice, data):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDRESS)

    read_write_choice = str(choice).encode(FORMAT)
    read_write_choice += b' ' * (1 - len(read_write_choice))    #extend to 1 byte
    client.send(read_write_choice)

    message = data.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))   #extend to 16 bytes
    client.send(send_length)
    client.send(message)
    if choice == READ:
        port = client.recv(16).decode(FORMAT)
        try:
            port = int(port)
        except Exception:
            print("Read Failed")
        client.close()
        print(port)
        contact_node(port, data)
    client.close()
    
if __name__ == "__main__":
    print("\n","*"*30,"Chain Replication with Apportioned Queries","*"*30,"\n")
    print("Type 'help' for lisitng all the available commands\n")
    command = ""

    while True:
        user_input = input("(CRAQ) ").split()
        if len(user_input) == 0:
            print("Please specify a command")
            continue

        command = user_input[0]

        if command == "read":
            if len(user_input) == 2:
                key = user_input[1]
                send_data(READ, key)
            else:
                print("Please specify a single key to read")

        elif command == "write":
            if len(user_input) == 3:
                key = user_input[1]
                value = user_input[2]
                data = key + "\n" + value
                send_data(WRITE, data)
            else:
                print("Please specify a key and value")

        elif command == "help":
            print("To read a file: 'read <key>'")
            print("To write a file: 'write <key> <value>'")
            print("To exit: 'exit'")

        elif command == "exit":
            break

        else:
            print("Please enter a valid command. Type 'help' for options.")
