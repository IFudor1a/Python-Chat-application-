import threading
from threading import Thread
from Socket import Socket


class Client(Socket):
    connection = False
    def __init__(self):
        super(Client, self).__init__()

        self.host = "127.0.0.1"
        self.port = 9090

    def connect(self, username):
        self.connection = True
        self.socket.connect(
            (self.host,
             self.port)
        )

        self.socket.sendall(username.encode('utf-8'))

    def receive(self):
        while self.connection:
            try:
                message = self.socket.recv(2048)
                message = message.decode('utf-8')
            except ConnectionResetError:
                print("[ERROR] CONNECTION IS LOST")
                self.connection = False
                break
            else:
                print(message)

    def broadcast(self):
        broadcast_thread = Thread(target=self.receive)
        broadcast_thread.start()

        while self.connection:
            try:
                self.socket.sendall((input(':::')).encode('utf-8'))
            except ConnectionResetError:
                print("[ERROR] CONNECTION IS LOST,MESSAGE COULDN'T BE SENT")
                self.connection = False
                break


if __name__ == '__main__':
    client = Client()
    username = input("Enter username:")
    client.connect(username)
    client.broadcast()
