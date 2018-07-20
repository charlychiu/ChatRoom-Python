import mysql.connector

class DataModel:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'user: {}'.format(self.name)

    def db_session_start(self):
        self.conn = mysql.connector.connect(
            user='chatroom',
            password='chatroom',
            host='127.0.0.1',
            database='chatroom'
        )

    def db_seesion_stop(self):
        self.conn.close()

    def insert_user_name(self):
        self.db_session_start()
        self.cursor = self.conn.cursor()




