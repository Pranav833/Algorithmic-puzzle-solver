from GameAction import GameAction
from GameState import GameState

from time import time
from typing import List
import numpy as np

TIMEOUT = 0.5


class MinimaxAi():

    def __init__(self):
        self.is_player1 = True
        self.global_time = 0


    def get_action(self, state: GameState) -> GameAction:
        self.is_player1 = state.player1_turn

        selected_action: GameAction = None
        self.global_time = time() + TIMEOUT

        row_not_filled = np.count_nonzero(state.row_status == 0)
        column_not_filled = np.count_nonzero(state.col_status == 0)
        for i in range(row_not_filled + column_not_filled):
            
            try:
                actions = self.generate_actions(state)
                x = [self.get_minimax_value(state=self.get_result(state, action), max_depth=i + 1) for action in actions]
                utilities = np.array(x)
                index = np.random.choice(
                    np.flatnonzero(utilities == utilities.max()))
                selected_action = actions[index]
            except TimeoutError:
                break

        return selected_action

    def generate_actions(self, state: GameState) -> List[GameAction]:
        row_positions = self.generate_positions(state.row_status)
        col_positions = self.generate_positions(state.col_status)
        actions: List[GameAction] = []


        for position in row_positions:
            actions.append(GameAction("row", position))
        for position in col_positions:
            actions.append(GameAction("col", position))

        return actions


    def generate_positions(self, matrix: np.ndarray):
        [ny, nx] = matrix.shape
        positions: List[tuple[int, int]] = []

        for y in range(ny):
            for x in range(nx):
                if matrix[y, x] == 0:
                    positions.append((x, y))

        return positions


    def get_result(self, state: GameState, action: GameAction) -> GameState:
        type = action.action_type
        x, y = action.position

        new_state = GameState(
            state.board_status.copy(),
            state.row_status.copy(),
            state.col_status.copy(),
            state.player1_turn,
        )

        player_modifier = -1 if new_state.player1_turn else 1

        is_point_scored = False
        val = 1

        [ny, nx] = new_state.board_status.shape


        if y < ny and x < nx:
            new_state.board_status[y, x] = (
                abs(new_state.board_status[y, x]) + val
            ) * player_modifier
            if abs(new_state.board_status[y, x]) == 4:
                is_point_scored = True


        if type == "row":
            new_state.row_status[y, x] = 1
            if y > 0:
                new_state.board_status[y - 1, x] = (
                    abs(new_state.board_status[y - 1, x]) + val
                ) * player_modifier
                if abs(new_state.board_status[y - 1, x]) == 4:
                    is_point_scored = True


        elif type == "col":
            new_state.col_status[y, x] = 1
            if x > 0:
                new_state.board_status[y, x - 1] = (
                    abs(new_state.board_status[y, x - 1]) + val
                ) * player_modifier
                if abs(new_state.board_status[y, x - 1]) == 4:
                    is_point_scored = True

        new_state = new_state._replace(
            player1_turn=not (new_state.player1_turn ^ is_point_scored)
        )

        return new_state

    def get_minimax_value(
        self,
        state: GameState,
        depth: int = 0,
        max_depth: int = 0,
        alpha: float = -np.inf,
        beta: float = np.inf,
    ) -> float:
        if time() >= self.global_time:
            raise TimeoutError()

        if self.terminal_test(state) or depth == max_depth:
            return self.get_heuristic(state)

    
        if self.is_player1 == state.player1_turn:
            value = -np.inf
            actions = self.generate_actions(state)
            for action in actions:
                value = max(
                    value,
                    self.get_minimax_value(
                        self.get_result(state, action),
                        depth=depth + 1,
                        max_depth=max_depth,
                        alpha=alpha,
                        beta=beta
                    ),
                )
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = np.inf
            actions = self.generate_actions(state)
            for action in actions:
                value = min(
                    value,
                    self.get_minimax_value(
                        self.get_result(state, action),
                        depth=depth + 1,
                        max_depth=max_depth,
                        alpha=alpha,
                        beta=beta
                    ),
                )
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value


    def terminal_test(self, state: GameState) -> bool:
        return np.all(state.row_status == 1) and np.all(state.col_status == 1)

    def get_heuristic(self, state: GameState) -> float:
        [ny, nx] = state.board_status.shape
        utility = 0


        box_won = 0
        box_lost = 0
        for y in range(ny):
            for x in range(nx):
                if self.is_player1:
                    if state.board_status[y, x] == -4:
                        utility += 1
                        box_won += 1
                    elif state.board_status[y, x] == 4:
                        utility -= 1
                        box_lost += 1
                else:
                    if state.board_status[y, x] == -4:
                        utility -= 1
                        box_lost += 1
                    elif state.board_status[y, x] == 4:
                        utility += 1
                        box_won += 1

        if box_won >= 5:
            utility = np.inf
        elif box_lost >= 5:
            utility = -np.inf

        return utility