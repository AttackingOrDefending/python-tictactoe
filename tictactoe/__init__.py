"""A tic-tac-toe library for boards of any size and number of dimensions, with any number of marks in a row to win.

Example:
    >>> from tictactoe import Board, X
    >>> board = Board(dimensions=(3, 3), x_in_a_row=3)
    >>> for move in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
    ...     board.push(move)
    >>> board.result() == X
    True
"""

from __future__ import annotations

import functools
import math
from collections.abc import Iterable
from typing import Self

import numpy as np
import numpy.typing as npt

__all__ = ["Board", "Move", "O", "X"]

__author__ = "Ioannis Pantidis"
__copyright__ = "2022-2026, " + __author__
__version__ = "0.1.0"

X = 1
"""The mark of the first player. Also returned by :meth:`Board.result` when X has won."""
O = 2  # noqa: E741
"""The mark of the second player. Also returned by :meth:`Board.result` when O has won."""

_SYMBOLS = np.array([" ", "X", "O"])


@functools.cache
def _directions(ndim: int) -> npt.NDArray[np.intp]:
    """Get one direction vector for every kind of line on a board with `ndim` dimensions.

    A direction and its opposite describe the same lines, so only the vectors whose first non-zero entry is +1 are kept.
    """
    # Every vector in {-1, 0, 1}^ndim, in lexicographic order with 1 < 0 < -1. The first half is
    # exactly the vectors that start with +1 (after any zeros), the middle row is all zeros and
    # the second half mirrors the first.
    vectors = 1 - np.indices((3,) * ndim).reshape(ndim, -1).T
    directions = vectors[: len(vectors) // 2]
    directions.flags.writeable = False
    return directions


@functools.cache
def _winning_lines(dimensions: tuple[int, ...], x_in_a_row: int) -> npt.NDArray[np.intp]:
    """Get every line of `x_in_a_row` cells on a board, as indices into ``board.ravel()``.

    Returns:
        A read-only array of shape ``(number_of_lines, x_in_a_row)``. It is cached, so every board with the same
        dimensions and `x_in_a_row` shares it.
    """
    cells = np.arange(math.prod(dimensions)).reshape(dimensions)
    if x_in_a_row == 1:
        lines = cells.reshape(-1, 1)  # Every cell is a line on its own, whatever the direction.
    else:
        # How far one step along each axis moves through board.ravel().
        strides = np.array(cells.strides) // cells.itemsize
        reach = x_in_a_row - 1
        # One direction at a time, so memory use stays close to the size of the result even with many dimensions.
        lines_by_direction = []
        for direction in _directions(len(dimensions)):
            # A line can start on any cell that is far enough from the edges it heads towards to fit on the board.
            starts = cells[
                tuple(
                    slice(0, max(size - reach, 0)) if step > 0 else slice(reach, None) if step < 0 else slice(None)
                    for size, step in zip(dimensions, direction, strict=True)
                )
            ]
            lines_by_direction.append(starts.reshape(-1, 1) + (direction @ strides) * np.arange(x_in_a_row))
        lines = np.concatenate(lines_by_direction)
    lines.flags.writeable = False
    return lines


class Board:
    """A tic-tac-toe board of any size and number of dimensions.

    The cells live in :attr:`board`, a NumPy array of shape :attr:`dimensions` that holds ``0`` for an empty cell,
    :data:`X` or :data:`O`. X always moves first.

    Attributes:
        dimensions: The size of the board along each axis, e.g. ``(3, 3)``.
        x_in_a_row: How many marks in a row are needed to win.
        board: The cells of the board.
        turn: The player to move next, :data:`X` or :data:`O`.
        move_count: How many moves have been pushed.
        moves: Every pushed move, in order.
        x: The moves made by X, in order.
        o: The moves made by O, in order.
    """

    def __init__(self, dimensions: Iterable[int] = (3, 3), x_in_a_row: int = 3) -> None:
        """Create an empty board.

        Args:
            dimensions: The size of the board along each axis. Use more than two numbers for a board with more than
                two dimensions, e.g. ``(4, 4, 4)``.
            x_in_a_row: How many marks in a row are needed to win.

        Raises:
            ValueError: If `x_in_a_row` is smaller than 1.
        """
        if x_in_a_row < 1:
            raise ValueError(f"x_in_a_row must be at least 1, not {x_in_a_row}.")
        self.dimensions = tuple(int(size) for size in dimensions)
        self.x_in_a_row = int(x_in_a_row)
        self.board = self.create_board()
        self.turn = X
        self.move_count = 0
        self.moves: list[Move] = []
        self.x: list[Move] = []
        self.o: list[Move] = []
        self._lines = _winning_lines(self.dimensions, self.x_in_a_row)

    def create_board(self) -> npt.NDArray[np.int8]:
        """Create an empty board state.

        Returns:
            An array of shape :attr:`dimensions` filled with zeros.
        """
        return np.zeros(self.dimensions, dtype=np.int8)

    def copy(self) -> Self:
        """Get an independent copy of the board, including the turn and the move history.

        Returns:
            A copy of the board.
        """
        board = self.__class__.__new__(self.__class__)
        board.__dict__.update(self.__dict__)
        board.board = self.board.copy()
        board.moves = self.moves.copy()
        board.x = self.x.copy()
        board.o = self.o.copy()
        return board

    def get_mark_at_position(self, position: Iterable[int]) -> int:
        """Get the mark at a position.

        Args:
            position: The coordinates of the cell.

        Returns:
            :data:`X`, :data:`O` or ``0`` if the cell is empty.
        """
        return int(self.board[tuple(position)])

    def set_mark(self, coordinates: Iterable[int], player: int) -> None:
        """Put a mark on a cell, without checking the cell or changing whose turn it is.

        Use :meth:`push` to play a move.

        Args:
            coordinates: The coordinates of the cell.
            player: The mark to put on the cell, :data:`X` or :data:`O`.
        """
        coordinates = tuple(coordinates)
        self.board[coordinates] = player
        if player == X:
            self.x.append(Move(coordinates))
        elif player == O:
            self.o.append(Move(coordinates))

    def is_empty(self, position: Iterable[int]) -> bool:
        """Get whether a cell is empty.

        Args:
            position: The coordinates of the cell.

        Returns:
            Whether the cell has no mark.
        """
        return self.get_mark_at_position(position) == 0

    def push(self, coordinates: Iterable[int]) -> None:
        """Play a move for the player whose turn it is.

        Args:
            coordinates: The coordinates of the cell to put a mark on.

        Raises:
            ValueError: If the cell is not on the board or is not empty.
        """
        position = tuple(int(coordinate) for coordinate in coordinates)
        on_board = len(position) == len(self.dimensions) and all(
            0 <= coordinate < size for coordinate, size in zip(position, self.dimensions, strict=True)
        )
        if not on_board:
            raise ValueError(f"Position {position} is not on a board of size {self.dimensions}.")
        if self.board[position]:
            raise ValueError("Position is not empty.")
        move = Move(position)
        self.board[position] = self.turn
        (self.x if self.turn == X else self.o).append(move)
        self.moves.append(move)
        self.move_count += 1
        self.turn = O if self.turn == X else X

    def find_directions(self) -> npt.NDArray[np.intp]:
        """Get the directions that a line can go in.

        A direction and its opposite describe the same lines, so only one of the two is included.

        Returns:
            A read-only array of shape ``(number_of_directions, len(dimensions))``, one direction vector per row.
        """
        return _directions(len(self.dimensions))

    def possible_moves(self) -> npt.NDArray[np.intp]:
        """Get all the legal moves.

        Returns:
            The coordinates of every empty cell, one cell per row.
        """
        return np.argwhere(self.board == 0)

    def in_bounds(self, pos: Iterable[int] | npt.NDArray[np.integer]) -> bool:
        """Get whether a position is on the board.

        Args:
            pos: The coordinates to check.

        Returns:
            Whether the coordinates point to a cell of the board.
        """
        position = np.asarray(pos)
        return position.shape == (len(self.dimensions),) and bool(((position >= 0) & (position < self.dimensions)).all())

    def out_of_bounds(self, pos: Iterable[int] | npt.NDArray[np.integer]) -> bool:
        """Get whether a position is outside the board.

        Args:
            pos: The coordinates to check.

        Returns:
            Whether the coordinates do not point to a cell of the board.
        """
        return not self.in_bounds(pos)

    def has_won(self, player: int) -> bool:
        """Get whether a player has :attr:`x_in_a_row` marks in a row in any direction.

        Args:
            player: :data:`X` or :data:`O`.

        Returns:
            Whether the player has a complete line.
        """
        return bool((self.board.reshape(-1)[self._lines] == player).all(axis=1).any())

    def result(self) -> int | None:
        """Get the result of the game.

        Returns:
            :data:`X` or :data:`O` if that player has won, ``0`` for a draw (the board is full and nobody has won) or
            ``None`` if the game is not over.

        Raises:
            ValueError: If both players have a complete line, which can't happen in a real game.
        """
        x_won = self.has_won(X)
        o_won = self.has_won(O)
        if x_won and o_won:
            raise ValueError(f"Both X and O have {self.x_in_a_row} pieces in a row.")
        if x_won:
            return X
        if o_won:
            return O
        if self.board.all():
            return 0
        return None

    def __repr__(self) -> str:
        """Draw the board.

        The first coordinate is the column and the second is the row. Boards with more dimensions are drawn as a
        stack of 2D slices, separated by more lines the higher the dimension.

        Returns:
            A drawing of the board.
        """
        return _draw(_SYMBOLS[self.board])


def _draw(symbols: npt.NDArray[np.str_]) -> str:
    """Draw a board (or part of a board) whose cells have been replaced by the symbols to show."""
    if symbols.ndim == 1:
        return "|".join(f" {symbol} " for symbol in symbols)
    divider = ("-" * (4 * symbols.shape[0] - 1) + "\n") * (symbols.ndim - 1)
    return f"\n{divider}".join(_draw(symbols[..., index]) for index in range(symbols.shape[-1]))


class Move:
    """A move, which can be written as coordinates or as a string such as ``"1-2"``.

    Moves are equal when they have the same coordinates.

    Attributes:
        coordinate_move: The coordinates of the move, e.g. ``(1, 2)``.
    """

    __slots__ = ("coordinate_move",)

    def __init__(self, coordinate_move: Iterable[int] | None = None, str_move: str | None = None) -> None:
        """Create a move from coordinates or from a string.

        Args:
            coordinate_move: The coordinates of the move, e.g. ``(1, 2)``.
            str_move: The move as numbers joined by dashes, e.g. ``"1-2"``. Used if `coordinate_move` is not given.

        Raises:
            ValueError: If neither `coordinate_move` nor `str_move` is given.
        """
        if coordinate_move is not None:
            self.coordinate_move = tuple(int(coordinate) for coordinate in coordinate_move)
        elif str_move is not None:
            self.coordinate_move = tuple(int(coordinate) for coordinate in str_move.split("-"))
        else:
            raise ValueError("Give either coordinate_move or str_move.")

    @property
    def str_move(self) -> str:
        """The move as numbers joined by dashes, e.g. ``"1-2"``."""
        return "-".join(map(str, self.coordinate_move))

    def __eq__(self, other: object) -> bool:
        """Check whether two moves have the same coordinates."""
        return isinstance(other, Move) and self.coordinate_move == other.coordinate_move

    def __hash__(self) -> int:
        """Hash the move by its coordinates."""
        return hash(self.coordinate_move)

    def __repr__(self) -> str:
        """Show the move as code that recreates it."""
        return f"Move({self.coordinate_move!r})"
