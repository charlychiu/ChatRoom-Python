import socket
import threading
from time import sleep

# from DataModel import DataModel

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

    global client_users_thread
    global client_users
    global user_id
    global admin_user_id

    print("start connection ---")

    while True:
        conn, address = server_socket.accept()
        user_id += 1

        # assign room admin
        if len(client_users) == 0:
            admin_user_id = user_id

        client_users[user_id] = conn
        client_users_thread[user_id] = threading.Thread(target=client_thread, args=(conn, address, user_id))
        client_users_thread[user_id].start()

        print(len(client_users), user_id, admin_user_id)


def client_thread(conn, address, user_id):
    global admin_user_id

    # let current user know itself is admin
    if user_id == admin_user_id:
        conn.send("\nyou are room admin!".encode('utf-8'))

    # first welcome msg to client when enter chatroom
    conn.send("\nhello".encode('utf-8'))
    userTemp = str(user_id) + ": "

    # keep listen client msg
    while True:
        data = conn.recv(1024).decode('utf-8')
        print(userTemp+data)
        if isinstance(data, str):
            if len(data) != 0:
                global client_users_thread
                if data == 'exit':
                    # close connection
                    client_users[user_id].close()
                    del client_users[user_id]
                    del client_users_thread[user_id]
                    # admin leave , clean mute_users
                    if user_id == admin_user_id:
                        global mute_users
                        mute_users = []
                    return
                else:
                    # and broadcast to other user in chatroom
                    if user_id == admin_user_id:
                        if "mute>" in data:
                            data = data.split()[1]
                            if int(data) in client_users_thread.keys():
                                mute_users.append(int(data))
                                print("add mute")
                            print(data)
                        else:
                            broadcasting(message=userTemp+data, self_user_id=user_id)
                    else:
                        broadcasting(message=userTemp+data, self_user_id=user_id)



def broadcasting(message, self_user_id):
    global client_users

    for user_id in client_users.keys():
        if user_id != self_user_id:
            try:
                client_users[user_id].send(message.encode('utf-8'))
            except OSError as err:
                print("OS error: {0}".format(err))
            except:
                client_users[self_user_id].close()



if __name__ == '__main__':
    server()
