import pygame
import sys
import os


pygame.init()

# setting various arbitrary values used later as constants so that they can be easily tweaked if needed
FONT_SIZE = 40
LABEL_HEIGHT = 50
PROGRESS_BAR_HEIGHT = 100
CORNER_ROUNDING = 40
TEXT_PADDING = 25

number_colours = {
    "1":"#38b6ff",
    "2":"#7ed957",
    "3":"#f65656",
    "4":"#5271ff",
    "5":"#db3934",
    "6":"#52dfbd",
    "7":"#6956ff",
    "8":"#768ccb"
}

class Label(): # for displaying text
    def __init__(self, colour, text, text_colour, scale):
        self.colour = colour
        self.text = text
        self.text_colour = text_colour
        self.scale = scale

        self.font = pygame.font.SysFont("couriernew", round(FONT_SIZE*self.scale), bold=True) # set font and text size
        self.rendered_text = self.font.render(self.text, True, self.text_colour) # render the text in the correct font and style
        self.box = pygame.Rect(0,0, round(self.rendered_text.get_width()+TEXT_PADDING*2*self.scale), round(self.rendered_text.get_height()+TEXT_PADDING*2*self.scale)) # create a quick render of the box so that any programs can use the width and height in calculations

    def draw(self, surface, x, y):
        self.rendered_text = self.font.render(self.text, True, self.text_colour) # render the text in the correct font and style
        self.box = pygame.Rect(x, y, round(self.rendered_text.get_width()+TEXT_PADDING*2*self.scale), round(self.rendered_text.get_height()+TEXT_PADDING*2*self.scale))
        if self.colour is not None:
            pygame.draw.rect(surface, self.colour, self.box, border_radius=round(CORNER_ROUNDING*self.scale)) # draw the box the same width as the text with some padding
        surface.blit(self.rendered_text, (round(x+TEXT_PADDING*self.scale),round(y+TEXT_PADDING*self.scale)))

class Button(Label): # for clickable buttons that display text
    def __init__(self, colour, hover_colour, text, text_colour, scale):
        super().__init__(colour, text, text_colour, scale)
        self.hover_colour = hover_colour
        self.highlighted = False

    # using polymorphism to change the draw method to draw differently depending on whether the mouse is hovering over
    def draw(self, surface, x, y):
        self.rendered_text = self.font.render(self.text, True, self.text_colour)
        self.box = pygame.Rect(x, y, round(self.rendered_text.get_width()+TEXT_PADDING*2*self.scale), round(self.rendered_text.get_height()+TEXT_PADDING*2*self.scale))
        # change colour if the cursor is hovering over
        if self.highlighted:
            pygame.draw.rect(surface, self.hover_colour, self.box, border_radius=round(CORNER_ROUNDING*self.scale))
        else:
            pygame.draw.rect(surface, self.colour, self.box, border_radius=round(CORNER_ROUNDING*self.scale))
        surface.blit(self.rendered_text, (round(x+TEXT_PADDING*self.scale),round(y+TEXT_PADDING*self.scale)))
    
    def isClicked(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if self.box.collidepoint(mouse_pos):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.highlighted = False
                return True # return whether or not there is was a click that frame
            else:
                self.highlighted = True # if the mouse hovers over without clicking, highlight the box
                return False
        else:
            self.highlighted = False
            return False

class StateButton(Button): # for buttons that cycle through different values eg, beginner, intermediate, expert, custom
    def __init__(self, colour, hover_colour, states, text_colour, scale):
        self.current_state = 0
        super().__init__(colour, hover_colour, states[self.current_state], text_colour, scale)
        self.states = states
        # the states are in a given array, and self.current_state points to the current state

    def updateState(self, event):
        if super().isClicked(event): # the StateButton runs the method it inherited from Button to check for clicks
            self.current_state = (self.current_state + 1) % len(self.states)
            self.text = self.states[self.current_state]
        return self.states[self.current_state]

class InputBox(Button): # for the user to input text
    def __init__(self, colour, hover_colour, default_text, text_colour, scale):
        self.default_text = default_text
        self.current_text = ""
        self.activated = False
        super().__init__(colour, hover_colour, default_text, text_colour, scale)

    def draw(self, surface, x, y):
        text = self.font.render(self.text, True, self.text_colour)
        default_text = self.font.render(self.default_text, True, self.text_colour)
        if text.get_width() < default_text.get_width():
            width = default_text.get_width()
        else:
            width = text.get_width()
        self.box = pygame.Rect(x, y, round(width+TEXT_PADDING*2*self.scale), round(text.get_height()+TEXT_PADDING*2*self.scale))
        # change colour if the cursor is hovering over
        if self.highlighted:
            pygame.draw.rect(surface, self.hover_colour, self.box, border_radius=round(CORNER_ROUNDING*self.scale))
        else:
            pygame.draw.rect(surface, self.colour, self.box, border_radius=round(CORNER_ROUNDING*self.scale))
        surface.blit(text, (round(x+TEXT_PADDING*self.scale),round(y+TEXT_PADDING*self.scale)))

    def update(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        # activated represents the state where the user can edit the text in the InputBox
        if not self.activated:
            self.highlighted = False
            # once the user clicks on the box it becomes activated and they can enter text
            if self.box.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.activated = True

        elif self.activated:
            self.highlighted = True
            keys = pygame.key.get_pressed()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.current_text = self.current_text[:-1]
                # if they click enter, return the text
                elif event.key == pygame.K_RETURN:
                    self.activated = False
                    self.highlighted = False
                    return self.current_text
                else:
                    if event.key not in [pygame.K_RETURN, pygame.K_BACKSPACE, pygame.K_LCTRL, pygame.K_RCTRL]:
                        self.current_text += event.unicode
            # if they click outside of the box, deactivate typing but do not return what has been typed
            elif not self.box.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.current_text = ""
                self.activated = False
                self.highlighted = False
            # display the default text if nothing has been entered
            if self.current_text == "" and not self.activated:
                self.text = self.default_text
            else:
                self.text = self.current_text+"_"
    
    def reset(self, new_default): # allows the InputBox to be reset or reset with a new default message if needed
        self.default_text = new_default
        self.text = self.default_text
        self.current_text = ""


class ProgressBar(): # to display a progress bar that can change during runtime
    def __init__(self, max_width, colour, outline_colour, scale):
        self.max_width = max_width
        self.colour = colour
        self.outline_colour = outline_colour
        self.scale = scale

    def draw(self, surface, x, y, percentage):
        if percentage > 1:
            percentage = 1
        pygame.draw.rect(surface, self.outline_colour, (x, y, round(self.max_width*self.scale), round(PROGRESS_BAR_HEIGHT*self.scale))) # draw outline
        pygame.draw.rect(surface, self.colour, (x, y, round(self.max_width*percentage*self.scale), round(PROGRESS_BAR_HEIGHT*self.scale))) # draw progress using the given float value for the percentage


class UISquare(): # a single square on the minesweeper board to detect clicks for the minesweeper section
    # does not inherit from any other classes as functionality is quite different
    def __init__(self, position, colour, covered_colour):
        self.position = position
        self.colour = colour
        self.covered_colour = covered_colour
        self.box = None
        self.highlighted = False
        self.font = None
        self.flag = None

    # number and number colour are given here intead of instantiation as they can change during runtime
    def draw(self, surface, x, y, width, number, is_revealed, is_flagged):
        self.box = pygame.Rect(x, y, width, width)
        # draw differently depending on whether the square is revealed
        if is_revealed:
            pygame.draw.rect(surface, self.colour, self.box)
            if self.highlighted:
                highlight = pygame.Surface((width, width), pygame.SRCALPHA)
                pygame.draw.rect(highlight, (255, 255, 255, 50), highlight.get_rect())  
                surface.blit(highlight, (x, y))
            if number != "0":
                text = square_font.render(number, True, number_colours[number])
                surface.blit(text, (x+abs((width-text.get_width())//2),y+abs((width-text.get_height())//2)))
        else:
            pygame.draw.rect(surface, self.covered_colour, self.box)
            if self.highlighted:
                highlight = pygame.Surface((width, width), pygame.SRCALPHA)
                pygame.draw.rect(highlight, (255, 255, 255, 50), highlight.get_rect())  
                surface.blit(highlight, (x, y))
            if is_flagged:
                surface.blit(flag, (x,y))

    def registerClick(self, event):
        mouse_pos = pygame.mouse.get_pos()
        # first check if mouse is hovering over, regardless of clicks
        if self.box.collidepoint(mouse_pos):
            self.highlighted = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # in pygame, left click is 1, right click is 3
                if event.button == 1:
                    return 0, self.position
                elif event.button == 3:
                    return 1, self.position
        else:
            self.highlighted = False

def loadResources(square_width):
    global square_font
    square_font = pygame.font.SysFont("arial", round((square_width/5)*4), bold=True)
    global flag
    flag = pygame.transform.smoothscale(pygame.image.load("current/flag.png").convert_alpha(), (square_width, square_width))