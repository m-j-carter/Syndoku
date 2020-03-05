##    Michael Carter        ##
##    mjcarter@ualberta.ca  ##
##    February/March 2020   ##


## This class represents the Sudoku game board ##


# Notes/Changelog:
#   - not sure if I still need solution_set since solution is now a list of Grapheme objects 
#
#   - coloring valid segments currently works, but doesn't automatically turn
#       off when made invalid. Gotta do some thinking on how to make this work well
# 
#   - I kind of want to add drag-drop abilities too 
# 
#   - currently has no functionality to permit setting is_colored for 
#       character presentation.
# 
#   - updating cells now uses a queue called update_queue, which stores the
#       changed cells until they are drawn. 


from grapheme import Grapheme
from uagame import Window
import pygame as pg
import time
import queue

FRAMERATE = 30

BOARD_ORIGIN_X = 70            # the top-left corner of the board 
BOARD_ORIGIN_Y = 70    
SOLUTION_ORIGIN_X = 200         # top-left corner of the solution string
SOLUTION_ORIGIN_Y = 15

CELL_SIZE = 40
CELL_COLOR_DEFAULT = pg.Color("white")
CELL_COLOR_HOVERED = pg.Color("lightyellow")
CELL_COLOR_CLICKED = pg.Color("gold")
CELL_COLOR_VALID = pg.Color("lightgreen")
CELL_COLOR_INVALID = pg.Color("red")
CELL_BORDER_COLOR_A = pg.Color("grey")
CELL_BORDER_COLOR_B = pg.Color("black")
CELL_BORDER_WIDTH = 1
WINDOW_BACKGROUND_COLOR = pg.Color("white")
DEFAULT_FONT_COLOR = pg.Color("black")

IGNORE_CAPS = True

# BORDER_COLOR_MATRIX is just a temporary solution for choosing border colors.
# It should actually be calculated so that it is scalable. 
BORDER_COLOR_MATRIX = [[0,0,0,1,1,1,0,0,0],
                       [0,0,0,1,1,1,0,0,0],
                       [0,0,0,1,1,1,0,0,0],
                       [1,1,1,0,0,0,1,1,1],
                       [1,1,1,0,0,0,1,1,1],
                       [1,1,1,0,0,0,1,1,1],
                       [0,0,0,1,1,1,0,0,0],
                       [0,0,0,1,1,1,0,0,0],
                       [0,0,0,1,1,1,0,0,0],
                       ]


# # If using numbers:
# ALLOWABLE_INPUTS = [pg.K_0, pg.K_1, pg.K_2, pg.K_3, pg.K_4, 
#                     pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9]
# # If using leters:
# ALLOWABLE_INPUTS = [pg.K_a, pg.K_b, pg.K_c, pg.K_d, pg.K_e, 
#                     pg.K_f, pg.K_g, pg.K_h, pg.K_i, pg.K_j, 
#                     pg.K_k, pg.K_l, pg.K_m, pg.K_n, pg.K_o, 
#                     pg.K_p, pg.K_q, pg.K_r, pg.K_s, pg.K_t, 
#                     pg.K_u, pg.K_v, pg.K_w, pg.K_x, pg.K_y, pg.K_z]

class Sudoku:
    """ This class represents everything needed to handle the game logic and 
        presentation for the Sudoku game.
        solution_set represents the set of characters required in each unit, 
        row, and column for the puzzle to be solved. 
    """
    def __init__(self, window, solution):

        assert len(solution) == len(set(solution)), "Each character in the solution must be unique"
        # create the solution set:
        self.__board_size = len(solution)
        self.__solution = []                    # self.__solution is a list that contains objects of the class Grapheme
        self.__solution_set = set()
        for item in solution:
            self.__solution.append(Grapheme(item))
            self.__solution_set.add(item.lower())

        self.__window = window
        self.__clock = pg.time.Clock()
        self.__quit = False
        self.__complete = False
        self.__delete_char = False
        self.__key_pressed_str = ""
        self.__lmb_pressed = False
        self.__lmb_press_pos = (0,0)        # coordinates of the cursor at last mouseclick
        self.__mouse_pos = (0,0)
        self.__clicked_cell = None
        self.__update_queue = queue.SimpleQueue()

        # initialize the board:
        self.__board = [[None for i in range(self.__board_size)] for j in range(self.__board_size)] 
        self.__create_board()

    def __create_board(self):
        """ create a board that is n*n cells """
        Cell.set_window(self.__window)

        # Set up the window
        self.__window.set_bg_color(WINDOW_BACKGROUND_COLOR)
        self.__window.set_font_color(DEFAULT_FONT_COLOR)
        self.__window.set_auto_update(False)

        screen_rect = self.__window.get_surface()
        screen_rect.fill(WINDOW_BACKGROUND_COLOR)
        
        for row in range(self.__board_size):
            for col in range(self.__board_size):
                
                # border color is calculated by ...
                if BORDER_COLOR_MATRIX[row][col]:
                    border_color = CELL_BORDER_COLOR_A
                else:
                    border_color = CELL_BORDER_COLOR_B

                # calculate x,y of the cell
                x = BOARD_ORIGIN_X + (col * CELL_SIZE)
                y = BOARD_ORIGIN_Y + (row * CELL_SIZE)
                # create the cell
                self.__board[row][col] = Cell(border_color, x, y) 
                # add the cell to the queue to be updated
                self.__update_queue.put(self.__board[row][col])

    def manually_set_cell(self, row, col, character):
        """ Manually sets the cell at the specified position to the character
            specified. Use this iteratively to create an initial game board.
        """ 
        self.__board[row][col].set_char(character)

### Methods for drawing and updating the game: ###

    def play(self):
        """ Handles the entire game loop"""
        while not self.__quit and not self.__complete:
            self.__check_events()
            self.__update_board()
            self.__draw_solution()
            self.__draw_board()
            self.__check_complete()
            self.__window.update()
            self.__clock.tick(FRAMERATE)    

    def __draw_solution(self):
        """ draw the solution/hint """
        y = SOLUTION_ORIGIN_Y
        x = SOLUTION_ORIGIN_X
        # surface is a temporary solution, might change to its own rect or something
        surface = self.__window.get_surface()   
        for  item in self.__solution:
            item.draw(surface, x, y)
            # dynamically adapt x based on width of the character
            x += item.get_width()           
            
    def __draw_board(self):
        """ draw each cell that has been updated """
        while not self.__update_queue.empty():
            cell = self.__update_queue.get()
            cell.draw_cell()

    def __check_events(self):
        """ Checks for, and handles, all events caused by player interaction """
        
        # reset variables
        self.__delete_char = False
        self.__key_pressed_str = ""
        self.__mouse_pos = pg.mouse.get_pos()       # save the mouse coordinates
        self.__lmb_pressed = False

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.__quit = True

            if event.type == pg.MOUSEBUTTONUP:
                # will treat both LMB and RMB as clicks
                self.__lmb_pressed = True
                self.__lmb_press_pos = pg.mouse.get_pos()

            if event.type == pg.KEYUP:
                self.__handle_keyup(event.key)
            
    def __handle_keyup(self, key):
        if key == pg.K_BACKSPACE or key == pg.K_DELETE:
            # delete the active character
            self.__delete_char = True
        else:                    
            for grapheme in self.__solution:
                if IGNORE_CAPS:
                    ch = grapheme.get_grapheme().lower()
                else:
                    ch = grapheme.get_grapheme()
                if pg.key.name(key) == ch:
                    self.__key_pressed_str = pg.key.name(key)

    def __update_board(self):
        """ Checks and updates each cell to change their color when 
            hovered/clicked, and to update their characters when changed.
        """
        # Note: With the current logic for checking clicks, a clicked cell that
        #       is then hovered over will still change to the hovered color. 
        #       This could easily be changed if desired. 
        for row in self.__board:
            for cell in row:
    
                # first check if it's been clicked on
                if cell.check_collides(self.__lmb_press_pos):
                   self.__handle_cell_clicked(cell)

                # otherwise. if it's hovered over...
                elif cell.check_collides(self.__mouse_pos):
                    self.__handle_cell_hovered(cell)

                else:
                    # if it isn't the clicked cell, make it the default 
                    # color. Otherwise, leave it. 
                    if cell is not self.__clicked_cell and cell.get_color() not in (
                                             CELL_COLOR_DEFAULT,
                                             CELL_COLOR_VALID, 
                                             CELL_COLOR_INVALID
                                             ):
                        self.__update_queue.put(cell)
                        cell.change_color(CELL_COLOR_DEFAULT)

    def __handle_cell_clicked(self, cell):
        """ Carry out the changes for when a specified cell has been clicked on """
        # only one cell can be selected at once, so the variable __clicked_cell 
        # keeps track of which is currently selected. 

        self.__update_queue.put(cell)

        if cell is not self.__clicked_cell:
            cell.click()
            # unclick the old cell, then click the new one.
            if self.__clicked_cell:
                self.__clicked_cell.change_color(CELL_COLOR_DEFAULT)
                self.__update_queue.put(self.__clicked_cell)
                self.__clicked_cell.unclick()
            self.__clicked_cell = cell
        
        if not cell.get_char() and self.__key_pressed_str:
            # if it's empty, set its character to what the player entered
            cell.set_char(self.__key_pressed_str)
        elif self.__delete_char:
            # otherwise, if del/backspace was pressed, empty the cell
            cell.set_char(None)

    def __handle_cell_hovered(self, cell):
        """ Carry out the changes for when a specified cell is hovered over """
        self.__update_queue.put(cell)
        cell.change_color(CELL_COLOR_HOVERED)
      
### Sudoku Game Logic: ###
    
    def __check_complete(self):
        """ check each row, column, and subgrid to see if the game board has 
            been solved. 
            For each row/column/subgrid that is solved, update its color.
            If all rows, columns, and subgrids are solved, set 
            is_complete to True. 
        """
        self.__is_complete = True
        # check rows and columns
        for i in range(self.__board_size):
            if not (self.__segment_is_complete(self.__board[i][0:]) or \
                    self.__segment_is_complete(self.__board[0:][i])):
                self.__is_complete = False
        
        # check subgrids
        for x in range(0, self.__board_size, 3):
            for y in range(0, self.__board_size, 3):
                if not self.__subgrid_is_complete(x, y, 3):
                    self.__is_complete = False
        


    def __segment_is_complete(self, cell_list):
        """ Checks if the row/column is complete and valid by removing valid
            cells as it finds them. In doing so, it will also report duplicates
            as an invalid row/column. 
        """
        temp_set = self.__solution_set.copy()
        for cell in cell_list:
            if cell.get_char() not in temp_set:
                return False
            else:
                # print("cell",cell.get_char(),"found in set")
                temp_set.remove(cell.get_char())
        if len(temp_set) > 0:
            # then not all elements were removed, meaning that the row/column
            # wasn't fully occupied.
            return False
        
        # Since they're valid, recolor the cells
        # print("valid segment!")
        for cell in cell_list:
            cell.change_color(CELL_COLOR_VALID)
            self.__update_queue.put(cell)

        return True

    def __subgrid_is_complete(self, x, y, edge):
        """ a square is represented by its top-left cell 
            and its edge length.
        """
        subgrid = []
        for i in range(edge):
            for j in range(edge):
                subgrid.append(self.__board[x+i][y+j])
        return self.__segment_is_complete(subgrid)

class Cell:
    """ Objects represent a cell of the game board. Cells can be either empty
        or filled with an object of class Grapheme. """
    
    @classmethod
    def set_window(cls, window_from_parent):
        cls.window = window_from_parent
        Grapheme.set_window(window_from_parent)

    def __init__(self, border_color, x, y):
        # I actually don't need self.__x or sel.__y, but methods still use it
        self.__x = x
        self.__y = y
        self.__border_color = border_color
        self.__size = CELL_SIZE
        self.__rect = pg.Rect((self.__x, self.__y), 
                              (self.__size, self.__size))
        self.__bg_color = CELL_COLOR_DEFAULT
        self.__char = Grapheme(None)
        self.__is_clicked = False

    def draw_cell(self):
        """ Draw the cell, and draw the char (if applicable) """
        self.__draw_rect()
        x, y = self.__get_char_xy()
        self.__char.draw(Cell.window.get_surface(), x, y)
    
    def __get_char_xy(self):
        """ calculates and returns a tuple of the cell's character's 
            (x,y) coordinates.         
        """
        x = int(self.__x + ((self.__size - self.__char.get_width()) / 2))
        y = int(self.__y + ((self.__size - self.__char.get_font_height()) / 2))
        return (x,y)

    def __draw_rect(self):
        """ Helper method to draw the cell with border """
        surface = Cell.window.get_surface()
        
        surface.fill(self.__border_color, self.__rect)
        surface.fill(self.__bg_color, 
                     self.__rect.inflate(-CELL_BORDER_WIDTH*2, 
                                         -CELL_BORDER_WIDTH*2))

    def change_color(self, color):
        """ Changes the background color of the cell.
            Expects the argument color to be a pygame-compatible string or RGB.    
        """
        self.__bg_color = color

    def get_color(self):
        """ Returns the cell's current pygame.Color object """
        return self.__bg_color

    def set_char(self, char):
        self.__char = Grapheme(char)

    def get_char(self):
        if self.__char:
            return self.__char.get_grapheme()
        else:
            return None
    
    def check_collides(self, point):
        """ returns True if the point collides with the cell.
            Point is a tuple of the coordinates (x,y) """
        return self.__rect.collidepoint(point)

    def click(self):
        """ sets is_clicked to True and changes color when clicked """
        if not self.__is_clicked:
            self.__is_clicked = True
            self.change_color(CELL_COLOR_CLICKED) 

    def unclick(self):
        """ unclicks the cell, changing its colour back """
        # Note: is_clicked currently does nothing, just acts as a flag
        self.__is_clicked = False
        self.change_color(CELL_COLOR_DEFAULT)



# For debugging only, since the class is only supposed to be called from main.py
if __name__ == "__main__":
    test_window = Window("Test Sudoku", 500, 500)
    test_window.set_auto_update(False)
    test_game = Sudoku(test_window, 'ABCDEFGHI')
    test_game.play()
    pg.quit()
