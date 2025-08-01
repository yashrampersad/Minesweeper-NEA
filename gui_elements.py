import pygame

pygame.init()

# setting various arbitrary values used later as constants so that they can be easily tweaked later if needed
FONT_SIZE = 40
LABEL_HEIGHT = 50
CORNER_ROUNDING = 15
TEXT_PADDING = 20

main_font = pygame.font.SysFont("couriernew", FONT_SIZE, bold=True) # set font and text size
number_font = pygame.font.SysFont("arial", FONT_SIZE, bold=True)

class Label():
    def __init__(self, colour, text, text_colour):
        self.colour = colour
        self.text = text
        self.text_colour = text_colour

    def draw(self, surface, x, y):
        text = main_font.render(self.text, True, self.text_colour)
        pygame.draw.rect(surface, self.colour, (x, y, text.get_width()+TEXT_PADDING, LABEL_HEIGHT), border_radius=CORNER_ROUNDING) # draw the box the same width as the text with some padding
        surface.blit(self.text, (x,y))

class Button(Label):
    def __init__(self, colour, hover_colour, text, text_colour):
        super().__init__(colour, text, text_colour)
        self.hover_colour = hover_colour
        self.hitbox = None
        self.hovered = False

    # using polymorphism to change the draw method to define a hitbox we can check for collisions with
    def draw(self, surface, x, y):
        text = main_font.render(self.text, True, self.text_colour)
        self.hitbox = pygame.Rect(x, y, text.get_width()+TEXT_PADDING, LABEL_HEIGHT)
        # change colour if the cursor is hovering over
        if self.hovered:
            pygame.draw.rect(surface, self.hover_colour, self.hitbox, border_radius=CORNER_ROUNDING)
        else:
            pygame.draw.rect(surface, self.hover_colour, self.hitbox, border_radius=CORNER_ROUNDING)
        surface.blit(text, (x,y))
    
    def isClicked(self, event):
        mouse_pos = pygame.mouse.get_pos()
        # first check if mouse is hovering over, regardless of clicks
        if self.hitbox.collidepoint(mouse_pos):
            self.hovered = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return True
            else:
                return False
        else:
            self.hovered = False

class StateButton(Button):
    def __init__(self, colour, hover_colour, states, text_colour):
        self.current_state = 0
        super().__init__(self, colour, hover_colour, states[self.current_state], text_colour)
        self.states = states

    def updateState(self):
        # the StateButton runs the method it inherited from Button to check for clicks
        if super().isClicked():
            self.current_state = (self.current_state + 1) % len(self.states)
            self.text = self.states[self.current_state]
        return self.states[self.current_state]

class UISquare():
    # does not inherit from any other classes as functionality is quite different
    def __init__(self, position, colour, hover_colour, covered_colour, covered_hover_colour):
        self.position = position
        self.colour = colour
        self.hover_colour = hover_colour
        self.covered_colour = covered_colour
        self.covered_hover_colour = covered_hover_colour
        self.hitbox = None
        self.hovered = False

    # number and number colour are given here intead of instantiation as they can change during runtime
    def draw(self, surface, x, y, width, number, number_colour, is_revealed, is_flagged):
        self.hitbox = pygame.Rect(x, y, width, width)
        # draw differently depending on whether the square is revealed
        if is_revealed:
            if self.hovered:
                pygame.draw.rect(surface, self.hover_colour, self.hitbox, border_radius=CORNER_ROUNDING)
            else:
                pygame.draw.rect(surface, self.colour, self.hitbox, border_radius=CORNER_ROUNDING)
            text = number_font.render(number, True, number_colour)
            surface.blit(text, (x,y))
        else:
            if self.hovered:
                pygame.draw.rect(surface, self.covered_hover_colour, self.hitbox, border_radius=CORNER_ROUNDING)
            else:
                pygame.draw.rect(surface, self.covered_colour, self.hitbox, border_radius=CORNER_ROUNDING)
            if is_flagged:
                # I will create a flag image later so a red F is used as a placeholder for the prototype
                text = number_font.render("F", True, "#ff3131")
                surface.blit(text, (x,y))

    def registerClick(self, event):
        mouse_pos = pygame.mouse.get_pos()
        # first check if mouse is hovering over, regardless of clicks
        if self.hitbox.collidepoint(mouse_pos):
            self.hovered = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # in pygame, left click is 1, right click is 3
                if event.button == 1:
                    return 0, self.position
                elif event.button == 3:
                    return 1, self.position
        else:
            self.hovered = False

