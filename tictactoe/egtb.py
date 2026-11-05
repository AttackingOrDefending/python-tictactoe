"""Endgame tablebases: who wins every position of a small board when both players play perfectly.

A :class:`Tablebase` solves the whole game once, by working backwards from the full board (retrograde analysis), and
then answers any position instantly. It holds one byte for each of the ``3 ** cells`` ways to fill the board, so it is
meant for small boards: a 3x3 board takes about 20 KB and a few milliseconds, a 4x4 board 43 MB and a few seconds
(with about 220 MB of memory in use while it is solved). Boards with more than :data:`MAX_CELLS` cells are refused.

Example:
    >>> from tictactoe import Board
    >>> from tictactoe.egtb import Tablebase
    >>> tablebase = Tablebase((3, 3), 3)
    >>> tablebase.result(Board((3, 3), 3))  # Tic-tac-toe is a draw.
    0
"""

from __future__ import annotations

import math
import os
from collections.abc import Iterable

import numpy as np
import numpy.typing as npt

from tictactoe import Board, O, X, _winning_lines

__all__ = ["MAX_CELLS", "Tablebase"]

MAX_CELLS = 16
"""The most cells a board can have to get a tablebase. A 4x4 board needs 43 MB; every extra cell triples that."""


class Tablebase:
    """The perfect-play result of every position of a board.

    Results use the same values as :meth:`tictactoe.Board.result`: :data:`tictactoe.X` or :data:`tictactoe.O` if that
    player wins and ``0`` for a draw. The result of a finished game is how it ended.

    Attributes:
        dimensions: The size of the board along each axis.
        x_in_a_row: How many marks in a row are needed to win.
        table: The result of every position, indexed by the position's code: its cells read as the digits of a base 3
            number. Positions that cannot come up in a game (for example, with more O's than X's) are ``0``.
    """

    def __init__(self, dimensions: Iterable[int] = (3, 3), x_in_a_row: int = 3) -> None:
        """Solve every position of a board.

        Args:
            dimensions: The size of the board along each axis.
            x_in_a_row: How many marks in a row are needed to win.

        Raises:
            ValueError: If the board has more than :data:`MAX_CELLS` cells or `x_in_a_row` is smaller than 1.
        """
        self.dimensions = tuple(int(size) for size in dimensions)
        self.x_in_a_row = int(x_in_a_row)
        if x_in_a_row < 1:
            raise ValueError(f"x_in_a_row must be at least 1, not {x_in_a_row}.")
        self.table = _solve(self.dimensions, self.x_in_a_row)

    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> Tablebase:
        """Load a tablebase saved with :meth:`save`.

        Args:
            path: The file to read.

        Returns:
            The tablebase.
        """
        with np.load(path) as data:
            tablebase = cls.__new__(cls)
            tablebase.dimensions = tuple(int(size) for size in data["dimensions"])
            tablebase.x_in_a_row = int(data["x_in_a_row"])
            tablebase.table = data["table"]
        if tablebase.table.shape != (3 ** math.prod(tablebase.dimensions),):
            raise ValueError(f"{path} does not hold a tablebase for a board of size {tablebase.dimensions}.")
        return tablebase

    def save(self, path: str | os.PathLike[str]) -> None:
        """Save the tablebase to a compressed ``.npz`` file.

        Args:
            path: The file to write. NumPy adds ``.npz`` to the name if it is missing.
        """
        np.savez_compressed(path, table=self.table, dimensions=self.dimensions, x_in_a_row=self.x_in_a_row)

    def result(self, board: Board) -> int:
        """Get who wins a position if both players play perfectly.

        Args:
            board: The position. Its size and :attr:`~tictactoe.Board.x_in_a_row` must match the tablebase's.

        Returns:
            :data:`tictactoe.X` or :data:`tictactoe.O` if that player wins and ``0`` for a draw.
        """
        self._check(board)
        return int(self.table[_code(board.board)])

    def best_moves(self, board: Board) -> npt.NDArray[np.intp]:
        """Get every move that keeps the best result for the player to move.

        Args:
            board: The position. Its size and :attr:`~tictactoe.Board.x_in_a_row` must match the tablebase's.

        Returns:
            The coordinates of the best moves, one move per row, in the same format as
            :meth:`tictactoe.Board.possible_moves`. Empty if the game is over.
        """
        self._check(board)
        moves = board.possible_moves()
        if board.result() is not None:
            return moves[:0]
        code = _code(board.board)
        empty = board.board.reshape(-1) == 0
        children = code + board.turn * _place_values(empty.size)[empty]
        best: npt.NDArray[np.intp] = moves[self.table[children] == self.table[code]]
        return best

    def _check(self, board: Board) -> None:
        """Raise a `ValueError` if the board is not one that this tablebase covers."""
        if board.dimensions != self.dimensions or board.x_in_a_row != self.x_in_a_row:
            raise ValueError(
                f"This tablebase is for {self.dimensions} boards with {self.x_in_a_row} in a row, "
                f"not {board.dimensions} boards with {board.x_in_a_row} in a row."
            )


def _place_values(cells: int) -> npt.NDArray[np.int64]:
    """Get what a mark in each cell (in ``board.ravel()`` order) adds to a position's code."""
    return 3 ** np.arange(cells - 1, -1, -1, dtype=np.int64)


def _code(board: npt.NDArray[np.int8]) -> int:
    """Get a position's code: its cells read as the digits of a base 3 number."""
    return int(board.reshape(-1) @ _place_values(board.size))


def _legal_positions(cells: int) -> tuple[npt.NDArray[np.intp], npt.NDArray[np.int8]]:
    """Get the code and the number of marks of every position in which X has made as many moves as O, or one more.

    Other positions can't come up in a game.
    """
    # How many marks every position has, and how many more of them are X's than O's, built up one cell at a time.
    marks = lead = np.zeros(1, dtype=np.int8)
    for _ in range(cells):
        marks = (marks + np.array([[0], [1], [1]], dtype=np.int8)).ravel()
        lead = (lead + np.array([[0], [1], [-1]], dtype=np.int8)).ravel()
    codes = np.flatnonzero((lead == 0) | (lead == 1))
    return codes, marks[codes]


def _solve(dimensions: tuple[int, ...], x_in_a_row: int) -> npt.NDArray[np.int8]:
    """Find the perfect-play result of every position by retrograde analysis.

    Positions are solved in batches by how many marks they have, from the full board down to the empty one, so every
    move leads to a position that is already solved.
    """
    cells = math.prod(dimensions)
    if cells > MAX_CELLS:
        raise ValueError(f"A board with {cells} cells is too big for a tablebase; the limit is {MAX_CELLS}.")
    lines = _winning_lines(dimensions, x_in_a_row)
    place_values = _place_values(cells)
    all_codes, marks = _legal_positions(cells)

    # Scores are from X's point of view: 1 if X wins, -1 if O wins and 0 for a draw.
    scores = np.zeros(3**cells, dtype=np.int8)
    for move_count in range(cells, -1, -1):
        codes = all_codes[marks == move_count]
        positions = np.empty((len(codes), cells), dtype=np.int8)
        for cell, place_value in enumerate(place_values):
            positions[:, cell] = codes // place_value % 3
        x_won = np.zeros(len(codes), dtype=bool)
        o_won = np.zeros(len(codes), dtype=bool)
        for line in lines:
            x_won |= (positions[:, line] == X).all(axis=1)
            o_won |= (positions[:, line] == O).all(axis=1)

        # The player to move picks the move with the best score for them. Here `best` is from their point of view.
        player, sign = (X, 1) if move_count % 2 == 0 else (O, -1)
        best = np.full(len(codes), -1, dtype=np.int8)
        for cell, place_value in enumerate(place_values):
            empty = positions[:, cell] == 0
            best[empty] = np.maximum(best[empty], sign * scores[codes[empty] + player * place_value])

        scores[codes] = np.select([x_won, o_won, positions.all(axis=1)], [1, -1, 0], sign * best)

    # -1 indexes the last entry, so this maps 1 to X, -1 to O and 0 to 0.
    return np.array([0, X, O], dtype=np.int8)[scores]
