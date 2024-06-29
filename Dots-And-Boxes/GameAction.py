from typing import NamedTuple, Literal, Tuple


class GameAction(NamedTuple):

    action_type: Literal["row", "col"]
    position: Tuple[int, int]
