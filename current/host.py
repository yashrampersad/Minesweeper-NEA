import socket, threading, time, json, random

DISCOVERY_PORT = 57575

class Host():
    def __init__(self, lobby_name):
        self.state = "LOBBY"
        self.lobby_name = lobby_name
        self.SERVER_PORT = random.randint(10000, 55555)
        self.clients = []

    def getInfo(self):
        return self.state
    
    def discoverClient(self):
        broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_sock.bind(('', DISCOVERY_PORT))
        while True:
        # search for clients and send a response
            data, addr = broadcast_sock.recvfrom(1024)
            if data == b"Locating Minesweeper Lobby":
                broadcast_sock.sendto(json.dumps(["Minesweeper Lobby", self.lobby_name, self.SERVER_PORT]).encode(), addr)

    def addClient(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.SERVER_PORT))
        data, client_addr = sock.recvfrom(1024)
        print("recieved request")
        data = json.loads(data)
        if data[0] == "REQUEST" and self.state == "LOBBY":
            client_port = int(data[1])
            sock.sendto(b"Adding to lobby", client_addr)
            self.clients.append(client_addr)
            print(f"added {client_addr} to lobby")


b = Host("yashabsh")
t_a = threading.Thread(target=b.discoverClient, daemon=True).start()
t_b = threading.Thread(target=b.addClient, daemon=True).start()

while True:
    pass