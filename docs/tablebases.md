# Tablebases

A {class}`~tictactoe.egtb.Tablebase` knows who wins every position of a board if both players play perfectly. It
solves the whole game once, then answers any position instantly.

```python
from tictactoe import Board
from tictactoe.egtb import Tablebase

tablebase = Tablebase(dimensions=(3, 3), x_in_a_row=3)

board = Board((3, 3), 3)
print(tablebase.result(board))  # 0: tic-tac-toe is a draw.

board.push((0, 0))
board.push((0, 1))
print(tablebase.result(board))  # 1: after this mistake by O, X wins.
print(tablebase.best_moves(board))  # The moves that keep the win for X.
```

{meth}`~tictactoe.egtb.Tablebase.result` uses the same values as {meth}`Board.result <tictactoe.Board.result>`:
`1` (X wins), `2` (O wins) or `0` (draw). For a finished game it is how the game ended.

## A perfect player

{meth}`~tictactoe.egtb.Tablebase.best_moves` returns every move that keeps the best result for the player to move, so
picking any of them is perfect play:

```python
import random

from tictactoe import Board
from tictactoe.egtb import Tablebase

tablebase = Tablebase((4, 3), 3)
board = Board((4, 3), 3)
while board.result() is None:
    board.push(random.choice(tablebase.best_moves(board)))
print(board.result())  # Always 1: X wins 4x3 with 3 in a row.
```

## Saving and loading

Small tablebases take milliseconds to solve, but bigger ones take seconds, so they can be saved to a compressed file:

```python
from tictactoe.egtb import Tablebase

Tablebase((4, 3), 3).save("4x3.npz")
tablebase = Tablebase.load("4x3.npz")
```

## Size limits

A tablebase holds one byte for each of the `3 ** cells` ways to fill the board, so the cost triples with every cell.
Boards with more than {data}`~tictactoe.egtb.MAX_CELLS` (16) cells are refused.

| Board            | Cells | Table size | Time to solve |
|------------------|------:|-----------:|--------------:|
| 3x3, 3 in a row  |     9 |      20 KB |          ~5 ms |
| 4x3, 3 in a row  |    12 |     531 KB |         ~30 ms |
| 5x3, 3 in a row  |    15 |      14 MB |           ~1 s |
| 4x4, 4 in a row  |    16 |      43 MB |           ~4 s |

Solving a 4x4 board uses about 220 MB of memory at its peak.

## How it works

Every position gets a code: its cells (`0` empty, `1` X, `2` O, in the order of `board.board.ravel()`) read as the
digits of a base 3 number. The table is a NumPy array indexed by that code.

The solver works backwards from the full board (retrograde analysis). It handles all positions with the same number of
marks at once: first it finds the positions where someone has already won or the board is full, then for the rest it
looks up the result after every possible move, which has one more mark and so is already solved, and keeps the best
one for the player to move. Only positions in which X has made as many moves as O, or one more, are solved; any other
position is `0` in the table.
