# python-tictactoe
[![PyPI version](https://badge.fury.io/py/python-tictactoe.svg)](https://badge.fury.io/py/python-tictactoe) [![Tests](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/tests.yml/badge.svg)](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/tests.yml) [![Build](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/build.yml/badge.svg)](https://github.com/AttackingOrDefending/python-tictactoe/actions/workflows/build.yml)

python-tictactoe is a tic-tac-toe library that supports different sizes and dimensions and how many marks in a row to win.

## Features

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
