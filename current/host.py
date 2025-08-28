import socket, threading, time, json, random

DISCOVERY_PORT = 57575

class Host():
    def __init__(self, lobby_name):
        self.state = "LOBBY"
        self.lobby_name = lobby_name

        self.return_info = {}
        self.player_info = {}
        self.ready_players = {}
        self.player_names = {}
        self.standings = {}
        self.total_points = {}
        self.countdown = 3.0
        self.games_remaining = None

        self.SERVER_IP = socket.gethostbyname(socket.gethostname()) # get the current IP address
        self.SERVER_PORT = random.randint(10000, 55555) # generate a unique port for the host so that it is sent unique information
        self.clients = []
        self.to_remove = []

    def getInfo(self, player_info):
        self.player_info = player_info
        self.player_info["player"] = ("HOST", 00000) # player info is the host's own player information, as the host is also a player
        self.updateInfo(self.player_info)
        return self.state, self.return_info
    
    def discoverClient(self):
        broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_sock.bind(('', DISCOVERY_PORT)) # bind to the broadcast discovery port
        while True:
        # fetch broadcast from clients and send a response
            data, addr = broadcast_sock.recvfrom(1024)
            if data == b"Locating Minesweeper Lobby":
                broadcast_sock.sendto(json.dumps(["Minesweeper Lobby", self.lobby_name, self.SERVER_PORT]).encode(), addr)

    def addClient(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.SERVER_IP, self.SERVER_PORT))
        while True:
            data, client_addr = sock.recvfrom(1024)
            print("recieved request")
            data = json.loads(data)
            # add them to the lobby if requested
            if data[0] == "REQUEST" and self.state == "LOBBY":
                sock.sendto(b"Adding to lobby", client_addr)
                self.clients.append(client_addr)
                print(f"added {client_addr} to lobby")

    def sendInfo(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            if self.state == "GAME":
                if self.countdown >= 0: # decrease the countdown if required
                    self.return_info["countdown"] = self.countdown.round()
                    self.countdown -= 0.5

            for addr in self.clients: # send the return info to all the clients in the lobby
                sock.sendto(json.dumps((self.state, self.return_info),).encode(), addr)

            while len(self.to_remove) > 0: # remove any players in the queue from all records 
                self.names.remove(self.to_remove[0])
                self.clients.remove(self.to_remove[0])
                sock.sendto(json.dumps(("QUIT", "Removed from lobby"),).encode(), self.to_remove[0]) # send a confirmation response
                self.to_remove.pop[0]

            time.sleep(0.5)
    
    def updateInfo(self, new_info):
        self.player_names[new_info["player"]] = new_info["name"]
        self.ready_players[new_info["player"]] = new_info["ready"]
        self.standings[new_info["name"]] = new_info["completion"]

    def recieveInfo(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.SERVER_IP, self.SERVER_PORT))
        while True:
            self.return_info["settings"] = self.player_info["settings"]
            self.games_remaining = self.player_info["num games"] # update board settings and the number of games from the host
            data, addr = sock.recvfrom(1024)
            msg = json.loads(data)
            if msg[0] == self.state: # only update information if the state of the client matches the host
                self.updateInfo(msg[1])
                if self.state == "LOBBY":
                    if all(self.ready_players.values()): # if everyone is ready, start the game
                        self.standings = {}
                        self.total_points = {}
                        self.countdown = 3.0
                        self.state = "GAME"
                if self.state == "GAME":
                    self.standings = sorted(self.standings.items(), key=lambda item: item[1], reverse=True) # sort standings
                    if all(completion == 1 for completion in self.standings.values()): # if everyone has finished, move on from the game
                        for key in self.ready_players:
                            self.ready_players[key] = False # reset ready players
                        if self.return_info["num games"] == 1:
                            if len(self.total_points) != 0: # if multiple games were selected allocate points to each player based on where they placed
                                for standing, player in enumerate(self.standings):
                                    self.total_points[player] += 100 - standing*10
                            self.state = "LOBBY"
                        else:
                            # update total points for multiple games
                            if len(self.total_points) != 0:
                                for standing, player in enumerate(self.standings):
                                    self.total_points[player] = 100 - standing*10
                            else:
                                for standing, player in enumerate(self.standings):
                                    self.total_points[player] += 100 - standing*10
                            self.games_remaining -= 1
                            self.state = "STANDINGS" # if everyone has finished, go to the standings
                self.return_info["num games"] = self.games_remaining # set all the return info to send to clients
                self.return_info["standings"] = self.standings
                self.return_info["total points"] = self.total_points
            # if a player has requested to quit, add them to the queue of players to remove
            elif msg[0] == "QUIT" and msg[1]["player"] not in self.to_remove:
                self.to_remove.append(msg[1]["player"])
            

                    



b = Host("yashabsh")
t_a = threading.Thread(target=b.discoverClient, daemon=True).start()
t_b = threading.Thread(target=b.addClient, daemon=True).start()

while True:
    pass