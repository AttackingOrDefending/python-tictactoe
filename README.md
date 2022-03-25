# python-tictactoe
[![PyPI version](https://badge.fury.io/py/python-tictactoe.svg)](https://badge.fury.io/py/python-tictactoe) [![Tests](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/tests.yml/badge.svg)](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/tests.yml) [![Build](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/build.yml/badge.svg)](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/build.yml) [![codecov](https://codecov.io/gh/AttackingOrDefending/python-tictactoe/branch/main/graph/badge.svg?token=7N5LHRA3OC)](https://codecov.io/gh/AttackingOrDefending/python-tictactoe)

A tic-tac-toe library that supports different sizes and dimensions and how many marks in a row to win.

Installing
----------

Download and install the latest release:

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

## License
python-tictactoe is licensed under the MIT License. Check out LICENSE for the full text.
