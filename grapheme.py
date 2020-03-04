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
#   - is_colored is currently a class attribute, meaning all letters are 
#       either colored or not. This could be changed to an object attribute
#       that is assigned at time of creation, or otherwise. 
#
#   - if I wanted to add the ability to randomly colorize graphemes for trials,
#     I could probably just do this with a method that shuffles/picks from
#     the dict SYN_COLORS

import pygame

DEFAULT_FONT_COLOR = pygame.Color('black')
DEFAULT_FONT_SIZE = 24
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
    
    is_colored = False
    
    @classmethod
    def set_window(cls, window_from_parent):
        cls.window = window_from_parent

    @classmethod
    def set_is_colored(cls, is_colored):
        cls.is_colored = is_colored


    def __init__(self, char):
        if char:
            self.__char = str(char)        # self.__char is a string of len 1 (python doesn't have char types)
        else:
            self.__char = ""
        self.__color = DEFAULT_FONT_COLOR         # initialize as default color
        self.__font_size = DEFAULT_FONT_SIZE
        self.set_font(DEFAULT_FONT_NAME)
        self.__generate_color()

    def __str__(self):
        return str(self.__char)

    def __repr__(self):
        return str(self.__char)    

    def __generate_color(self):
        """ If the grapheme is in SYN_COLORS, this generates 
            and assigns the synesthetic color to the grapheme. 
        """

        temp = Grapheme.SYN_COLORS.get(str(self.__char).upper())
        if temp:
            color_name = Grapheme.SYN_COLORS.get(str(self.__char).upper())    
            self.__color = pygame.Color(color_name) 

    def draw(self, surface, x, y):
        """ draws the character to the display in its uniquely-specified 
            color, font, and size using modules in the uagame library.
        """
        # Note: is_colored is now a class attribute, rather than a parameter
        # font.render(text, antialias, color, background=None)
        text_image = self.__font.render(self.__char,
                                        True, 
                                        self.__color)
        surface.blit(text_image, (x, y))





        # save previous window attributes so they can be restored afterwards
        # old_bg_color = Grapheme.window.get_bg_color()
        # old_font_color = Grapheme.window.get_font_color()
        # old_font_height = Grapheme.window.get_font_height()
        # old_font = Grapheme.window.get_font()

        # Grapheme.window.set_font(self.__font)
        # Grapheme.window.set_font_size(self.__font_size)
        
        # if Grapheme.is_colored:
        #     Grapheme.window.set_font_color(self.__color)   
        # else:
        #     Grapheme.window.set_font_color(DEFAULT_FONT_COLOR)   

        # Grapheme.window.draw_string(self.__char, x, y)   

        # Restore window attributes     
        # Grapheme.window.set_bg_color(old_bg_color)
        # Grapheme.window.set_font_color(old_font_color)
        # Grapheme.window.set_font_size(old_font_height)
        # Grapheme.window.set_font(old_font)

    def get_grapheme(self):
        """ returns the grapheme character """
        return self.__char

    def get_width(self):
        """ returns size of the grapheme """
        # save the current font
        old_font_height = Grapheme.window.get_font_height()
        old_font = Grapheme.window.get_font()

        # set to the grapheme's font
        Grapheme.window.set_font(self.__font)
        Grapheme.window.set_font_size(self.__font_size)

        width = Grapheme.window.get_string_width(self.get_grapheme())

        # restore the original font
        Grapheme.window.set_font_size(old_font_height)
        Grapheme.window.set_font(old_font)

        return width

    def set_font(self, name):
        """ Set the name of the window font used to draw strings
            - name is the str name of the font
        """
        self.__font_name = name
        self.__font = pygame.font.SysFont(self.__font_name, self.__font_size, True)

    def get_font_name(self):
        # gets and returns the string name of the active font.
        return self.__font_name

    def set_size(self, point_size):
        """ Set the point size of the window font used to draw strings
            - point_size is the int point size of the font        
        """
        self.__size = point_size
        self.__font = pygame.SysFont(self.__font_name, self.__font_size, True)

    def get_font_height(self):
        # Return the int pixel height of the current font.
        return self.__font.size('')[1]