import random

class Square():
    def __init__(self):
        self.number = 0
        self.revealed = False
        self.flagged = False

    # getters
    def getNumber(self):
        return self.number
    def isRevealed(self):
        return self.revealed
    def isFlagged(self):
        return self.flagged
    
    # setter methods
    def setNumber(self, new_num):
        self.number = new_num
    def reveal(self):
        self.revealed = True
        self.flagged = False # revealed squares cannot be flagged
    def cover(self):
        self.revealed = False
    def flag(self):
        self.flagged = not self.flagged # in game, flags are toggleable so the flag method just needs to swap the value

def createBoard(board_dimensions):
    board = []
    for y in range(board_dimensions[0]):
        row = []
        for x in range(board_dimensions[1]):
            row.append(Square())
        board.append(row)
    return board



def placeMines(board, click_y, click_x, num_mines): # click_x and click_y hold the location of the first click
    placed = [] # holds location of already placed mines

    for i in range(num_mines):
        mine_y = random.randint(0, len(board)-1)
        mine_x = random.randint(0, len(board[0])-1)
        # regenerate mines if they are on the first click or directly adjacent to it
        while abs(mine_y-click_y) <= 1 or abs(mine_x-click_x) <= 1 or [mine_y, mine_x] in placed:
            mine_y = random.randint(0, len(board)-1)
            mine_x = random.randint(0, len(board[0])-1)

        board[mine_y][mine_x].setNumber(-1)
        placed.append([mine_y, mine_x])

def generateNumbers(board):
    # loop to find each mine in the board
    for y in range(len(board)):
        for x in range(len(board[0])):
            # if a mine is found, increment the adjacent squares by 1
            if board[y][x].getNumber() == -1:
                for i in range(-1,2): # to search every vertically adjacent square
                    for j in range(-1,2): # to search every horizontally adjacent square
                        # ensure searching is within boundaires and the current square is not changed
                        if 0<=y+i<len(board) and 0<=x+j<len(board[0]) and not (i==j==0):
                            square = board[y+i][x+j]
                            # increment the square number if it is not a mine
                            if square.getNumber() != -1:
                                num = square.getNumber()
                                num += 1
                                board[y+i][x+j].setNumber(num)

def revealArea(board, y, x):
    if board[y][x].isRevealed(): # ensuring that the algorithm stops if the square has already been revealed
        return
    
    value = board[y][x].getNumber()
    if value == 0: # if it is an empty square, reveal it and search all adjacent squares
        for i in range(-1,2): # to search every vertically adjacent square
            for j in range(-1,2): # to search every horizontally adjacent square
                # ensuring searching is within boundaires
                if 0<=y+i<len(board) and 0<=x+j<len(board[0]):
                    if i==j==0:
                        # reveal the current square 
                        board[y][x].reveal()
                    else:
                        # search and reveal adjacent squares
                        revealArea(board, y+i, x+j)
    elif value > 0: # if it is a numbered square, reveal it and end - this is the base case
        board[y][x].reveal()
        return

def updateStats(board, max_flags):
    game_result = None
    total_squares = len(board) * len(board[0])
    completed_squares = 0 # "completed squares" are squares that have been revealed or flagged
    all_revealed = True # flag that is reset if a covered safe square is found
    flags_placed = 0
    for row in board:
        for square in row:
            if square.isFlagged():
                flags_placed += 1
                completed_squares += 1
            if square.isRevealed():
                completed_squares += 1
            # if there is a safe square that hasnt been revealed, the user has not won yet
            elif not square.getNumber() == -1:
                all_revealed = False
    if all_revealed:
        game_result = 1
    # return flags remaining and board completion (in float form)
    return game_result, max_flags-flags_placed, completed_squares/total_squares

def performChord(board, y, x):
    adjacent_mines = 0
    placed_flags = 0
    for i in range(-1,2):
        for j in range(-1,2):
            if 0<=y+i<len(board) and 0<=x+j<len(board[0]) and not (i==j==0):
                square = board[y+i][x+j]
                if square.getNumber() == -1:
                    adjacent_mines += 1
                if square.isFlagged():
                    placed_flags += 1
    if placed_flags == adjacent_mines:
        for i in range(-1,2):
            for j in range(-1,2):
                if 0<=y+i<len(board) and 0<=x+j<len(board[0]) and not (i==j==0):
                    square = board[y+i][x+j]
                    if not square.isFlagged():
                        if square.getNumber() == -1:
                            return -1 # -1 represents game over, 1 represents game won
                        else:
                            revealArea(board, y+i, x+j)

def performClick(board, key, position, max_flags): # key will be an integer; 0 for left click and 1 for right click
    game_result = None
    square = board[position[0]][position[1]]
    if key == 0:
        if not square.isFlagged(): # flagged squares cannot be revealed
            if square.getNumber() == -1:
                game_result = -1 # -1 represents game over, 1 represents game won
            elif not square.isRevealed():
                revealArea(board, position[0],position[1])
            else:
                # perform a chord if they have left clicked a number
                game_result = performChord(board, position[0],position[1])
    elif not square.isRevealed():
        square.flag()
    if game_result != -1: # if they have not lost, continue updating stats
        game_result, remaining_flags, completion = updateStats(board, max_flags)
    else:
        completion = 0
        remaining_flags = 0
    return game_result, remaining_flags, completion

def calculateBenchmark(board):
    benchmark = 0
    # re-cover the board
    for row in board:
        for square in row:
            square.cover()
    # reveal flood fill areas
    for y in range(len(board)):
        for x in range(len(board[0])):
            if not board[y][x].isRevealed() and board[y][x].getNumber() == 0:
                revealArea(board, y, x)
                benchmark += 1
    # count remaining numbers
    for row in board:
        for square in row:
            if not square.isRevealed() and square.getNumber() > 0:
                benchmark += 1
                square.reveal()

    return benchmark

def textDisplay(board):
    for row in board:
        line = ""
        for square in row:
            if square.getNumber() == -1:
                line += "8"
            else:
                line += str(square.getNumber())
        print(line)