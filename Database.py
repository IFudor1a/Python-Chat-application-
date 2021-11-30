import sqlite3

class Database:
    conn = None
    cursor = None

    def connect(self):
        self.conn = sqlite3.connect('chat.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.cursor()