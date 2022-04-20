from tictactoe.egtb import Generator, Reader
import tictactoe


def test_egtb():
    # Generate EGTBs.
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
    with open("3_3-3-2.ttb", "rb") as file:
        file_bytes = file.read()
    incorrect_file_bytes = file_bytes[:-1] + b"\x81"
    with open("3_3-3-2.ttb", "wb") as file:
        file.write(incorrect_file_bytes)
    Reader((3, 3), 3, 2, two_piece_hash)
    with open("3_3-3-2.ttb", "wb") as file:
        file.write(file_bytes)
