# Nightmare Minesweeper

A new game based on the original Minesweeper, but with some additions to increase the difficulty. The main difference is that periodically, the entire game board is recreated from scratch, meaning that the player has to identify the positions of mines quickly, before they move. 

To make the game actually playable, some things are preserved when the game board is recreated. Those things are:

1. The cells that the player has clicked on
2. The mines that have been correctly marked by the player

When the game board is recreated, no mines are generated on cells where the player has clicked previously. Additionally, mines that have been correctly marked by the player keep their position. Once the game board has been recreated, the game simulates click events on all cells that the player has clicked previously. Since these cells do not contain any mines, this will not lead to game over.

Another difference from regular minesweeper is that if a cell is incorrectly marked as a mine, the game is over. 

## Controls

The only controls used for the game are left and right click. Left click reveals all cells around the clicked cells similar to regular minesweeper. Right click marks a cell as containing a mine, and locks the position of that mine for the rest of the game. 

## Changing the difficulty

Right now, the method for changing the difficulty is quite rudimentary. There are three factors that change the difficulty of the game:

1. The size of the game board. This can be changed by altering the values of `xdim` and `ydim` when creating the Minesweeper object:
    
    `game = MineSweeper(xdim = 25, ydim = 25, n_mines = 20)`

2. The number of mines. This can be changed by altering the valus of `n_mines` on the row mentioned above. 
3. The time between board regenerations. This can be altered by changing the values of `self.slowest_refresh` and `self.fastest_refresh` within the constructor of the `Minesweeper` class. `self.slowest_refresh` corresponds to the initial refresh time. As mines are marked on the game board, the refresh time linearly approaches `self.fastest_refresh`, making the game more difficult as it progresses. 

## Example recreation

<p align="center">
	<img src="/examples/example.gif" width="60%" />
</p>

Here we can see how the game board is recreated, while preserving the locations of the correctly marked mines. The cells that have been clicked are marked with a white `x` in the bottom left corner. 

## Installation

To get everything running, first create your `virtualenv`:

    python3 -m venv .venv
    
and activate it:

    source .venv/bin/activate
    
Then install all required packages:

    pip3 install -r requirements.txt
    
Now you're good to go! To play the game, use:

    python3 minesweeper.py
