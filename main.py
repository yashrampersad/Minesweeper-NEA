import pygame

pygame.init()

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 900

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

import screens as scr



pygame.key.set_repeat(500, 40) # allow the ability to hold keys like backspace to input them multiple times. 500 and 40 are used as these are the standard millisecond timings for key repeats across many operating systems

# making the colour palette easily accessible through a dictionary and using memorable names
colours = {"WHITE":"#d9d9d9",
           "LIGHT SILVER":"#717d9f",
           "DARK SILVER":"#667192",
           "GREY":"#4e5770",
           "LIGHT COAL":"#353a49",
           "DARK COAL":"#2c2f3b",}


pygame.display.set_caption("Minespeeder")
clock = pygame.time.Clock()

title_screen = scr.MainMenu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
available_lobbies = ["Yash's Lobby", "Guest's Lobby"]
finding_lobbies_screen = scr.FindingLobbies(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
lobby_screen = scr.Lobby(screen, SCREEN_WIDTH, SCREEN_HEIGHT, "Test Lobby")
player_names = ["Yash", "Guest", "Best_player67"]

state = "MAIN"

# game loop
running = True
while running:

    screen.fill(colours["GREY"])

    if state == "MAIN":
        state = title_screen.run()
    elif state == "LOBBY":
        state = lobby_screen.run(player_names)
    elif state == "BROADCAST":
        state = finding_lobbies_screen.run(available_lobbies)
    elif state == "QUIT":
        running = False

    pygame.display.update()

    clock.tick(60)

pygame.quit()