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

    def getInfo(self, current_info): # exchange information with the main part of the program
        self.current_info = current_info # get information in like player name or board completion
        return self.state, self.return_info # return the current state and the info gained from communicating with the host
    
    def discoverLobby(self):
        found_lobbies = {}
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # set up a broadcast socket to search for lobbies
        while self.state == "BROADCAST":
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
                    else:
                        time.sleep(3) # wait to prevent overloading the network
                except TypeError:
                    time.sleep(3)
            except socket.timeout:
                continue
            self.return_info["lobbies"] = found_lobbies # add the dictionary of found lobbies to the return information

    def requestLobby(self, server_addr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
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
                    self.sendInfo()
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
