from __future__ import annotations

import numpy as np
from typing import List, Optional

from src.domain import GameStatus, Role


class Node:
    def __init__(self, state, parent: Optional[Node] = None, move=None, rng=None):
        self.state = state
        self.parent = parent
        self.move = move

        self.children: List[Node] = []
        self.visits: int = 0
        self.wins: int = 0
        self.sum_of_squared_results: float = 0.0

        self.proven_status: Optional[GameStatus] = None

        self.untried_moves: list = []
        if self.state.game_status == GameStatus.ONGOING:
            self.untried_moves = sorted(self.state.get_legal_moves())

        self.rng = rng if rng is not None else np.random.default_rng()

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def is_terminal_node(self) -> bool:
        return self.state.game_status != GameStatus.ONGOING

    def expand(self) -> Node:
        move_index = self.rng.integers(0, len(self.untried_moves))
        move = self.untried_moves.pop(move_index)

        next_state = self.state.clone()

        if next_state.turn == Role.POINTER:
            next_state.apply_index(move)
        elif next_state.turn == Role.INSERTER:
            next_state.apply_letter(move)

        child_node = Node(state=next_state, parent=self, move=move, rng=self.rng)
        self.children.append(child_node)

        return child_node

    def update(self, result: GameStatus) -> None:
        self.visits += 1

        player_who_moved = Role.POINTER if self.state.turn == Role.INSERTER else Role.INSERTER

        win_value = 0.0
        if player_who_moved == Role.POINTER and result == GameStatus.P1_WINS_TWINS:
            self.wins += 1
            win_value = 1.0
        elif player_who_moved == Role.INSERTER and result == GameStatus.P2_WINS_LIMIT:
            self.wins += 1
            win_value = 1.0

        self.sum_of_squared_results += win_value * win_value
