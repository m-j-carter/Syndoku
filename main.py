###############################################################################
#   Synesthetic Sudoku
#   
#   Author: Michael Carter
#           mjcarter@ualberta.ca
#           February/March 2020
#       
#
###############################################################################


import pygame as pg
from pygame.locals import *

from uagame import Window
from grapheme import Grapheme
from sudoku import Sudoku


### PARAMETERS ###



## PARAMETERS ##
WINDOW_SIZE = (800, 600)

DEFAULT_FONT_COLOR = "black"
DEFAULT_FONT_SIZE = 18
DEFAULT_FONT_NAME = "Arial"
BG_COLOR = "white"


def main():
	## SET VARIABLES ##

    try:
        # Launch Game:
        window = create_window()
        game = Sudoku(window, 9)

    except Exception as e:
        print(e.args, e.with_traceback)

        

def create_window():
	# Create a window for the game and open it.
	window = Window("Sudoku", WINDOW_SIZE[0], WINDOW_SIZE[1])
	window.clear()
	window.update()

	return window   

def reset_window_defaults(window):
	# returns the window's colors, fonts, etc. to their defaults
	window.set_bg_color(BG_COLOR)
	window.set_font_color(DEFAULT_FONT_COLOR)
	window.set_font_size(DEFAULT_FONT_SIZE)
	window.set_font_name(DEFAULT_FONT_NAME)	


if __name__ == "__main__":
	main()
