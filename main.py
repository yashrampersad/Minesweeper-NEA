import pygame

pygame.init()

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

colours = {"WHITE":"#d9d9d9",
           "LIGHT SILVER":"#717d9f",
           "DARK SILVER":"#667192",
           "GREY":"#4e5770",
           "LIGHT COAL":"#353a49",
           "DARK COAL":"#2c2f3b",}

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minespeeder")

# game loop
while True:

    screen.fill(colours["GREY"])
    
    # event handler for actions like mouse clicks
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    
    pygame.display.update()