import numpy as np
import math
from src.domain import GameStatus, Role
from src.engine.game import Game
from src.mcts.node import Node
from src.mcts.config import MCTSConfig

class MCTS:
    def __init__(self, iterations: int = 100, exploration_cost: float = math.sqrt(2), rng=None):
        self.iterations = iterations
        self.exploration_cost = exploration_cost
        self.rng = rng if rng is not None else np.random.default_rng()

    def get_best_move(self, initial_state: Game) -> object:
        root = Node(initial_state.clone(), rng=self.rng)

        for _ in range(self.iterations):
            if MCTSConfig.USE_SOLVER and root.proven_winner is not None:
                break
            
            node = self._select(root)

            if (not node.is_terminal_node()) and (not node.is_fully_expanded()):
                node.expand()

            simulation_result = self._simulate(node.state)

            self._backpropagate(node, simulation_result)
        
        if not root.children:
            return None
        return self._get_best_move(root).move

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
        winner = None
        if result == GameStatus.P1_WINS_TWINS:
            winner = Role.POINTER
        elif result == GameStatus.P2_WINS_LIMIT:
            winner = Role.INSERTER

        while node is not None:
            node.update(result)
            
            if MCTSConfig.USE_SOLVER and node.proven_winner is None:
                if node.is_terminal_node():
                    node.proven_winner = winner
                else:
                    current_turn = node.state.turn
                    other_turn = Role.INSERTER if current_turn == Role.POINTER else Role.POINTER
                    
                    if any(c.proven_winner == current_turn for c in node.children):
                        node.proven_winner = current_turn
                    elif node.is_fully_expanded() and all(c.proven_winner == other_turn for c in node.children):
                        node.proven_winner = other_turn
                        
            node = node.parent

    def _get_best_move(self, root: Node):
        if root.children is None:
            raise Exception("Root has no children")
        
        return max(root.children, key=lambda child: child.get_uct_score(self.exploration_cost))