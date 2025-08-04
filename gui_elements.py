import pygame

pygame.init()

# setting various arbitrary values used later as constants so that they can be easily tweaked if needed
FONT_SIZE = 40
LABEL_HEIGHT = 50
PROGRESS_BAR_HEIGHT = 50
CORNER_ROUNDING = 15
TEXT_PADDING = 20

main_font = pygame.font.SysFont("couriernew", FONT_SIZE, bold=True) # set font and text size
number_font = pygame.font.SysFont("arial", FONT_SIZE, bold=True)

class Label(): # for displaying text
    def __init__(self, colour, text, text_colour):
        self.colour = colour
        self.text = text
        self.text_colour = text_colour

    def draw(self, surface, x, y):
        text = main_font.render(self.text, True, self.text_colour) # render the text in the correct font and style
        pygame.draw.rect(surface, self.colour, (x, y, text.get_width()+TEXT_PADDING, LABEL_HEIGHT), border_radius=CORNER_ROUNDING) # draw the box the same width as the text with some padding
        surface.blit(self.text, (x,y))

class Button(Label): # for clickable buttons that display text
    def __init__(self, colour, hover_colour, text, text_colour):
        super().__init__(colour, text, text_colour)
        self.hover_colour = hover_colour
        self.hitbox = None
        self.highlighted = False

    # using polymorphism to change the draw method to define a hitbox we can check for collisions with
    def draw(self, surface, x, y):
        text = main_font.render(self.text, True, self.text_colour)
        self.hitbox = pygame.Rect(x, y, text.get_width()+TEXT_PADDING, LABEL_HEIGHT)
        # change colour if the cursor is hovering over
        if self.highlighted:
            pygame.draw.rect(surface, self.hover_colour, self.hitbox, border_radius=CORNER_ROUNDING)
        else:
            pygame.draw.rect(surface, self.hover_colour, self.hitbox, border_radius=CORNER_ROUNDING)
        surface.blit(text, (x,y))
    
    def isClicked(self, event):
        mouse_pos = pygame.mouse.get_pos()
        # first check if mouse is hovering over, regardless of clicks
        if self.hitbox.collidepoint(mouse_pos):
            self.highlighted = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return True # return whether or not there is was a click that frame
            else:
                return False
        else:
            self.highlighted = False

class StateButton(Button): # for buttons that cycle through different values eg, beginner, intermediate, expert, custom
    def __init__(self, colour, hover_colour, states, text_colour):
        self.current_state = 0
        super().__init__(self, colour, hover_colour, states[self.current_state], text_colour)
        self.states = states
        # the states are in a given array, and self.current_state points to the current state

    def updateState(self):
        if super().isClicked(): # the StateButton runs the method it inherited from Button to check for clicks
            self.current_state = (self.current_state + 1) % len(self.states)
            self.text = self.states[self.current_state]
        return self.states[self.current_state]

class UISquare(): # a single square on the minesweeper board to detect clicks for the mineswepper section
    # does not inherit from any other classes as functionality is quite different
    def __init__(self, position, colour, hover_colour, covered_colour, covered_hover_colour):
        self.position = position
        self.colour = colour
        self.hover_colour = hover_colour
        self.covered_colour = covered_colour
        self.covered_hover_colour = covered_hover_colour
        self.hitbox = None
        self.highlighted = False

    # number and number colour are given here intead of instantiation as they can change during runtime
    def draw(self, surface, x, y, width, number, number_colour, is_revealed, is_flagged):
        self.hitbox = pygame.Rect(x, y, width, width)
        # draw differently depending on whether the square is revealed
        if is_revealed:
            if self.highlighted:
                pygame.draw.rect(surface, self.hover_colour, self.hitbox, border_radius=CORNER_ROUNDING)
            else:
                pygame.draw.rect(surface, self.colour, self.hitbox, border_radius=CORNER_ROUNDING)
            text = number_font.render(number, True, number_colour)
            surface.blit(text, (x,y))
        else:
            if self.highlighted:
                pygame.draw.rect(surface, self.covered_hover_colour, self.hitbox, border_radius=CORNER_ROUNDING)
            else:
                pygame.draw.rect(surface, self.covered_colour, self.hitbox, border_radius=CORNER_ROUNDING)
            if is_flagged:
                surface.blit(pygame.image.load("flag.png").convert_alpha(), (x,y))

    def registerClick(self, event):
        mouse_pos = pygame.mouse.get_pos()
        # first check if mouse is hovering over, regardless of clicks
        if self.hitbox.collidepoint(mouse_pos):
            self.highlighted = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # in pygame, left click is 1, right click is 3
                if event.button == 1:
                    return 0, self.position
                elif event.button == 3:
                    return 1, self.position
        else:
            self.highlighted = False

class InputBox(Button): # for the user to input text
    def __init__(self, colour, hover_colour, default_text, text_colour):
        self.default_text = default_text
        self.current_text = ""
        self.activated = False
        super().__init__(self, colour, hover_colour, default_text, text_colour)

    def update(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        # activated represents the state where the user can edit the text in the InputBox
        if not self.activated:
            self.highlighted = False
            # once the user clicks on the box it becomes activated and they can enter text
            if self.hitbox.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.activated = True
        elif self.activated:
            self.highlighted = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.current_text = self.current_text[:-1]
                # if they click enter, return the text
                elif event.key == pygame.K_RETURN:
                    self.activated = False
                    return self.current_text
                else:
                    if event.key not in [pygame.K_RETURN, pygame.K_BACKSPACE, pygame.K_LCTRL, pygame.K_RCTRL]:
                        self.current_text += event.unicode
            # if they click outside of the box, deactivate typing but do not return what has been typed
            elif not self.hitbox.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.activated = False
            # display the default text if nothing has been entered
            if self.current_text == "":
                self.text = self.default_text
            else:
                self.text = self.current_text
    
    def reset(self, new_default): # allows the InputBox to be reset or reset with a new default message if needed
        self.default_text = new_default
        self.current_text = ""

class ProgressBar(): # to display a progress bar that can change during runtime
    def __init__(self, max_width, colour, outline_colour):
        self.max_width = max_width
        self.colour = colour
        self.outline_colour = outline_colour

    def draw(self, surface, x, y, percentage):
        pygame.draw.rect(surface, self.outline_colour, (x, y, self.max_width, PROGRESS_BAR_HEIGHT)) # draw outline
        pygame.draw.rect(surface, self.colour, (x, y, self.max_width*percentage, PROGRESS_BAR_HEIGHT)) # draw progress using the given float value for the percentage