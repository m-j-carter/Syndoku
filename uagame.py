
## A module to streamline some simple graphical operations within PyGame ##

# Notes/Changelog:
#   - now supports window.get_font_name() (3/2/2020)


from pygame import init, quit, Color, Surface, Rect, KEYUP, K_SPACE, K_RETURN, K_z, K_LSHIFT, K_RSHIFT, K_CAPSLOCK, K_BACKSPACE
from pygame.display import set_caption, set_mode, update
from pygame.font import SysFont, Font
from pygame.event import poll
from pygame.key import get_pressed, name

class Window:
    # A Window represents a display window with a title bar,
    # close box and interior drawing surface.

    def __init__(self, title, width, height):
        # Create and open a window to draw in.
        # - self is the new Window
        # - title is the str title of the window
        # - width is the int pixel width of the window
        # - height is the int pixel height of the window
        init()
        self.__surface__ = set_mode((width, height), 0, 0)
        set_caption(title)
        self.__font_name__ = ''
        self.__font_size__ = 18
        self.__font__ = SysFont(self.__font_name__, self.__font_size__, True)
        self.__font_color__ = 'white'
        self.__bg_color__ = 'black'
        self.__auto_update__ = True

    def close(self):
        # Close the window
        quit()

    def set_font(self, font):
        """ set the font to the pygame.Font object specified """
        # assert isinstance(font, SysFont)
        self.__font = font
        self.__font_name = ""       # I don't know how to get font name from font...


    def set_font_name(self, name):
        # Set the name of the window font used to draw strings
        # - name is the str name of the font
        self.__font_name__ = name
        self.__font__ = SysFont(self.__font_name__, self.__font_size__, True)

    def get_font(self):
        """ gets and returns the pygame.Font object of the active font. """
        return self.__font__

    def get_font_name(self):
        # gets and returns the string name of the active font.
        return self.__font_name__

    def set_font_size(self, point_size):
        # Set the point size of the window font used to draw strings
        # - point_size is the int point size of the font        
        self.__font_size__ = point_size
        self.__font__ = SysFont(self.__font_name__, self.__font_size__, True)

    def set_font_color(self, given_color):
        # Set the font color used to draw in the window.
        # Will accept colors as either a tuple of RGB values, 
        # pygame-compatible color names as strings, or pygame.color() objects.
        if type(given_color) == Color:
            self.__font_color__ = given_color
            return
        self.__font_color__ = Color(given_color)
    
    def set_bg_color(self, given_color):
        # Set the background color used to draw in the window.
        # Will accept colors as either a tuple of RGB values, 
        # pygame-compatible color names as strings, or pygame.color() objects.
        if type(given_color) == Color:
            self.__bg_color__ = given_color
            return
        self.__bg_color__ = Color(given_color)

    def set_auto_update(self, true_false):
        # Set the background color used to draw in the window
        # - true_or_false is a Boolean indicating if auto update should be on or off
        self.__auto_update__ = true_false
     
    def get_font_height(self):
        # Return the int pixel height of the current font.
        return self.__font__.size('')[1]

    def get_font_color(self):
        # Returns the pygame.Color object for the font.
        return self.__font_color__

    def get_bg_color(self):
        # Returns the pygame.Color object for the background.
        return self.__bg_color__

    def get_width(self):
        """ Return the int pixel width of the window's drawable
            interior surface.
        """
        return self.__surface__.get_width()

    def get_height(self):
        """ Return the int pixel height of the window's drawable
            interior surface.
        """
        return self.__surface__.get_height()

    def clear(self):
        """ Erase the window contents """
        self.__surface__.fill(self.__bg_color__)
        if self.__auto_update__:
            update()
     
    def get_surface(self):
        """ Return the Pygame.Surface object that represents the
            interior drawing surface of the window.
        """
        return self.__surface__

    def draw_string(self, string, x, y):
        """ Draw a string in the window using the current font and
            colors.
            - string is the str object to draw
            - x is the int x coord of the upper left corner of the
            string in the window
            - y is the int y coord of the upper left corner of the
            string in the window
        """
        # text_image = self.__font__.render(string, True, Color(self.__font_color__), Color(self.__bg_color__))
        text_image = self.__font__.render(string, True, self.__font_color__, self.__bg_color__)
        self.__surface__.blit(text_image, (x, y))
        if self.__auto_update__:
            text_rect = Rect((x, y), text_image.get_size())
            update(text_rect)

    def input_string(self, prompt, x, y):
        """ Draw a prompt string in the window using the current font
            and colors. Check keys pressed by the user until an enter
            key is pressed and return the sequence of key presses as a
            str object.
            - self is the Window
            - prompt is the str to display
            - x is the int x coord of the upper left corner of the
            string in the window
            - y is the int y coord of the upper left corner of the
            string in the window
        """
        key = K_SPACE
        answer = ''
        while key != K_RETURN:
            self.draw_string(prompt + answer + '    ', x, y)
            if not self.__auto_update__:
                update()
            key = self._get_key()
            key_state = get_pressed()
            if (K_SPACE <= key <= K_z):
                if key == K_SPACE:
                    letter = ' '
                else:
                    letter = name(key)
                if key_state[K_LSHIFT] or key_state[K_RSHIFT] or key_state[K_CAPSLOCK]:
                    letter = letter.upper()
                answer = answer + letter
            if key == K_BACKSPACE:
                answer = answer[0:len(answer)-1]
        return answer

    def get_string_width(self, string):
        """ Return the int pixel width of the string using the current
            font.
            - self is the Window
            - string is the str object
        """
        return self.__font__.size(string)[0]
     
    def update(self):
        """ Update the window by copying all drawn objects from the
            frame buffer to the display.
            - self is the Window
        """
        update()

    def _get_key(self):
        # Poll the events until the user presses a key and return it.
        # Discard all other events.
        # - self is the Window
    
        event = poll()
        while event.type != KEYUP:
            event = poll()
        return event.key
        
def _test():
    # To test the code in this module remove the # from
    # the #_test line below. Don't forget to put the #
    # back before saving the module for production use.
    # When testing try the backspace key.

    window_width = 500
    window_height = 400
    title = 'Window Title'
    window = Window(title, window_width, window_height)
    string = window.input_string('Enter text >', 0, 0)
    window.clear()
    surface = window.get_surface()
    width = window.get_width()
    height = window.get_height()
    s_width = surface.get_width()
    s_height = surface.get_height()
    if width == s_width == window_width:
        window.draw_string(str(width), 0, 0)
    else:
        window.draw_string('width error', 0, 0)
    if height == s_height == window_height:
        window.draw_string(str(height), width // 2, height // 2)
    else:
        window.draw_string('height error', width // 2, height // 2)   
    height = window.get_font_height()
    width = window.get_string_width(string)
    window.draw_string(string, 0, height)
    window.draw_string(string, width, height)
    window.update()
    window.set_font_name('couriernew')
    window.set_font_size(24)
    window.set_font_color('yellow')
    window.set_bg_color('blue')
    font_color = window.get_font_color()
    bg_color = window.get_bg_color()
    window.draw_string(font_color, 200, 200)       
    window.draw_string(bg_color, 300, 300)
    height = window.get_font_height()
    window.input_string('press any key to close window', 0, window_height - height)
    window.close()
    
#_test()