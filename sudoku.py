##    Michael Carter
##    mjcarter@ualberta.ca
##    February/March 2020


## This class represents the Sudoku game board

from grapheme import Grapheme
import pygame as pg

CELL_SIZE = 25
CELL_COLOR = "white"
CELL_BORDER_COLOR = "black"
CELL_BORDER_WIDTH = 5

class Sudoku:

    def __init__(self, window, board_size):
        self.__window = window
        self.__board_size = board_size
        self.__board[board_size][board_size]
        self.__create_board()
        self.__draw_board()


    def __create_board(self):
        """ create a board that is n*n cells """
        Cell.set_window(self.__window)
        for row in range(self.__board_size):
            for col in range(self.__board_size):
                # calculate x,y of the cell
                # TODO
                self.__board[col][row] = Cell(x, y) 


    def __draw_board(self):
        #TODO
        pass


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
        self.__char = None


    def draw_cell(self):
        """ Draw the cell, and draw the char (if applicable) """
        # Rect((left, top), (width, height))
        cell_rect = pg.Rect((self.__x, self.__y), (self.__size, self.__size))
        pg.draw.rect(Cell.window, CELL_COLOR, cell_rect, CELL_BORDER_WIDTH)
        


    def set_char(self, char):
        self.__char = Grapheme(char)

    def get_char(self):
        return self.__char.get_char()




    