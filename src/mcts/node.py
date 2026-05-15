import math
import random
import numpy as np
from typing import List, Optional 
from domain import GameStatus, Role

class Node:
    def __init__(self, state, parent=None, move=None, rng=None):
        self.state = state
        self.parent = parent
        self.move = move

        self.children: List['Node'] = []
        self.visits = 0
        self.wins = 0

        self.untried_moves = []
        if self.state.game_status == GameStatus.ONGOING:
            self.untried_moves = self.state.get_legal_moves()

        self.rng = rng if rng is not None else np.random.default_rng()

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0
    
    def is_terminal_node(self) -> bool:
        return self.state.game_status != GameStatus.ONGOING
    
    def expand(self) -> 'Node':
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
    
    def update(self, result: GameStatus):
        self.visits += 1

        player_who_moved = Role.POINTER if self.state.turn == Role.INSERTER else Role.INSERTE

        if player_who_moved == Role.POINTER and result == GameStatus.P1_WINS_TWINS:
            self.wins += 1
        elif player_who_moved == Role.INSERTER and result == GameStatus.P2_WINS_LIMIT:
            self.wins += 1

    def get_uct_score(self, exploration_constant: float = math.sqrt(2)) -> float:
        if self.visits == 0:
            return float('inf')
        
        exploitation_term = self.wins / self.visits
        exploration_term = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)

        return exploitation_term + exploration_term
        


        
    