import itertools
import math
import random

import numpy as np
import pytest

from tictactoe import Board, Move, O, X


def draw_board():
    board = Board()
    board.push((0, 0))
    board.push((0, 1))
    board.push((0, 2))
    board.push((1, 1))
    board.push((1, 0))
    board.push((2, 0))
    board.push((1, 2))
    board.push((2, 2))
    board.push((2, 1))
    return board


def x_win_board():
    board = Board()
    board.push((0, 0))
    board.push((0, 1))
    board.push((0, 2))
    board.push((1, 1))
    board.push((1, 0))
    board.push((1, 2))
    board.push((2, 0))
    return board


def o_win_board():
    board = Board()
    board.push((0, 0))
    board.push((0, 1))
    board.push((0, 2))
    board.push((1, 1))
    board.push((1, 0))
    board.push((2, 0))
    board.push((1, 2))
    board.push((2, 1))
    return board


def unfinished_board():
    board = Board()
    board.push((0, 0))
    board.push((0, 1))
    board.push((0, 2))
    board.push((1, 1))
    board.push((1, 0))
    board.push((2, 0))
    board.push((1, 2))
    board.push((2, 2))
    return board


def reference_lines(dimensions, x_in_a_row):
    """Every line on the board, found by walking from every cell in every direction."""
    lines = set()
    for direction in itertools.product([1, 0, -1], repeat=len(dimensions)):
        if not any(direction) or next(step for step in direction if step) < 0:
            continue  # Skip the zero vector and one of each pair of opposite directions.
        for start in itertools.product(*map(range, dimensions)):
            cells = [tuple(s + i * d for s, d in zip(start, direction, strict=True)) for i in range(x_in_a_row)]
            if all(0 <= c < n for cell in cells for c, n in zip(cell, dimensions, strict=True)):
                lines.add(tuple(int(np.ravel_multi_index(cell, dimensions)) for cell in cells))
    return lines


def reference_has_won(board, player):
    flat = board.board.reshape(-1)
    return any(all(flat[cell] == player for cell in line) for line in reference_lines(board.dimensions, board.x_in_a_row))


CONFIGURATIONS = [
    ((3, 3), 3),
    ((4, 5), 3),
    ((4, 5), 4),
    ((7,), 3),
    ((3, 3, 3), 3),
    ((2, 3, 4), 2),
    ((3, 2, 2, 3), 2),
    ((3, 3), 1),
    ((3, 3), 4),
    ((2, 5), 3),
]


def test_result():
    assert x_win_board().result() == X
    assert o_win_board().result() == O
    assert draw_board().result() == 0
    assert unfinished_board().result() is None
    assert Board().result() is None


def test_copy():
    board = unfinished_board()
    copy = board.copy()
    assert board.possible_moves().tolist() == copy.possible_moves().tolist()
    assert (copy.turn, copy.move_count, copy.moves, copy.x, copy.o) == (
        board.turn,
        board.move_count,
        board.moves,
        board.x,
        board.o,
    )

    copy.push((2, 1))
    assert board.is_empty((2, 1))
    assert board.move_count == 8
    assert len(board.moves) == 8
    assert len(board.x) == 4
    assert board.turn == X


def test_inbound_outofbounds():
    board = unfinished_board()
    assert board.in_bounds(np.array([2, 2]))
    assert board.out_of_bounds(np.array([3, 2]))
    assert board.out_of_bounds((-1, 0))
    assert board.out_of_bounds((0, 0, 0))
    assert board.in_bounds([0, 0])


def test_move():
    assert Move((2, 2)).str_move == "2-2"
    assert Move(str_move="1-2").coordinate_move == (1, 2)
    assert Move(np.array([1, 2])) == Move(str_move="1-2")
    assert Move((1, 2)) != Move((2, 1))
    assert len({Move((1, 2)), Move(str_move="1-2")}) == 1
    assert repr(Move((1, 2))) == "Move((1, 2))"
    with pytest.raises(ValueError):
        Move()


def test_illegal_move():
    board = unfinished_board()
    with pytest.raises(ValueError, match="not empty"):
        board.push((0, 0))
    for position in [(3, 0), (-1, 0), (0, 0, 0), (0,)]:
        with pytest.raises(ValueError, match="not on a board"):
            board.push(position)
    assert board.move_count == 8


def test_invalid_x_in_a_row():
    with pytest.raises(ValueError):
        Board((3, 3), 0)


def test_x_and_o_won():
    board = Board()
    board.push((0, 0))
    board.push((1, 0))
    board.push((0, 1))
    board.push((1, 1))
    board.push((0, 2))
    board.push((1, 2))
    with pytest.raises(ValueError):
        board.result()


def test_push_history():
    board = Board()
    board.push((1, 1))
    board.push(np.array([0, 2]))
    assert board.turn == X
    assert board.move_count == 2
    assert board.moves == [Move((1, 1)), Move((0, 2))]
    assert board.x == [Move((1, 1))]
    assert board.o == [Move((0, 2))]
    assert board.get_mark_at_position((1, 1)) == X
    assert board.get_mark_at_position((0, 2)) == O
    assert board.is_empty((0, 0))
    assert len(board.possible_moves()) == 7


def test_set_mark():
    board = Board()
    board.set_mark((2, 2), O)
    board.set_mark((0, 0), X)
    assert board.get_mark_at_position((2, 2)) == O
    assert board.o == [Move((2, 2))]
    assert board.x == [Move((0, 0))]
    assert board.turn == X
    assert board.move_count == 0


@pytest.mark.parametrize("ndim", [1, 2, 3, 4])
def test_find_directions(ndim):
    directions = Board((3,) * ndim).find_directions()
    assert directions.shape == ((3**ndim - 1) // 2, ndim)
    vectors = {tuple(direction) for direction in directions}
    opposites = {tuple(-direction) for direction in directions}
    assert len(vectors) == len(directions)
    assert not vectors & opposites
    assert vectors | opposites == set(itertools.product([1, 0, -1], repeat=ndim)) - {(0,) * ndim}


@pytest.mark.parametrize(("dimensions", "x_in_a_row"), CONFIGURATIONS)
def test_winning_lines(dimensions, x_in_a_row):
    lines = Board(dimensions, x_in_a_row)._lines
    assert set(map(tuple, lines.tolist())) == reference_lines(dimensions, x_in_a_row)


@pytest.mark.parametrize(("dimensions", "x_in_a_row"), CONFIGURATIONS)
def test_has_won(dimensions, x_in_a_row):
    rng = random.Random(0)
    cells = math.prod(dimensions)
    for _ in range(50):
        board = Board(dimensions, x_in_a_row)
        board.board = np.array(rng.choices([0, X, O], k=cells), dtype=np.int8).reshape(dimensions)
        for player in (X, O):
            assert board.has_won(player) == reference_has_won(board, player)


def test_random_games():
    rng = random.Random(1)
    for dimensions, x_in_a_row in CONFIGURATIONS:
        for _ in range(5):
            board = Board(dimensions, x_in_a_row)
            while board.result() is None:
                moves = board.possible_moves()
                board.push(moves[rng.randrange(len(moves))])
            assert board.move_count == len(board.moves) == len(board.x) + len(board.o)
            if board.result() == 0:
                assert not board.possible_moves().size


def test_repr():
    board = Board((2, 2, 2), 2)
    board.push((0, 0, 0))
    board.push((0, 1, 0))
    board.push((0, 0, 1))
    board.push((1, 1, 0))
    board.push((1, 0, 1))
    board.push((1, 0, 0))
    board.push((1, 1, 1))

    correct_repr = "\n".join([" X | O ", "-------", " O | O ", "-------", "-------", " X | X ", "-------", "   | X "])
    assert correct_repr == str(board)


def test_repr_2d():
    board = Board((3, 2), 3)
    board.push((0, 0))
    board.push((2, 1))
    assert str(board) == " X |   |   \n-----------\n   |   | O "
