import pygame

font = pygame.font.SysFont("couriernew", 40, bold=True) # set font and text size

class Label():
    def __init__(self, colour, text, text_colour):
        self.colour = colour
        self.text = text
        self.text_colour = text_colour

    def draw(self, surface, x, y):
        pass