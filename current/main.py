import pygame
import multiplayer
import threading

pygame.init()

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 900
global_scale = 0.6

# screen = pygame.display.set_mode((SCREEN_WIDTH*global_scale, SCREEN_HEIGHT*global_scale))
screen = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN | pygame.SCALED)
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()
global_scale = SCREEN_WIDTH // 1800

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

# scale_screen = scr.InitialScale(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale)  

# state = "SCALE"

# set_scale = True
# while set_scale:
#     screen.fill(colours["GREY"])
#     if state == "SCALE":
#         state, new_scale = scale_screen.run()
#         if new_scale != global_scale:
#             global_scale = new_scale
#             screen = pygame.display.set_mode((SCREEN_WIDTH*global_scale, SCREEN_HEIGHT*global_scale))
#     elif state == "MAIN":
#         set_scale = False
#     elif state == "QUIT":
#         set_scale = False
#         running = False

#     pygame.display.update()

# set default current and return info
current_info = {
    "name":"",
    "ready":False,
    "completion":0
}
return_info = {
    "lobbies":{},
    "settings":["Beginner", [9,9], 10], 
    "num games":[1,1],
    "names":{},
    "ready players":{}
}

title_screen = scr.MainMenu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale)
finding_lobbies_screen = scr.FindingLobbies(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale)

is_host = None

state = "MAIN"
prev_state = "MAIN"

# game loop
while running:
    screen.fill(colours["GREY"])

    if state == "MAIN":
        quit_requested, is_host, lobby_name = title_screen.run()
        # if they have requested to quit on the main screen, close the program immediatley as there is no need to disconnect from any lobbies
        running = not quit_requested
        if is_host is not None:
            if is_host: # create different lobby screens depending on whether they have selected to host or join a lobby
                host_lobby_screen = scr.HostLobby(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale, lobby_name)
                network = multiplayer.Host(lobby_name)
                state = "LOBBY"
            else:
                network = multiplayer.Client()
                state = "BROADCAST"
        prev_state = "MAIN"

    if state == "BROADCAST":
        quit_requested, chosen_lobby = finding_lobbies_screen.run(return_info["lobbies"])
        if chosen_lobby is not None:
            # request to join the lobby onn a separate thread so that the program does not stop
            lobby_request_thread = threading.Thread(target=network.requestLobby(return_info["lobbies"][chosen_lobby])) 
            client_lobby_screen = scr.ClientLobby(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale, chosen_lobby)
        prev_state = "BROADCAST"

    if state == "LOBBY":
        if is_host:
            if prev_state == "GAME":
                host_lobby_screen.show_final_standings = True # if they have just finished a game, show the final standings overlay
            quit_requested, current_info = host_lobby_screen.run(return_info)
        else:
            if prev_state == "GAME":
                client_lobby_screen.show_final_standings = True # if they have just finished a game, show the final standings overlay
            quit_requested, current_info = client_lobby_screen.run(return_info)
        try:
            player_name = current_info["name"]
        except KeyError:
            pass
        prev_state = "LOBBY"

    if state == "GAME":
        if prev_state != "GAME":
            game_screen = scr.Game(screen, SCREEN_WIDTH, SCREEN_HEIGHT, global_scale, player_name, return_info)
        quit_requested, current_info = game_screen.run(return_info)
        prev_state = "GAME"

    if state == "STANDINGS":
        game_screen.show_standings = True # show the standings on the game screen if they still have games left to play
        quit_requested, current_info = game_screen.run(return_info)
        prev_state = "STANDINGS"

    if is_host is not None:
        if quit_requested:
            if is_host:
                network.quit()
                state = "MAIN"
                is_host = None
            else:
                if state == "BROADCAST":
                    network.quit()
                    state = "MAIN"
                    is_host = None
                else:
                    temp = state
                    network.state = "QUIT"
                    state, return_info = network.getInfo(current_info)
                    if state != "MAIN":
                        state = temp # if the user has not yet been removed from the lobby, ensure that they remain in the screen that they were in
                    else:
                        network.quit()
                        is_host = None
        else:
            state, return_info = network.getInfo(current_info)

        if state == "DISCONNECT":
                        title_screen.was_disconnected = True
                        state = "MAIN"
                        is_host = None

    pygame.display.update()

    clock.tick(60)

pygame.quit()