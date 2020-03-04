##    Michael Carter        ##
##    mjcarter@ualberta.ca  ##
##    February/March 2020   ##


## This class represents the Sudoku game board ##


# Notes/Changelog:
#   - not sure if I still need solution_set since solution is now a list of Grapheme objects 
#
#   - colors of cells not currently changing, not sure why not.
#   - colors are also reversed for some reason
#   - the update_cells() method needs a significant overhaul. 
#       - I'm thinking instead of polling each cell, on mouseclick the position
#           will be saved and handed to a method which will find the 
#           corresponding cell and return it. 



from grapheme import Grapheme
from uagame import Window
import pygame as pg

FRAMERATE = 60

BOARD_ORIGIN_X = 20            # the top-left corner of the board 
BOARD_ORIGIN_Y = 50    
SOLUTION_ORIGIN_X = 150         # top-left corner of the solution string
SOLUTION_ORIGIN_Y = 5

CELL_SIZE = 40
CELL_COLOR_DEFAULT = pg.Color("white")
CELL_COLOR_HOVERED = pg.Color("orange")
CELL_COLOR_CLICKED = pg.Color("blue")
CELL_BORDER_COLOR = pg.Color("black")
CELL_BORDER_WIDTH = 2
WINDOW_BACKGROUND_COLOR = pg.Color("white")
DEFAULT_FONT_COLOR = pg.Color("black")

IGNORE_CAPS = True

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
        self.__delete_char = False
        self.__key_pressed_str = ""
        self.__lmb_pressed = False
        self.__lmb_press_pos = (0,0)        # coordinates of the cursor at last mouseclick
        self.__mouse_pos = (0,0)
        self.__clicked_cell = None

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
            
                # calculate x,y of the cell
                x = BOARD_ORIGIN_X + (col * CELL_SIZE)
                y = BOARD_ORIGIN_Y + (row * CELL_SIZE)

                self.__board[row][col] = Cell(x, y) 

    def play(self):
        """ Handles the entire game loop"""
        while not self.__quit:
            self.__check_events()
            self.__update_board()
            self.__window.clear()
            self.__draw_solution()
            self.__draw_board()
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
        """ draw each cell """
        for row in self.__board:
            for cell in row:
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
                print("LMB Pressed")

            if event.type == pg.KEYUP:
                self.__handle_keyup(event.key)
            
    def __handle_keyup(self, key):
        print(pg.key.name(key))   ## DEBUG ##
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
                    if cell is not self.__clicked_cell:
                        cell.change_color(CELL_COLOR_DEFAULT)

    def __handle_cell_clicked(self, cell):
        """ Carry out the changes for when a specified cell has been clicked on """
        # only one cell can be selected at once, so the variable __clicked_cell 
        # keeps track of which is currently selected. 
        if cell is not self.__clicked_cell:
            cell.click()
            # unclick the old cell, then click the new one.
            if self.__clicked_cell:
                self.__clicked_cell.unclick()
            self.__clicked_cell = cell

    def __handle_cell_hovered(self, cell):
        """ Carry out the changes for when a specified cell is hovered over """
        cell.change_color(CELL_COLOR_HOVERED)
        if not cell.get_char() and self.__key_pressed_str:
            # if it's empty, set its character to what the player entered
            cell.set_char(self.__key_pressed_str)
        elif self.__delete_char:
            # otherwise, if del/backspace was pressed, empty the cell
            cell.set_char(None)


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
        self.__rect = pg.Rect((self.__x, self.__y), 
                              (self.__size, self.__size))
        self.__bg_color = CELL_COLOR_DEFAULT
        self.__char = Grapheme(None)
        self.__is_clicked = False

    def draw_cell(self):
        """ Draw the cell, and draw the char (if applicable) """
        # Rect((left, top), (width, height))

        # old_bg_color = Cell.window.get_bg_color()
        # Cell.window.set_bg_color(self.__bg_color)
        
        self.__draw_rect()
        x, y = self.__get_char_xy()
        self.__char.draw(Cell.window.get_surface(), x, y)

        # Cell.window.set_bg_color(old_bg_color)
    
    def __get_char_xy(self):
        """ calculates and returns a tuple of the cell's character's 
            (x,y) coordinates. 
            char's x = cell's x + ((cell size + letter width) / 2)
            char's y = cell's y - ((cell size + letter height) / 2)
        """
        x = int(self.__x + ((self.__size + self.__char.get_width()) / 2))
        y = int(self.__y - ((self.__size + self.__char.get_font_height()) / 2))
        return (x,y)

    def __draw_rect(self):
        """ Helper method to draw the cell with border """
        # pg.draw.rect(Cell.window.get_surface(), CELL_BORDER_COLOR, self.__rect, CELL_BORDER_WIDTH)
        # pg.draw.rect(Cell.window.get_surface(), self.__bg_color, self.__rect)

        surface = Cell.window.get_surface()
        
        surface.fill(CELL_BORDER_COLOR, self.__rect)
        surface.fill(self.__bg_color, 
                     self.__rect.inflate(-CELL_BORDER_WIDTH*2, 
                                         -CELL_BORDER_WIDTH*2))

    def change_color(self, color):
        """ Changes the background color of the cell.
            Expects the argument color to be a pygame-compatible string or RGB.    
        """
        self.__bg_color = color

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
    test_game = Sudoku(test_window, 'OITERSCLA')
    test_game.play()
    pg.quit()