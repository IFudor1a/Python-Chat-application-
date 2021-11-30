from Socket import Socket
from threading import Thread
from Database import Database


class Server(Socket):
    def __init__(self):
        super(Server, self).__init__()

        self.chat_id = None
        self.message_id = 0
        self.users = []
        self.nicknames = []
        self.address = []

    def set_connection(self):
        self.socket.bind(
            (self.host,
             self.port)
        )
        self.socket.listen(5)
        print("Server is working")

    def check_private(self, message):
        if message.startswith('/private'):
            return True
        else:
            return False

    def broadcast(self, message):
        for user in range(len(self.users)):
            self.users[user].send(f"{self.nicknames[user]}: {message}".encode('utf-8'))

    def broadcast_private(self,message,receiver):
        for user in range(len(self.nicknames)):
            if self.nicknames[user] == receiver:
                self.users[user].send(f"message from {self.address[user]}: ",message)
                break
    def handle(self, user, addr, database,nickname):
        while True:
            try:
                message = user.recv(2048)
                index = self.users.index(user)
            except ConnectionResetError:
                print(f"Connection with {addr} was lost")
                self.users.remove(user)
                username = self.nicknames[index]
                self.broadcast(f"{username} left!".encode('utf-8'))
                self.nicknames.remove(username)
                self.address.remove(index)
                break
            else:
                decoded_message = message.decode('utf-8')
                private_message = self.check_private(decoded_message)
                if private_message:
                    new_data = decoded_message.split('/private to')[1].strip()
                    receiver = new_data.split(' ', 1)[0]
                    private_data = new_data.split(' ', 1)[1]
                    database.cursor.execute("""SELECT message_id FROM messages
                                                        ORDER BY message_id DESC LIMIT 1""")
                    result = database.cursor.fetchone()[0]
                    result = result+1
                    database.cursor.execute(f"""INSERT INTO messages(message_id, chat_id, username, receiver, message_data)
                                                                                VALUES({result}, {self.chat_id}, '{nickname}', '{receiver}', '{private_data}')""")
                    database.conn.commit()
                    print(f"({addr}) {nickname} private message sent to {receiver}: ", private_data)
                    self.broadcast_private(private_data, receiver)
                else:
                    database.cursor.execute("""SELECT message_id FROM messages
                                                                            ORDER BY message_id DESC LIMIT 1""")
                    result = database.cursor.fetchone()[0]
                    result = result + 1
                    database.cursor.execute(f"""INSERT INTO messages(message_id, chat_id, username, receiver, message_data)
                                                      VALUES({result}, {self.chat_id}, '{nickname}', 'all', '{decoded_message}')""")
                    database.conn.commit()
                    print(f"{addr}) {self.nicknames[index]}: {decoded_message}".encode('utf-8'))
                    self.broadcast(decoded_message)


    def handle_server(self, database):
        database.cursor.execute("""CREATE TABLE IF NOT EXISTS chats (chat_id SERIAL PRIMARY KEY);""")
        database.conn.commit()

        database.cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                                     message_id SERIAL PRIMARY KEY,
                                     username VARCHAR  NOT NULL,
                                     receiver VARCHAR  NOT NULL,
                                     message_data TEXT NOT NULL,
                                     chat_id SERIAL ,
                                     FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
                                     );""")
        database.conn.commit()

        database.cursor.execute("""SELECT chat_id FROM chats
                                    ORDER BY chat_id DESC LIMIT 1""")
        result = database.cursor.fetchone()
        if result is None:
            self.chat_id = 1
        else:
            self.chat_id = int(result[0] + 1)

        database.cursor.execute(f"""INSERT INTO chats(chat_id) VALUES ({self.chat_id})""")
        database.conn.commit()

        self.set_connection()

    def receive(self, database):
        while True:
            user, addr = self.socket.accept()
            print(f"Connection established with {str(addr)}")
            username = (user.recv(2048)).decode()
            self.nicknames.append(username)
            self.users.append(user)
            self.address.append(addr)
            print(f"Username is {username}")
            self.broadcast(f"{username} joined!".encode('utf-8'))
            user.send("Connected to the server!".encode('utf-8'))

            thread = Thread(target=self.handle, args=(user, addr, database,username))
            thread.start()


if __name__ == '__main__':
    database = Database()
    database.connect()
    server = Server()
    server.handle_server(database)
    server.receive(database)
