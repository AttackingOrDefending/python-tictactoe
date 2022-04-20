from __future__ import annotations
import itertools
import functools
import tictactoe
import numpy
import operator
import re
import hashlib
from typing import Tuple, List, Dict, Optional
import logging

logger = logging.getLogger("tictactoe")

EGTB_X = 0
EGTB_O = 1


class Generator:
    def __init__(self, dimensions: Tuple[int, ...] = (3, 3), x_in_a_row: int = 3, pieces: int = 9) -> None:
        self.dimensions = dimensions
        self.x_in_a_row = x_in_a_row
        self.pieces = pieces
        self.results: List[str] = []
        self.previous_egtb = self.open_previous_egtb()
        self.get_all_board()
        self.correct_hash = self.save_results()

    def save_results(self) -> str:
        logger.debug(f"Saving the EGTB.")
        name = f"{'_'.join(map(str, self.dimensions))}-{self.x_in_a_row}-{self.pieces}.ttb"
        with open(name, "wb") as file:
            for eight_bits in re.findall(r"\d{1,8}", "".join(self.results)):
                eight_bits = eight_bits + (8 - len(eight_bits)) * "0"
                file.write(int.to_bytes(int(eight_bits, 2), 1, "little", signed=False))
        with open(name, "rb") as file:
            file_bytes = file.read()
            sha256_hash = hashlib.sha256(file_bytes).hexdigest()
            logger.debug(f"The sha256 hash of {name} is {sha256_hash}.")
        return sha256_hash

    def open_previous_egtb(self) -> Reader:
        logger.debug(f"Opening previous EGTB (pieces = {self.pieces + 1}).")
        return Reader(self.dimensions, self.x_in_a_row, self.pieces + 1)

    def get_all_board(self) -> None:
        logger.debug(f"Generating the EGTB.")
        total_squares = functools.reduce(operator.mul, self.dimensions)
        empty_squares = total_squares - self.pieces
        number_of_x = self.pieces // 2 + self.pieces % 2
        number_of_o = self.pieces // 2
        initial_board = numpy.array([tictactoe.X] * number_of_x + [tictactoe.O] * number_of_o + [0] * empty_squares)
        for permutation in set(itertools.permutations(initial_board)):
            numpy_board = numpy.array(permutation).reshape(self.dimensions)
            board = tictactoe.Board(self.dimensions, self.x_in_a_row)
            board.board = numpy_board
            board.turn = tictactoe.X if number_of_x == number_of_o else tictactoe.O
            has_x_won = board.has_won(tictactoe.X)
            has_o_won = board.has_won(tictactoe.O)
            if has_x_won and has_o_won:
                continue
            flattened_board = board.board.flatten()
            conversion_dict = {0: "00", 1: "01", 2: "10"}
            fen = "".join(map(lambda piece: conversion_dict[piece], flattened_board))
            if has_x_won:
                result = f"{fen}{EGTB_X}"
                self.results.append(result)
            elif has_o_won:
                result = f"{fen}{EGTB_O}"
                self.results.append(result)
            elif empty_squares == 0:
                continue
            else:
                best_score = None
                scores = []
                for move in board.possible_moves():
                    board_copy = board.copy()
                    board_copy.push(move)
                    score = self.previous_egtb.index(board_copy)
                    if board.turn == score:
                        best_score = score
                        break
                    scores.append(score)
                else:
                    if 0 not in scores:
                        best_score = tictactoe.X if board.turn == tictactoe.O else tictactoe.O
                if best_score:
                    best_score = EGTB_X if best_score == tictactoe.X else EGTB_O
                    result = f"{fen}{best_score}"
                    self.results.append(result)


class Reader:
    def __init__(self, dimensions: Tuple[int, ...] = (3, 3), x_in_a_row: int = 3, pieces: int = 9, verification_hash: Optional[str] = None) -> None:
        self.dimensions = dimensions
        self.x_in_a_row = x_in_a_row
        self.pieces = pieces
        self.verification_hash = verification_hash
        self.ttb: Dict[str, int] = {}
        self.read()

    def read(self) -> None:
        total_squares = functools.reduce(operator.mul, self.dimensions)
        number_of_bits = total_squares * 2 + 1
        if self.pieces > total_squares or self.pieces < 0:
            return

        name = f"{'_'.join(map(str, self.dimensions))}-{self.x_in_a_row}-{self.pieces}.ttb"
        self.verify()
        logger.debug(f"Opening {name}.")
        all_positions = ""
        with open(name, "rb") as file:
            byte = file.read(1)
            while byte:
                position_int = int.from_bytes(byte, "little", signed=False)
                all_positions += bin(position_int)[2:].zfill(8)
                byte = file.read(1)
        positions = [all_positions[i:i + number_of_bits] for i in range(0, len(all_positions), number_of_bits)]
        if positions and len(positions[-1]) != number_of_bits:
            positions.pop(-1)
        for position in positions:
            result = int(position[-1])
            bin_fen = position[:-1]
            self.ttb[bin_fen] = result
        logger.debug(f"Completed reading {name}.")

    def verify(self) -> None:
        if not self.verification_hash:
            return
        logger.debug("Verifying EGTB.")
        name = f"{'_'.join(map(str, self.dimensions))}-{self.x_in_a_row}-{self.pieces}.ttb"
        with open(name, "rb") as file:
            file_bytes = file.read()
            sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        if sha256_hash != self.verification_hash:
            logger.error(f"The calculated sha256 hash of {name} is {sha256_hash}, but the correct one is {self.verification_hash}.")
        else:
            logger.debug("EGTB has no errors.")

    def index(self, board: tictactoe.Board) -> int:
        flattened_board = board.board.flatten()
        conversion_dict = {0: "00", 1: "01", 2: "10"}
        fen = "".join(map(lambda piece: conversion_dict[piece], flattened_board))
        result = self.ttb.get(fen)
        if result == EGTB_X:
            result = tictactoe.X
        elif result == EGTB_O:
            result = tictactoe.O
        else:  # Draw
            result = 0
        return result
