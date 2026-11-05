# python-tictactoe
[![PyPI version](https://badge.fury.io/py/python-tictactoe.svg)](https://badge.fury.io/py/python-tictactoe)
[![Tests](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/tests.yml/badge.svg)](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/tests.yml)
[![Build](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/build.yml/badge.svg)](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/build.yml)
[![Mypy](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/mypy.yml/badge.svg)](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/mypy.yml)
[![Read the Docs](https://img.shields.io/readthedocs/python-tictactoe)](https://python-tictactoe.readthedocs.io/en/latest/)
[![codecov](https://codecov.io/gh/AttackingOrDefending/python-tictactoe/branch/main/graph/badge.svg?token=7N5LHRA3OC)](https://codecov.io/gh/AttackingOrDefending/python-tictactoe)

A tic-tac-toe library that supports different sizes and dimensions and how many marks in a row to win.

**Documentation:** <https://python-tictactoe.readthedocs.io/>

Installing
----------

Download and install the latest release (Python 3.11 or newer):

    pip install python-tictactoe

## Features

* Includes mypy typings.

* Different board sizes
```python
from tictactoe import Board

board = Board(dimensions=(4, 5))
```
* More than 2 dimensions
```python
from tictactoe import Board

board = Board(dimensions=(6, 2, 5, 8))
```
* More than 3 in a row to win
```python
from tictactoe import Board

board = Board(dimensions=(10, 10, 10), x_in_a_row=8)
```
* Play moves and get the result
```python
from tictactoe import Board

board = Board()
for move in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
    board.push(move)
print(board.result())  # 1, because X has won. 2 means O won, 0 a draw and None that the game is not over.
```
* See the board
```python
from tictactoe import Board

board = Board(dimensions=(2, 2, 2), x_in_a_row=2)
board.push((0, 0, 0))
board.push((0, 1, 0))
print(board)

"""
 X |   
-------
 O |   
-------
-------
   |   
-------
   |   
"""
```
* Endgame tablebases: the perfect-play result and the best moves of every position, for boards with up to 16 cells
```python
from tictactoe import Board
from tictactoe.egtb import Tablebase

tablebase = Tablebase((3, 3), 3)
board = Board((3, 3), 3)
board.push((0, 0))
board.push((0, 1))
print(tablebase.result(board))  # 1: X wins with perfect play.
print(tablebase.best_moves(board))  # The moves that keep the win.

tablebase.save("3x3.npz")
tablebase = Tablebase.load("3x3.npz")
```

## Development

Install the package with its development tools (needs pip 25.1 or newer), then run the tests, linters and docs build:

    pip install -e . --group dev
    pytest
    ruff check . && ruff format --check .
    mypy
    sphinx-build -W -b html docs docs/_build/html

## License
python-tictactoe is licensed under the MIT License. Check out LICENSE for the full text.
