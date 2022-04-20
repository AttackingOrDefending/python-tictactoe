from tictactoe.egtb import Generator, Reader
import tictactoe


def test_egtb():
    # Generate egtbs.
    two_piece_hash = None
    for index in reversed(range(10)):
        egtb_hash = Generator((3, 3), 3, index).correct_hash
        if index == 2:
            two_piece_hash = egtb_hash

    reader = Reader((3, 3), 3, 2, two_piece_hash)
    board = tictactoe.Board((3, 3), 3)
    board.push((0, 0))
    board.push((0, 1))
    assert reader.index(board) == tictactoe.X

    # Incorrect hash.
    Reader((3, 3), 3, 2, two_piece_hash[:-1] + "0")
