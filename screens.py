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
    def __init__(self, surface, screen_width, screen_height, available_lobbies):
        super().__init__(surface, screen_width, screen_height)
        self.title = gui.Label(colours["GREY"], "Available Lobbies", colours["WHITE"], 1.5)
        self.lobbies = []
        for lobby in available_lobbies:
            self.lobbies.append(gui.Button(colours["WHITE"], colours["LIGHT SILVER"], lobby, colours["GREY"], 1.2))

    def drawElements(self):
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
        self.title = gui.Label(colours["GREY"], "Test Lobby", colours["WHITE"], 2)
        self.quit_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit", colours["GREY"], 0.6)
        self.magnification_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["small", "medium", "large"], colours["GREY"], 0.5)
        self.magnification_label = gui.Label(colours["GREY"], "board magnification", colours["WHITE"], 0.5)

    def drawElements(self):
        self.title.draw(self.surface, -15, -15)
        self.quit_button.draw(self.surface, self.title.box.width-15, -5+self.title.box.height//2-self.quit_button.box.height//2)
        self.magnification_label.draw(self.surface, 5, self.screen_height-self.magnification_label.box.height-10)
        self.magnification_button.draw(self.surface, self.magnification_label.box.width+10, self.screen_height-self.magnification_button.box.height-10)

    def handleEvents(self):
        for event in pygame.event.get():
            magnification = self.magnification_button.updateState(event)
            if self.quit_button.isClicked(event):
                return "MAIN"

            if event.type == pygame.QUIT:
                return "QUIT"
        return "LOBBY"


