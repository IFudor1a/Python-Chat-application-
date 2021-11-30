import socket
import threading
import asyncio
host = "127.0.0.1"
port = 1234

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.bind(
    (host, port)
)
server.listen(4)
print("Server running!")

users = []
nicknames = []
main_loop = asyncio.new_event_loop()

def broadcast(message):
    for user in users:
        user.send(message)


def handle(user):
    while True:
        try:
            message = user.recv(2048)
            print(message.decode('utf-8'))
            broadcast(message)
        except:
            index = users.index(user)
            users.remove(user)
            user.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode('utf-8'))
            nicknames.remove(nickname)
            break


def receive():
    while True:
        user, address = server.accept()
        print("Connected with {}".format(str("address")))
        user.send('NICKNAME'.encode('utf-8'))
        nickname = user.recv(2048).decode('utf-8')
        nicknames.append(nickname)
        users.append(user)
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('utf-8'))
        user.send('Connected to the server!'.encode('utf-8'))
        thread = threading.Thread(target=handle, args=(user,))
        thread.start()


receive()
