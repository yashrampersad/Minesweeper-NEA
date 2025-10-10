import pygame
import gui_elements as gui
import game
import time
import random
import math
import copy

# making the colour palette easily accessible through a dictionary and using memorable names
colours = {"WHITE":"#d9d9d9",
           "LIGHT SILVER":"#717d9f",
           "DARK SILVER":"#667192",
           "GREY":"#4e5770",
           "LIGHT COAL":"#353a49",
           "DARK COAL":"#2c2f3b",}

# board_dimensions = (height, width)

class Base(): # base class with attributes and methods every screen needs so that it can be inherited from to save time
    def __init__(self, surface, screen_width, screen_height, global_scale):
        gui.setScale(global_scale)
        self.global_scale = global_scale
        self.surface = surface
        self.screen_width, self.screen_height = screen_width*self.global_scale, screen_height*self.global_scale
        self.scale = "Small"

    def run(self):
        self.drawElements()
        return self.handleEvents()
    
class InitialScale(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale):
        super().__init__(surface, screen_width, screen_height, global_scale)
        gui.setScale(self.global_scale)
        self.scale_label = gui.Label(colours["GREY"], "Set screen size:", colours["WHITE"], 1)
        self.scale_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Small", "Medium", "Large"], colours["GREY"], 1)
        self.done_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Done", colours["GREY"], 0.8)
    
    def drawElements(self):
        self.scale_label.draw(self.surface, 50, 50)
        self.scale_button.draw(self.surface, 50, 120)
        self.done_button.draw(self.surface, 50, 220)

    def handleEvents(self):
        state = "SCALE"
        for event in pygame.event.get():
            self.scale = self.scale_button.updateState(event)
            if self.scale == "Small":
                self.global_scale = 0.65
            elif self.scale == "Medium":
                self.global_scale = 0.8
            elif self.scale == "Large":
                self.global_scale = 1
            if self.scale_button.isClicked(event):
                gui.setScale(self.global_scale)
            if self.done_button.isClicked(event):
                state = "MAIN"
            elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return "QUIT"
        return state, self.global_scale

class MainMenu(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale):
        super().__init__(surface, screen_width, screen_height, global_scale)
        # initialising the gui elements that will be used
        self.title = gui.Label(colours["GREY"], "Minespeeder", colours["WHITE"], 4)
        self.subtitle = gui.Label(colours["GREY"], "a real-time minesweeper racer", colours["WHITE"], 0.7)
        self.create_lobby = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Create Lobby", colours["GREY"], 1)
        self.join_lobby = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Join Lobby", colours["GREY"], 1)
        self.quit = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit", colours["GREY"], 0.8)

        self.was_disconnected = False
        self.disconnected_label = gui.Label(None, "Disconnected from Lobby", colours["WHITE"], 1.5)
        self.continue_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Continue", colours["GREY"], 1)

        self.choose_lobby_name = False
        self.lobby_name_box = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "Enter lobby name...", colours["GREY"], 1)
        self.lobby_name_desc = gui.Label(None, "Press Enter to confirm", colours["WHITE"], 0.8)
        self.back = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Back", colours["GREY"], 0.8)

    def drawElements(self):
        if self.was_disconnected:
            self.disconnected_label.draw(self.surface, self.screen_width//2-self.disconnected_label.box.width//2, self.screen_height//2-(self.disconnected_label.box.height+self.continue_button.box.height)//2)
            self.continue_button.draw(self.surface, self.screen_width//2-self.continue_button.box.width//2, self.screen_height*11//16-(self.disconnected_label.box.height+self.continue_button.box.height)//2)
        elif self.choose_lobby_name:
            self.lobby_name_box.draw(self.surface, self.screen_width//2-self.lobby_name_box.box.width//2, self.screen_height//2-self.lobby_name_box.box.height)
            self.lobby_name_desc.draw(self.surface, self.screen_width//2-self.lobby_name_desc.box.width//2, self.screen_height*8//16)
            self.back.draw(self.surface, 20, 20)
        else:
            # drawing gui elements
            self.title.draw(self.surface, (self.screen_width//2)-self.title.box.width//2, self.screen_height//3-self.title.box.height//2)
            self.subtitle.draw(self.surface, (self.screen_width//2), self.screen_height//3-self.title.box.height//2+self.title.box.height*2//3)
            self.create_lobby.draw(self.surface, (self.screen_width//2)-self.create_lobby.box.width//2, self.screen_height//2)
            self.join_lobby.draw(self.surface, (self.screen_width//2)-self.join_lobby.box.width//2, self.screen_height*21//32)
            self.quit.draw(self.surface, (self.screen_width//2)-self.quit.box.width//2, self.screen_height*13//16)

    def handleEvents(self):
        is_host = None
        quit_requested = False
        lobby_name = ""
        if self.was_disconnected:
            for event in pygame.event.get():
                if self.continue_button.isClicked(event):
                    self.was_disconnected = False
                if event.type == pygame.QUIT:
                    quit_requested = True
        elif self.choose_lobby_name:
            for event in pygame.event.get():
                lobby_name = self.lobby_name_box.update(event)
                if lobby_name is not None:
                    if len(lobby_name) > 0:
                        is_host = True
                        self.choose_lobby_name = False
                        self.lobby_name_desc.text = "Press Enter to confirm"
                    else:
                        self.lobby_name_desc.text = "Invalid lobby name"
                    self.lobby_name_box.reset("Enter lobby name...")
                
                if self.back.isClicked(event) or event.type == pygame.QUIT:
                    self.choose_lobby_name = False
                    self.lobby_name_box.reset("Enter lobby name...")
                    self.lobby_name_desc.text = "Press Enter to confirm"

                    
        else:
            # depending on the button that is clicked, switch states to go to a different screen
            for event in pygame.event.get():
                if self.create_lobby.isClicked(event):
                    self.choose_lobby_name = True
                if self.join_lobby.isClicked(event):
                    is_host = False
                if self.quit.isClicked(event):
                    quit_requested = True
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    quit_requested = True
            # if nothing is pressed, remain in the current state/screen

        return quit_requested, is_host, lobby_name
    
class FindingLobbies(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale):
        super().__init__(surface, screen_width, screen_height, global_scale)
        self.title = gui.Label(colours["GREY"], "Available Lobbies", colours["WHITE"], 1.5)
        self.back_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Back", colours["GREY"], 0.8)
        # self.error_message = gui.Label(None, "Lobby not available. Please try again later.", colours["WHITE"], 0.6)
        self.drawn_lobbies = {}
        self.lobby_dict = {}
    
    def run(self, available_lobbies): # pass in the list of available lobbies so that they can be constantly updated
        self.drawElements(available_lobbies)
        return self.handleEvents()

    def drawElements(self, available_lobbies):
        self.back_button.draw(self.surface, 20, 20)
        # refresh lobbies if they have changed
        if self.lobby_dict != available_lobbies:
            self.drawn_lobbies = {}
            self.lobby_dict = available_lobbies.copy()
            for lobby in available_lobbies.keys():
                self.drawn_lobbies[lobby] = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], lobby, colours["GREY"], 1.2)
        y = 1
        self.title.draw(self.surface, (self.screen_width//2)-self.title.box.width//2, self.screen_height*y//18)
        for lobby in self.drawn_lobbies.values():
            y += 3
            lobby.draw(self.surface, (self.screen_width//2)-lobby.box.width//2, self.screen_height*y//18)

    def handleEvents(self):
        chosen_lobby = None
        quit_requested = False
        for event in pygame.event.get():
            for lobby_name, lobby in self.drawn_lobbies.items():
                if lobby.isClicked(event):
                    chosen_lobby = lobby_name

            if self.back_button.isClicked(event):
                quit_requested = True

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit_requested = True
        return quit_requested, chosen_lobby
    
class ClientLobby(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale, lobby_name):
        super().__init__(surface, screen_width, screen_height, global_scale)
        self.board_difficulty = "Beginner"
        self.board_dimensions = [9,9]
        self.num_mines = 10
        self.num_games = 1
        self.total_games = 1
        self.board_squares = []
        self.square_width = 0
        self.current_dimensions = None
        self.player_names = None
        self.player_labels = None
        self.own_player_name = f"Guest {random.randint(1, 100)}"
        self.prev_player_name = self.own_player_name
        self.ready = False
        self.current_info = {"name":self.own_player_name,
                             "ready":self.ready}
        
        self.final_standings = FinalStandings(surface, screen_width, screen_height, global_scale)
        self.show_final_standings = False
        self.final_return_info = None


        self.own_player_name_box = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], f"{self.own_player_name}", colours["GREY"], 0.6)
        self.player_name_prompt = gui.Label(None, "click to change name", colours["WHITE"], 0.4)

        self.title = gui.Label(None, lobby_name, colours["WHITE"], 1.5)
        self.quit_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit", colours["GREY"], 0.6)

        # self.time_label = gui.Label(None, "Time:", colours["WHITE"], 1)
        # self.time = gui.Label(None, "0.0s", colours["WHITE"], 1)
        # self.flag_label = gui.Label(None, "Flags:", colours["WHITE"], 1)
        # self.flag_count = gui.Label(None, "10", colours["WHITE"], 1)

        self.board_size_label = gui.Label(None, "Board size", colours["WHITE"], 0.6)
        self.board_height = gui.Label(colours["WHITE"], "9", colours["GREY"], 0.6)
        self.x_label = gui.Label(None, "X", colours["WHITE"], 0.6)
        self.board_width = gui.Label(colours["WHITE"], "9", colours["GREY"], 0.6)

        self.num_mines_desc = gui.Label(None, "Mines:", colours["WHITE"], 0.6)
        self.num_mines_label = gui.Label(colours["WHITE"], "10", colours["GREY"], 0.6)
        self.num_games_desc = gui.Label(None, "Best of:", colours["WHITE"], 0.6)
        self.num_games_label = gui.Label(colours["WHITE"], "1", colours["GREY"], 0.6)

        self.board_difficulty_label = gui.Label(colours["WHITE"], self.board_difficulty, colours["GREY"], 0.6)

        self.ready_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Ready up!", colours["GREY"], 0.8)
        self.waiting_label = gui.Label(None, "Waiting to start...", colours["WHITE"], 0.8)
        self.ready_label = gui.Label(None, "Ready", colours["LIGHT SILVER"], 0.6)

    def run(self, return_info):
        if not self.show_final_standings:
            self.final_return_info = None
            if self.board_dimensions != self.current_dimensions:
                self.setBoard()
                self.current_dimensions = self.board_dimensions.copy()
            self.drawElements(return_info)
            return self.handleEvents()
        else:
            if self.final_return_info is None:
                self.final_return_info = copy.deepcopy(return_info)
            self.ready = False
            self.final_standings.drawElements(self.final_return_info)
            params = self.final_standings.handleEvents()
            self.show_final_standings = params[0]
            return params[1], params[2]

    def drawElements(self, return_info):

        self.board_difficulty_label.text = self.board_difficulty
        self.board_height.text = str(self.board_dimensions[0])
        self.board_width.text = str(self.board_dimensions[1])
        self.num_mines_label.text = str(self.num_mines)
        self.num_games_label.text = str(self.num_games)

        # self.time_label.draw(self.surface, (self.screen_width//2)-50-self.time_label.box.width, self.screen_height//18)
        # self.time.draw(self.surface, (self.screen_width//2)-50-self.time_label.box.width//2-self.time.box.width//2, self.screen_height//9)
        # self.flag_label.draw(self.surface, (self.screen_width//2)+50, self.screen_height//18)
        # self.flag_count.draw(self.surface, (self.screen_width//2)+50+self.flag_label.box.width//2-self.flag_count.box.width//2, self.screen_height//9)

        self.title.draw(self.surface, self.screen_width//2-(self.title.box.width+self.quit_button.box.width+10)//2, -5)
        self.quit_button.draw(self.surface, self.screen_width//2-(-self.title.box.width+self.quit_button.box.width-10)//2, self.title.box.height//2-5-self.quit_button.box.height//2)
        
        self.drawBoard()

        self.board_size_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_label.box.width-60, self.screen_height*3//16)
        self.board_height.draw(self.surface, self.screen_width-self.board_height.box.width-20, self.screen_height//4)
        self.x_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-30, self.screen_height//4)
        self.board_width.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-40, self.screen_height//4)
        self.board_difficulty_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_label.box.width-60, self.screen_height//4)


        self.num_mines_desc.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_label.box.width-60, self.screen_height*3//8)
        self.num_mines_label.draw(self.surface, self.screen_width-self.num_mines_label.box.width-20, self.screen_height*3//8)
        self.num_games_desc.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_label.box.width-60, self.screen_height*4//8)
        self.num_games_label.draw(self.surface, self.screen_width-self.num_games_label.box.width-20, self.screen_height*4//8)

        # refresh the player labels if anything has changed
        if return_info["names"].values() != self.player_names:
            self.player_names = [x for x in return_info["names"].values()]
            while self.player_names.count(self.own_player_name) > 1: # if a guest happens to have the same number name, regenerate it
                self.own_player_name = f"Guest {random.randint(1, 100)}"
                self.own_player_name_box.reset(self.own_player_name)
                self.current_info["name"] = self.own_player_name
            self.player_labels = []
            for player in self.player_names:
                if self.own_player_name != player and self.prev_player_name != player:
                    self.player_labels.append(gui.Label(None, player, colours["WHITE"], 0.6))

        # draw all the player labels at regular intervals
        y = 5
        x = 20
        self.own_player_name_box.draw(self.surface, x, self.screen_height*y//16)
        try:
            if return_info["ready players"][self.own_player_name] == True:
                self.ready_label.draw(self.surface, x+self.own_player_name_box.box.width, self.screen_height*y//16)
        except KeyError:
            pass
        y += 1
        self.player_name_prompt.draw(self.surface, x, self.screen_height*y//16)
        y += 1
        for player_label in self.player_labels:
            player_label.draw(self.surface, x, self.screen_height*y//16)
            try:
                if return_info["ready players"][player_label.text] == True:
                    self.ready_label.draw(self.surface, x+player_label.box.width, self.screen_height*y//16)
            except KeyError:
                pass
            y += 1.5

        if self.ready:
            self.waiting_label.draw(self.surface, self.screen_width//2-self.waiting_label.box.width//2, self.screen_height-self.ready_button.box.height-10)
        else:
            self.ready_button.draw(self.surface, self.screen_width//2-self.ready_button.box.width//2, self.screen_height-self.ready_button.box.height-10)

        # update from return info
        self.board_difficulty = return_info["settings"][0]
        self.board_dimensions = return_info["settings"][1]
        self.num_mines = return_info["settings"][2]
        self.num_games = return_info["num games"][0]
        self.total_games = return_info["num games"][1]

    def setBoard(self):
        # self.board_squares is a list of all the UISquares so that the class can keep track of all of them
        self.board_squares.clear()
        for i in range(self.board_dimensions[0]):
            for j in range(self.board_dimensions[1]):
                # draw squares in alternating colours to create a checkerboard pattern
                if (i+j)%2 == 0:
                    square = gui.UISquare((i,j), colours["LIGHT COAL"], colours["LIGHT SILVER"])
                else:
                    square = gui.UISquare((i,j), colours["DARK COAL"], colours["DARK SILVER"])
                self.board_squares.append(square)

    def drawBoard(self):
        # get the maximum scale based on the available space
        max_square_width_x = (self.screen_width-self.screen_width*3//7)//self.board_dimensions[1]
        max_square_width_y = (self.screen_height-self.screen_height*9//24)//self.board_dimensions[0]
        # choose the smaller value to result in the board being as large as possible while still fitting
        if max_square_width_x > max_square_width_y:
            self.square_width = max_square_width_y
        else:
            self.square_width = max_square_width_x
        current_square = 0
        y = self.screen_height//4
        for i in range(self.board_dimensions[0]):
            x = (self.screen_width//2) - self.square_width*self.board_dimensions[1]//2
            for j in range(self.board_dimensions[1]):
                self.board_squares[current_square].draw(self.surface, x, y, self.square_width, "1", False, False)
                current_square += 1
                x += self.square_width
            y += self.square_width


    def handleEvents(self):
        quit_requested = False
        for event in pygame.event.get():
            new_name = self.own_player_name_box.update(event)
            if new_name is not None:
                if 0 < len(new_name) <= 15 and (self.player_names.count(new_name) == 0 or new_name == self.own_player_name) and new_name not in self.player_names:
                    self.own_player_name_box.reset(new_name)
                    self.player_name_prompt.text = "click to change name"
                    self.prev_player_name = self.own_player_name
                    self.own_player_name = new_name
                    self.current_info["name"] = self.own_player_name
                else:
                    self.own_player_name_box.reset(self.own_player_name_box.default_text)
                    self.player_name_prompt.text = "invalid name"
            if not self.ready:
                if self.ready_button.isClicked(event):
                    self.ready = True
            self.current_info["ready"] = self.ready

            if self.quit_button.isClicked(event):
                quit_requested = True

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit_requested = True
        return quit_requested, self.current_info
    
class HostLobby(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale, lobby_name):
        super().__init__(surface, screen_width, screen_height, global_scale)
        self.board_difficulty = "Beginner"
        self.board_dimensions = [9,9]
        self.num_mines = 10
        self.num_games = 1
        self.board_squares = []
        self.square_width = 0
        self.current_dimensions = None
        self.player_names = None
        self.player_labels = None
        self.own_player_name = f"Guest {random.randint(1, 100)}"
        self.ready = False
        self.current_info = {"name":self.own_player_name,
                             "ready":self.ready,
                             "settings":[self.board_difficulty, self.board_dimensions, self.num_mines],
                             "num games":[1,1]} # num games is [to be played, total]
        
        self.final_standings = FinalStandings(surface, screen_width, screen_height, global_scale)
        self.final_return_info = None
        self.show_final_standings = False

        self.own_player_name_box = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], f"{self.own_player_name}", colours["GREY"], 0.6)
        self.player_name_prompt = gui.Label(None, "click to change name", colours["WHITE"], 0.4)

        self.title = gui.Label(None, lobby_name, colours["WHITE"], 1.5)
        self.quit_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Close Lobby", colours["GREY"], 0.6)

        self.time_label = gui.Label(None, "Time:", colours["WHITE"], 1)
        self.time = gui.Label(None, "0.0s", colours["WHITE"], 1)
        self.flag_label = gui.Label(None, "Flags:", colours["WHITE"], 1)
        self.flag_count = gui.Label(None, "10", colours["WHITE"], 1)

        self.board_size_label = gui.Label(None, "Board size", colours["WHITE"], 0.6)
        self.board_height = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "9", colours["GREY"], 0.6)
        self.x_label = gui.Label(None, "X", colours["WHITE"], 0.6)
        self.board_width = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "9", colours["GREY"], 0.6)

        self.num_mines_desc = gui.Label(None, "Mines:", colours["WHITE"], 0.6)
        self.num_mines_box = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "10", colours["GREY"], 0.6)
        self.num_games_desc = gui.Label(None, "Best of:", colours["WHITE"], 0.6)
        self.num_games_box = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "1", colours["GREY"], 0.6)

        self.board_difficulty_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Beginner", "Intermediate", "Expert", "Custom"], colours["GREY"], 0.6)
        self.board_dimension_prompt = gui.Label(None, "click to change size and mines", colours["WHITE"], 0.4)

        self.ready_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Ready up!", colours["GREY"], 0.8)
        self.waiting_label = gui.Label(None, "Waiting to start...", colours["WHITE"], 0.8)
        self.ready_label = gui.Label(None, "Ready", colours["LIGHT SILVER"], 0.6)

    def run(self, return_info):
        if not self.show_final_standings:
            self.final_return_info = None
            if self.board_dimensions != self.current_dimensions:
                self.setBoard()
                self.current_dimensions = self.board_dimensions.copy()
            self.drawElements(return_info)
            return self.handleEvents()
        else:
            if self.final_return_info is None:
                self.final_return_info = copy.deepcopy(return_info)
            self.ready = False
            self.final_standings.drawElements(self.final_return_info)
            params = self.final_standings.handleEvents()
            self.show_final_standings = params[0]
            return params[1], params[2]

    def drawElements(self, return_info):

        self.title.draw(self.surface, self.screen_width//2-(self.title.box.width+self.quit_button.box.width+10)//2, -5)
        self.quit_button.draw(self.surface, self.screen_width//2-(-self.title.box.width+self.quit_button.box.width-10)//2, self.title.box.height//2-5-self.quit_button.box.height//2)
        
        self.drawBoard()

        self.board_size_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, self.screen_height*3//16)
        self.board_height.draw(self.surface, self.screen_width-self.board_height.box.width-20, self.screen_height//4)
        self.x_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-30, self.screen_height//4)
        self.board_width.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-40, self.screen_height//4)
        self.board_difficulty_button.draw(self.surface, -self.screen_width//18, -self.screen_height//9)
        self.board_difficulty_button.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, self.screen_height//4)


        self.num_mines_desc.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, self.screen_height*3//8)
        self.num_mines_box.draw(self.surface, self.screen_width-self.num_mines_box.box.width-20, self.screen_height*3//8)
        self.num_games_desc.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, self.screen_height*4//8)
        self.num_games_box.draw(self.surface, self.screen_width-self.num_games_box.box.width-20, self.screen_height*4//8)

        # if the board difficulty is set to Custom, prompt the user to enter their own width and height
        if self.board_difficulty == "Custom":
            self.board_dimension_prompt.draw(self.surface, self.screen_width-self.board_dimension_prompt.box.width, self.screen_height//3)

        # refresh the player labels if anything has changed
        if return_info["names"].values() != self.player_names:
            self.player_names = [x for x in return_info["names"].values()]
            while self.player_names.count(self.own_player_name) > 1: # if a guest happens to have the same number name, regenerate it
                self.own_player_name = f"Guest {random.randint(1, 100)}"
                self.own_player_name_box.reset(self.own_player_name)
                self.current_info["name"] = self.own_player_name
            self.player_labels = []
            for player in self.player_names:
                if self.own_player_name != player:
                    self.player_labels.append(gui.Label(None, player, colours["WHITE"], 0.6))

        # draw all the player labels at regular intervals
        y = 5
        x = 20
        self.own_player_name_box.draw(self.surface, x, self.screen_height*y//16)
        try:
            if return_info["ready players"][self.own_player_name] == True:
                self.ready_label.draw(self.surface, x+self.own_player_name_box.box.width, self.screen_height*y//16)
        except KeyError:
            pass
        y += 1
        self.player_name_prompt.draw(self.surface, x, self.screen_height*y//16)
        y += 1
        for player_label in self.player_labels:
            player_label.draw(self.surface, x, self.screen_height*y//16)
            try:
                if return_info["ready players"][player_label.text] == True:
                    self.ready_label.draw(self.surface, x+player_label.box.width, self.screen_height*y//16)
            except KeyError:
                pass
            y += 1.5
        if self.ready:
            self.waiting_label.draw(self.surface, self.screen_width//2-self.waiting_label.box.width//2, self.screen_height-self.ready_button.box.height-10)
        else:
            self.ready_button.draw(self.surface, self.screen_width//2-self.ready_button.box.width//2, self.screen_height-self.ready_button.box.height-10)

    def setBoard(self):
        # self.board_squares is a list of all the UISquares so that the class can keep track of all of them
        self.board_squares.clear()
        for i in range(self.board_dimensions[0]):
            for j in range(self.board_dimensions[1]):
                # draw squares in alternating colours to create a checkerboard pattern
                if (i+j)%2 == 0:
                    square = gui.UISquare((i,j), colours["LIGHT COAL"], colours["LIGHT SILVER"])
                else:
                    square = gui.UISquare((i,j), colours["DARK COAL"], colours["DARK SILVER"])
                self.board_squares.append(square)

    def drawBoard(self):
        # get the maximum scale based on the available space
        max_square_width_x = (self.screen_width-self.screen_width*3//7)//self.board_dimensions[1]
        max_square_width_y = (self.screen_height-self.screen_height*9//24)//self.board_dimensions[0]
        # choose the smaller value to result in the board being as large as possible while still fitting
        if max_square_width_x > max_square_width_y:
            self.square_width = max_square_width_y
        else:
            self.square_width = max_square_width_x
        current_square = 0
        y = self.screen_height//4
        for i in range(self.board_dimensions[0]):
            x = (self.screen_width//2) - self.square_width*self.board_dimensions[1]//2
            for j in range(self.board_dimensions[1]):
                self.board_squares[current_square].draw(self.surface, x, y, self.square_width, "1", False, False)
                current_square += 1
                x += self.square_width
            y += self.square_width


    def handleEvents(self):
        quit_requested = False
        for event in pygame.event.get():
            self.board_difficulty = self.board_difficulty_button.updateState(event)
            if self.board_difficulty == "Custom":
                # if the difficulty is set to Custom, allow the input boxes to have text entered into them
                new_width = self.board_width.update(event)
                new_height = self.board_height.update(event)
                new_mine_num = self.num_mines_box.update(event)
                if new_width is not None:
                    # ensure that the width and height entered is a number and is 50 or below as to not overload the program
                    if new_width.isnumeric() and 3 < int(new_width) <= 30:
                        self.board_dimensions[1] = int(new_width)
                        self.board_width.reset(new_width)
                        self.board_dimension_prompt.text = "click to change size and mines"
                        midpoint = math.ceil(0.15*self.board_dimensions[0]*self.board_dimensions[1]) # set the default to a mine density of 15%, similar to intermediate
                        self.num_mines = midpoint
                        self.current_info["settings"][2] = self.num_mines
                        self.num_mines_box.reset(f"{midpoint}")
                        self.current_info["settings"][1] = self.board_dimensions
                    else:
                        self.board_width.reset(self.board_width.default_text)
                        self.board_dimension_prompt.text = "invalid board dimension"
                if new_height is not None:
                    if new_height.isnumeric() and 3 < int(new_height) <= 30:
                        self.board_dimensions[0] = int(new_height)
                        self.board_height.reset(new_height)
                        self.board_dimension_prompt.text = "click to change size and mines"
                        midpoint = math.ceil(0.15*self.board_dimensions[0]*self.board_dimensions[1]) # set the default to a mine density of 15%, similar to intermediate
                        self.num_mines = midpoint
                        self.current_info["settings"][2] = self.num_mines
                        self.num_mines_box.reset(f"{midpoint}")
                        self.current_info["settings"][1] = self.board_dimensions
                    else:
                        self.board_height.reset(self.board_height.default_text)
                        self.board_dimension_prompt.text = "invalid board dimension"
                if new_mine_num is not None:
                    # ensure that thay have a number of mines that will allow them to guarantee that the first click is safe (have at least a 3x3 area free)
                    if new_mine_num.isnumeric() and math.ceil(0.05*self.board_dimensions[0]*self.board_dimensions[1]) <= int(new_mine_num) <= (self.board_dimensions[0]*self.board_dimensions[1])-9:
                        self.num_mines = int(new_mine_num)
                        self.num_mines_box.reset(new_mine_num)
                        self.current_info["settings"][2] = self.num_mines
                        self.board_dimension_prompt.text = "click to change size and mines"
                    else:
                        self.num_mines_box.reset(self.num_mines_box.default_text)
                        self.board_dimension_prompt.text = "invalid number of mines"
            else:
                if self.board_difficulty_button.isClicked(event):
                    if self.board_difficulty == "Beginner":
                        self.board_dimensions = [9,9]
                        self.num_mines = 10
                    elif self.board_difficulty == "Intermediate":
                        self.board_dimensions = [16, 16]
                        self.num_mines = 40
                    elif self.board_difficulty == "Expert":
                        self.board_dimensions = [16, 30]
                        self.num_mines = 99
                    # reset the text in the width and height boxes to reflect the new width and height
                    self.board_height.reset(str(self.board_dimensions[0]))
                    self.board_width.reset(str(self.board_dimensions[1]))
                    self.num_mines_box.reset(str(self.num_mines))
                    # self.flag_count.text = str(self.num_mines)
                    self.current_info["settings"][1] = self.board_dimensions
                    self.current_info["settings"][2] = self.num_mines
            self.current_info["settings"][0] = self.board_difficulty

            new_name = self.own_player_name_box.update(event)
            if new_name is not None:
                if 0 < len(new_name) <= 15 and (self.player_names.count(new_name) == 0 or new_name == self.own_player_name):
                    self.own_player_name_box.reset(new_name)
                    self.player_name_prompt.text = "click to change name"
                    self.own_player_name = new_name
                    self.current_info["name"] = self.own_player_name
                else:
                    self.own_player_name_box.reset(self.own_player_name_box.default_text)
                    self.player_name_prompt.text = "invalid name"

            games = self.num_games_box.update(event)
            if games is not None:
                if games.isnumeric() and int(games) <= 10:
                    self.num_games_box.reset(games)
                    self.num_games = int(games)
                    self.current_info["num games"] = [self.num_games, self.num_games]
                else:
                    self.num_games_box.reset(str(self.num_games))

            if not self.ready:
                if self.ready_button.isClicked(event):
                    self.ready = True
            self.current_info["ready"] = self.ready

            if self.quit_button.isClicked(event):
                quit_requested = True

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit_requested = True

        return quit_requested, self.current_info

class Game(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale, player_name, return_info):
        super().__init__(surface, screen_width, screen_height, global_scale)
        self.board_dimensions = return_info["settings"][1]
        self.current_dimensions = return_info["settings"][1]
        self.square_width = 0
        self.board_squares = []
        self.board = self.setBoard()
        self.total_clicks = 0
        self.num_mines = return_info["settings"][2]
        self.remaining_flags = return_info["settings"][2]
        self.first_click = True
        self.first_game = True
        self.start_time = None
        self.game_result = None
        self.completion = 0
        self.current_info = {}
        self.show_standings = False
        self.sort_standings_by = "Game standings"
        self.num_games = return_info["num games"][0]
        self.total_games = return_info["num games"][1]
        self.ready = False
        self.player_name = player_name
        self.game_started = False
        self.countdown = "3"
        self.countdown_label = gui.Label(colours["WHITE"], self.countdown, colours["GREY"], 1.5)


        if self.total_games > 1:
            self.title = gui.Label(None, f"Game {(self.total_games+1)-self.num_games} of {self.total_games}", colours["WHITE"], 1.5)
        else:
            self.title = gui.Label(None, "Play!", colours["WHITE"], 1.5)
        self.quit_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit", colours["GREY"], 0.6)

        self.time_label = gui.Label(None, "Time:", colours["WHITE"], 1)
        self.time = gui.Label(None, "0.0s", colours["WHITE"], 1)
        self.current_time = 0.000
        self.flag_label = gui.Label(None, "Flags:", colours["WHITE"], 1)
        self.flag_count = gui.Label(None, "10", colours["WHITE"], 1)
        self.reset_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Reset", colours["GREY"], 0.8)

        self.finished_title = gui.Label(None, "Game Finished!", colours["WHITE"], 1)
        self.num_clicks = gui.Label(None, "No. of clicks: 0", colours["WHITE"], 0.8)
        self.extra_stats_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Extra stats", colours["GREY"], 0.8)
        self.show_extra_stats = False
        self.benchmark = gui.Label(None, "3BV: 0", colours["WHITE"], 0.8)
        self.benchmark_value = 0
        self.benchmark_description = gui.Label(None, "(How much work the board was)", colours["WHITE"], 0.5)
        self.benchmark_sec = gui.Label(None, "3BV/s: 0", colours["WHITE"], 0.8)
        self.benchmark_sec_value = 0
        self.benchmark_sec_description = gui.Label(None, "(Your speed)", colours["WHITE"], 0.5)
        self.efficiency = gui.Label(None, "Efficiency: 0", colours["WHITE"], 0.8)
        self.efficiency_value = 0
        self.efficiency_description = gui.Label(None, "(Percentage of nessecary clicks)", colours["WHITE"], 0.5)
        self.stats_calculated = False

        self.sort_by_label = gui.Label(None, "Sort by", colours["WHITE"], 0.6)
        self.sort_by_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Game standings", "Overall points"], colours["GREY"], 0.6)
        self.ready_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Ready up!", colours["GREY"], 0.8)
        self.standings_label = gui.Label(None, "Name", colours["WHITE"], 0.6)
        self.points_label = gui.Label(None, "Overall points", colours["WHITE"], 0.6)

        self.ready_label = gui.Label(None, "Ready", colours["LIGHT COAL"], 0.6)
        self.waiting_label = gui.Label(None, "Waiting to start...", colours["WHITE"], 0.8)
        
    def run(self, return_info):
        self.board_dimensions = return_info["settings"][1]
        self.num_mines = return_info["settings"][2]
        self.remaining_flags = self.num_mines
        self.num_games = return_info["num games"][0]
        self.total_games = return_info["num games"][1]
        if self.board_dimensions != self.current_dimensions:
            self.setBoard()
            self.current_dimensions = self.board_dimensions.copy()
        self.drawElements(return_info)
        return self.handleEvents()
    
    def drawElements(self, return_info):
        try:
            self.countdown = return_info["countdown"]
        except KeyError:
            pass
        if not self.game_started:
            self.title.text = "Get ready..."
            if self.countdown == "0":
                self.game_started = True
        elif not self.show_standings:
            if self.total_games > 1:
                self.title.text = f"Game {(self.total_games+1)-self.num_games} of {self.total_games}"
            else:
                self.title.text = "Play!"
        else:
            if self.num_games == 1:
                self.title.text = f"{self.num_games} game left"
            else:
                self.title.text = f"{self.num_games} games left"

        self.title.draw(self.surface, self.screen_width//2-(self.title.box.width+self.quit_button.box.width)//2, -10)
        self.quit_button.draw(self.surface, self.screen_width//2-(-self.title.box.width+self.quit_button.box.width)//2, self.title.box.height//2-15-self.quit_button.box.height//2)

        if not self.first_game and self.game_result != 1:
            self.current_time = time.time() - self.start_time
            self.time.text = str(self.current_time)[:str(self.current_time).index(".")+2] + "s" # print to 1 dp during game so that it is not too overwhelming
        elif self.game_result == 1:
            self.time.text = str(self.current_time)[:str(self.current_time).index(".")+4] + "s" # print to 3 dp after game so that it is to the millisecond
        self.time_label.draw(self.surface, (self.screen_width//2)-50-self.time_label.box.width, self.screen_height*2//18)
        self.time.draw(self.surface, (self.screen_width//2)-50-self.time_label.box.width//2-self.time.box.width//2, self.screen_height*3//18)
        self.flag_label.draw(self.surface, (self.screen_width//2)+50, self.screen_height*2//18)
        self.flag_count.draw(self.surface, (self.screen_width//2)+50+self.flag_label.box.width//2-self.flag_count.box.width//2, self.screen_height*3//18)


        if self.game_result == 1:
            self.finished_title.text = "Game Finished!"
            self.finished_title.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, self.screen_height//9)
            self.extra_stats_button.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*2)//7)
        else:
            self.reset_button.draw(self.surface, self.screen_width//2-self.reset_button.box.width//2, self.screen_height-self.reset_button.box.height-10)
            
        if self.game_result == -1:
            self.finished_title.text = "Try again!"
            self.finished_title.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, self.screen_height//9)
            # reveal the whole board to show where the mines where
            for row in self.board:
                for square in row:
                    square.reveal()

        if self.show_extra_stats:
            self.num_clicks.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*3)//7)
            self.benchmark.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*4)//7)
            self.benchmark_description.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*9)//14)
            self.benchmark_sec.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*5)//7)
            self.benchmark_sec_description.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*11)//14)
            self.efficiency.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*6)//7)
            self.efficiency_description.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*13)//14)


        if len(return_info["standings"]) != len(return_info["names"]):
            standings = {name:0 for name in return_info["names"].values()}
        else:
            standings = return_info["standings"]
        standings[self.player_name] = self.completion # update the player's progress instantly with the current completion to reduce lag

        y = 5
        x = self.screen_width//30
        max_width = ((self.screen_width)//2)-((self.square_width*self.board_dimensions[1])//2)-100
        for i, (name, completion) in enumerate(standings.items()):
            num = gui.Label(None, str(i+1),  colours["WHITE"], 0.6)
            num.draw(self.surface, self.screen_width//180, self.screen_height*y//16)
            bar = gui.ProgressBar(max_width, colours["DARK SILVER"], colours["LIGHT COAL"], 0.6)
            bar.draw(self.surface, x, self.screen_height*y//16, completion)
            y += 1.5

        self.drawBoard()

        if self.show_standings:
            self.sort_by_label.draw(self.surface, x, self.screen_height*3//16)
            self.sort_by_button.draw(self.surface, x+self.sort_by_label.box.width+10, self.screen_height*3//16)
            if self.ready:
                self.waiting_label.draw(self.surface, self.screen_width//2-self.waiting_label.box.width//2, self.screen_height-self.ready_button.box.height-10)
            else:
                self.ready_button.draw(self.surface, self.screen_width//2-self.ready_button.box.width//2, self.screen_height-self.ready_button.box.height-10)
            self.standings_label.draw(self.surface, x, self.screen_height*4//16)
            self.points_label.draw(self.surface, x+max_width-self.points_label.box.width, self.screen_height*4//16)
            y = 5
            if self.sort_standings_by == "Game standings": # draw names and total points in order of the standings of the current game
                for name in return_info["standings"].keys():
                    points = gui.Label(None, str(return_info["total points"][name]), colours["WHITE"], 0.6)
                    points.draw(self.surface, self.screen_width//30+max_width-points.box.width, self.screen_height*y//16)
                    name = gui.Label(None, name, colours["WHITE"], 0.6)
                    name.draw(self.surface, x, self.screen_height*y//16)
                    try:
                        if return_info["ready players"][name.text] == True:
                            self.ready_label.draw(self.surface, x+name.box.width, self.screen_height*y//16)
                    except KeyError:
                        pass
                    y += 1.5
            elif self.sort_standings_by == "Overall points":
                for name, points in return_info["total points"].items():
                    points = gui.Label(None, str(points), colours["WHITE"], 0.6)
                    points.draw(self.surface, self.screen_width//30+max_width-points.box.width, self.screen_height*y//16)
                    name = gui.Label(None, name, colours["WHITE"], 0.6)
                    name.draw(self.surface, x, self.screen_height*y//16)
                    try:
                        if return_info["ready players"][name.text] == True:
                            self.ready_label.draw(self.surface, x+name.box.width, self.screen_height*y//16)
                    except KeyError:
                        pass
                    y += 1.5
        else:
            while True:
                try:
                    y = 5
                    for name in standings.keys():
                        name = gui.Label(None, name, colours["WHITE"], 0.6)
                        name.draw(self.surface, x, self.screen_height*y//16)
                        y += 1.5
                    break
                except RuntimeError:
                    pass

        if not self.game_started:
            self.countdown_label.text = str(self.countdown)
            self.countdown_label.draw(self.surface, self.screen_width//2-self.countdown_label.box.width//2, self.screen_height//2-self.countdown_label.box.height//2)

    def setBoard(self):
        self.board_squares.clear()
        for i in range(self.board_dimensions[0]):
            for j in range(self.board_dimensions[1]):
                if (i+j)%2 == 0:
                    square = gui.UISquare((i,j), colours["LIGHT COAL"], colours["LIGHT SILVER"])
                else:
                    square = gui.UISquare((i,j), colours["DARK COAL"], colours["DARK SILVER"])
                self.board_squares.append(square)
        board = game.createBoard(self.board_dimensions)
        return board

    def drawBoard(self):
        previous_width = self.square_width
        max_square_width_x = (self.screen_width-self.screen_width*3//7)//self.board_dimensions[1]
        max_square_width_y = (self.screen_height-self.screen_height*9//24)//self.board_dimensions[0]
        if max_square_width_x > max_square_width_y:
            self.square_width = max_square_width_y
        else:
            self.square_width = max_square_width_x
        if previous_width != self.square_width:
            gui.loadResources(self.square_width)
        current_square = 0
        y = self.screen_height//4
        for row in self.board:
            x = (self.screen_width//2) - self.square_width*self.board_dimensions[1]//2
            for square in row:
                self.board_squares[current_square].draw(self.surface, x, y, self.square_width, str(square.getNumber()), square.isRevealed(), square.isFlagged())
                current_square += 1
                x += self.square_width
            y += self.square_width

    def handleEvents(self):
        self.current_info["completion"] = self.completion
        self.current_info["ready"] = self.ready
        quit_requested = False
        for event in pygame.event.get():
            if self.game_result is None and self.game_started: # if the game has not finished, continue
                for square in self.board_squares:
                    result = square.registerClick(event)
                    if result is not None:
                        if self.first_click:
                            if result[0] == 0 and not self.board[result[1][0]][result[1][1]].isFlagged(): # ensure the first click is a left click and not the user just flagging the board
                                if self.first_game: # start the timer at their first try, but if they lose or reset, continue the timer so the race is fair
                                    self.start_time = time.time()
                                    self.first_game = False
                                game.placeMines(self.board, square.position[0], square.position[1], self.num_mines)
                                game.generateNumbers(self.board)
                                self.first_click = False
                        self.game_result, self.remaining_flags, self.completion = game.performClick(self.board, result[0], result[1], self.num_mines)
                        self.flag_count.text = str(self.remaining_flags)
                        self.total_clicks += 1
            elif self.game_result == 1:
                if self.show_standings:
                    self.sort_standings_by = self.sort_by_button.updateState(event)
                    if not self.ready and self.ready_button.isClicked(event):
                        self.ready = True
                        self.ready_button.highlighted = True
                self.completion = 1
                if self.extra_stats_button.isClicked(event):
                    self.show_extra_stats = not self.show_extra_stats # toggle the extra stats when the button is clicked
                if not self.stats_calculated:
                    self.num_clicks.text = f"No. of clicks: {self.total_clicks}"
                    self.benchmark_value = game.calculateBenchmark(self.board)
                    self.benchmark.text = f"3BV: {self.benchmark_value}"
                    if self.current_time == 0: # avoid zero error if completed instantly
                        self.benchmark_sec.text = "3BV/s: infinite!"
                    else:
                        self.benchmark_sec_value = self.benchmark_value / self.current_time
                        self.benchmark_sec.text = "3BV/s: " + str(self.benchmark_sec_value)[:5]
                    self.efficiency_value = (self.benchmark_value*100)//self.total_clicks
                    self.efficiency.text = f"Efficiency: {self.efficiency_value}%"

                    self.stats_calculated = True
            if self.game_result != 1:
                if self.reset_button.isClicked(event):
                    self.board = self.setBoard()
                    self.remaining_flags = self.num_mines
                    self.completion = 0
                    self.total_clicks = 0
                    self.stats_calculated = False
                    self.show_extra_stats = False
                    self.game_result = None
                    self.first_click = True
                    break
        
            if self.quit_button.isClicked(event):
                quit_requested = True
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit_requested = True

        return quit_requested, self.current_info

    
class FinalStandings(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale):
        super().__init__(surface, screen_width, screen_height, global_scale)
        self.title = gui.Label(None, "Game Finished!", colours["WHITE"], 1.5)
        self.continue_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Continue to Lobby", colours["GREY"], 0.8)
        self.quit_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit to Main Menu", colours["GREY"], 0.8)
        self.points_label = gui.Label(None, "Points", colours["WHITE"], 0.8)
        self.name_label = gui.Label(None, "Name", colours["WHITE"], 0.8)
        self.bar = gui.ProgressBar(self.screen_width*8//18, colours["LIGHT SILVER"], colours["DARK COAL"], 0.8)

    def run(self, return_info):
        self.drawElements(return_info)
        return self.handleEvents()
    
    def drawElements(self, return_info):
        self.title.draw(self.surface, 0, 0)
        y = 1.5
        x = self.screen_width*5//18
        self.name_label.draw(self.surface, x, self.screen_height*y//9)
        if return_info["num games"][1] > 1:
            self.points_label.draw(self.surface, self.screen_width*13//18-self.points_label.box.width, self.screen_height*y//9)
            y += 1
            for i, (name, points) in enumerate(return_info["total points"].items()):
                self.bar.draw(self.surface, x, self.screen_height*y//9, 1)
                num = gui.Label(None, str(i+1)+". ",  colours["WHITE"], 0.8)
                num.draw(self.surface, x-(self.screen_width//18), self.screen_height*y//9)
                name_label = gui.Label(None, name, colours["WHITE"], 0.8)
                name_label.draw(self.surface, x, self.screen_height*y//9)
                point_label = gui.Label(None, str(points), colours["WHITE"], 0.8)
                point_label.draw(self.surface, self.screen_width*13//18-point_label.box.width, self.screen_height*y//9)
                y += 1
        else:
            y += 1
            for i, (name) in enumerate(return_info["standings"].keys()):
                self.bar.draw(self.surface, x, self.screen_height*y//9, 1)
                num = gui.Label(None, str(i+1)+". ",  colours["WHITE"], 0.8)
                num.draw(self.surface, x-(self.screen_width//18), self.screen_height*y//9)
                name_label = gui.Label(None, name, colours["WHITE"], 0.8)
                name_label.draw(self.surface, x, self.screen_height*y//9)
                y += 1

        self.continue_button.draw(self.surface, self.screen_width//2-self.continue_button.box.width//2, self.screen_height*(y+0.5)//9)
        self.quit_button.draw(self.surface, self.screen_width//2-self.quit_button.box.width//2, self.screen_height*(y+1.5)//9)

    def handleEvents(self):
        quit_requested = False
        cont = True
        for event in pygame.event.get():
            cont = not self.continue_button.isClicked(event)
            
            if self.quit_button.isClicked(event):
                quit_requested = True

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit_requested = True
        return cont, quit_requested, {}