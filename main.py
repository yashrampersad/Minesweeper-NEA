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

# label = gui.Label(colours["WHITE"], "1x scale", colours["GREY"], 1)
# button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"],"test button", colours["GREY"], 1)
# state_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["state 1", "state 2"], colours["GREY"], 1)
# current_state = "state 1"
# input_box = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "test input box", colours["GREY"], 1)
# progress_bar = gui.ProgressBar(300, colours["LIGHT SILVER"], colours["LIGHT COAL"], 1)
# ui_square = gui.UISquare((0,0), colours["DARK COAL"], colours["LIGHT COAL"], colours["DARK SILVER"], colours["LIGHT SILVER"])



pygame.display.set_caption("Minespeeder")
clock = pygame.time.Clock()

title_screen = scr.MainMenu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
available_lobbies = ["Yash's Lobby", "Guest's Lobby"]
finding_lobbies_screen = scr.FindingLobbies(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
lobby_screen = scr.Lobby(screen, SCREEN_WIDTH, SCREEN_HEIGHT, "Test Lobby")

state = "MAIN"

# game loop
running = True
while running:

    screen.fill(colours["GREY"])

    # label.draw(screen, 100, 100)
    # button.draw(screen, 500, 100)
    # state_button.draw(screen, 100, 250)
    # input_box.draw(screen, 500, 250)
    # progress_bar.draw(screen, 100, 400, 0.67)
    # ui_square.draw(screen, 500, 400, 200, "2", colours["WHITE"], False, True)

    if state == "MAIN":
        state = title_screen.run()
    elif state == "LOBBY":
        state = lobby_screen.run()
    elif state == "BROADCAST":
        state = finding_lobbies_screen.run(available_lobbies)
    elif state == "QUIT":
        running = False


    # event handler for actions like mouse clicks
    for event in pygame.event.get():

        # if button.isClicked(event):
        #     print("Button clicked")

        # new_state = state_button.updateState(event)
        # if new_state != current_state:
        #     print(f"state changed to {new_state}")
        #     current_state = new_state

        # new_input = input_box.update(event)
        # if new_input != None:
        #     print(f"{new_input} entered in input box")
        #     input_box.reset(new_input)

        # square_input = ui_square.registerClick(event)
        # if square_input != None:
        #     print(f"ui square clicked, click type {square_input[0]}, position {square_input[1]}")


        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

    clock.tick(60)

pygame.quit()