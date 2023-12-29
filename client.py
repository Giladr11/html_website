import socket
import threading
import time
from _datetime import datetime
import colorama
from colorama import Back,Fore


colorama.init(autoreset=True)
print(Fore.BLUE + f"WELCOME TO {Fore.LIGHTGREEN_EX}C-{Fore.RESET}{Fore.LIGHTMAGENTA_EX}W-{Fore.RESET}{Fore.YELLOW}M"+Fore.RESET)

nickname = input("type your Username: ")
if nickname.lower() == 'admin':
    password = input("Type the Admin's password: ")


colorama.init(autoreset=True)
color_nicknames_dict = {}
color_choice = input(f"Choose a color for received messages ({Fore.YELLOW}YELLOW{Fore.RESET}, {Fore.LIGHTBLUE_EX}BLUE{Fore.RESET}, {Fore.LIGHTGREEN_EX}GREEN{Fore.RESET}, {Fore.LIGHTCYAN_EX}CYAN{Fore.RESET}, {Fore.LIGHTMAGENTA_EX}PURPLE{Fore.RESET}): ")
match color_choice.lower():
    case "yellow":
        COLOR = Fore.YELLOW
        color_nicknames_dict[nickname] = COLOR

    case "blue":
        COLOR = Fore.LIGHTBLUE_EX
        color_nicknames_dict[nickname] = COLOR

    case "green":
        COLOR = Fore.LIGHTGREEN_EX
        color_nicknames_dict[nickname] = COLOR

    case  "cyan":
        COLOR = Fore.LIGHTCYAN_EX
        color_nicknames_dict[nickname] = COLOR

    case "purple":
        COLOR = Fore.LIGHTMAGENTA_EX
        color_nicknames_dict[nickname] = COLOR

    case _:
        COLOR = Fore.WHITE
        color_nicknames_dict[nickname] = COLOR

host = '10.100.102.9'
#host = '172.17.89.63'
port = 50000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
stop_process = False


def receive():
    while True:
        colorama.init(autoreset=True)
        global stop_process
        if stop_process is True:
            break
        try:

            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                new_message = client.recv(1024).decode('ascii')
                if new_message == 'MTO':
                    print(f"{Fore.LIGHTRED_EX}There is already an admin active in the server.. Try again later!{Fore.RESET}")
                    stop_process = True
                    continue

                if new_message == 'PASS':
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'REFUSED':
                        print(f"{Fore.LIGHTRED_EX}Admin's password is incorrect!{Fore.RESET}")
                        time.sleep(1)
                        stop_process = True

                    else:
                        print("You are an admin now!")

                elif new_message == 'USED':
                    print(f"{Fore.LIGHTRED_EX}You typed a Nickname that has already been taken!{Fore.RESET}")
                    time.sleep(1)
                    stop_process = True

                elif new_message == 'BANNED':
                    print(f"{Fore.LIGHTRED_EX}YOUR NICKNAME IS BANNED FROM THE SERVER!{Fore.RESET}")
                    time.sleep(1)
                    client.close()
                    stop_process = True

                else:
                    print(f"{color_nicknames_dict[nickname]}{new_message}{Fore.RESET}")

            elif message == 'YOURSELF':
                print(f"{Fore.LIGHTRED_EX}you cant start a chat with yourself..{Fore.RESET}")

            elif message == 'REFUSED':
                print(f"{Fore.LIGHTRED_EX}The client you were trying to chat with does not exist!{Fore.RESET}")

            elif message.startswith('ANSWER'):
                respond = str(input(f"{Fore.YELLOW}{message[len('ANSWER') + 1:]} would like to chat with you privately. Type yes/no :{Fore.RESET}"))
                client.send(f"CHECK {respond}".encode('ascii'))

            elif message.startswith('YES'):
                print(f"{Fore.GREEN}{message[len('YES')+1:]} Agreed to chat with you privately!{Fore.RESET}")
                print(f"{Fore.GREEN}Moving you and {message[len('YES')+1:]} to a private server...{Fore.RESET}")
                # receive_private()

            elif message.startswith('NO'):
                print(f"{Fore.LIGHTRED_EX}{message[len('NO') + 1:]} Didnt want to chat with you privately!{Fore.RESET}")

            elif message.startswith('SEND'):
                print(f"{Fore.GREEN}Moving you and {message[len('SEND')+1:]} to a private server...{Fore.RESET}")
                client.send('AGREED'.encode('ascii'))
                # receive_private()

            elif message.startswith('ADMIN_RECV'):
                print(f"{Fore.LIGHTRED_EX}{message[len('ADMIN_RECV')+1:]}{Fore.RESET}")

            elif message.startswith('ADMIN_NOT'):
                print(f"{Fore.LIGHTRED_EX}There is no admin connected to the server at this moment..{Fore.RESET}")

            else:
                print(f"{color_nicknames_dict[nickname]}{message}{Fore.RESET}")

        except Exception:
            print("an error occurred!")
            client.close()
            break


def write():

    while True:
        colorama.init(autoreset=True)
        if stop_process is True:
            break
        message = f'{nickname}: {input("")}'
        if message[len(nickname)+2:].startswith("/"):

            if nickname == "admin":
                if message[len(nickname)+2:].startswith("/kick"):
                    client.send(f"KICK {message[len(nickname)+8:]}".encode('ascii'))

                elif message[len(nickname)+2:].startswith("/ban"):
                    client.send(f"BAN {message[len(nickname)+7:]}".encode('ascii'))

                elif message[len(nickname)+2:].startswith("/show_data"):
                    if nickname == "admin":
                        client.send('DATA'.encode('ascii'))
                else:
                    print(f"{Fore.LIGHTRED_EX}the only commands you can you are [/kick, /ban, /show_data]{Fore.RESET}")
            else:
                print(f"{Fore.LIGHTRED_EX}Only admins can you these type of commands!{Fore.LIGHTRED_EX}")

        elif message[len(nickname)+2:].startswith("*"):

            if message[len(nickname)+3:].lower().startswith("search"):
                exist = False

                if message[len(nickname)+9:] == "":
                    if nickname != 'admin':
                        print(f"{Fore.LIGHTRED_EX}Only the admin can see the entire chat!{Fore.RESET}")
                        continue

                elif message[len(nickname)+9:].isspace():
                    if nickname != 'admin':
                        print(f"{Fore.LIGHTRED_EX}Only the admin can see the entire chat!{Fore.RESET}")
                        continue

                    else:
                        with open("chat.txt", "r") as f:
                            for line in f:
                                if message[len(nickname) + 10:] in line:
                                    exist = True
                        if exist is True:
                            client.send(f"SEARCH {message[len(nickname) + 10:]}".encode('ascii'))
                        else:
                            print(f"{Fore.LIGHTRED_EX}The message you were trying to search does not exist!{Fore.RESET}")

                else:
                    with open("chat.txt", "r") as f:
                        for line in f:
                            if message[len(nickname)+10:] in line:
                                exist = True

                    if exist is True:
                        client.send(f"SEARCH {message[len(nickname)+10:]}".encode('ascii'))

                    else:
                        print(f"{Fore.LIGHTRED_EX}The message you were trying to search does not exist!{Fore.RESET}")

            elif message[len(nickname)+3:].lower().startswith("private_chat"):
                client.send(f"PRIVATE {message[len(nickname)+16:]}".encode('ascii'))

            elif message[len(nickname)+3:].lower().startswith("send_to_admin"):
                if nickname != 'admin':
                    client.send(f"SEND_ADMIN {message[len(nickname)+17:]}".encode('ascii'))

                else:
                    print(f"{Fore.LIGHTRED_EX}The only commands you can use are [*search , *private_chat]{Fore.RESET}")

            else:
                if nickname != 'admin':
                    print(f"{Fore.LIGHTRED_EX}The only commands you can use are [*search , *private_chat, *send_to_admin]{Fore.RESET}")
                else:
                    print(f"{Fore.LIGHTRED_EX}The only commands you can use are [*search , *private_chat]{Fore.RESET}")

        else:
            client.send(message.encode('ascii'))
            with open("chat.txt", "a") as f:
                f.write(str(datetime.now()) + f"-->{message}"+"\n")


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()



