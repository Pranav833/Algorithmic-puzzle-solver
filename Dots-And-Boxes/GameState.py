from typing import NamedTuple
from numpy import ndarray


class GameState(NamedTuple):

    board_status: ndarray
    row_status: ndarray
    col_status: ndarray
    player1_turn: bool
