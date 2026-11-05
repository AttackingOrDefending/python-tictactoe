# User guide

## Creating a board

A {class}`~tictactoe.Board` takes the size of the board along each axis and how many marks in a row are needed to win.
The defaults give the classic 3x3 game with 3 in a row.

```python
from tictactoe import Board

classic = Board()
wide = Board(dimensions=(4, 5), x_in_a_row=4)
cube = Board(dimensions=(4, 4, 4), x_in_a_row=4)
hypercube = Board(dimensions=(6, 2, 5, 8), x_in_a_row=3)
```

A line can run along any axis or along any diagonal, including diagonals that cross several axes at once.

## Playing moves

{meth}`~tictactoe.Board.push` plays a move for the player whose turn it is. X always moves first. A move is the
coordinates of a cell, starting from 0.

```python
from tictactoe import O, X, Board

board = Board()
board.push((1, 1))  # X
board.push((0, 0))  # O
assert board.turn == X
assert board.get_mark_at_position((0, 0)) == O
assert board.is_empty((2, 2))
```

Pushing a move on a cell that is taken, or that is not on the board, raises a {class}`ValueError`.

{meth}`~tictactoe.Board.possible_moves` returns the coordinates of every empty cell as a NumPy array, one cell per row.
Each row can be passed straight to `push`, so a random game is only a few lines:

```python
import random

from tictactoe import Board

board = Board(dimensions=(5, 5), x_in_a_row=4)
while board.result() is None:
    moves = board.possible_moves()
    board.push(random.choice(moves))
print(board)
```

## Results

{meth}`~tictactoe.Board.result` returns:

- {data}`tictactoe.X` (1) or {data}`tictactoe.O` (2) if that player has won,
- `0` for a draw (the board is full and nobody has won),
- `None` if the game is not over.

{meth}`~tictactoe.Board.has_won` checks a single player.

```python
from tictactoe import X, Board

board = Board()
for move in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
    board.push(move)
assert board.has_won(X)
assert board.result() == X
```

## Drawing the board

Printing a board draws it. The first coordinate is the column and the second is the row:

```python
from tictactoe import Board

board = Board()
board.push((0, 0))
board.push((2, 1))
print(board)
```

```text
 X |   |   
-----------
   |   | O 
-----------
   |   |   
```

Boards with more dimensions are drawn as a stack of 2D slices, with more dividing lines between slices of higher
dimensions:

```python
from tictactoe import Board

board = Board(dimensions=(2, 2, 2), x_in_a_row=2)
board.push((0, 0, 0))
board.push((0, 1, 0))
board.push((1, 1, 1))
print(board)
```

```text
 X |   
-------
 O |   
-------
-------
   |   
-------
   | X 
```

## Copying and inspecting

{meth}`~tictactoe.Board.copy` returns an independent copy, which is handy for trying out moves in a search:

```python
from tictactoe import Board

board = Board()
board.push((1, 1))
trial = board.copy()
trial.push((0, 0))
assert board.is_empty((0, 0))
```

The cells are in {attr}`Board.board <tictactoe.Board>`, a NumPy array of shape `dimensions` with `0` for empty
cells, `1` for X and `2` for O. The move history is in `board.moves`, and the moves of each player in `board.x` and
`board.o`.

## Moves as strings

A {class}`~tictactoe.Move` converts between coordinates and a short string form, such as for saving or for user input:

```python
from tictactoe import Move

assert Move((1, 2)).str_move == "1-2"
assert Move(str_move="1-2").coordinate_move == (1, 2)
```
