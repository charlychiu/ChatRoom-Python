import socket
import threading
from time import sleep

# from DataModel import DataModel

# global access
client_users = dict()
client_users_thread = dict()
mute_users = []
admin_user_id = 0
user_id = 0  # allocate user id (increase)


def server():
    # get host
    host = socket.gethostname()
    port = 8888

    """The first argument AF_INET is the address domain of the
    socket. This is used when we have an Internet Domain with
    any two hosts The second argument is the type of socket.
    SOCK_STREAM means that data or characters are read in
    a continuous flow."""
    # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(99)

    print("--- start socket server ---")

    while True:
        conn, address = server_socket.accept()
        user_join(conn)


def user_join(socket_connection):
    global user_id
    user_id += 1

    current_user_id = user_id

    global client_users
    client_users[current_user_id] = socket_connection

    # Start Thread session
    global client_users_thread
    client_users_thread[current_user_id] = threading.Thread(target=client_thread,
                                                            args=(socket_connection, current_user_id))
    client_users_thread[current_user_id].start()

    # Assign room admin
    if len(client_users) == 1:
        global admin_user_id
        admin_user_id = current_user_id

    print(current_user_id, "join")


def client_thread(connection, current_user_id):
    global admin_user_id

    # let current user know itself is admin
    if current_user_id == admin_user_id:
        send_message(connection, "you are room admin!")

    # first welcome msg to client when enter chat room
    send_message(connection, "Hello")

    client_listening(connection, current_user_id)



def user_leave(current_user_id):
    # global user_id
    # user_id -= 1

    # close connection
    global client_users
    try:
        client_users[current_user_id].close()
    except:
        pass
    del client_users[current_user_id]
    del client_users_thread[current_user_id]

    # admin leave , clean mute_users
    global admin_user_id
    if current_user_id == admin_user_id:
        global mute_users
        mute_users = []

    print(current_user_id, "leave")


def send_message(socket_connection, message):
    tmp = message + "\n"
    socket_connection.send(tmp.encode('utf-8'))

def client_listening(socket_connection, current_user_id):

    # keep listening client msg
    while True:
        client_msg = fetch_message(socket_connection, current_user_id)
        if len(client_msg) != 0:
            if client_msg == 'exit':
                # send_message(socket_connection, "exit")
                # sleep(2)
                user_leave(current_user_id)
                return
            elif "mute>" in client_msg:
                pass
            elif "kick>" in client_msg:
                pass
            else:
                broadcasting(client_msg, current_user_id)


        # if isinstance(data, str):
        #     if len(data) != 0:
        #         global client_users_thread
        #         if data == 'exit':
        #             # close connection
        #             client_users[user_id].close()
        #             del client_users[user_id]
        #             del client_users_thread[user_id]
        #             # admin leave , clean mute_users
        #             if user_id == admin_user_id:
        #                 global mute_users
        #                 mute_users = []
        #             return
        #         else:
        #             # and broadcast to other user in chatroom
        #             if user_id == admin_user_id:
        #
        #                     data = data.split()[1]
        #                     if int(data) in client_users_thread.keys():
        #                         mute_users.append(int(data))
        #                         print("add mute")
        #                     print(data)
        #                 else:
        #                     broadcasting(message=userTemp + data, self_user_id=user_id)
        #             else:
        #                 broadcasting(message=userTemp + data, self_user_id=user_id)


def fetch_message(socket_connection, current_user_id):
    global client_users

    tmp = ''
    try:
        tmp = client_users[current_user_id].recv(1024).decode('utf-8')
    except:
        user_leave(current_user_id)
        # socket_connection.close()
    return tmp



def broadcasting(message, current_user_id):
    global client_users
    for each_user_id in client_users.keys():
        if each_user_id != current_user_id:
            send_message(client_users[each_user_id], str(current_user_id)+":"+message)



if __name__ == '__main__':
    server()
