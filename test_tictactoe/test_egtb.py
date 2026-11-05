import numpy as np
import pytest

from tictactoe import Board, O, X
from tictactoe.egtb import MAX_CELLS, Tablebase


def minimax_all(dimensions, x_in_a_row):
    """The perfect-play result of every reachable position, found by searching the game tree."""
    results = {}

    def solve(board):
        key = board.board.tobytes()
        if key not in results:
            result = board.result()
            if result is None:
                outcomes = set()
                for move in board.possible_moves():
                    child = board.copy()
                    child.push(move)
                    outcomes.add(solve(child))
                opponent = O if board.turn == X else X
                result = board.turn if board.turn in outcomes else 0 if 0 in outcomes else opponent
            results[key] = (board, result)
        return results[key][1]

    solve(Board(dimensions, x_in_a_row))
    return list(results.values())


@pytest.fixture(scope="module")
def tablebase():
    return Tablebase((3, 3), 3)


def test_tablebase(tablebase):
    board = Board((3, 3), 3)
    assert tablebase.result(board) == 0
    board.push((0, 0))
    board.push((0, 1))
    assert tablebase.result(board) == X


@pytest.mark.parametrize(
    ("dimensions", "x_in_a_row"), [((3, 3), 3), ((2, 2), 2), ((2, 2, 2), 2), ((3, 4), 3), ((5,), 3), ((2, 3), 3), ((1,), 1)]
)
def test_matches_minimax(dimensions, x_in_a_row):
    tablebase = Tablebase(dimensions, x_in_a_row)
    for board, result in minimax_all(dimensions, x_in_a_row):
        assert tablebase.result(board) == result


def test_best_moves(tablebase):
    for board, result in minimax_all((3, 3), 3):
        best = {tuple(move) for move in tablebase.best_moves(board).tolist()}
        if board.result() is not None:
            assert not best
            continue
        assert best
        for move in board.possible_moves():
            child = board.copy()
            child.push(move)
            assert (tablebase.result(child) == result) == (tuple(move) in best)


def test_save_and_load(tablebase, tmp_path):
    path = tmp_path / "3x3.npz"
    tablebase.save(path)
    loaded = Tablebase.load(path)
    assert loaded.dimensions == (3, 3)
    assert loaded.x_in_a_row == 3
    assert np.array_equal(loaded.table, tablebase.table)


def test_load_wrong_file(tmp_path):
    path = tmp_path / "wrong.npz"
    np.savez(path, table=np.zeros(10, dtype=np.int8), dimensions=(3, 3), x_in_a_row=3)
    with pytest.raises(ValueError):
        Tablebase.load(path)


def test_wrong_board(tablebase):
    with pytest.raises(ValueError):
        tablebase.result(Board((3, 3), 2))
    with pytest.raises(ValueError):
        tablebase.best_moves(Board((3, 4), 3))


def test_limits():
    with pytest.raises(ValueError):
        Tablebase((MAX_CELLS + 1,), 3)
    with pytest.raises(ValueError):
        Tablebase((3, 3), 0)
