#! /usr/local/bin/python3
import socket, sys, threading, time, re
import game, env
from game import Player
G = None
class Game_Controller():
    msgs = []
    conns = {}
    players = []

    def append(self, msg):
        self.msgs.append(msg)
    def join(self, conn, name):
        self.conns[name] = conn

    def send_to(self, name, msg):
        if isinstance(msg, dict):
            msg = f"{msg.get('name')}: {msg.get('action')}ed {msg.get('content')}"
        msg = ('\n' + str(msg)).encode()
        self.conns[name].sendall(msg)
    def run(self):
        global G
        while True:
            time.sleep(1)
            if self.msgs:
                msg = self.msgs.pop(0)
                print(msg)
                if msg['action'] == 'disconnect':
                    self.sendall(f'{msg["name"]} disconnected')
                    player = self.conns.pop(msg['name'])
                    if G:
                        restart()
                        continue
                elif msg['action'] == 'start':
                    if G: continue
                    players = list(self.conns.keys())
                    G = game.Game(players)
                    G.start()
                    self.sendall(f'Game started, the first player is {G.current_player.name}')
                    continue
                if not G: 
                    self.send_to(msg['name'], 'No game started')
                    continue 
                if msg['action'] == 'show':
                    player = G.find_player(msg['name'])  
                    if not player: continue
                    self.send_to(player.name, f'Your hand: {player.show_hand()}')
                    continue
                elif msg['action'] == 'status':
                    self.send_to(msg['name'], str(G))
                    continue
                elif msg['action'] == 'transfer':
                    msg = msg.get('content')
                    if not msg: continue
                    nbs = re.findall(r'\d+', msg)
                    nbs = [int(nb) for nb in nbs]
                    for card in G.find_player(msg['name']).hand:
                        if not nbs: break
                        if isinstance(card, game.Card) and card.suit == 'Joker':
                            card.value = nbs.pop(0)
                    continue

                if G.current_player.name != msg['name']:
                    self.send_to(msg['name'], 'Not your turn')
                    continue
                if msg['action'] == 'skip':
                    G.skip()
                elif msg['action'] == 'play':
                    ok, ans = G.play(msg['content'])
                    if not ok:
                        self.send_to(msg['name'], ans)
                    else: 
                        self.sendall(msg)
                        if not G.current_player.hand:
                            self.sendall(f'{G.current_player.name} wins')
                elif msg['action'] == 'draw':
                    ok, ans = G.draw()
                    if not ok:
                        self.send_to(msg['name'], ans)
                    else: self.sendall(msg)

            if isinstance(G,game.Game) and G.empty():
                restart()



    def sendall(self, msg):
        print(msg)
        for name in self.conns.keys():
            self.send_to(name, msg)


controller = Game_Controller()


def handle_client(conn, addr):
    print('Connected by', addr)
    name = None
    while True:
        try:
            data = eval(conn.recv(1024))
            if not name: 
                name = data.get('name')
                controller.join(conn, name)
            controller.append(data)
        except ConnectionResetError:
            break
    controller.append({'name': name, 'action': 'disconnect'})
    conn.close()


def start_server(port = env.port):
    global conn
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen()
    print('Server started')
    threading.Thread(target=controller.run).start()
    threading.Thread(target=restarter).start()
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def restart():
    global G
    G = None
    controller.msgs = []
    controller.sendall('Game ended, restarting')


def restarter():
    while True:
        cmd = input('>')
        if cmd[0] == 'r':
            restart()


if __name__ == '__main__':
    start_server()

