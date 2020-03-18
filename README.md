# Syndoku -- Synesthetic Sudoku
A library for training artificially-induced pseudo-synesthesia using Sudoku puzzles.


## Module Breakdown
### main.py
Calls Sudoku, timing, etc., to run an entire procedure. 
From here, the starting board is also created.

### sudoku.py
Contains all the code required to handle the display, manipulation, and game logic for the sudoku board. 
An object of class Sudoku is created with the arguments: 
 - ***window***
  	- a uagame.Window object that represents the game window.
 - ***subgrid_size***
	- an integer representing the size of each subgrid on the board (3 for a normal 9x9 Sudoku board).
 - ***solution***
	- the string which must appear in each column, row, and subgrid for the Sudoku board to be solved.
  	- for normal sudoku, this would be "123456789".
	- this string is also used to determine the board size.
the Sudoku class includes the following methods:.
- **manually_set_cell(_row_, _col_, _character_)**	
	- Manually sets the cell at the specified position to the specified character. This also makes the cell uneditable.
	- This method is used to create the starting game board.
	- _row_ and _col_ must be integers, and _character_ must be a single-character string.
- **play()**
	- Handles the entire game loop.
	- Once called, the game will run until it is either complete or the player exits.
### grapheme.py


### uagame.py
A module of basic methods to streamline and simplify the creation and management of basic graphical games using PyGame. 
