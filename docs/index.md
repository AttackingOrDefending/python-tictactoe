# python-tictactoe

A tic-tac-toe library that supports boards of any size and number of dimensions, and any number of marks in a row to
win. The board is a [NumPy](https://numpy.org) array, so it is easy to inspect, and checking for a win is vectorized,
so it stays fast on big boards.

```python
from tictactoe import Board

board = Board(dimensions=(3, 3), x_in_a_row=3)
board.push((1, 1))
board.push((0, 0))
print(board)
print(board.result())  # None: the game is not over yet.
```

## Installation

python-tictactoe needs Python 3.11 or newer.

```bash
pip install python-tictactoe
```

## Features

- Boards of any size: `Board(dimensions=(4, 5))`.
- Boards with more than two dimensions: `Board(dimensions=(6, 2, 5, 8))`.
- Any number of marks in a row to win: `Board(dimensions=(10, 10, 10), x_in_a_row=8)`.
- A text drawing of the board, in any number of dimensions.
- {doc}`Tablebases <tablebases>` that know the perfect-play result and the best moves of every position of a small
  board.
- Type hints, checked with `mypy --strict`.

```{toctree}
:maxdepth: 2
:hidden:

usage
tablebases
api
changelog
```

## Contents

- {doc}`usage`: boards, moves, results and drawing.
- {doc}`tablebases`: solving small boards completely.
- {doc}`api`: every class and function.
- {doc}`changelog`: what changed in each version.
