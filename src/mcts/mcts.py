from __future__ import annotations

import numpy as np

from src.domain import GameStatus, Role
from src.engine.game import Game
from src.mcts.node import Node
from src.mcts.config import MCTSConfig

class MCTS:
    def __init__(
        self,
        iterations: int,
        selection: SelectionStrategy,
        simulation: SimulationStrategy,
        backpropagation: BackpropagationStrategy,
        rng: np.random.Generator | None = None,
    ):
        self.iterations = iterations
        self.selection = selection
        self.simulation = simulation
        self.backpropagation = backpropagation
        self.rng = rng if rng is not None else np.random.default_rng()

    def get_best_move(self, initial_state: Game) -> object:
        root = Node(initial_state.clone(), rng=self.rng)

        for _ in range(self.iterations):
            if MCTSConfig.USE_SOLVER and root.proven_winner is not None:
                break
            
            node = self._select(root)

            if (not node.is_terminal_node()) and (not node.is_fully_expanded()):
                node = node.expand()

            result = self.simulation.simulate(node.state, self.rng)
            self.backpropagation.backpropagate(node, result)

        if not root.children:
            return None
        return self._get_best_move(root).move

    def _select(self, node: Node) -> Node:
        while (not node.is_terminal_node()) and node.is_fully_expanded():
            proven = self._pick_proven_child(node)
            if proven is not None:
                node = proven
            else:
                node = max(
                    node.children, key=lambda child: self.selection.score(child)
                )
        return node

    @staticmethod
    def _pick_proven_child(node: Node) -> Node | None:
        """If any child is a proven win for the current mover, return it."""
        if not node.children:
            return None
        mover = node.state.turn
        for child in node.children:
            if child.proven_status is not None and child.proven_status != GameStatus.ONGOING:
                if mover == Role.POINTER and child.proven_status == GameStatus.P1_WINS_TWINS:
                    return child
                if mover == Role.INSERTER and child.proven_status == GameStatus.P2_WINS_LIMIT:
                    return child
        return None

    @staticmethod
    def _get_best_move(root: Node) -> Node:
        if not root.children:
            raise RuntimeError("Root has no children")
        return max(root.children, key=lambda child: child.visits)
    
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
