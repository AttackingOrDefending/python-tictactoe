# Changelog

## 0.1.0 (unreleased)

### Breaking changes

- Python 3.11 or newer is required (3.6 to 3.10 are end-of-life), along with NumPy 2.0 or newer.
- `tictactoe.egtb` has been rewritten. `Generator`, `Reader` and the `.ttb` files (one per number of pieces) are
  replaced by `Tablebase`, which solves every position of a board in one go and saves to a single `.npz` file. It is
  hundreds of times faster (a 3x3 board takes milliseconds instead of a second) and handles boards up to 16 cells,
  such as 4x4.
- `Board.find_directions()` returns a NumPy array instead of a list of tuples.
- `Board.result()` raises `ValueError` (instead of a bare `Exception`) when both players have a line.
- `Board.push()` raises `ValueError` for coordinates that are not on the board. Negative coordinates used to wrap
  around to the other side.
- `Board(x_in_a_row=0)` raises `ValueError`.
- `Move()` without arguments raises `ValueError` instead of `AssertionError`. `Move.str_move` is now read-only and
  always in the normalized `"1-2"` form.

### New

- `Tablebase.best_moves()` returns every move that keeps the best result.
- `Move` objects can be compared with `==`, hashed and printed.
- Documentation at <https://python-tictactoe.readthedocs.io/>.

### Fixes

- `Board.copy()` copies the move history (`moves`, `x`, `o` and `move_count`) instead of resetting it.

### Performance

- Checking for a win is vectorized with NumPy: every line on the board is computed once per board size and checked in
  one step. `Board.result()` is about 10 times faster on a 3x3 board and hundreds of times faster on big boards.
- `Board.copy()` and `Board.push()` are faster.
