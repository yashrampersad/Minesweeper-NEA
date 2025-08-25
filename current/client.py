import socket, threading, time, json, random

DISCOVERY_PORT = 57575


class Client():
    def __init__(self):
        self.state = "BROADCAST"
        self.return_info = {}
        self.CLIENT_PORT = random.randint(10000, 55555)

    def getInfo(self):
        return self.state, self.return_info
    
    def discoverLobbies(self):
        found_lobbies = {}
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.state == "BROADCAST":
            sock.sendto(b"Locating Minesweeper Lobby", ("255.255.255.255", DISCOVERY_PORT))
            sock.settimeout(3.0)
            try:
                data, addr = sock.recvfrom(1024)
                try:
                    data = json.loads(data)
                    if type(data) is list and data[0] == "Minesweeper Lobby":
                        lobby_name = data[1]
                        server_ip = addr[0]
                        server_port = data[2]
                        if lobby_name not in found_lobbies:
                            print(f"found {lobby_name}, {server_ip}, {server_port}")
                            found_lobbies[lobby_name] = (server_ip, server_port) # add the lobby and IP to the found lobbies
                            self.request_lobby((server_ip, server_port))
                    else:
                        time.sleep(3)
                except TypeError:
                    time.sleep(3)
            except socket.timeout:
                pass
            self.return_info = found_lobbies

    def request_lobby(self, server_addr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            sock.settimeout(3.0)
            print("sending request")
            sock.sendto(json.dumps(("REQUEST", self.CLIENT_PORT)).encode(), server_addr)
            try:
                data, addr = sock.recvfrom(1024)
                if data == b"Adding to lobby":
                    self.state = "LOBBY"
                    print("added to lobby")
                    sock.close()
                    return
                else:
                    time.sleep(3)
            except socket.timeout:
                pass



b = Client()
t_b = threading.Thread(target=b.discoverLobbies, daemon=True).start()
while True:
    pass