##    Michael Carter
##    mjcarter@ualberta.ca
##    February/March 2020


## This class represents the Sudoku game board

from grapheme import Grapheme
from uagame import Window
import pygame as pg

BOARD_ORIGIN_X = 100            # the top-left corner of the board 
BOARD_ORIGIN_Y = 100    

CELL_SIZE = 25
CELL_COLOR = "white"
CELL_COLOR_HOVERED = "shadow"
CELL_COLOR_CLICKED = "gray"
CELL_BORDER_COLOR = "black"
CELL_BORDER_WIDTH = 5

class Sudoku:

    def __init__(self, window, board_size):
        self.__window = window
        self.__board_size = board_size
        self.__quit = False
        # initialize the board:
        self.__board = [[None for i in range(board_size)] for j in range(board_size)] 
        self.__create_board()
    

    def __create_board(self):
        """ create a board that is n*n cells """
        Cell.set_window(self.__window)

        for row in range(self.__board_size):
            for col in range(self.__board_size):
               
                # calculate x,y of the cell
                x = BOARD_ORIGIN_X + (col * CELL_SIZE)
                y = BOARD_ORIGIN_Y + (row * CELL_SIZE)

                self.__board[row][col] = Cell(x, y) 

    def play(self):
        """ Handles the entire game loop"""
        while not self.__quit:
            self.__check_events()
            self.__update_board()
            self.__draw_board()
            self.__window.update()

    def __draw_board(self):
        #TODO
        for row in self.__board:
            for col in self.__board[row]:
                self.__board[row][col].draw_cell()

    def __check_events(self):
        """ Checks for, and handles, all events caused by player interaction """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.__quit = True
            



    def __update_board(self):
        """ Checks and updates each cell to change their color when 
            hovered/clicked, and to update their characters when changed.
        """
        for row in self.__board:
            for col in self.__board[row]:




    def __check_hovered_cell(self, cell):
        """ returns True if the cursor is above the cell """
        pass 


    def __check_clicked_cell(self):
        """ returns True if a click is detected within the cell """




# Logic for checking if complete:

    def __col_is_complete(self, col):
        # TODO
        pass

    def __row_is_complete(self, row):
        # TODO
        pass

    def __square_is_complete(self, row, col, edge):
        """ a square is represented by its top-left cell 
            and its edge length
        """
        # TODO
        pass


class Cell:
    """ Objects represent a cell of the game board. Cells can be either empty
        or filled with an object of class Grapheme. """
    
    @classmethod
    def set_window(cls, window_from_parent):
        cls.window = window_from_parent
        Grapheme.set_window(window_from_parent)

    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.__size = CELL_SIZE
        self.__bg_color = CELL_COLOR
        self.__char = None

    def draw_cell(self):
        """ Draw the cell, and draw the char (if applicable) """
        # Rect((left, top), (width, height))
        cell_rect = pg.Rect((self.__x, self.__y), (self.__size, self.__size))
        pg.draw.rect(Cell.window, CELL_COLOR, cell_rect, CELL_BORDER_WIDTH)
       
        if self.__char:
            old_bg_color = self.__window.get_bg_color()
            self.__window.set_bg_color(self.__bg_color)
            self.__char.draw(self.__x, self.__y)
            self.__window.set_bg_color(old_bg_color)
       
        # self.__window.update()
        # only the main loop in Sudoku will update window

    def change_color(self, color):
        """ Changes the background color of the cell.
            Expects the argument color to be a pygame-compatible string or RGB.    
        """
        self.__bg_color = color

    def set_char(self, char):
        self.__char = Grapheme(char)

    def get_char(self):
        return self.__char.get_char()




# For debugging only, since the class is only supposed to be called from main.py
if __name__ == "__main__":
    test_window = Window("Test Sudoku", 500, 500)
    test_window.set_auto_update(False)
    test_game = Sudoku(test_window, 9)
    test_game.play()
    pg.quit()