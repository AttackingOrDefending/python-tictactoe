from tictactoe import Board, Move
import numpy


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


def test_copy():
    board = unfinished_board()
    assert board.possible_moves().tolist() == board.copy().possible_moves().tolist()


def test_inbound_outofbounds():
    board = unfinished_board()
    assert board.in_bounds(numpy.array([2, 2]))
    assert board.out_of_bounds(numpy.array([3, 2]))


def test_move():
    assert Move((2, 2)).str_move == "2-2"
    assert Move(str_move="1-2").coordinate_move == (1, 2)


def test_illegal_move():
    board = unfinished_board()
    try:
        board.push((0, 0))
        assert False
    except ValueError:
        assert True


def test_x_and_o_won():
    board = Board()
    board.push((0, 0))
    board.push((1, 0))
    board.push((0, 1))
    board.push((1, 1))
    board.push((0, 2))
    board.push((1, 2))
    try:
        board.result()
        assert False
    except Exception:
        assert True


def test_repr():
    board = Board((2, 2, 2), 2)
    board.push((0, 0, 0))
    board.push((0, 1, 0))
    board.push((0, 0, 1))
    board.push((1, 1, 0))
    board.push((1, 0, 1))
    board.push((1, 0, 0))
    board.push((1, 1, 1))

    correct_repr = """ X | O 
-------
 O | O 
-------
-------
 X | X 
-------
   | X """
    assert correct_repr == str(board)


if __name__ == "__main__":
    test_result()
    test_copy()
    test_inbound_outofbounds()
    test_move()
    test_illegal_move()
    test_repr()
