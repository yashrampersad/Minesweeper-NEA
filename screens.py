import pygame
import gui_elements as gui

# making the colour palette easily accessible through a dictionary and using memorable names
colours = {"WHITE":"#d9d9d9",
           "LIGHT SILVER":"#717d9f",
           "DARK SILVER":"#667192",
           "GREY":"#4e5770",
           "LIGHT COAL":"#353a49",
           "DARK COAL":"#2c2f3b",}

class Base():
    def __init__(self, surface, screen_width, screen_height):
        self.surface = surface
        self.screen_width, self.screen_height = screen_width, screen_height

    def run(self):
        self.drawElements()
        return self.handleEvents()

class MainMenu(Base):
    def __init__(self, surface, screen_width, screen_height):
        super().__init__(surface, screen_width, screen_height)
        self.title = gui.Label(colours["GREY"], "Minespeeder", colours["WHITE"], 4)
        self.subtitle = gui.Label(colours["GREY"], "a real-time minesweeper racer", colours["WHITE"], 0.7)
        self.create_lobby = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Create Lobby", colours["GREY"], 1.2)
        self.join_lobby = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Join Lobby", colours["GREY"], 1.2)
        self.quit = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit", colours["GREY"], 1.2)

    def drawElements(self):
        self.title.draw(self.surface, (self.screen_width//2)-self.title.box.width//2, 100)
        self.subtitle.draw(self.surface, (self.screen_width//2), self.title.box.height-40)
        self.create_lobby.draw(self.surface, (self.screen_width//2)-self.create_lobby.box.width//2, 450)
        self.join_lobby.draw(self.surface, (self.screen_width//2)-self.join_lobby.box.width//2, 600)
        self.quit.draw(self.surface, (self.screen_width//2)-self.quit.box.width//2, 750)

    def handleEvents(self):
        for event in pygame.event.get():
            if self.create_lobby.isClicked(event):
                return "LOBBY"
            if self.join_lobby.isClicked(event):
                return "BROADCAST"
            if self.quit.isClicked(event):
                return "QUIT"
            if event.type == pygame.QUIT:
                return "QUIT"
        return "MAIN"
    
class FindingLobbies(Base):
    def __init__(self, surface, screen_width, screen_height):
        super().__init__(surface, screen_width, screen_height)
        self.title = gui.Label(colours["GREY"], "Available Lobbies", colours["WHITE"], 1.5)
        self.lobbies = []
        self.lobby_list = []
    
    def run(self, available_lobbies):
        self.drawElements(available_lobbies)
        return self.handleEvents()

    def drawElements(self, available_lobbies):
        # refresh lobbies if they have changed
        if self.lobby_list != available_lobbies:
            self.lobbies = []
            self.lobby_list = available_lobbies.copy()
            for lobby in available_lobbies:
                self.lobbies.append(gui.Button(colours["WHITE"], colours["LIGHT SILVER"], lobby, colours["GREY"], 1.2))
        y = 50
        self.title.draw(self.surface, (self.screen_width//2)-self.title.box.width//2, y)
        for lobby in self.lobbies:
            y += 150
            lobby.draw(self.surface, (self.screen_width//2)-lobby.box.width//2, y)

    def handleEvents(self):
        for event in pygame.event.get():
            for lobby in self.lobbies:
                if lobby.isClicked(event):
                    return "LOBBY"

            if event.type == pygame.QUIT:
                return "QUIT"
        return "BROADCAST"
    
class Lobby(Base):
    def __init__(self, surface, screen_width, screen_height, lobby_name):
        super().__init__(surface, screen_width, screen_height)
        self.board_magnification = "Medium"
        self.board_difficulty = "Beginner"
        self.board_dimensions = [9,9]
        self.board_squares = []
        self.current_dimensions = None
        self.player_names = None
        self.player_labels = None

        self.own_player_name = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "Guest", colours["GREY"], 0.6)
        self.player_name_prompt = gui.Label(None, "click to change name", colours["WHITE"], 0.4)

        self.title = gui.Label(colours["GREY"], lobby_name, colours["WHITE"], 2)
        self.quit_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit", colours["GREY"], 0.6)

        self.time_label = gui.Label(None, "Time:", colours["WHITE"], 1)
        self.time = gui.Label(None, "0.0s", colours["WHITE"], 1)
        self.flag_label = gui.Label(None, "Flags:", colours["WHITE"], 1)
        self.flag_count = gui.Label(None, "10", colours["WHITE"], 1)

        self.board_size_label = gui.Label(None, "Board size", colours["WHITE"], 0.6)
        self.board_height = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "30", colours["GREY"], 0.6)
        self.x_label = gui.Label(None, "X", colours["WHITE"], 0.6)
        self.board_width = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "16", colours["GREY"], 0.6)

        self.num_games_label = gui.Label(None, "Best of", colours["WHITE"], 0.6)
        self.num_games = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "1", colours["GREY"], 0.6)

        self.board_difficulty_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Beginner", "Intermediate", "Expert", "Custom"], colours["GREY"], 0.6)
        self.board_dimension_prompt = gui.Label(None, "click to change size", colours["WHITE"], 0.4)

        self.magnification_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Medium", "Large", "Small"], colours["GREY"], 0.6)
        self.magnification_label = gui.Label(colours["GREY"], "board magnification", colours["WHITE"], 0.6)

        self.ready_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Ready up!", colours["GREY"], 0.8)

    def run(self, player_list):
        if self.board_dimensions != self.current_dimensions:
            self.setBoard()
            self.current_dimensions = self.board_dimensions.copy()
        self.drawElements(player_list)
        return self.handleEvents()

    def drawElements(self, player_list):
        self.time_label.draw(self.surface, self.screen_width//4+100, 100)
        self.time.draw(self.surface, self.screen_width//4+70+self.time_label.box.width, 100)
        self.flag_label.draw(self.surface, (self.screen_width//2)+50, 100)
        self.flag_count.draw(self.surface, (self.screen_width//2)+30+self.flag_label.box.width, 100)

        self.title.draw(self.surface, -20, -30)
        self.quit_button.draw(self.surface, self.title.box.width-30, 40)
        
        self.drawBoard()

        self.board_size_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, 170)
        self.board_height.draw(self.surface, self.screen_width-self.board_height.box.width-20, 230)
        self.x_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-30, 230)
        self.board_width.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-40, 230)
        self.board_difficulty_button.draw(self.surface, -100, -100)
        self.board_difficulty_button.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, 230)


        self.num_games_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, 320)
        self.num_games.draw(self.surface, self.screen_width-self.num_games.box.width-20, 320)

        if self.board_difficulty == "Custom":
            self.board_dimension_prompt.draw(self.surface, self.screen_width-self.board_dimension_prompt.box.width, 280)

        # refresh the player labels if anything has changed
        if player_list != self.player_names:
            self.player_names = player_list.copy()
            self.player_labels = []
            for player in player_list:
                self.player_labels.append(gui.Label(None, player, colours["WHITE"], 0.6))
        # draw all the player labels at regular intervals
        y = 190
        x = 20
        self.own_player_name.draw(self.surface, x, y)
        y += 55
        self.player_name_prompt.draw(self.surface, x, y)
        y += 30
        for player_label in self.player_labels:
            player_label.draw(self.surface, x, y)
            y += 80

        self.magnification_label.draw(self.surface, 5, self.screen_height-self.magnification_label.box.height-10)
        self.magnification_button.draw(self.surface, self.magnification_label.box.width+10, self.screen_height-self.magnification_button.box.height-10)

        self.ready_button.draw(self.surface, self.screen_width//2-self.ready_button.box.width//2, self.screen_height-self.ready_button.box.height-10)

    def setBoard(self):
        self.board_squares.clear()
        for i in range(self.board_dimensions[0]):
            for j in range(self.board_dimensions[1]):
                if (i+j)%2 == 0:
                    square = gui.UISquare((j, i), colours["LIGHT COAL"], colours["LIGHT SILVER"])
                else:
                    square = gui.UISquare((j, i), colours["DARK COAL"], colours["DARK SILVER"])
                self.board_squares.append(square)

    def drawBoard(self):
        if self.board_magnification == "Small":
            square_width = 35
        elif self.board_magnification == "Medium":
            square_width = 45
        elif self.board_magnification == "Large":
            square_width = 65
        current_square = 0
        y = 180
        for i in range(self.board_dimensions[0]):
            x = (self.screen_width//2) - square_width*self.board_dimensions[1]//2
            for j in range(self.board_dimensions[1]):
                self.board_squares[current_square].draw(self.surface, x, y, square_width, "1", colours["WHITE"], False, False)
                current_square += 1
                x += square_width
            y += square_width


    def handleEvents(self):
        for event in pygame.event.get():
            self.board_magnification = self.magnification_button.updateState(event)
            self.board_difficulty = self.board_difficulty_button.updateState(event)
            if self.board_difficulty == "Custom":
                new_width = self.board_width.update(event)
                new_height = self.board_height.update(event)
                if new_width is not None:
                    if new_width.isnumeric() and int(new_width) <= 50:
                        self.board_dimensions[1] = int(new_width)
                        self.board_width.reset(new_width)
                    else:
                        self.board_width.reset(self.board_width.default_text)
                if new_height is not None:
                    if new_height.isnumeric() and int(new_height) <= 50:
                        self.board_dimensions[0] = int(new_height)
                        self.board_height.reset(new_height)
                    else:
                        self.board_height.reset(self.board_height.default_text)
            else:
                if self.board_difficulty == "Beginner":
                    self.board_dimensions = [9,9]
                elif self.board_difficulty == "Intermediate":
                    self.board_dimensions = [16, 16]
                elif self.board_difficulty == "Expert":
                    self.board_dimensions = [16, 30]
                self.board_height.reset(str(self.board_dimensions[0]))
                self.board_width.reset(str(self.board_dimensions[1]))

            new_name = self.own_player_name.update(event)
            if new_name is not None:
                if 0 < len(new_name) <= 10:
                    self.own_player_name.reset(new_name)
                else:
                    self.own_player_name.reset(self.own_player_name.default_text)

            games = self.num_games.update(event)
            if games is not None:
                if games.isnumeric() and int(games) <= 10:
                    self.num_games.reset(games)
                else:
                    self.num_games.reset(self.num_games.default_text)

            if self.ready_button.isClicked(event):
                global board_magnification
                board_magnification = self.board_magnification
                global board_dimensions
                board_dimensions = self.board_dimensions
                return "GAME"

            if self.quit_button.isClicked(event):
                return "MAIN"

            for square in self.board_squares:
                result = square.registerClick(event)
                if result != None:
                    print(f"square click {result[0]} at position {result[1]}")

            if event.type == pygame.QUIT:
                return "QUIT"
        return "LOBBY"

class Game(Base):
    def __init__(self, surface, screen_width, screen_height):
        super().__init__(surface, screen_width, screen_height)
        self.board_dimensions = board_dimensions
        self.board_magnification = board_magnification
        self.board_squares = []
        self.finished = False

        self.magnification_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Medium", "Large", "Small"], colours["GREY"], 0.6)
        self.magnification_button.current_state = self.magnification_button.states.index(self.board_magnification)
        self.magnification_button.text = self.board_magnification
        self.magnification_label = gui.Label(colours["GREY"], "board magnification", colours["WHITE"], 0.6)
        self.setBoard()
        
    def run(self, standings):
        self.drawElements(standings)
        return self.handleEvents()
    
    def drawElements(self, standings):

        y = 190
        x = 60
        self.finished = True
        for i, (key, value) in enumerate(standings.items()):
            if value < 1:
                self.finished = False
            num = gui.Label(None, str(i+1),  colours["WHITE"], 0.6)
            num.draw(self.surface, 10, y)
            bar = gui.ProgressBar(500, colours["DARK SILVER"], colours["LIGHT COAL"], 0.6)
            bar.draw(self.surface, x, y, value)
            name = gui.Label(None, key, colours["WHITE"], 0.6)
            name.draw(self.surface, x, y)
            y += 80

        self.magnification_label.draw(self.surface, 5, self.screen_height-self.magnification_label.box.height-10)
        self.magnification_button.draw(self.surface, self.magnification_label.box.width+10, self.screen_height-self.magnification_button.box.height-10)
        self.drawBoard()

    def setBoard(self):
        self.board_squares.clear()
        for i in range(self.board_dimensions[0]):
            for j in range(self.board_dimensions[1]):
                if (i+j)%2 == 0:
                    square = gui.UISquare((j, i), colours["LIGHT COAL"], colours["LIGHT SILVER"])
                else:
                    square = gui.UISquare((j, i), colours["DARK COAL"], colours["DARK SILVER"])
                self.board_squares.append(square)

    def drawBoard(self):
        if self.board_magnification == "Small":
            square_width = 35
        elif self.board_magnification == "Medium":
            square_width = 45
        elif self.board_magnification == "Large":
            square_width = 65
        current_square = 0
        y = 180
        for i in range(self.board_dimensions[0]):
            x = (self.screen_width//2) - square_width*self.board_dimensions[1]//2
            for j in range(self.board_dimensions[1]):
                self.board_squares[current_square].draw(self.surface, x, y, square_width, "1", colours["WHITE"], False, False)
                current_square += 1
                x += square_width
            y += square_width

    def handleEvents(self):
        for event in pygame.event.get():
            self.board_magnification = self.magnification_button.updateState(event)

            for square in self.board_squares:
                result = square.registerClick(event)


            if event.type == pygame.QUIT:
                    return "QUIT"
        if self.finished:
                return "STANDINGS"
        return "GAME"
    
class FinalStandings(Base):
    def __init__(self, surface, screen_width, screen_height):
        super().__init__(surface, screen_width, screen_height)
        self.title = gui.Label(None, "Game Finished!", colours["WHITE"], 2)
        self.continue_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Continue to lobby", colours["GREY"], 1)
        self.quit_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit to Main Menu", colours["GREY"], 1)


    def run(self, standings):
        self.drawElements(standings)
        return self.handleEvents()
    
    def drawElements(self, standings):
        self.title.draw(self.surface, -20, -30)

        y = 190
        x = 500
        for i, (key) in enumerate(standings.keys()):
            num = gui.Label(None, str(i+1),  colours["WHITE"], 1)
            num.draw(self.surface, x-50, y)
            name = gui.Label(None, key, colours["WHITE"], 1)
            name.draw(self.surface, x, y)
            y += 80

        self.continue_button.draw(self.surface, self.screen_width//2-self.continue_button.box.width//2, y+50)
        self.quit_button.draw(self.surface, self.screen_width//2-self.quit_button.box.width//2, y+200)

    def handleEvents(self):
        for event in pygame.event.get():
            if self.continue_button.isClicked(event):
                return "LOBBY"
            
            if self.quit_button.isClicked(event):
                return "MAIN"

            if event.type == pygame.QUIT:
                return "QUIT"
        return "STANDINGS"