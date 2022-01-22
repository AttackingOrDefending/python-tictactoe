from tictactoe import Board


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


def test_result():
    assert x_win_board().result() == 1
    assert o_win_board().result() == 2
    assert draw_board().result() == 0
    assert unfinished_board().result() is None


if __name__ == "__main__":
    test_result()
