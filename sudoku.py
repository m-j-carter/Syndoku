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
#   - currently any cell is editable. I need to add a flag bool(is_editable) so that
#       I can make the starting grid read-only. 
# 
#   - I kind of want to add drag-drop abilities too 
#   - I also kind of want to add arrow key board navigation
# 
#   - currently has no functionality to permit setting is_colored for 
#       character presentation.
# 
#   - updating cells now uses a queue called update_queue, which stores the
#       changed cells until they are drawn. 
# 
#   - there's some weirdness with checking if inputs are valid. Doesn't seem to detect
#       invalid inputs if the duplicate cell appears after the user inputted cell.  

from grapheme import Grapheme
from uagame import Window
import pygame as pg
import time
import queue
import yaml

# can't use yaml.safe_load() b/c the config file includes pygame objects
config = yaml.safe_load(open("config.yml"))

class Sudoku:
    """ This class represents everything needed to handle the game logic and 
        presentation for the Sudoku game.
        solution_set represents the set of characters required in each unit, 
        row, and column for the puzzle to be solved. 
    """

    def __init__(self, window, subgrid_size, solution):

        assert len(solution) == len(set(solution)), "Each character in the solution must be unique"        
        assert len(solution) % subgrid_size == 0, "The subgrid size must be a factor of the board size"

        self.__board_size = len(solution)
        self.__subgrid_size = subgrid_size
        
        # create the solution set:
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
        """ creates a board that is n*n cells, dynamically setting the
            cell background colors according to the subgrid_size. """
        Cell.set_window(self.__window)

        # Set up the window
        self.__window.set_bg_color( pg.Color( config['window']['background_color'] ) )
        self.__window.set_font_color( pg.Color( config['font']['color']['default'] ) )
        self.__window.set_auto_update(False)

        screen_rect = self.__window.get_surface()
        screen_rect.fill(pg.Color( config['window']['background_color'] ))
        
        j=0       # i and j are used to calculate the background color of the cells
        color_switch = True
        for row in range(self.__board_size):
            i=0
            for col in range(self.__board_size):
                
                # Determine the color of the cell background
                if i >= self.__subgrid_size:
                    color_switch = not color_switch
                    i=0
                if j >= self.__subgrid_size:
                    color_switch = not color_switch
                    j=0
                if color_switch:
                    bg_color = pg.Color( config['cell']['color']['default_a'] )
                    border_color = pg.Color( config['cell']['border']['color_a'] )
                else:
                    bg_color = pg.Color( config['cell']['color']['default_b'] )
                    border_color = pg.Color( config['cell']['border']['color_b'] )

                # calculate x,y of the cell
                x = config['window']['board']['origin_x'] + (col * config['cell']['size'])
                y = config['window']['board']['origin_y'] + (row * config['cell']['size'])
                
                # create the cell
                self.__board[row][col] = Cell(bg_color, border_color, x, y) 
                
                # add the cell to the queue to be updated
                self.__update_queue.put(self.__board[row][col])

                i+=1
            j+=1

    def manually_set_cell(self, row, col, character):
        """ Manually sets the cell at the specified position to the character
            specified. Use this iteratively to create an initial game board.
            Note that this also automatically sets the cell to be read-only.
        """ 
        if config['game']['ignore_caps']:
            character = character.upper()
        self.__board[row][col].set_char(character)
        self.__board[row][col].set_editable(False)

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
            self.__clock.tick(config['window']['framerate'])    

    def __draw_solution(self):
        """ draw the solution/hint """
        y = config['window']['solution']['origin_y']
        x = config['window']['solution']['origin_x']
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
                if config['game']['ignore_caps']:
                    # set both to uppercase, that way caps doesn't affect it
                    ch = grapheme.get_grapheme().upper()
                    keyname = pg.key.name(key).upper()
                else:
                    ch = grapheme.get_grapheme()
                    keyname = pg.key.name(key)
                    # handle shift or capslock
                    if pg.key.get_mods() & pg.KMOD_LSHIFT or \
                       pg.key.get_mods() & pg.KMOD_RSHIFT or \
                       pg.key.get_mods() & pg.KMOD_CAPS:
                       keyname = keyname.upper()

                if keyname == ch:
                    self.__key_pressed_str = keyname

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

                # otherwise, if it's hovered over...
                elif cell.check_collides(self.__mouse_pos):
                    self.__handle_cell_hovered(cell)

                else:
                    if cell is not self.__clicked_cell and \
                        cell.get_color() not in (pg.Color( config['cell']['color']['default_a'] ),
                                                 pg.Color( config['cell']['color']['default_b'] ),                                                
                                                 pg.Color( config['cell']['color']['valid'] )
                                                 ):
                        # cell.reset_color()
                        cell.change_color()
                        self.__update_queue.put(cell)

    def __handle_cell_clicked(self, cell):
        """ Carry out the changes for when a specified cell has been clicked on """
        # only one cell can be selected at once, so the variable __clicked_cell 
        # keeps track of which is currently selected. 

        self.__update_queue.put(cell)

        if cell is not self.__clicked_cell:
            cell.click()
            # unclick the old cell, then click the new one.
            if self.__clicked_cell:
                self.__clicked_cell.change_color()
                self.__update_queue.put(self.__clicked_cell)
                self.__clicked_cell.unclick()
            self.__clicked_cell = cell

        if self.__key_pressed_str:
            if self.__check_valid_input(cell, self.__key_pressed_str):
                # if the move is valid, set its character to what the player entered
                cell.set_char(self.__key_pressed_str)
       
        elif self.__delete_char:    
            # otherwise, if del/backspace was pressed, empty the cell
            cell.set_char(None)

    def __handle_cell_hovered(self, cell):
        """ Carry out the changes for when a specified cell is hovered over """
        self.__update_queue.put(cell)
        cell.change_color(pg.Color( config['cell']['color']['hovered'] ))
      
### Sudoku Game Logic: ###

    def __check_valid_input(self, cell, input_char):
        """ checks if the inputted character is valid (i.e. no duplicates in
            its row/column/subgrid), and returns True if valid, False if not.
        """
        # If you want it so that the cell must be cleared before 
        # writing to it, add "if not cell.get_char()..."
       
        # a variable is used to store the return value so that it checks all
        # cells. This is only useful since checking also sets the color of 
        # invalid cells. 
        output = True

        # get row and column of the cell
        row, col = self.__get_cell_row_col(cell)

        # check if the character exists in the cell's row/column.
        if (self.__char_is_in_segment(self.__board[row][:], input_char) or \
            self.__char_is_in_segment(self.__board[:][col], input_char)):
            output = False        

        # check if the character exists in the cell's subgrid.
        # A cell's subgrid index (its top-left corner cell) is defined by:
        # subgrid_index = cell_index - (cell_index % 3)
        row_sg = row - (row % self.__subgrid_size)
        col_sg = col - (col % self.__subgrid_size)        
        if self.__char_is_in_subgrid(row_sg, col_sg, self.__subgrid_size, input_char):
            output = False

        return output
        
    def __char_is_in_segment(self, cell_list, check_char):
        """ Checks if the check_char is in a row/column. """
        output = False
        for cell in cell_list:
            if cell.get_char() == check_char:
                ## CHANGE THIS TO MODIFY INVALID CELL COLORING SETTINGS ##  
                cell.set_invalid()
                # cell.change_color(CELL_COLOR_INVALID)
                self.__update_queue.put(cell)
                
                output = True
        return output

    def __char_is_in_subgrid(self, row, col, edge, check_char):
        """ creates a segment from the subgrid, then calls 
            self.__char_is_in_segment() to check this segment. 
            A subgrid is represented by its top-left cell 
            and its edge length.
        """
        subgrid = []
        for i in range(edge):
            for j in range(edge):
                subgrid.append(self.__board[row+i][col+j])
        return self.__char_is_in_segment(subgrid, check_char)
    
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
            cell.change_color(pg.Color( config['cell']['color']['valid'] ))
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

    def __get_cell_row_col(self, cell):
        """ Finds and returns a tuple of the cell's (row, col) indices.
            If not found, returns (-1, -1).
        """
        for row in range(self.__board_size):
            for col in range(self.__board_size):
                if self.__board[row][col] == cell:
                    return (row, col)
        return (-1, -1)
         
class Cell:
    """ Objects represent a cell of the game board. Cells can be either empty
        or filled with an object of class Grapheme. """
    
    INVALID_TIMER = 100     # time (ms) for which the cell is highlighted red

    @classmethod
    def set_window(cls, window_from_parent):
        cls.window = window_from_parent
        Grapheme.set_window(window_from_parent)

    def __init__(self, bg_color, border_color, x, y):
        # x and y correspond to the pixel of the top-left corner of the cell.
        # I actually don't need self.__x or sel.__y, but methods still use it
        self.__x = x
        self.__y = y
        self.__size = config['cell']['size']
        self.__rect = pg.Rect((self.__x, self.__y), 
                              (self.__size, self.__size))

        self.__border_color = border_color
        self.__bg_color = bg_color
        self.__color = bg_color

        self.__char = Grapheme(None)
        self.__is_clicked = False
        self.__is_editable = True
        self.__set_invalid_at_ms = 0     # time at which the cell was set invalid

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
        surface.fill(self.__color, 
                     self.__rect.inflate(-config['cell']['border']['width'] * 2, 
                                         -config['cell']['border']['width'] * 2))

    def change_color(self, color=None):
        """ Changes the background color of the cell.
            Expects the argument color to be a pygame-compatible string or RGB.
            If called without an argument, it will reset it to the background
            color.     
            If the cell is currently invalid, it will ignore the color change 
            until it is no longer invalid. 
        """
        if self.__check_invalid():
            # currently invalid, so don't change its color
            return
        if color:
            # handle both color name strings and pygame.Color objects
            if isinstance(color, pg.Color):
                self.__color = color
            elif isinstance(color, str):
                self.__color = pg.Color(color)
        else:
            self.__color = self.__bg_color

    def set_invalid(self):
        """ set the cell to its invalid state. """
        self.__set_invalid_at_ms = time.time()*1000.0
        self.__color = pg.Color( config['cell']['color']['invalid'] )

    def __check_invalid(self):
        """ check if the cell is in the invalid state """
        if (self.__set_invalid_at_ms + Cell.INVALID_TIMER) > (time.time()*1000.0):
            return True
        return False

    def get_color(self):
        """ Returns the cell's current pygame.Color object """
        return self.__color

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
            self.change_color(pg.Color( config['cell']['color']['clicked'] )) 

    def unclick(self):
        """ unclicks the cell, changing its colour back """
        # Note: is_clicked currently does nothing, just acts as a flag
        self.__is_clicked = False
        self.change_color()

    def set_editable(self, flag):
        """ set the cell to be editable or read-only. This is used to keep the 
            starting grid from being modified.
        """
        assert isinstance(flag, bool), "variable must be a boolean"
        self.__is_editable = flag



# For debugging only, since the class is only supposed to be called from main.py
if __name__ == "__main__":
    
    # test_board = [['8','7','6','9','','','','',''],
    #               ['','1','','','','6','','',''],
    #               ['','4','','','','5','8','',''],
    #               ['4','','','','','','2','1',''],
    #               ['','9','','5','','','','',''],
    #               ['','5','','','4','','3','','6'],
    #               ['','2','9','','','','','','8'],
    #               ['','','4','6','9','','1','7','3'],
    #               ['','','','','','1','','','4']
    #               ]
    test_board = [['H','G','F','I','','','','',''],
                  ['','A','','','','F','','',''],
                  ['','D','','','','E','H','',''],
                  ['D','','','','','','B','A',''],
                  ['','I','','E','','','','',''],
                  ['','E','','','D','','C','','F'],
                  ['','B','I','','','','','','H'],
                  ['','','D','F','I','','A','G','C'],
                  ['','','','','','A','','','D']
                  ]

    test_window = Window("Test Sudoku", 500, 500)
    test_window.set_auto_update(False)
    # test_game = Sudoku(test_window, 3, '123456789')
    test_game = Sudoku(test_window, 3, 'ABCDEFGHI')

    # generate the test board
    for row in range(len(test_board)):
        for col in range(len(test_board[row])):
            if test_board[row][col]:
                test_game.manually_set_cell(row, col, test_board[row][col])

    test_game.play()
    pg.quit()
