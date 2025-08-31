import socket, threading, time, json, random

DISCOVERY_PORT = 57575

# current_info = {
#     "player": ip, port tuple,
#     "name": player name string,
#     "ready": ready for game boolean,
#     "completion" board completion float,
#     (HOST) "settings": difficulty, board dimensions, num mines tuple,
#     (HOST) "num games": number of games remaining int,
# }

# -----> host converts current into return ----->

# return_info = {
#     "lobbies": {lobby name:(ip, port)}
#     "names": (ip port):name dict,
#     "standings": name, float tuple,
#     "settings": difficulty, board dimensions, num mines tuple,
#     "num games": number of games remaining int,
#     "countdown": start of game countdown int,
#     "total points": points across multiple games: name, int tuple
# }

class Host():
    def __init__(self, lobby_name):
        self.state = "LOBBY"
        self.lobby_name = lobby_name

        self.return_info = {"settings":["Beginner", [9,9], 10], "num games":[1,1]}
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

        self.discover_client_thread = threading.Thread(target=self.discoverClient).start()
        self.add_client_thread = threading.Thread(self.addClient).start()
        self.send_info_thread = threading.Thread(self.sendInfo).start()
        self.recieve_info_thread = threading.Thread(self.recieveInfo).start()

    def getInfo(self, player_info):
        for key, value in player_info.items():
            self.player_info[key] = value
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
            self.games_remaining = self.player_info["num games"][0] # update board settings and the number of games from the host
            data, addr = sock.recvfrom(1024)
            msg = json.loads(data)
            if msg[0] == self.state: # only update information if the state of the client matches the host
                self.updateInfo(msg[1])
                if self.state == "LOBBY" or self.state == "STANDINGS":
                    if len(self.ready_players) > 0 and all(self.ready_players.values()): # if everyone is ready, start the game
                        self.standings = {}
                        self.total_points = {}
                        self.countdown = 3.0
                        self.state = "GAME"
                if self.state == "GAME":
                    self.standings = sorted(self.standings.items(), key=lambda item: item[1], reverse=True) # sort standings
                    if all(completion == 1 for completion in self.standings.values()): # if everyone has finished, move on from the game
                        for key in self.ready_players:
                            self.ready_players[key] = False # reset ready players
                        if self.return_info["num games"][0] == 1:
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
                            self.ready_players = {}
                self.return_info["num games"][0] = self.games_remaining # set all the return info to send to clients
                self.return_info["standings"] = self.standings
                self.return_info["total points"] = sorted(self.total_points.items(), key=lambda item: item[1], reverse=True) 
            # if a player has requested to quit, add them to the queue of players to remove
            elif msg[0] == "QUIT" and msg[1]["player"] not in self.to_remove:
                self.to_remove.append(msg[1]["player"])

class Client():
    def __init__(self):
        self.state = "BROADCAST"
        self.connected = False
        self.return_info = {}
        self.current_info = None
        self.CLIENT_IP = socket.gethostbyname(socket.gethostname()) # get the current IP address
        self.CLIENT_PORT = random.randint(10000, 55555) # randomly generate a unique port so that other clients do not end up recieving the same messages
        self.SERVER_IP = None
        self.SERVER_PORT = None

        self.discover_lobby_thread = threading.Thread(target=self.discoverLobby).start()
        self.send_info_thread = None
        self.recieve_info_thread = None

    def getInfo(self, current_info): # exchange information with the main part of the program
        for key, value in current_info.items():
            self.current_info[key] = value # get information in like player name or board completion
        return self.state, self.return_info # return the current state and the info gained from communicating with the host
    
    def discoverLobby(self):
        found_lobbies = {}
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # set up a broadcast socket to search for lobbies
        while True:
            if self.state == "BROADCAST":
                sock.sendto(b"Locating Minesweeper Lobby", ("255.255.255.255", DISCOVERY_PORT)) # this ip targets all devices on the network
                sock.settimeout(3.0) # set a timeout to resend the broadcast if nothing is found
                try:
                    try:
                        data, addr = sock.recvfrom(1024)
                    except ConnectionResetError:
                        time.sleep(3)
                        continue # if no host is found, resend the broadcast
                    try:
                        data = json.loads(data)
                        if type(data) is list and data[0] == "Minesweeper Lobby":
                            lobby_name = data[1]
                            server_ip = addr[0]
                            server_port = data[2]
                            if lobby_name not in found_lobbies:
                                print(f"found {lobby_name}, {server_ip}, {server_port}")
                                found_lobbies[lobby_name] = (server_ip, server_port) # add the lobby and IP to the found lobbies
                                self.requestLobby((server_ip, server_port))
                        else:
                            time.sleep(3) # wait to prevent overloading the network
                    except TypeError:
                        time.sleep(3)
                except socket.timeout:
                    continue
                self.return_info["lobbies"] = found_lobbies # add the dictionary of found lobbies to the return information

    def requestLobby(self, server_addr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self.connected:
            print("sending request")
            sock.sendto(json.dumps(("REQUEST", self.CLIENT_PORT)).encode(), server_addr) # send a request to that specific server
            sock.settimeout(3.0)
            try:
                try:
                    data, addr = sock.recvfrom(1024)
                except ConnectionResetError:
                    time.sleep(3)
                    continue # if no host is found, resend the request
                if data == b"Adding to lobby":
                    print("added to lobby")
                    sock.close()
                    self.connected = True
                    self.SERVER_IP = server_addr[0]
                    self.SERVER_PORT = server_addr[1]
                    self.state = "LOBBY"
                    self.send_info_thread = threading.Thread(target=self.sendInfo).start()
                    self.recieve_info_thread = threading.Thread(target=self.recieveInfo).start()
                    return
                else:
                    time.sleep(3)
            except socket.timeout:
                pass

    def sendInfo(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            if self.state == "MAIN" or self.state == "BROADCAST":
                time.sleep(1) # nothing to be sent, wait to prevent any overloading
            elif self.state != "QUIT":
                self.current_info["player"] = (self.CLIENT_IP, self.CLIENT_PORT) # add player ip, port to the info to be sent for unique identification
                sock.sendto(json.dumps((self.state, self.current_info),).encode(), (self.SERVER_IP, self.SERVER_PORT)) # send info to the host
                time.sleep(0.5)
            else:
                while self.connected: # keep sending quit messages until removed as the message may be lost due to UDP
                    sock.sendto(json.dumps(("QUIT", {"player":(self.CLIENT_IP, self.CLIENT_PORT)}),).encode(), self.SERVER_IP, self.SERVER_PORT)
                    time.sleep(0.5)

    def recieveInfo(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.CLIENT_IP, self.CLIENT_PORT))
        while True:
            if self.state != "MAIN" and self.state != "BROADCAST":
                sock.settimeout(5.0)
                try:
                    data, addr = sock.recvfrom(1024)
                except socket.timeout: # return back to main screen if there is nothing recieved from the host for a while
                    self.state = "MAIN"
                    self.connected = False
                    self.SERVER_IP = None
                    self.SERVER_PORT = None
                msg = json.loads(data)
                if self.state != "QUIT":
                    self.state = msg[0] # synchronise client state with host
                    self.return_info = msg[1] # get information from host
                elif self.state == "QUIT" and msg[1] == "Removed from lobby": # if successfully removed from the lobby, quit to the main screen
                        self.state = "MAIN"
                        self.connected = False
                        self.SERVER_IP = None
                        self.SERVER_PORT = None
            else:
                time.sleep(1) # wait if there is nothing to recieve to prevent overloading
