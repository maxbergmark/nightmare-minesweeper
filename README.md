# Nightmare Minesweeper

A new game based on the original Minesweeper, but with some additions to increase the difficulty. The main difference is that periodically, the entire game board is recreated from scratch, meaning that the player has to identify the positions of bombs quickly, before they move. 

To make the game actually playable, some things are preserved when the game board is recreated. Those things are:

1. The cells that the player has clicked on
2. The bombs that have been correctly marked by the player

When the game board is recreated, no bombs are generated on cells where the player has clicked previously. Additionally, bombs that have been correctly marked by the player keep their position. Once the game board has been recreated, the game simulates click events on all cells that the player has clicked previously. Since these cells do not contain any bombs, this will not lead to game over.

## Example recreation

TODO

## Installation

To get everything running, first create your `virtualenv`:

    python3 -m venv .venv
    
and activate it:

    source .venv/bin/activate
    
Then install all required packages:

    pip3 install -r requirements.txt
    
Now you're good to go! To play the game, use:

    python3 minesweeper.py
