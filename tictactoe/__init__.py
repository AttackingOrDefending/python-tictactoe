from __future__ import annotations
import itertools
import numpy as np
import numpy.typing as npt
from typing import List, Tuple, Iterable, Optional, Union

__author__ = "AttackingOrDefending"
__copyright__ = "2022, " + __author__
__version__ = "0.0.6"


_all_numpy_int_types = Union[np.int8, np.int16, np.int32, np.int64]

X = 1
O = 2


class Board:
    def __init__(self, dimensions: Iterable[int] = (3, 3), x_in_a_row: int = 3) -> None:
        """
        TicTacToe board.
        :param dimensions: The dimensions of the board.
        :param x_in_a_row: How many marks in a row are needed to win.
        """
        self.dimensions = tuple(dimensions)
        self.x_in_a_row = x_in_a_row
        self.board = self.create_board()
        self._directions = self.find_directions()
        self.move_count = 0
        self.moves: List[Move] = []
        self.x: List[Move] = []
        self.o: List[Move] = []
        self.turn = X

    def create_board(self) -> npt.NDArray[np.int8]:
        """
        Create the board state.
        :return: A `numpy.ndarray` filled with 0s.
        """
        return np.zeros(self.dimensions, dtype=np.int8)

    def copy(self) -> Board:
        """
        Get a copy of the board.
        :return: A copy of the board.
        """
        board = Board(self.dimensions, self.x_in_a_row)
        board.turn = self.turn
        board.board = self.board.copy()
        return board

    def get_mark_at_position(self, position: Iterable[int]) -> int:
        """
        Get the mark at a position.
        :param position: The position to check.
        :return: The player that has a mark at the position.
        """
        position = tuple(position)
        return int(self.board[position])

    def set_mark(self, coordinates: Iterable[int], player: int) -> None:
        """
        Set a mark at a position.
        :param coordinates: The position to add a mark at.
        :param player: The player that put the mark at the position.
        """
        self.board[tuple(coordinates)] = player
        if player == X:
            self.x.append(Move(coordinates))
        else:
            self.o.append(Move(coordinates))

    def is_empty(self, position: Iterable[int]) -> bool:
        """
        Get if a position is empty.
        :param position: The position to check.
        :return: If the position is empty.
        """
        return self.get_mark_at_position(position) == 0

    def push(self, coordinates: Iterable[int]) -> None:
        """
        Push a move.
        :param coordinates: The position to add a mark at.
        """
        coordinates = tuple(coordinates)
        if not self.is_empty(coordinates):
            raise ValueError("Position is not empty.")
        move = Move(coordinates)
        self.set_mark(coordinates, self.turn)
        self.turn = X if self.turn == O else O
        self.moves.append(move)
        self.move_count += 1

    def find_directions(self) -> List[Tuple[int, ...]]:
        """
        Get directions to be used when checking for a win.
        :return: The directions to check for a win.
        """
        directions = list(itertools.product([1, 0, -1], repeat=len(self.dimensions)))
        correct_directions = []
        for direction in directions:
            for item in direction:
                if item > 0:
                    correct_directions.append(direction)
                    break
                elif item < 0:
                    break
        return correct_directions

    def possible_moves(self) -> npt.NDArray[np.int64]:
        """
        Get all possible moves.
        :return: All the positions where there is no mark.
        """
        return np.argwhere(self.board == 0)

    def out_of_bounds(self, pos: npt.NDArray[_all_numpy_int_types]) -> np.bool_:
        """
        Get if a position is out of the board.
        :param pos: The position to check.
        :return: If the position is out of the board.
        """
        return (pos < 0).any() or (pos >= self.dimensions).any()

    def in_bounds(self, pos: npt.NDArray[_all_numpy_int_types]) -> bool:
        """
        Get if a position is inside the board.
        :param pos: The position to check.
        :return: If the position is inside the board.
        """
        return not self.out_of_bounds(pos)

    def has_won(self, player: int) -> bool:
        """
        Get if a player has won.
        :param player: The player to check.
        :return: If the player has won.
        """
        positions = np.argwhere(self.board == player)
        for position in positions:
            for direction in self._directions:
                for in_a_row in range(1, self.x_in_a_row):
                    pos = position + np.multiply(direction, in_a_row)
                    if self.out_of_bounds(pos) or self.board[tuple(pos)] != player:
                        break
                else:
                    return True
        return False

    def result(self) -> Optional[int]:
        """
        Get the result of the game.
        :return: The result of the board.
        """
        x_won = self.has_won(X)
        o_won = self.has_won(O)
        if x_won and o_won:
            raise Exception(f"Both X and O have {self.x_in_a_row} pieces in a row.")
        elif x_won:
            return X
        elif o_won:
            return O
        elif self.board.all():
            return 0
        return None

    def _get_dimension_repr(self, board_partition: npt.NDArray[np.int8]) -> str:
        """
        Get a visual representation of a part of the board.
        :param board_partition: A part of the board.
        :return: A visual representation of a part of the board.
        """
        if len(board_partition.shape) > 1:
            board_repr = ""
            divider = ((board_partition.shape[0] * 4 - 1) * "-" + "\n") * (len(board_partition.shape) - 1)
            for board_partition_index in range(board_partition.shape[-1]):
                board_repr += self._get_dimension_repr(board_partition[..., board_partition_index]) + "\n"
                board_repr += divider
            board_repr = board_repr[:-(len(divider) + 1)]
            return board_repr
        else:
            row = ""
            for item in board_partition:
                mark = "O" if item == O else ("X" if item == X else " ")
                row += f" {mark} |"
            row = row[:-1]
            return row

    def __repr__(self) -> str:
        """
        Get a visual representation of the board.
        :return: A visual representation of the board.
        """
        return self._get_dimension_repr(self.board)


class Move:
    def __init__(self, coordinate_move: Optional[Iterable[int]] = None, str_move: Optional[str] = None) -> None:
        """
        Convert a move to other types.
        :param coordinate_move: A `tuple` with the position of the move.
        :param str_move: A move that is in a human-readable format.
        """
        assert coordinate_move or str_move
        self.coordinate_move = coordinate_move
        self.str_move = str_move
        if self.coordinate_move:
            self.str_move = "-".join(map(str, tuple(self.coordinate_move)))
        elif self.str_move:
            self.coordinate_move = tuple(map(int, self.str_move.split("-")))
