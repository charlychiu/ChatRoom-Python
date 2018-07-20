import socket
from threading import Thread
from time import sleep

def client():
    host = socket.gethostname()
    port = 8888

    client_socket = socket.socket()
    client_socket.connect((host, port))

    thread = Thread(target=listen_from_server, args=[client_socket])
    thread.start()

    while True:
        sleep(1)
        message = input("")
        client_socket.send(message.encode('utf-8'))

def listen_from_server(conn):
    data = conn.recv(1024).decode('utf-8')
    print('Received from server :' + data + '\n')

    while True:
        data = conn.recv(1024).decode('utf-8')
        print('> ' + data)

    # while message.lower().strip() != "bye":
    #
    #     message = input(" -> ")
    #
    #     data = client_socket.recv(1024).decode('utf-8')
    #     print('Received from server :' + data)
    #     message = input(" -> ")
    #     client_socket.send(message.encode('utf-8'))
    #
    # client_socket.close()

if __name__ == '__main__':
    client()
