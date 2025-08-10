import pygame
import gui_elements as gui # import the GUI core element classes from the separate file 

pygame.init()

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

pygame.key.set_repeat(500, 40) # allow the ability to hold keys like backspace to input them multiple times. 500 and 40 are used as these are the standard millisecond timings for key repeats across many operating systems

# making the colour palette easily accessible through a dictionary and using memorable names
colours = {"WHITE":"#d9d9d9",
           "LIGHT SILVER":"#717d9f",
           "DARK SILVER":"#667192",
           "GREY":"#4e5770",
           "LIGHT COAL":"#353a49",
           "DARK COAL":"#2c2f3b",}

label = gui.Label(colours["WHITE"], "test label", colours["GREY"])
button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"],"test button", colours["GREY"])
state_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["state 1", "state 2"], colours["GREY"])
current_state = "state 1"
input_box = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "test input box", colours["GREY"])
progress_bar = gui.ProgressBar(300, colours["LIGHT SILVER"], colours["LIGHT COAL"])
ui_square = gui.UISquare((0,0), colours["DARK COAL"], colours["LIGHT COAL"], colours["DARK SILVER"], colours["LIGHT SILVER"])


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minespeeder")

# game loop
running = True
while running:

    screen.fill(colours["GREY"])

    label.draw(screen, 100, 100)
    button.draw(screen, 500, 100)
    state_button.draw(screen, 100, 250)
    input_box.draw(screen, 500, 250)
    progress_bar.draw(screen, 100, 400, 0.67)
    ui_square.draw(screen, 500, 400, 50, "1", colours["WHITE"], True, True)

       
    # event handler for actions like mouse clicks
    for event in pygame.event.get():

        if button.isClicked(event):
            print("Button clicked")

        new_state = state_button.updateState(event)
        if new_state != current_state:
            print(f"state changed to {new_state}")
            current_state = new_state

        new_input = input_box.update(event)
        if new_input != None:
            print(f"{new_input} entered in input box")
            input_box.reset(new_input)

        square_input = ui_square.registerClick(event)
        if square_input != None:
            print(f"ui square clicked, click type {square_input[0]}, position {square_input[1]}")


        if event.type == pygame.QUIT:
            running = False
    
    pygame.display.update()

pygame.quit()