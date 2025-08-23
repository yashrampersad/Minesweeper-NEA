import pygame
import gui_elements as gui
import game
import time


# making the colour palette easily accessible through a dictionary and using memorable names
colours = {"WHITE":"#d9d9d9",
           "LIGHT SILVER":"#717d9f",
           "DARK SILVER":"#667192",
           "GREY":"#4e5770",
           "LIGHT COAL":"#353a49",
           "DARK COAL":"#2c2f3b",}

# board_dimensions = (height, width)

# def reinitialiseWindow(global_scale, screen_width, screen_height):
#     return pygame.display.set_mode((screen_width*global_scale, screen_height*global_scale))


class Base(): # base class with attributes and methods every screen needs so that it can be inherited from to save time
    def __init__(self, surface, screen_width, screen_height, global_scale):
        self.global_scale = global_scale
        self.surface = surface
        self.screen_width, self.screen_height = screen_width*self.global_scale, screen_height*self.global_scale
        self.scale = "Small"

    def run(self):
        self.drawElements()
        return self.handleEvents()
    
class InitialScale(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale):
        super().__init__(surface, screen_width, screen_height, global_scale)
        gui.setScale(self.global_scale)
        self.scale_label = gui.Label(colours["GREY"], "Set screen size:", colours["WHITE"], 1)
        self.scale_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Small", "Medium", "Large"], colours["GREY"], 1)
        self.done_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Done", colours["GREY"], 0.8)
    
    def drawElements(self):
        self.scale_label.draw(self.surface, 50, 50)
        self.scale_button.draw(self.surface, 50, 120)
        self.done_button.draw(self.surface, 50, 220)

    def handleEvents(self):
        state = "SCALE"
        for event in pygame.event.get():
            self.scale = self.scale_button.updateState(event)
            if self.scale == "Small":
                self.global_scale = 0.65
            elif self.scale == "Medium":
                self.global_scale = 0.8
            elif self.scale == "Large":
                self.global_scale = 1
            if self.scale_button.isClicked(event):
                gui.setScale(self.global_scale)
            if self.done_button.isClicked(event):
                state = "MAIN"
            elif event.type == pygame.QUIT:
                return "QUIT"
        return state, self.global_scale

class MainMenu(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale):
        super().__init__(surface, screen_width, screen_height, global_scale)
        # initialising the gui elements that will be used
        self.title = gui.Label(colours["GREY"], "Minespeeder", colours["WHITE"], 4)
        self.subtitle = gui.Label(colours["GREY"], "a real-time minesweeper racer - beta v2", colours["WHITE"], 0.7)
        self.create_lobby = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Play", colours["GREY"], 1)
        self.quit = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit", colours["GREY"], 0.8)

    def drawElements(self):
        # drawing gui elements
        self.title.draw(self.surface, (self.screen_width//2)-self.title.box.width//2, self.screen_height//3-self.title.box.height//2)
        self.subtitle.draw(self.surface, (self.screen_width//2), self.screen_height//3-self.title.box.height//2+self.title.box.height*2//3)
        self.create_lobby.draw(self.surface, (self.screen_width//2)-self.create_lobby.box.width//2, self.screen_height//2)
        self.quit.draw(self.surface, (self.screen_width//2)-self.quit.box.width//2, self.screen_height*21//32)

    def handleEvents(self):
        # depending on the button that is clicked, switch states to go to a different screen
        for event in pygame.event.get():
            if self.create_lobby.isClicked(event):
                return "LOBBY"
            if self.quit.isClicked(event):
                return "QUIT"
            if event.type == pygame.QUIT:
                return "QUIT"
        # if nothing is pressed, remain in the current state/screen
        return "MAIN"
    
class Lobby(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale, lobby_name):
        super().__init__(surface, screen_width, screen_height, global_scale)
        # self.board_magnification = "Medium"
        self.board_difficulty = "Beginner"
        self.board_dimensions = [9,9]
        self.board_squares = []
        self.square_width = 0
        self.current_dimensions = None
        self.mine_count = 10

        self.title = gui.Label(None, "Minespeeder", colours["WHITE"], 1.5)
        self.quit_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Quit", colours["GREY"], 0.6)

        self.time_label = gui.Label(None, "Time:", colours["WHITE"], 1)
        self.time = gui.Label(None, "0.0s", colours["WHITE"], 1)
        self.flag_label = gui.Label(None, "Flags:", colours["WHITE"], 1)
        self.flag_count = gui.Label(None, "10", colours["WHITE"], 1)

        self.board_size_label = gui.Label(None, "Board size", colours["WHITE"], 0.6)
        self.board_height = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "30", colours["GREY"], 0.6)
        self.x_label = gui.Label(None, "X", colours["WHITE"], 0.6)
        self.board_width = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "16", colours["GREY"], 0.6)

        self.num_mines_label = gui.Label(None, "Mines:", colours["WHITE"], 0.6)
        self.num_mines = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "10", colours["GREY"], 0.6)
        self.num_games_label = gui.Label(None, "Best of:", colours["WHITE"], 0.6)
        self.num_games = gui.InputBox(colours["WHITE"], colours["LIGHT SILVER"], "1", colours["GREY"], 0.6)

        self.board_difficulty_button = gui.StateButton(colours["WHITE"], colours["LIGHT SILVER"], ["Beginner", "Intermediate", "Expert", "Custom"], colours["GREY"], 0.6)
        self.board_dimension_prompt = gui.Label(None, "click to change size and mines", colours["WHITE"], 0.4)

        self.ready_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Play!", colours["GREY"], 0.8)

    def run(self):
        if self.board_dimensions != self.current_dimensions:
            self.setBoard()
            self.current_dimensions = self.board_dimensions.copy()
        self.drawElements()
        return self.handleEvents()

    def drawElements(self):
        self.time_label.draw(self.surface, (self.screen_width//2)-50-self.time_label.box.width, self.screen_height//18)
        self.time.draw(self.surface, (self.screen_width//2)-50-self.time_label.box.width//2-self.time.box.width//2, self.screen_height//9)
        self.flag_label.draw(self.surface, (self.screen_width//2)+50, self.screen_height//18)
        self.flag_count.draw(self.surface, (self.screen_width//2)+50+self.flag_label.box.width//2-self.flag_count.box.width//2, self.screen_height//9)

        self.title.draw(self.surface, -10, -5)
        self.quit_button.draw(self.surface, self.title.box.width-10, self.title.box.height//2-5-self.quit_button.box.height//2)
        
        self.drawBoard()

        self.board_size_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, self.screen_height//6)
        self.board_height.draw(self.surface, self.screen_width-self.board_height.box.width-20, self.screen_height//4)
        self.x_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-30, self.screen_height//4)
        self.board_width.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-40, self.screen_height//4)
        self.board_difficulty_button.draw(self.surface, -self.screen_width//18, -self.screen_height//9)
        self.board_difficulty_button.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, self.screen_height//4)


        self.num_mines_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, self.screen_height*3//8)
        self.num_mines.draw(self.surface, self.screen_width-self.num_mines.box.width-20, self.screen_height*3//8)
        # self.num_games_label.draw(self.surface, self.screen_width-self.board_height.box.width-self.x_label.box.width-self.board_width.box.width-self.board_difficulty_button.box.width-60, self.screen_height//2)
        # self.num_games.draw(self.surface, self.screen_width-self.num_games.box.width-20, self.screen_height//2)

        # if the board difficulty is set to Custom, prompt the user to enter their own width and height
        if self.board_difficulty == "Custom":
            self.board_dimension_prompt.draw(self.surface, self.screen_width-self.board_dimension_prompt.box.width, self.screen_height//3)

        self.ready_button.draw(self.surface, self.screen_width//2-self.ready_button.box.width//2, self.screen_height-self.ready_button.box.height-10)

    def setBoard(self):
        # self.board_squares is a list of all the UISquares so that the class can keep track of all of them
        self.board_squares.clear()
        for i in range(self.board_dimensions[0]):
            for j in range(self.board_dimensions[1]):
                # draw squares in alternating colours to create a checkerboard pattern
                if (i+j)%2 == 0:
                    square = gui.UISquare((i,j), colours["LIGHT COAL"], colours["LIGHT SILVER"])
                else:
                    square = gui.UISquare((i,j), colours["DARK COAL"], colours["DARK SILVER"])
                self.board_squares.append(square)

    def drawBoard(self):
        # get the maximum scale based on the available space
        max_square_width_x = (self.screen_width-self.screen_width*3//7)//self.board_dimensions[1]
        max_square_width_y = (self.screen_height-self.screen_height//3)//self.board_dimensions[0]
        # choose the smaller value to result in the board being as large as possible while still fitting
        if max_square_width_x > max_square_width_y:
            self.square_width = max_square_width_y
        else:
            self.square_width = max_square_width_x
        current_square = 0
        y = self.screen_height//5
        for i in range(self.board_dimensions[0]):
            x = (self.screen_width//2) - self.square_width*self.board_dimensions[1]//2
            for j in range(self.board_dimensions[1]):
                self.board_squares[current_square].draw(self.surface, x, y, self.square_width, "1", False, False)
                current_square += 1
                x += self.square_width
            y += self.square_width


    def handleEvents(self):
        for event in pygame.event.get():
            self.board_difficulty = self.board_difficulty_button.updateState(event)
            if self.board_difficulty == "Custom":
                # if the difficulty is set to Custom, allow the input boxes to have text entered into them
                new_width = self.board_width.update(event)
                new_height = self.board_height.update(event)
                new_mine_num = self.num_mines.update(event)
                if new_width is not None:
                    # ensure that the width and height entered is a number and is 50 or below as to not overload the program
                    if new_width.isnumeric() and 3 < int(new_width) <= 30:
                        self.board_dimensions[1] = int(new_width)
                        self.board_width.reset(new_width)
                        self.board_dimension_prompt.text = "click to change size and mines"
                        if ((self.board_dimensions[0]*self.board_dimensions[1])**2)//10000 <= self.mine_count <= (self.board_dimensions[0]*self.board_dimensions[1])-9: # reset mines to default if too big for new dimensions
                            midpoint = round(((self.board_dimensions[0]*self.board_dimensions[1])-9 + ((self.board_dimensions[0]*self.board_dimensions[1])**2)//10000)//6, -1) # set the default to a suitable midpoint between the given range
                            self.mine_count = midpoint
                            self.num_mines.reset(f"{midpoint}")
                    else:
                        self.board_width.reset(self.board_width.default_text)
                        self.board_dimension_prompt.text = "invalid board dimension"
                if new_height is not None:
                    if new_height.isnumeric() and 3 < int(new_height) <= 30:
                        self.board_dimensions[0] = int(new_height)
                        self.board_height.reset(new_height)
                        self.board_dimension_prompt.text = "click to change size and mines"
                        if not ((self.board_dimensions[0]*self.board_dimensions[1])**2)//10000 <= self.mine_count <= (self.board_dimensions[0]*self.board_dimensions[1])-9: # reset mines to default if too big for new dimensions
                            midpoint = midpoint = round(((self.board_dimensions[0]*self.board_dimensions[1])-9 + ((self.board_dimensions[0]*self.board_dimensions[1])**2)//10000)//6, -1) # set the default to a suitable midpoint between the given range
                            self.mine_count = midpoint
                            self.num_mines.reset(f"{midpoint}")
                    else:
                        self.board_height.reset(self.board_height.default_text)
                        self.board_dimension_prompt.text = "invalid board dimension"
                if new_mine_num is not None:
                    # ensure that thay have a number of mines that will allow them to guarantee that the first click is safe (have at least a 3x3 area free)
                    if new_mine_num.isnumeric() and ((self.board_dimensions[0]*self.board_dimensions[1])**2)//10000 <= int(new_mine_num) <= (self.board_dimensions[0]*self.board_dimensions[1])-9:
                        self.mine_count = int(new_mine_num)
                        self.num_mines.reset(new_mine_num)
                        self.board_dimension_prompt.text = "click to change size and mines"
                    else:
                        self.num_mines.reset(self.num_mines.default_text)
                        self.board_dimension_prompt.text = "invalid number of mines"
            else:
                if self.board_difficulty == "Beginner":
                    self.board_dimensions = [9,9]
                    self.mine_count = 10
                elif self.board_difficulty == "Intermediate":
                    self.board_dimensions = [16, 16]
                    self.mine_count = 40
                elif self.board_difficulty == "Expert":
                    self.board_dimensions = [16, 30]
                    self.mine_count = 99
                # reset the text in the width and height boxes to reflect the new width and height
                self.board_height.reset(str(self.board_dimensions[0]))
                self.board_width.reset(str(self.board_dimensions[1]))
                self.num_mines.reset(str(self.mine_count))
            self.flag_count.text = str(self.mine_count)

            # games = self.num_games.update(event)
            # if games is not None:
            #     if games.isnumeric() and int(games) <= 10:
            #         self.num_games.reset(games)
            #     else:
            #         self.num_games.reset(self.num_games.default_text)

            if self.ready_button.isClicked(event):
                global board_dimensions
                board_dimensions = self.board_dimensions
                global mine_count
                mine_count = self.mine_count
                return "GAME"

            if self.quit_button.isClicked(event):
                return "MAIN"

            if event.type == pygame.QUIT:
                return "QUIT"
        return "LOBBY"

class Game(Base):
    def __init__(self, surface, screen_width, screen_height, global_scale):
        super().__init__(surface, screen_width, screen_height, global_scale)
        self.board_dimensions = board_dimensions # get the board dimensions from the Lobby screen
        self.square_width = 0
        self.board_squares = []
        self.finished = False
        self.board = self.setBoard()
        self.total_clicks = 0
        self.mine_count = mine_count
        self.remaining_flags = mine_count
        self.first_click = True
        self.first_game = True
        self.start_time = None
        self.game_result = None
        self.completion = 0

        self.time_label = gui.Label(None, "Time:", colours["WHITE"], 1)
        self.time = gui.Label(None, "0.0s", colours["WHITE"], 1)
        self.current_time = 0.000
        self.flag_label = gui.Label(None, "Flags:", colours["WHITE"], 1)
        self.flag_count = gui.Label(None, "10", colours["WHITE"], 1)
        self.reset_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Reset", colours["GREY"], 0.8)

        self.finished_title = gui.Label(None, "Game Finished!", colours["WHITE"], 1)
        self.num_clicks = gui.Label(None, "No. of clicks: 0", colours["WHITE"], 0.8)
        self.extra_stats_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Extra stats", colours["GREY"], 0.8)
        self.show_extra_stats = False
        self.benchmark = gui.Label(None, "3BV: 0", colours["WHITE"], 0.8)
        self.benchmark_value = 0
        self.benchmark_description = gui.Label(None, "(How much work the board was)", colours["WHITE"], 0.5)
        self.benchmark_sec = gui.Label(None, "3BV/s: 0", colours["WHITE"], 0.8)
        self.benchmark_sec_value = 0
        self.benchmark_sec_description = gui.Label(None, "(Your speed)", colours["WHITE"], 0.5)
        self.efficiency = gui.Label(None, "Efficiency: 0", colours["WHITE"], 0.8)
        self.efficiency_value = 0
        self.efficiency_description = gui.Label(None, "(Percentage of nessecary clicks)", colours["WHITE"], 0.5)
        self.stats_calculated = False

        self.return_button = gui.Button(colours["WHITE"], colours["LIGHT SILVER"], "Back", colours["GREY"], 0.8)
        
    def run(self):
        self.drawElements()
        return self.handleEvents()
    
    def drawElements(self):
        if not self.first_game and self.game_result != 1:
            self.current_time = time.time() - self.start_time
            self.time.text = str(self.current_time)[:str(self.current_time).index(".")+2] + "s" # print to 1 dp during game so that it is not too overwhelming
        elif self.game_result == 1:
            self.time.text = str(self.current_time)[:str(self.current_time).index(".")+4] + "s" # print to 3 dp after game so that it is to the millisecond
        self.time_label.draw(self.surface, (self.screen_width//2)-50-self.time_label.box.width, self.screen_height//18)
        self.time.draw(self.surface, (self.screen_width//2)-50-self.time_label.box.width//2-self.time.box.width//2, self.screen_height//9)
        self.flag_label.draw(self.surface, (self.screen_width//2)+50, self.screen_height//18)
        self.flag_count.text = str(self.remaining_flags)
        self.flag_count.draw(self.surface, (self.screen_width//2)+50+self.flag_label.box.width//2-self.flag_count.box.width//2, self.screen_height//9)

        self.reset_button.draw(self.surface, self.screen_width//2-self.reset_button.box.width//2, self.screen_height-self.reset_button.box.height-10)
        self.return_button.draw(self.surface, self.screen_height//45, self.screen_width//90)

        if self.game_result == 1:
            self.finished_title.text = "Game Finished!"
            self.finished_title.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, self.screen_height//9)
            
            self.extra_stats_button.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*2)//7)
        elif self.game_result == -1:
            self.finished_title.text = "Try again!"
            self.finished_title.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, self.screen_height//9)
            # reveal the whole board to show where the mines where
            for row in self.board:
                for square in row:
                    square.reveal()

        if self.show_extra_stats:
            self.num_clicks.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*3)//7)
            self.benchmark.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*4)//7)
            self.benchmark_description.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*9)//14)
            self.benchmark_sec.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*5)//7)
            self.benchmark_sec_description.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*11)//14)
            self.efficiency.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*6)//7)
            self.efficiency_description.draw(self.surface, (3*self.screen_width+self.square_width*self.board_dimensions[1])//4-self.screen_width//10, (self.screen_height*13)//14)

        bar = gui.ProgressBar(((self.screen_width)//2)-((self.square_width*self.board_dimensions[1])//2)-100, colours["DARK SILVER"], colours["LIGHT COAL"], 0.6)
        bar.draw(self.surface, self.screen_width//30, self.screen_height*2//9, self.completion)
        name = gui.Label(None, "You", colours["WHITE"], 0.6)
        name.draw(self.surface, self.screen_width//30, self.screen_height*2//9)
        self.finished = True

        self.drawBoard()

    def setBoard(self):
        self.board_squares.clear()
        for i in range(self.board_dimensions[0]):
            for j in range(self.board_dimensions[1]):
                if (i+j)%2 == 0:
                    square = gui.UISquare((i,j), colours["LIGHT COAL"], colours["LIGHT SILVER"])
                else:
                    square = gui.UISquare((i,j), colours["DARK COAL"], colours["DARK SILVER"])
                self.board_squares.append(square)
        board = game.createBoard(board_dimensions)
        return board

    def drawBoard(self):
        previous_width = self.square_width
        max_square_width_x = (self.screen_width-self.screen_width*3//7)//self.board_dimensions[1]
        max_square_width_y = (self.screen_height-self.screen_height//3)//self.board_dimensions[0]
        if max_square_width_x > max_square_width_y:
            self.square_width = max_square_width_y
        else:
            self.square_width = max_square_width_x
        if previous_width != self.square_width:
            gui.loadResources(self.square_width)
        current_square = 0
        y = self.screen_height//5
        for row in self.board:
            x = (self.screen_width//2) - self.square_width*self.board_dimensions[1]//2
            for square in row:
                self.board_squares[current_square].draw(self.surface, x, y, self.square_width, str(square.getNumber()), square.isRevealed(), square.isFlagged())
                current_square += 1
                x += self.square_width
            y += self.square_width

    def handleEvents(self):
        for event in pygame.event.get():
            
            if self.game_result is None: # if the game has not finished, continue
                for square in self.board_squares:
                    result = square.registerClick(event)
                    if result is not None:
                        if self.first_click:
                            if result[0] == 0 and not self.board[result[1][0]][result[1][1]].isFlagged(): # ensure the first click is a left click and not the user just flagging the board
                                if self.first_game: # start the timer at their first try, but if they lose or reset, continue the timer so the race is fair
                                    self.start_time = time.time()
                                    self.first_game = False
                                game.placeMines(self.board, square.position[0], square.position[1], self.mine_count)
                                game.generateNumbers(self.board)
                                self.first_click = False
                        self.game_result, self.remaining_flags, self.completion = game.performClick(self.board, result[0], result[1], self.mine_count)
                        self.total_clicks += 1
            elif self.game_result == 1:
                self.completion = 1
                if self.extra_stats_button.isClicked(event):
                    self.show_extra_stats = not self.show_extra_stats # toggle the extra stats when the button is clicked
                if not self.stats_calculated:
                    self.num_clicks.text = f"No. of clicks: {self.total_clicks}"
                    self.benchmark_value = game.calculateBenchmark(self.board)
                    self.benchmark.text = f"3BV: {self.benchmark_value}"
                    if self.current_time == 0: # avoid zero error if completed instantly
                        self.benchmark_sec.text = "3BV/s: infinite!"
                    else:
                        self.benchmark_sec_value = self.benchmark_value / self.current_time
                        self.benchmark_sec.text = "3BV/s: " + str(self.benchmark_sec_value)[:5]
                    self.efficiency_value = (self.benchmark_value*100)//self.total_clicks
                    self.efficiency.text = f"Efficiency: {self.efficiency_value}%"
                    self.stats_calculated = True

            if self.reset_button.isClicked(event):
                self.board = self.setBoard()
                self.remaining_flags = self.mine_count
                self.completion = 0
                self.total_clicks = 0
                self.stats_calculated = False
                self.show_extra_stats = False
                self.game_result = None
                self.first_click = True
                break

            if self.return_button.isClicked(event):
                return "LOBBY"

            if event.type == pygame.QUIT:
                    return "QUIT"
        return "GAME"