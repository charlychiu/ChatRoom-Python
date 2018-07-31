import socket
from threading import Thread
import sys


def client():
    host = socket.gethostname()
    port = 8888

    client_socket = socket.socket()
    client_socket.connect((host, port))

    thread = Thread(target=listen_from_server, args=[client_socket])
    thread.start()

    while True:
        message = input("")
        if message == 'exit':
            client_socket.send(message.encode('utf-8'))
            client_socket.close()
            sys.exit(0)
        else:
            client_socket.send(message.encode('utf-8'))


def listen_from_server(conn):
    while True:
        try:
            tmp = conn.recv(1024)
        except:
            return
            pass
        if not tmp:
            tmp = ''
            pass
        else:
            tmp = tmp.decode('utf-8')
        print('> ' + tmp)


if __name__ == '__main__':
    client()
