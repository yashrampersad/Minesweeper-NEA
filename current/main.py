import pygame

pygame.init()

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 900
global_scale = 0.6

screen = pygame.display.set_mode((SCREEN_WIDTH*global_scale, SCREEN_HEIGHT*global_scale))

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

running = True

scale_screen = scr.InitialScale(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale)  

state = "SCALE"

set_scale = True
while set_scale:
    screen.fill(colours["GREY"])
    if state == "SCALE":
        state, new_scale = scale_screen.run()
        if new_scale != global_scale:
            global_scale = new_scale
            screen = pygame.display.set_mode((SCREEN_WIDTH*global_scale, SCREEN_HEIGHT*global_scale))
    elif state == "MAIN":
        set_scale = False
    elif state == "QUIT":
        set_scale = False
        running = False

    pygame.display.update()

title_screen = scr.MainMenu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale)
available_lobbies = ["Yash's Lobby", "Guest's Lobby"]
finding_lobbies_screen = scr.FindingLobbies(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale)
lobby_screen = scr.Lobby(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale, "Test Lobby")
player_names = ["Yash", "Guest", "Best_player67"]
standings = {"You":0, "Yash":0, "Guest":0, "Best_player67":0}
standings_screen = scr.FinalStandings(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale)

state = "MAIN"
prev_state = "MAIN"

# game loop
while running:

    screen.fill(colours["GREY"])

    if state == "MAIN":
        state = title_screen.run()
    elif state == "LOBBY":
        state = lobby_screen.run(player_names)
        prev_state = "LOBBY"
    elif state == "BROADCAST":
        state = finding_lobbies_screen.run(available_lobbies)
    elif state == "GAME":
        if prev_state != "GAME":
            game_screen = scr.Game(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale)
            standings = {"You":0, "Yash":0, "Guest":0, "Best_player67":0}
        state = game_screen.run(standings)
        # for key in standings.keys():
        #     if standings[key] < 1:
        #         x = random.randint(0,10)/(10**random.randint(3,6))
        #         standings[key] += x
        #         if standings[key] > 1:
        #             standings[key] = 1
        # standings = dict(sorted(standings.items(), key=lambda item: item[1], reverse=True))
        prev_state = "GAME"
    elif state == "STANDINGS":
        state = standings_screen.run(standings)
    elif state == "QUIT":
        running = False


    pygame.display.update()

    clock.tick(60)

pygame.quit()