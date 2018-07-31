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
    current_user_id = generate_new_user()

    set_socket_connection_list(current_user_id, socket_connection)

    start_user_session(current_user_id, socket_connection)

    print(current_user_id, "join")
    broadcasting("***join chatroom***", current_user_id)


def user_leave(current_user_id, active=True):
    broadcasting("***leave chatroom***", current_user_id)
    # close connection
    global client_users

    if active:
        try:
            client_users[current_user_id].close()
        except:
            pass

    # admin leave , clean mute_users
    if check_admin_permission(current_user_id):
        clean_mute_list()

    remote_user(current_user_id)

    print(current_user_id, "leave")


def client_thread(socket_connection, current_user_id):
    # first welcome msg to client when enter chat room
    send_message(socket_connection, "Server: Hello")

    # let current user know its role
    if check_admin_permission(current_user_id):
        send_message(socket_connection, "Server: you are room admin!")

    client_listening(current_user_id)


def client_listening(current_user_id):
    # keep listening client msg
    while True:
        client_msg = fetch_message(current_user_id)
        if len(client_msg) != 0:
            if client_msg == 'exit':
                user_leave(current_user_id)
                return
            elif "unmute>" in client_msg:
                if check_admin_permission(current_user_id):
                    unmuted_user(client_msg, current_user_id)
                else:
                    system_notify(current_user_id, "permission denied")
            elif "mute>" in client_msg:
                if check_admin_permission(current_user_id):
                    muted_user(client_msg, current_user_id)
                else:
                    system_notify(current_user_id, "permission denied")
            elif "kick>" in client_msg:
                if check_admin_permission(current_user_id):
                    kick_user_processing(client_msg, current_user_id)
                else:
                    system_notify(current_user_id, "permission denied")
            elif "crush" == client_msg:
                return
            else:
                client_msg = filter_muted_user(client_msg, current_user_id)
                broadcasting(client_msg, current_user_id)


def send_message(socket_connection, message):
    msg = message + "\n"
    socket_connection.send(msg.encode('utf-8'))


def fetch_message(current_user_id):
    global client_users
    try:
        if check_user_exist(current_user_id):
            tmp = client_users[current_user_id].recv(1024)
            if not tmp:
                tmp = ''
                pass
            else:
                tmp = tmp.decode('utf-8')
                return tmp
        else:
            return 'crush'
    except:
        if check_user_exist(current_user_id):
            user_leave(current_user_id, False)
        return 'crush'


def broadcasting(message, current_user_id):
    global client_users
    if message != '':
        for each_user_id in client_users.keys():
            if each_user_id != int(current_user_id):
                send_message(client_users[each_user_id], str(current_user_id) + ":" + message)


def muted_user(message, current_user_id):
    tmp = message.split()
    if len(tmp) == 2:
        muted_user_id = tmp[1]
        if check_user_exist(muted_user_id) and int(muted_user_id) != int(current_user_id):
            add_mute_user(muted_user_id)
            system_notify(current_user_id, "muted action success")
            print("add muted user", muted_user_id)
        else:
            system_notify(current_user_id, "muted action fail")


def unmuted_user(message, current_user_id):
    tmp = message.split()
    if len(tmp) == 2:
        unmuted_user_id = tmp[1]
        if check_user_exist(unmuted_user_id) and int(unmuted_user_id) != int(current_user_id):
            remote_mute_user(unmuted_user_id)
            system_notify(current_user_id, "unmuted action success")
            print("remove muted user", unmuted_user_id)
        else:
            system_notify(current_user_id, "unmuted action fail")


def filter_muted_user(message, current_user_id):
    global mute_users
    if current_user_id in mute_users:
        system_notify(current_user_id, "you had been muted")
        return ''
    else:
        return message


def kick_user_processing(message, current_user_id):
    if check_admin_permission(current_user_id):
        tmp = message.split()
        if len(tmp) == 2:
            kick_user = tmp[1]
            global client_users
            if check_user_exist(kick_user) and int(kick_user) != int(current_user_id):
                print("kick user", kick_user)
                user_leave(int(kick_user))
            else:
                system_notify(current_user_id, "user not found")


def generate_new_user():
    global user_id
    user_id += 1
    return user_id


def set_admin_user(user):
    global admin_user_id
    admin_user_id = user


def start_user_session(user, socket_connection):
    global client_users_thread
    client_users_thread[int(user)] = threading.Thread(target=client_thread, args=(socket_connection, int(user)))
    client_users_thread[int(user)].start()


def set_socket_connection_list(user, socket_connection):
    global client_users
    client_users[int(user)] = socket_connection
    # Assign room admin
    if len(client_users) == 1:
        set_admin_user(user)


def remote_user(user):
    global client_users
    if int(user) in client_users:
        del client_users[int(user)]

    global client_users_thread
    if int(user) in client_users_thread:
        del client_users_thread[int(user)]


def check_admin_permission(user):
    global admin_user_id
    if int(user) == admin_user_id:
        return True
    else:
        return False


def check_user_exist(user):
    global client_users
    if int(user) in client_users:
        return True
    else:
        return False


def add_mute_user(user):
    global mute_users
    if int(user) not in mute_users:
        mute_users.append(int(user))


def remote_mute_user(user):
    global mute_users
    if int(user) in mute_users:
        mute_users.remove(int(user))


def clean_mute_list():
    global mute_users
    mute_users = []


def system_notify(user, message):
    global client_users
    send_message(client_users[user], message)


if __name__ == '__main__':
    server()
