from __future__ import annotations
import itertools
import numpy
from typing import List, Tuple, Iterable, Optional

X = 1
O = 2


class Board:
    def __init__(self, dimensions: Tuple[int, ...] = (3, 3), x_in_a_row: int = 3) -> None:
        self.dimensions = dimensions
        self.x_in_a_row = x_in_a_row
        self.board = self.create_board()
        self._directions = self.find_directions()
        self.move_count = 0
        self.moves: List[Move] = []
        self.x: List[Move] = []
        self.o: List[Move] = []
        self.turn = X

    def create_board(self) -> numpy.ndarray:
        return numpy.zeros(self.dimensions)

    def copy(self) -> Board:
        board = Board(self.dimensions, self.x_in_a_row)
        board.turn = self.turn
        board.board = self.board.copy()
        return board

    def get_mark_at_position(self, position: Iterable[int]) -> int:
        position = tuple(position)
        return self.board[position]

    def set_mark(self, coordinates: Tuple[int, ...], player: int) -> None:
        self.board[coordinates] = player
        if player == X:
            self.x.append(Move(coordinates))
        else:
            self.o.append(Move(coordinates))

    def is_empty(self, position):
        return self.get_mark_at_position(position) == 0

    def push(self, coordinates: Iterable[int]) -> None:
        coordinates = tuple(coordinates)
        if not self.is_empty(coordinates):
            raise ValueError("Position is not empty.")
        move = Move(coordinates)
        self.set_mark(coordinates, self.turn)
        self.turn = X if self.turn == O else O
        self.moves.append(move)
        self.move_count += 1

    def find_directions(self) -> List[Tuple[int, ...]]:
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

    def possible_moves(self) -> numpy.ndarray:
        return numpy.argwhere(self.board == 0)

    def out_of_bounds(self, pos: numpy.ndarray) -> numpy.bool_:
        return (pos < 0).any() or (pos >= self.dimensions).any()

    def in_bounds(self, pos: numpy.ndarray) -> bool:
        return not self.out_of_bounds(pos)

    def has_won(self, player: int) -> bool:
        positions = numpy.argwhere(self.board == player)
        for position in positions:
            for direction in self._directions:
                for in_a_row in range(1, self.x_in_a_row):
                    pos = position + numpy.multiply(direction, in_a_row)
                    if self.out_of_bounds(pos) or self.board[tuple(pos)] != player:
                        break
                else:
                    return True
        return False

    def result(self) -> Optional[int]:
        if self.has_won(X):
            return X
        elif self.has_won(O):
            return O
        elif self.board.all():
            return 0
        return None


class Move:
    def __init__(self, coordinate_move: Optional[Tuple[int, ...]] = None, str_move: Optional[str] = None) -> None:
        assert coordinate_move or str_move
        self.coordinate_move = coordinate_move
        self.str_move = str_move
        if self.coordinate_move:
            self.str_move = "-".join(map(str, tuple(self.coordinate_move)))
        elif self.str_move:
            self.coordinate_move = tuple(map(int, self.str_move.split("-")))
