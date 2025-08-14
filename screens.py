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

    def drawElements(self):
        self.title.draw(self.surface, (self.screen_width//2)-self.title.box.width//2, 100)
        self.subtitle.draw(self.surface, (self.screen_width//2), self.title.box.height-40)
        self.create_lobby.draw(self.surface, (self.screen_width//2)-self.create_lobby.box.width//2, 450)
        self.join_lobby.draw(self.surface, (self.screen_width//2)-self.join_lobby.box.width//2, 600)

    def handleEvents(self):
        for event in pygame.event.get():
            if self.create_lobby.isClicked(event):
                return "LOBBY"
            elif self.join_lobby.isClicked(event):
                return "BROADCAST"

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
        if self.lobby_list != available_lobbies:
            self.lobby_list = available_lobbies
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

        self.title = gui.Label(colours["GREY"], lobby_name, colours["WHITE"], 2)
        self.quit_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit", colours["GREY"], 0.6)

        self.time_label = gui.Label(colours["GREY"], "Time:", colours["WHITE"], 1)
        self.time = gui.Label(colours["GREY"], "0.0s", colours["WHITE"], 1)
        self.flag_label = gui.Label(colours["GREY"], "Flags:", colours["WHITE"], 1)
        self.flag_count = gui.Label(colours["GREY"], "10", colours["WHITE"], 1)

        self.board_height = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "30", colours["GREY"], 0.6)
        self.x_label = gui.Label(colours["GREY"], "X", colours["WHITE"], 0.6)
        self.board_width = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "16", colours["GREY"], 0.6)

        self.board_difficulty_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Beginner", "Intermediate", "Expert", "Custom"], colours["GREY"], 0.6)

        self.board_dimension_prompt = gui.Label(colours["GREY"], "click to change size", colours["WHITE"], 0.4)

        self.magnification_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Medium", "Large", "Small"], colours["GREY"], 0.6)
        self.magnification_label = gui.Label(colours["GREY"], "board magnification", colours["WHITE"], 0.6)
        self.board = []
        self.current_dimensions = None

    def run(self):
        # print(self.board_dimensions, self.current_dimensions)
        if self.board_dimensions != self.current_dimensions:
            self.setBoard()
            self.current_dimensions = self.board_dimensions.copy()
        self.drawElements()
        return self.handleEvents()

    def drawElements(self):
        self.time_label.draw(self.surface, self.screen_width//4+100, self.title.box.height-100)
        self.time.draw(self.surface, self.screen_width//4+70+self.time_label.box.width, self.title.box.height-100)
        self.flag_label.draw(self.surface, (self.screen_width//2)+50, self.title.box.height-100)
        self.flag_count.draw(self.surface, (self.screen_width//2)+30+self.flag_label.box.width, self.title.box.height-100)

        self.title.draw(self.surface, -20, -30)
        self.quit_button.draw(self.surface, self.title.box.width-30, 40)
        
        self.drawBoard()

        self.board_height.draw(self.surface, self.screen_width-self.board_height.box.width-10, 40)
        self.x_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-20, 40)
        self.board_width.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-30, 40)

        self.board_difficulty_button.draw(self.surface, -100, -100)
        self.board_difficulty_button.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-50, 40)

        if self.board_difficulty == "Custom":
            self.board_dimension_prompt.draw(self.surface, self.screen_width-self.board_dimension_prompt.box.width, 0)

        self.magnification_label.draw(self.surface, 5, self.screen_height-self.magnification_label.box.height-10)
        self.magnification_button.draw(self.surface, self.magnification_label.box.width+10, self.screen_height-self.magnification_button.box.height-10)

    def setBoard(self):
        self.board.clear()
        for i in range(self.board_dimensions[0]):
            for j in range(self.board_dimensions[1]):
                if (i+j)%2 == 0:
                    square = gui.UISquare((j, i), colours["LIGHT COAL"], colours["WHITE"], colours["LIGHT SILVER"], colours["WHITE"])
                else:
                    square = gui.UISquare((j, i), colours["DARK COAL"], colours["WHITE"], colours["DARK SILVER"], colours["WHITE"])
                self.board.append(square)

    def drawBoard(self):
        if self.board_magnification == "Small":
            square_width = 40
        elif self.board_magnification == "Medium":
            square_width = 60
        elif self.board_magnification == "Large":
            square_width = 80
        current_square = 0
        y = self.title.box.height-20
        for i in range(self.board_dimensions[0]):
            x = (self.screen_width//2) - square_width*self.board_dimensions[1]//2
            for j in range(self.board_dimensions[1]):
                self.board[current_square].draw(self.surface, x, y, square_width, "1", colours["WHITE"], False, False)
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
                if new_width != None and new_width.isnumeric() and int(new_width) < 50:
                    self.board_dimensions[1] = int(new_width)
                    self.board_width.reset(new_width)
                if new_height != None and new_height.isnumeric() and int(new_height) < 50:
                    self.board_dimensions[0] = int(new_height)
                    self.board_height.reset(new_height)
            else:
                if self.board_difficulty == "Beginner":
                    self.board_dimensions = [9,9]
                elif self.board_difficulty == "Intermediate":
                    self.board_dimensions = [16, 16]
                elif self.board_difficulty == "Expert":
                    self.board_dimensions = [16, 30]
                self.board_height.reset(str(self.board_dimensions[0]))
                self.board_width.reset(str(self.board_dimensions[1]))

            if self.quit_button.isClicked(event):
                return "MAIN"

            for square in self.board:
                result = square.registerClick(event)
                if result != None:
                    print(f"square click {result[0]} at position {result[1]}")

            if event.type == pygame.QUIT:
                return "QUIT"
        return "LOBBY"


