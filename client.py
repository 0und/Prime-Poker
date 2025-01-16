#! /usr/local/bin/python3
import socket, threading, time, sys
port = 60012
# host = 'silvertech.duckdns.org'
host = '10.0.0.152'
help_msg = '''Commands: 
    b: Begin game
    s: Show your hand
    S: Show game status
    p: Pass your turn
    d: Draw a card
    h: Help
    e: Exit
'''
def client_receive(conn):
    while True:
        data = conn.recv(1024)
        
        msg = data.decode().strip()
        if msg == 'EXIT':
            return
        print(msg)


def start_client(port = port, name = ''):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    if not name:
        name = input('Enter your name: ')
    join_msg = {'action': 'join', 'name': name}
    client.sendall(str(join_msg).encode())
    threading.Thread(target=client_receive, args=(client,)).start()
    print('Connected to server')
    while True:
        msg = input('Enter message: ')
        if not msg: continue
        if msg == 'e':
            message = {'action': 'disconnect', 'name': name}
        elif msg[0] == 'h':
            print(help_msg)
            continue
        elif msg[0] == 'b':
            message = {'action': 'start'}
        elif msg[0] == 's':
            message = {'action': 'show', 'name': name}
        elif msg[0] == 'p':
            message = {'action': 'skip', 'name': name}
        elif msg[0] == 'd':
            message = {'action': 'draw', 'name': name}
        elif msg[0] == 'S':
            message = {'action': 'status', 'name': name}
        elif msg[0] == 't':
            message = {'action': 'transfer', 'name': name, 'content': msg}
        else:
            message = {'action': 'play', 'name': name, 'content': msg}
        print(message)
        client.sendall(str(message).encode())
        time.sleep(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        start_client()
    elif len(sys.argv) == 2:
        start_client(name = sys.argv[1])

