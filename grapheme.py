## Michael Carter
## mjcarter@ualberta.ca
## February/March 2020

## Objects of this class represent a single grapheme (a letter or number), 
## which will be presented on the main game board. 
## This is done so that colours can be easily changed and turned on/off.
## This class is based on my class Word from Synesthetic-Word-Presenter:
##   https://github.com/m-j-carter/Synesthetic-Word-Presenter

## Class utilizes methods in the uagame library

# Notes/Changelog:
#   - draw_grapheme() now saves and restores the window's prior attributes. 
#   - color of the printed grapheme is currently determined at calltime
#       by the calling function. This could get changed to an object attribute
#       that would need to be set at time of creation, or otherwise. 
#
#   - if I wanted to add the ability to randomly colorize graphemes for trials,
#     I could probably just do this with a method that shuffles/picks from
#     the dict SYN_COLORS

import pygame

DEFAULT_FONT_COLOR = 'black'
DEFAULT_FONT_SIZE = 72
DEFAULT_FONT_NAME = 'arial'

pygame.init()

class Grapheme:
    """ Represents a grapheme object (letter/number), which is assigned a corresponding colour,
        as stated in SYN_COLORS. draw_grapheme() can be called with the boolean attribute
        is_colored, which draws it with either those colors or the DEFAULT_FONT_COLOR.
    """

    """
    # Colour Correspondences:
    # Based on the modal results from Witthoft, Winawer, and Eagleman (2015)
    "A":"red",
    "B":"blue",
    "C":"yellow",
    "D":"blue",
    "E":"green",
    "F":"green",
    "G":"green",
    "H":"orange",
    "I":"white",
    "J":"orange",
    "K":"orange",
    "L":"yellow",
    "M":"red",
    "N":"orange",
    "O":"white",
    "P":"purple",
    "Q":"purple",
    "R":"red",
    "S":"yellow",
    "T":"blue",
    "U":"orange",
    "V":"purple",
    "W":"blue",
    "X":"black",
    "Y":"yellow",
    "Z":"black",
    """    

    SYN_COLORS = {
        "A":"red",
        "B":"blue",
        "E":"green",
        "G":"green",
        "L":"yellow",
        "N":"orange",
        "Y":"yellow"
    }

    @classmethod
    def set_window(cls, window_from_parent):
        cls.window = window_from_parent
        
    @classmethod
    def set_is_colored(cls, is_colored):
        cls.is_colored = is_colored


    def __init__(self, char):
        self.__char = str(char)        # self.__char is a string of len 1 (python doesn't have char types)
        self.__color = DEFAULT_FONT_COLOR         # initialize as default color
        self.__size = DEFAULT_FONT_SIZE
        self.__font = DEFAULT_FONT_NAME
        self.__generate_color()

    def __str__(self):
        return str(self.__char)

    def __repr__(self):
        return str(self.__char)    

    def __generate_color(self):
        """ If the grapheme is in SYN_COLORS, this generates 
            and assigns the synesthetic color to the grapheme. """

        temp = Grapheme.SYN_COLORS.get(str(self.__char).upper())
        if temp:
            self.__color = Grapheme.SYN_COLORS.get(str(self.__char).upper())     

    def draw(self, x, y):
        """ draws the character to the display using modules 
            in the uagame library. """
        # Note: is_colored is now a class attribute, rather than a parameter

        # save previous window attributes so they can be restored afterwards
        old_bg_color = Grapheme.window.get_bg_color()
        old_font_color = Grapheme.window.get_font_color()
        old_font_size = Grapheme.window.get_font_size()
        # old_font_name = Grapheme.window.get_font_name()
        # ^^^ uagame currently doesn't support get_font_name()

        #Grapheme.window.set_font_name(self.__font)
        Grapheme.window.set_font_size(self.__size)
        if Grapheme.is_colored:
            Grapheme.window.set_font_color(self.__color)   
        else:
            Grapheme.window.set_font_color(DEFAULT_FONT_COLOR)   

        Grapheme.window.draw_string(self.__char, x, y)   

        # Restore window attributes     
        Grapheme.window.set_bg_color(old_bg_color)
        Grapheme.window.set_font_color(old_font_color)
        Grapheme.window.set_font_size(old_font_size)
        # Grapheme.window.set_font_name(old_font_name)

    def get_grapheme(self):
        """ returns the grapheme character """
        return self.__char