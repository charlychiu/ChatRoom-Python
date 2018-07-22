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

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

    # Assign room admin
    if len(client_users) == 1:
        global admin_user_id
        admin_user_id = current_user_id

    # Start Thread session
    global client_users_thread
    client_users_thread[current_user_id] = threading.Thread(target=client_thread,
                                                            args=(socket_connection, current_user_id))
    client_users_thread[current_user_id].start()

    print(current_user_id, "join")
    broadcasting("***join chatroom***", current_user_id)


def client_thread(connection, current_user_id):
    global admin_user_id

    # first welcome msg to client when enter chat room
    send_message(connection, "Server: Hello")

    # let current user know itself is admin
    if current_user_id == admin_user_id:
        send_message(connection, "Server: you are room admin!")

    client_listening(current_user_id)


def user_leave(current_user_id, avtive = True):
    broadcasting("***leave chatroom***", current_user_id)
    # close connection
    global client_users
    global client_users_thread
    if avtive:
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


def client_listening(current_user_id):
    # keep listening client msg
    while True:
        client_msg = fetch_message(current_user_id)
        if len(client_msg) != 0:
            if client_msg == 'exit':
                user_leave(current_user_id)
                return
            elif "unmute>" in client_msg:
                unmuted_user(client_msg, current_user_id)
            elif "mute>" in client_msg:
                muted_user(client_msg, current_user_id)
            elif "kick>" in client_msg:
                kick_user_processing(client_msg, current_user_id)
            elif "crush" == client_msg:
                return
            else:
                client_msg = filter_muted_user(client_msg, current_user_id)
                broadcasting(client_msg, current_user_id)


def fetch_message(current_user_id):
    global client_users
    try:
        tmp = client_users[current_user_id].recv(1024)
        if not tmp:
            tmp = ''
            pass
        else:
            tmp = tmp.decode('utf-8')
            return tmp
    except:
        user_leave(current_user_id, False)
        return 'crush'

    # return tmp or ""

    # tmp = ''
    # try:
    #     tmp = client_users[current_user_id].recv(1024)
    # except:
    #     # user_leave(current_user_id)
    #     pass
    #     # socket_connection.close()
    # return tmp


def muted_user(message, current_user_id):
    global admin_user_id
    if current_user_id == admin_user_id:
        tmp = message.split()
        if len(tmp) == 2:
            muted_user_id = tmp[1]
            if muted_user_id != current_user_id:
                global mute_users
                mute_users.append(int(muted_user_id))
                print("add muted user", muted_user_id)


def unmuted_user(message, current_user_id):
    global admin_user_id
    if current_user_id == admin_user_id:
        tmp = message.split()
        if len(tmp) == 2:
            unmuted_user_id = tmp[1]
            if unmuted_user_id != current_user_id:
                global mute_users
                mute_users.remove(int(unmuted_user_id))
                print("remove muted user", unmuted_user_id)


def filter_muted_user(message, current_user_id):
    global mute_users
    if current_user_id in mute_users:
        global client_users
        send_message(client_users[current_user_id], "you had been muted")
        return ''
    else:
        return message


def kick_user_processing(message, current_user_id):
    global admin_user_id
    if current_user_id == admin_user_id:
        tmp = message.split()
        if len(tmp) == 2:
            kick_user = tmp[1]
            if kick_user != current_user_id:
                print("kick user", kick_user)
                user_leave(int(kick_user))


def broadcasting(message, current_user_id):
    global client_users
    if message != '':
        for each_user_id in client_users.keys():
            if each_user_id != current_user_id:
                send_message(client_users[each_user_id], str(current_user_id) + ":" + message)


if __name__ == '__main__':
    server()
