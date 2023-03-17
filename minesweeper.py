# scuffed online version - https://trinkey.trinket.io/sites/minesweep ~ https://trinket.io/pygame/7babfe187e

difficulty = 4

# +----------------------------------+
# | Difficulty:                      \
# \ 0 - very easy - 10x10, 1 bomb    |
# | 1 - easy      - 10x10, 10 bombs  \
# \ 2 - normal    - 16x16, 20 bombs  |
# | 3 - hard      - 25x25, 50 bombs  \
# \ 4 - expert    - 40x40, 150 bombs |
# | Anything else - custom, use      \
# \     `bombs = ` and `size = `     |
# +----------------------------------+

bombs = 10
size  = 10

# =====================================================
# Everything under this is just for personal reference,
# you don't need to understand anything under this
# comment in the slightest if you aren't coding with
# this application.
# =====================================================


# +----------------------------------------+
# \ TODO LIST:                             |
# | Add a difficulty selection screen on   \
# \   startup so you don't have to edit    |
# |   the file                             \
# \ Allow changing the width and height    |
# |   separately                           \
# +----------------------------------------+

# clicked (list) -
# 0 - No modifier
# 1 - Clicked normally
# 2 - Flagged

# Allowed transformations for Minesweeper click rules:
# 0 -> 1 (L)
# 0 -> 2 (R)
# 2 -> 0 (R)


# board (list) -
# -1  - Bomb
# 0   - Blank tile of adjacent bombs
# 1-8 - Number

# if clicked[x][y] == 1 and board[x][y] == -1: kaboom

# Libraries
from random import randint        # Used to randomly place bombs
from os import listdir            # Used to easily import all image sprites
from time import time             # Used for the timer when you win a game
from sys import setrecursionlimit # Used to prevent RecursionError with larger board sizes
from turtle import Turtle, Screen # Used for graphics

difficultyReference = { # Referenced when selecting difficulty.
    "0": [10, 1],       # Feel free to add more
    "1": [10, 10],
    "2": [16, 20],
    "3": [25, 50],
    "4": [40, 150]
}
if str(difficulty) in difficultyReference:
    size  = difficultyReference[str(difficulty)][0]
    bombs = difficultyReference[str(difficulty)][1]
del difficultyReference
del difficulty

class Board:
    def __init__(self, bombs, size): # Setup function
        # Setup variables
        self.firstClick = True
        self.originalTime = 0
        self.bombs = bombs
        self.size = size
        self.checked = []
        self.correspondingShapes = { # Corresponding "shapes" (images) to render when
            "-1": "bomb",            # certain tiles are clicked (corresponds to board
            "0": "blankClick",       # (list) format seen at start of program)
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8"
        }

        # Setup screen
        self.screen = Screen()
        self.screen.bgcolor("#999999")
        self.screen.tracer(0)
        self.screen.title("Python Minesweeper -1.2")

        self.screen.onclick(self.leftClick, 1)
        self.screen.onclick(self.rightClick, 3)
        self.screen.onkey(self.bye, "space")
        self.screen.listen()

        # Setup turtle object for writing on screen when you win/lose
        self.text = Turtle()
        self.text.pu()
        self.text.ht()
        self.text.goto(0, self.size * 8)

        # Add shapes
        for i in listdir("./minesweep/"):
            if i[-4::] == ".gif":
                 self.screen.addshape(f"minesweep/{i}")

        self.generateNewBoard(self.size, self.size, self.bombs)

        class Tile: # Controls the rendering of the individual tiles on the board.
            def __init__(self, x, y, shape):
                self.turtle = Turtle()
                self.turtle.pu()
                self.turtle.speed(0)
                self.turtle.goto(x, y)
                self.turtle.shape(f"minesweep/{shape}.gif")
                self.turtle.shapesize(2, 2)

            def updateShape(self, shape):
                self.turtle.shape(f"minesweep/{shape}.gif")


        # Create list of Tile class for later use
        self.tiles = []
        for i in range(self.size):
            self.tiles.append([])
            for o in range(self.size):
                self.tiles[-1].append(
                    Tile(o * 16 - (self.size * 8 - 8),
                    (self.size * 8 - 25) - i * 16, "blankTile")
                )

        self.screen.update() # Update display needed because of `self.screen.tracer(0)`
        self.screen.mainloop()

    def reset(self, x = 0, y = 0): # Reset the game
        for i in self.tiles:
            for o in i:
                o.updateShape("blankTile")
        self.text.goto(0, self.size * 8)
        self.text.clear()
        self.screen.onclick(self.leftClick, 1) # reset click events
        self.screen.onclick(self.rightClick, 3)

        self.firstClick = True
        self.generateNewBoard(self.size, self.size, self.bombs)
        self.screen.update()

    def determineWhereTileIs(self, x, y): # Function determines where in the list a pair
                                          # of x/y coordinates are (works with clicked,
                                          # board, and self.tiles)
        return [
                int(x / 16 + self.size / 2),
                int(-((y + 1) / 16 - self.size / 2 + 1))
            ] if self.coordsAreOnBoard(
                int(x / 16 + self.size / 2),
                int(-((y + 1) / 16 - self.size / 2 + 1))
            ) else False

    def coordsAreOnBoard(self, x, y): # Checks if a pair of coordinates are on the board
        return x >= 0 and x <= self.size - 1 and y >= 0 and y <= self.size - 1

    def leftClick(self, x, y): # Function called on a left click
        written = False
        coords = self.determineWhereTileIs(x, y)
        if coords:
            if self.firstClick: # If it is first click, make sure you click on blank
                self.originalTime = time() # tile so you dont die or anything like that
                c = 10000
                while self.board[coords[1]][coords[0]] != 0:
                    self.generateNewBoard(self.size, self.size, self.bombs)
                    c -= 1
                    if not c:
                        print("Could not generate a valid starting board in 10000 attempts. Using what we currently have...")
                        break
                self.firstClick = False

            self.checked = []
            self.flood(coords[0], coords[1])
            if len(self.checked) == 1 and self.clicked[self.checked[0][1]][self.checked[0][0]] == 1 and \
                self.board[self.checked[0][1]][self.checked[0][0]] in [1, 2, 3, 4, 5, 6, 7, 8]:
                tmp = self.checked[0]
                flagCount = 0
                for i in range(3):
                    for o in range(3):
                        if self.coordsAreOnBoard(self.checked[0][1] + i - 1, self.checked[0][0] + o - 1):
                            if self.clicked[self.checked[0][1] + i - 1][self.checked[0][0] + o - 1] == 2:
                                flagCount += 1
                if flagCount == self.board[self.checked[0][1]][self.checked[0][0]]:
                    for i in range(3):
                        for o in range(3):
                            if self.coordsAreOnBoard(tmp[1] + i - 1, tmp[0] + o - 1) and \
                                self.clicked[tmp[1] + i - 1][tmp[0] + o - 1] == 0:
                                if self.board[tmp[1] + i - 1][tmp[0] + o - 1] == 0:
                                    self.flood(tmp[0] + o - 1, tmp[1] + i - 1)
                                    for u in self.checked:
                                        self.tiles[u[1]][u[0]].updateShape(
                                            self.correspondingShapes[str(self.board[u[1]][u[0]])]
                                        )
                                        self.clicked[u[1]][u[0]] = 1
                                else:
                                    self.tiles[tmp[1] + i - 1][tmp[0] + o - 1].updateShape(
                                        self.correspondingShapes[str(self.board[tmp[1] + i - 1][tmp[0] + o - 1])]
                                    )
                                    self.clicked[tmp[1] + i - 1][tmp[0] + o - 1] = 1
            else:
                for i in self.checked: # Every tile to reveal
                    if self.clicked[i[1]][i[0]] == 0 or i != coords:
                        self.tiles[i[1]][i[0]].updateShape(
                            self.correspondingShapes[str(self.board[i[1]][i[0]])]
                        )
                        self.clicked[i[1]][i[0]] = 1
        if not written and self.checkIfDie():
            self.revealEntireBoard()
            self.text.write("You lost! noooo...", False, "center", ("Arial", 24, "normal"))
            self.text.goto(0, self.text.ycor() - 12)
            self.text.write("Click to restart.", False, "center", ("Arial", 12, "normal"))
            self.screen.onclick(self.reset, 1)
            self.screen.onclick(None, 3)
            written = True
        elif not written and self.checkIfWin():
            self.text.write("Yay! You win!", False, "center", ("Arial", 24, "normal"))
            self.text.goto(0, self.text.ycor() - 12)
            self.text.write("Click to restart.", False, "center", ("Arial", 12, "normal"))
            self.text.goto(0, self.text.ycor() + 45)
            self.text.write(f"Time: {time() - self.originalTime} seconds", False, "center", ("Arial", 12, "normal"))
            self.screen.onclick(self.reset, 1)
            self.screen.onclick(None, 3)
            written = True
        self.screen.update() # Update display

    def rightClick(self, x, y): # Function called on a right click (places flag)
        coords = self.determineWhereTileIs(x, y)
        if coords:
            if self.clicked[coords[1]][coords[0]] == 0: # Place flag if there is none
                self.tiles[coords[1]][coords[0]].updateShape("flag")
                self.clicked[coords[1]][coords[0]] = 2
                self.screen.update()
            elif self.clicked[coords[1]][coords[0]] == 2: # Remove flag if there is one
                self.tiles[coords[1]][coords[0]].updateShape("blankTile")
                self.clicked[coords[1]][coords[0]] = 0
                self.screen.update()

    def bye(self, x = 0, y = 0): # Kill the screen
        self.screen.bye()

    def checkIfDie(self): # Checks if a bomb has been clicked
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == -1 and self.clicked[x][y] == 1:
                    return True
        return False

    def revealEntireBoard(self): # Reveals entire board.
        for x in range(self.size):      # If a tile is a flag and a bomb, it doesn't update
            for y in range(self.size):  # and stays a flag.
                if self.clicked[x][y] != 2 or self.board[x][y] != -1:
                    self.clicked[x][y] = 1
                    self.tiles[x][y].updateShape(
                        self.correspondingShapes[str(self.board[x][y])]
                    )

    def checkIfWin(self): # Checks to see if you won
        for x in range(self.size):
            for y in range(self.size):
                if self.clicked[x][y] != 1 and self.board[x][y] != -1:
                    return False
        return True

    def generateNewBoard(self, height = 10, width = 10, bombs = 10): # Generates a new minesweeper board
        if bombs >= width * height: # If there are too many bombs to fill the board
            return False
        boardTemplate = []

        # Randomly place bombs
        for i in range(height * width):
            if randint(0, (width * height) - i - 1) < bombs:
                bombs -= 1
                boardTemplate.append(-1)
            else:
                boardTemplate.append(0)

        self.board = []
        self.clicked = []

        # Makes board list into nested list and creates the clicked list
        for i in range(height):
            self.board.append([])
            self.clicked.append([])
            for o in range(width):
                self.board[-1].append(boardTemplate[i * width + o])
                self.clicked[-1].append(False)

        del boardTemplate

        # Calculates the numbers
        for row in range(len(self.board)):
            for column in range(len(self.board[0])):
                if self.board[row][column] != -1:
                    b = 0
                    if row != 0:
                        if self.board[row - 1][column] == -1:
                            b += 1
                        if column != 0 and self.board[row - 1][column - 1] == -1:
                            b += 1
                        if column != len(self.board[0]) - 1 and \
                            self.board[row - 1][column + 1] == -1:
                            b += 1
                    if row != len(self.board) - 1:
                        if self.board[row + 1][column] == -1:
                            b += 1
                        if column != 0 and self.board[row + 1][column - 1] == -1:
                            b += 1
                        if column != len(self.board[0]) - 1 and \
                            self.board[row + 1][column + 1] == -1:
                            b += 1
                    if column != 0 and self.board[row][column - 1] == -1:
                        b += 1
                    if column != len(self.board[0]) - 1 and \
                        self.board[row][column + 1] == -1:
                        b += 1
                    self.board[row][column] = b
        return True

    def flood(self, x, y): # WHen clicking a blank space it floods the area with other
        if [x, y] not in self.checked:
            self.checked.append([x, y])
        if self.board[y][x] == 0:
            if [x + 1, y - 1] not in self.checked and self.coordsAreOnBoard(x + 1, y - 1):
                self.flood(x + 1, y - 1)
            if [x + 1, y] not in self.checked and self.coordsAreOnBoard(x + 1, y):
                self.flood(x + 1, y)
            if [x + 1, y + 1] not in self.checked and self.coordsAreOnBoard(x + 1, y + 1):
                self.flood(x + 1, y + 1)
            if [x, y - 1] not in self.checked and self.coordsAreOnBoard(x, y - 1):
                self.flood(x, y - 1)
            if [x, y + 1] not in self.checked and self.coordsAreOnBoard(x, y + 1):
                self.flood(x, y + 1)
            if [x - 1, y + 1] not in self.checked and self.coordsAreOnBoard(x - 1, y + 1):
                self.flood(x - 1, y + 1)
            if [x - 1, y - 1] not in self.checked and self.coordsAreOnBoard(x - 1, y - 1):
                self.flood(x - 1, y - 1)
            if [x - 1, y] not in self.checked and self.coordsAreOnBoard(x - 1, y):
                self.flood(x - 1, y)

try:
    setrecursionlimit(size ** 2 + 1)
except RecursionError:
    print("[ERROR] Recursion limit too low, try increasing board size.")
game = Board(bombs, size)
