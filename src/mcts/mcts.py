import numpy as np
import math
from domain import GameStatus, Role
from engine.game import Game
from mcts.node import Node

class MCTS:
    def __init__(self, iterations: int = 100, exploratoin_cost: float = math.sqrt(2), rng=None):
        self.iterations = iterations
        self.exploration_cost = self.exploration_cost
        self.rng = rng if rng is not None else np.random.default_rng()

    def search(self, initial_state: Game) -> object:
        root = Node(initial_state.clone(), rng=self.rng)

        for _ in range(self.iterations):
            node = self._select(root)

            if (not node.is_terminal_node()) and (not node.is_fully_expanded()):
                node.expand()

            simulation_result = self._simulate(node.state)

            self._backpropagate(node, simulation_result)
        return self._get_best_move(root)

    def _select(self, node: Node) -> Node:
        while (not node.is_terminal_node()) and node.is_fully_expanded():
            node = max(node.children, key=lambda child: child.get_uct_score(self.exploration_cost))
        return node
    
    def _simulate(self, game: Game) -> GameStatus:
        current_game = game.clone()

        while current_game.game_status == GameStatus.ONGOING:
            legal_moves = current_game.get_legal_moves()

            if not legal_moves:
                break

            move_ind = self.rng.integers(0, len(legal_moves))
            move = legal_moves[move_ind]

            if current_game.turn == Role.POINTER:
                current_game.apply_index(move)
            elif current_game.turn == Role.INSERTER:
                current_game.apply_letter(move)
            
        return current_game.game_status

    def _backpropagate(self, node: Node, result: GameStatus):
        while node is not None:
            node.update(result)
            node = node.parent

    def _get_best_move(self, root: Node):
        if root.children is None:
            raise Exception("Root has no children")
        
        return max(root.children, key=lambda child: child.get_uct_score(self.exploration_cost))