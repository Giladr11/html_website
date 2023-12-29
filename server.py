import socket
import threading
import hashlib
import time
from colorama import Back
from datetime import datetime

# h4 = hashlib.new("SHA256")
# h4.update("".encode())
# print(h4.hexdigest())

with open("p", "r") as f:
    for line in f:
        (name, password2) = line.split("=")
        if name == "server":
            hashed_pass = password2

        elif name == "admin_password":
            admin_pass = password2


password = input("Type the password to start a server: ")
h = hashlib.new("SHA256")
h.update(password.encode())

if h.hexdigest()+"\n" == hashed_pass:
    print("Password is correct!")
    HOST = '10.100.102.9'
    # HOST = ''
    PORT = 50000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()


    clients = []
    nicknames = []
    private_dict = {}


    def broadcast(message, client_left):
        for client in clients:
            if client != client_left:
                client.send(message+"\n".encode('ascii'))


    def broadcast_all(message):
        for client in clients:
            client.send(message)


    def exist(nickname):
        flag = False
        for nick in nicknames:
            if nickname == nick:
                flag = True

        return flag

    stop_process = False


    def handle_main(client):
        global client_to_chat_with
        global client_started
        global nickname_to_chat_with
        global sent_nickname
        global stop_process
        while True:
            try:
                msg = message = client.recv(1024)
                if msg.decode('ascii').startswith('KICK'):
                    if nicknames[clients.index(client)] == "admin":
                        kick_name = msg.decode('ascii')[5:]
                        if kick_name in nicknames:
                            kick(kick_name)

                        else:
                            client.send("The client you were trying to Kick does not exist!".encode('ascii'))

                    else:
                        client.send("Only admins can you these type of commands!".encode('ascii'))

                elif msg.decode('ascii').startswith('BAN'):
                    if nicknames[clients.index(client)] == "admin":
                        banned_name = msg.decode('ascii')[4:]
                        if banned_name in nicknames:
                            ban(banned_name)
                            print(f"{banned_name} was banned!")

                        else:
                            client.send("The client you were trying to Ban does not exist!".encode('ascii'))

                elif msg.decode('ascii') == 'DATA':
                    if nicknames[clients.index(client)] == "admin":
                        client.send("\nDATA BASE:".encode('ascii'))
                        with open("chat.txt", "r") as f:
                            for line in f:
                                client.send(line.encode('ascii'))

                    else:
                        client.send("Only admins can you these type of commands!".encode('ascii'))

                elif msg.decode('ascii').startswith('SEARCH'):
                    client.send((search_word(msg.decode('ascii')[len("SEARCH")+1:]).encode('ascii')))

                elif msg.decode('ascii').startswith('PRIVATE'):
                    index = clients.index(client)
                    client_started = client
                    sent_nickname = nicknames[index]
                    if msg.decode('ascii')[len("PRIVATE")+1:] != sent_nickname:
                        if msg.decode('ascii')[len("PRIVATE")+1:] in nicknames:
                            nickname_to_chat_with = nickname = msg.decode('ascii')[len("PRIVATE")+1:]
                            index = nicknames.index(nickname)
                            client_to_chat_with = clients[index]
                            client_to_chat_with.send(f"ANSWER {sent_nickname}".encode('ascii'))

                        else:
                            client.send("REFUSED".encode('ascii'))
                    else:
                        client.send('YOURSELF'.encode('ascii'))

                elif msg.decode('ascii').startswith('CHECK'):
                    if msg.decode('ascii')[len('CHECK')+1:] == 'yes':
                        client_started.send(f'YES {nickname_to_chat_with}'.encode('ascii'))
                        client_to_chat_with.send(f'SEND {sent_nickname}'.encode('ascii'))

                    else:
                        client_started.send(f'NO {nickname_to_chat_with}'.encode('ascii'))

                elif msg.decode('ascii') == 'AGREED':
                    private_dict[sent_nickname] = client_started
                    private_dict[nickname_to_chat_with] = client_to_chat_with
                    client_started.close()
                    client_to_chat_with.close()
                    #private_chat_function here
                    continue

                elif msg.decode('ascii').startswith('SEND_ADMIN'):
                    if 'admin' in nicknames:
                        index_admin = nicknames.index('admin')
                        admin_client = clients[index_admin]
                        admin_client.send(f"ADMIN_RECV {message[len('SEND_ADMIN')+1:]}".encode('ascii'))
                    else:
                        client.send('ADMIN_NOT'.encode('ascii'))

                else:
                    broadcast(msg, client)

            except Exception:
                if client in clients:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    left_nickname = nicknames[index]
                    broadcast_all(f"{left_nickname} left the chat!".encode('ascii'))
                    print(f"{left_nickname} left the chat!")
                    nicknames.remove(left_nickname)
                    break


    def receive_main():
        while True:
            client, address = server.accept()
            print(f"connected to {str(address)}")

            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')

            with open("ban_list", "r") as f:
                banned_names = f.readlines()

            if nickname+'\n' in banned_names:
                client.send("BANNED".encode('ascii'))
                client.close()
                continue

            elif nickname.lower() == 'admin':
                if 'admin' not in nicknames:
                    client.send("PASS".encode('ascii'))
                    password = client.recv(1024).decode('ascii')
                    h2 = hashlib.new("SHA256")
                    h2.update(password.encode())
                    if h2.hexdigest() == admin_pass:
                        client.send("Connection to admin was successful!".encode('ascii'))

                    else:
                        client.send('REFUSED'.encode('ascii'))

                else:
                    client.send('MTO'.encode('ascii'))

            elif exist(nickname) is True:
                client.send('USED'.encode('ascii'))

            nicknames.append(nickname)
            print(nicknames)
            clients.append(client)
            client.send("you are connected to the server!".encode('ascii'))
            print(f"Nickname of the new client is '{nickname}'")
            broadcast(f"{nickname} just joined the server!".encode('ascii'), client)
            thread = threading.Thread(target=handle_main, args=(client,))
            thread.start()


    def kick(kick_name):
        nickname_index = nicknames.index(kick_name)
        nicknames.remove(kick_name)
        client_kick = clients[nickname_index]
        clients.remove(client_kick)
        client_kick.send("You were kicked by an admin!".encode('ascii'))
        client_kick.close()
        broadcast_all(f"{kick_name} was Kicked from the server!".encode('ascii'))

    def ban(banned_name):
        index_nickname = nicknames.index(banned_name)
        nicknames.remove(banned_name)
        banned_client = clients[index_nickname]
        clients.remove(banned_client)
        banned_client.send("You were banned from the server!".encode('ascii'))
        banned_client.close()
        broadcast_all(f"{banned_name} was Banned from the server!".encode('ascii'))
        with open("ban_list", "a") as f:
            f.write(f"{banned_name}\n")


    def search_word(word_message):
        with open("chat.txt", "r") as f:
            new_str = ""
            for line in f:
                if word_message in line:
                    new_str += line

            colored_line = ""
            for line in new_str:
                if word_message.lower() in new_str.lower():
                    colored_line = new_str.replace(word_message, f"{Back.LIGHTYELLOW_EX}{word_message}{Back.RESET}")

            return colored_line

    print("server is Waiting for connections...")
    receive_main()

else:
    print("Wrong Password!")
