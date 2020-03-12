# Synesthetic-Sudoku
A library for training artificially-induced pseudo-synesthesia using Sudoku puzzles.


## main.py
Calls Sudoku, timing, etc., to run an entire procedure. 

## sudoku.py
Contains all the code required to handle the display, manipulation, and game logic for the sudoku board. 
An object of class Sudoku is created with the arguments: 
  ### window
  - a uagame.Window object that represents the game window.
  ### subgrid_size
  - an integer representing the size of each subgrid on the board (3 for a normal 9x9 Sudoku board).
  ### solution
  - the string which must appear in each column, row, and subgrid for the Sudoku board to be solved.
  - for normal sudoku, this is "123456789".

## grapheme.py


## uagame.py
A module of basic methods to streamline and simplify the creation and management of basic graphical games using PyGame. 
